"""
Quarm Charm Calculator - Flask Web Server

A web interface for calculating charm effectiveness and break probabilities
based on the EQMacEmu (Quarm) server resist mechanics.
"""

from flask import Flask, render_template, request, jsonify
from charm_calculator import CharmCalculator
from charm_spells_data import get_all_charm_spells, get_player_charm_spells

app = Flask(__name__)
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
        if not (10 <= caster_charisma <= 300):
            return jsonify({'error': 'Caster charisma must be between 10 and 300'}), 400
        if not (1 <= num_ticks <= 1000):
            return jsonify({'error': 'Number of ticks must be between 1 and 1000'}), 400
        if not (100 <= num_simulations <= 100000):
            return jsonify({'error': 'Number of simulations must be between 100 and 100000'}), 400

        # Calculate initial land chance
        initial_land = calculator.calculate_initial_land_chance(
            caster_level, target_level, target_mr, resist_diff, caster_charisma, is_enchanter
        )

        # Calculate charm break probabilities over time
        break_prob = calculator.calculate_charm_break_probability(
            caster_level, target_level, target_mr, resist_diff,
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


if __name__ == '__main__':
    print("Starting Quarm Charm Calculator Web Server...")
    print("Open http://localhost:5000 in your browser")
    app.run(debug=True, host='0.0.0.0', port=5000)

