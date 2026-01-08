"""
Quarm Charm Calculator - Flask Web Server

A web interface for calculating charm effectiveness and break probabilities
based on the EQMacEmu (Quarm) server resist mechanics.
"""

from flask import Flask, render_template, request, jsonify
from charm_calculator import CharmCalculator
from charm_spells_data import get_all_charm_spells, get_player_charm_spells
from log_parser import CharmLogParser
from werkzeug.utils import secure_filename
import os
import zipfile
import io

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB max file size
calculator = CharmCalculator()


@app.route('/')
def index():
    """Serve the main calculator page."""
    response = app.make_response(render_template('index.html'))
    # Prevent browser caching for development
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.route('/api/calculate', methods=['POST'])
def calculate():
    """
    API endpoint to calculate charm probabilities.

    Expected JSON payload:
    {
        "caster_level": int,
        "target_level": int,
        "target_mr": int,
        "pet_mr_items": int (optional, default 0 - total -MR from debuffs and items),
        "resist_diff": int,
        "caster_charisma": int (optional, default 75),
        "is_enchanter": bool (optional, default true - only enchanters get CHA bonus!),
        "num_ticks": int (optional, default 100),
        "num_simulations": int (optional, default 10000)
    }
    """
    try:
        data = request.get_json()

        # Required parameters
        caster_level = int(data.get('caster_level'))
        target_level = int(data.get('target_level'))
        target_mr = int(data.get('target_mr'))
        resist_diff = int(data.get('resist_diff'))

        # Optional parameters
        pet_mr_items = int(data.get('pet_mr_items', 0))
        caster_charisma = int(data.get('caster_charisma', 75))
        is_enchanter = bool(data.get('is_enchanter', True))
        num_ticks = int(data.get('num_ticks', 100))
        num_simulations = int(data.get('num_simulations', 10000))

        # Validate inputs
        if not (1 <= caster_level <= 60):
            return jsonify({'error': 'Caster level must be between 1 and 60'}), 400
        if not (1 <= target_level <= 65):
            return jsonify({'error': 'Target level must be between 1 and 65'}), 400
        if not (-200 <= target_mr <= 500):
            return jsonify({'error': 'Target MR must be between -200 and 500'}), 400
        if not (0 <= pet_mr_items <= 200):
            return jsonify({'error': 'Pet MR items must be between 0 and 200'}), 400
        if not (10 <= caster_charisma <= 300):
            return jsonify({'error': 'Caster charisma must be between 10 and 300'}), 400
        if not (1 <= num_ticks <= 1000):
            return jsonify({'error': 'Number of ticks must be between 1 and 1000'}), 400
        if not (100 <= num_simulations <= 100000):
            return jsonify({'error': 'Number of simulations must be between 100 and 100000'}), 400

        # Calculate initial land chance (uses base MR, before pet items)
        initial_land = calculator.calculate_initial_land_chance(
            caster_level, target_level, target_mr, resist_diff, caster_charisma, is_enchanter
        )

        # Calculate charm break probabilities over time
        # Uses effective MR after applying -MR debuffs and giving pet -MR items (lower MR = less likely to break)
        effective_mr = target_mr - pet_mr_items
        break_prob = calculator.calculate_charm_break_probability(
            caster_level, target_level, effective_mr, resist_diff,
            caster_charisma, is_enchanter, num_ticks, num_simulations
        )

        return jsonify({
            'success': True,
            'initial_land_chance': initial_land,
            'break_probability': break_prob
        })

    except ValueError as e:
        return jsonify({'error': f'Invalid input: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@app.route('/api/spell_presets', methods=['GET'])
def spell_presets():
    """Get available charm spell presets."""
    spells = get_player_charm_spells()
    # Format for the UI
    formatted_spells = {}
    for spell in sorted(spells, key=lambda x: (x['classes'][0], x.get('spell_level', 0))):
        class_name = spell['classes'][0]
        if class_name not in formatted_spells:
            formatted_spells[class_name] = []

        special = []
        if spell.get('animal_only'):
            special.append("Animals Only")
        if spell.get('undead_only'):
            special.append("Undead Only")

        formatted_spells[class_name].append({
            'id': spell['id'],
            'name': spell['name'],
            'level': spell.get('spell_level'),
            'resist_diff': spell['resist_diff'],
            'max_level': spell['max_level'],
            'special': special
        })

    return jsonify({
        'success': True,
        'spells': formatted_spells
    })


@app.route('/api/analyze_log', methods=['POST'])
def analyze_log():
    """
    Analyze an uploaded EQ log file for charm duration statistics.

    Expects a file upload with key 'logfile'.
    Returns statistics about charm durations found in the log.
    """
    try:
        # Check if file was uploaded
        if 'logfile' not in request.files:
            return jsonify({'error': 'No log file uploaded'}), 400

        file = request.files['logfile']

        # Check if filename is present
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Check if file is a ZIP
        if not file.filename.lower().endswith('.zip'):
            return jsonify({'error': 'Only ZIP compressed files are accepted. Please compress your log file first.'}), 400

        # Extract and read log content from ZIP
        try:
            # Read ZIP file content
            zip_bytes = file.read()

            # Open ZIP file
            with zipfile.ZipFile(io.BytesIO(zip_bytes), 'r') as zip_ref:
                # Get list of files in ZIP
                file_list = zip_ref.namelist()

                if len(file_list) == 0:
                    return jsonify({'error': 'ZIP file is empty'}), 400

                # Find a log file (*.txt or *.log)
                log_file = None
                for filename in file_list:
                    if filename.lower().endswith(('.txt', '.log')) and not filename.startswith('__MACOSX'):
                        log_file = filename
                        break

                if not log_file:
                    return jsonify({'error': 'No .txt or .log file found in ZIP archive'}), 400

                # Extract and decode log content
                log_content = zip_ref.read(log_file).decode('utf-8', errors='ignore')

        except zipfile.BadZipFile:
            return jsonify({'error': 'Invalid ZIP file format'}), 400
        except Exception as e:
            return jsonify({'error': f'Failed to extract ZIP file: {str(e)}'}), 400

        # Parse log content
        parser = CharmLogParser()
        stats = parser.parse_log_content(log_content)

        if not stats['overall']:
            return jsonify({
                'success': False,
                'message': 'No charm data found in log file. Make sure the log contains "begin casting" and "Your charm spell has worn off" messages.'
            })

        # Format the response
        response = {
            'success': True,
            'total_charms': stats['total_charms_found'],
            'overall': {
                'count': stats['overall']['count'],
                'avg': round(stats['overall']['avg'], 1),
                'avg_formatted': CharmLogParser.format_duration(stats['overall']['avg']),
                'median': round(stats['overall']['median'], 1),
                'median_formatted': CharmLogParser.format_duration(stats['overall']['median']),
                'min': round(stats['overall']['min'], 1),
                'min_formatted': CharmLogParser.format_duration(stats['overall']['min']),
                'max': round(stats['overall']['max'], 1),
                'max_formatted': CharmLogParser.format_duration(stats['overall']['max']),
                'p90': round(stats['overall']['p90'], 1),
                'p90_formatted': CharmLogParser.format_duration(stats['overall']['p90']),
                'p95': round(stats['overall']['p95'], 1),
                'p95_formatted': CharmLogParser.format_duration(stats['overall']['p95']),
                'p99': round(stats['overall']['p99'], 1),
                'p99_formatted': CharmLogParser.format_duration(stats['overall']['p99']),
            },
            'by_spell': {}
        }

        # Add per-spell statistics
        for spell_name, spell_stats in stats['by_spell'].items():
            response['by_spell'][spell_name] = {
                'count': spell_stats['count'],
                'avg': round(spell_stats['avg'], 1),
                'avg_formatted': CharmLogParser.format_duration(spell_stats['avg']),
                'median': round(spell_stats['median'], 1),
                'median_formatted': CharmLogParser.format_duration(spell_stats['median']),
                'min': round(spell_stats['min'], 1),
                'min_formatted': CharmLogParser.format_duration(spell_stats['min']),
                'max': round(spell_stats['max'], 1),
                'max_formatted': CharmLogParser.format_duration(spell_stats['max']),
                'p90': round(spell_stats['p90'], 1),
                'p90_formatted': CharmLogParser.format_duration(spell_stats['p90']),
                'p95': round(spell_stats['p95'], 1),
                'p95_formatted': CharmLogParser.format_duration(spell_stats['p95']),
                'p99': round(spell_stats['p99'], 1),
                'p99_formatted': CharmLogParser.format_duration(spell_stats['p99']),
            }

        return jsonify(response)

    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


if __name__ == '__main__':
    print("Starting Quarm Charm Calculator Web Server...")
    print("Open http://localhost:5000 in your browser")
    app.run(debug=True, host='0.0.0.0', port=5000)

