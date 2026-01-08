#!/usr/bin/env python3
"""
Generate charm_spells_data.py from pqdi_charm_spells.json.

The JSON file is created by scrape_pqdi_spells.py which fetches
live data from pqdi.cc spell database.

To update:
1. Run: python3 scrape_pqdi_spells.py (fetches latest from pqdi.cc)
2. Run: python3 update_charm_spells.py (generates charm_spells_data.py)
"""

import json
import sys

def load_pqdi_charm_spells():
    """Load charm spells from the scraped JSON file."""
    try:
        with open('pqdi_charm_spells.json', 'r') as f:
            data = json.load(f)
        return data['spells']
    except FileNotFoundError:
        print("ERROR: pqdi_charm_spells.json not found!", file=sys.stderr)
        print("Run 'python3 scrape_pqdi_spells.py' first to fetch spell data.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR loading pqdi_charm_spells.json: {e}", file=sys.stderr)
        sys.exit(1)




def convert_to_charm_spells_format():
    """Convert PQDI data to CHARM_SPELLS dictionary format."""
    charm_spells = {}

    for spell in PQDI_CHARM_SPELLS:
        spell_id = spell['id']
        charm_spells[spell_id] = {
            'name': spell['name'],
            'resist_diff': spell['resist_diff'],
            'max_level': spell['max_level'],
            'classes': [spell['class']],
            'spell_level': spell['level']
        }

        if spell.get('animal_only'):
            charm_spells[spell_id]['animal_only'] = True
        if spell.get('undead_only'):
            charm_spells[spell_id]['undead_only'] = True

    return charm_spells


def generate_charm_spells_data():
    """Generate the charm_spells_data.py file."""
    charm_spells = convert_to_charm_spells_format()

    with open('charm_spells_data.py', 'w') as f:
        f.write('"""\n')
        f.write('Charm spell data for Quarm server.\n')
        f.write('\n')
        f.write('Data sourced from pqdi.cc spell database (https://www.pqdi.cc/spells).\n')
        f.write('Accurate for Classic through Velious era (Quarm/P99).\n')
        f.write('\n')
        f.write('To update: Run update_charm_spells.py\n')
        f.write('"""\n\n')

        f.write('# Charm spell database\n')
        f.write('# Format: spell_id: {name, resist_diff, max_level, classes, spell_level, ...}\n')
        f.write('CHARM_SPELLS = {\n')

        # Sort by class, then level
        sorted_spells = sorted(
            [(spell_id, data) for spell_id, data in charm_spells.items()],
            key=lambda x: (x[1]['classes'][0], x[1]['spell_level'])
        )

        for spell_id, data in sorted_spells:
            f.write(f"    {spell_id}: {{\n")
            f.write(f"        'name': {repr(data['name'])},\n")
            f.write(f"        'resist_diff': {data['resist_diff']},\n")
            f.write(f"        'max_level': {data['max_level']},\n")
            f.write(f"        'classes': {data['classes']},\n")
            f.write(f"        'spell_level': {data['spell_level']}")

            if data.get('animal_only'):
                f.write(',\n        \'animal_only\': True')
            if data.get('undead_only'):
                f.write(',\n        \'undead_only\': True')

            f.write('\n    },\n')

        f.write('}\n\n\n')

        # Add helper functions
        f.write('def get_charm_spell(spell_id):\n')
        f.write('    """Get charm spell data by ID."""\n')
        f.write('    return CHARM_SPELLS.get(spell_id)\n\n\n')

        f.write('def get_charm_spell_by_name(name):\n')
        f.write('    """Get charm spell data by name (case-insensitive)."""\n')
        f.write('    name_lower = name.lower()\n')
        f.write('    for spell_id, data in CHARM_SPELLS.items():\n')
        f.write('        if data[\'name\'].lower() == name_lower:\n')
        f.write('            return {**data, \'id\': spell_id}\n')
        f.write('    return None\n\n\n')

        f.write('def get_all_charm_spells():\n')
        f.write('    """Get all charm spells."""\n')
        f.write('    return [{**data, \'id\': spell_id} for spell_id, data in CHARM_SPELLS.items()]\n\n\n')

        f.write('def get_charm_spells_by_class(class_name):\n')
        f.write('    """Get all charm spells for a specific class."""\n')
        f.write('    return [\n')
        f.write('        {**data, \'id\': spell_id}\n')
        f.write('        for spell_id, data in CHARM_SPELLS.items()\n')
        f.write('        if class_name in data.get(\'classes\', [])\n')
        f.write('    ]\n\n\n')

        f.write('def get_player_charm_spells():\n')
        f.write('    """Get only player-usable charm spells (exclude NPC spells)."""\n')
        f.write('    return [\n')
        f.write('        {**data, \'id\': spell_id}\n')
        f.write('        for spell_id, data in CHARM_SPELLS.items()\n')
        f.write('        if not data.get(\'npc_only\', False)\n')
        f.write('    ]\n\n\n')

        f.write('if __name__ == "__main__":\n')
        f.write('    print("Quarm Charm Spells Database")\n')
        f.write('    print("=" * 80)\n\n')
        f.write('    for class_name in [\'Enchanter\', \'Druid\', \'Necromancer\']:\n')
        f.write('        spells = get_charm_spells_by_class(class_name)\n')
        f.write('        print(f"\\n{class_name} Charms ({len(spells)}):")\n')
        f.write('        print("-" * 80)\n')
        f.write('        for spell in sorted(spells, key=lambda x: x.get(\'spell_level\', 0)):\n')
        f.write('            special = []\n')
        f.write('            if spell.get(\'animal_only\'):\n')
        f.write('                special.append("Animals Only")\n')
        f.write('            if spell.get(\'undead_only\'):\n')
        f.write('                special.append("Undead Only")\n')
        f.write('            special_str = f" ({\', \'.join(special)})" if special else ""\n\n')
        f.write('            print(f"  [{spell[\'id\']:4d}] {spell[\'name\']:30s} "\n')
        f.write('                  f"Level {spell.get(\'spell_level\', \'?\'):2} | "\n')
        f.write('                  f"Max NPC: {spell[\'max_level\']:2d} | "\n')
        f.write('                  f"Resist: {spell[\'resist_diff\']:4d}{special_str}")\n')


if __name__ == '__main__':
    print("=" * 80)
    print("Quarm Charm Spell Data Updater")
    print("=" * 80)
    print()
    print("Loading spell data from pqdi_charm_spells.json...")
    print("Source: pqdi.cc (scraped by scrape_pqdi_spells.py)")
    print()

    # Load spells from JSON
    PQDI_CHARM_SPELLS = load_pqdi_charm_spells()

    print(f"Loaded {len(PQDI_CHARM_SPELLS)} charm spells:")
    print()

    for class_name in ['Enchanter', 'Druid', 'Necromancer']:
        class_spells = [s for s in PQDI_CHARM_SPELLS if s['class'] == class_name]
        print(f"{class_name}: {len(class_spells)} spells")
        for spell in sorted(class_spells, key=lambda x: x.get('level') or 0):
            special = []
            if spell.get('animal_only'):
                special.append("Animals")
            if spell.get('undead_only'):
                special.append("Undead")
            special_str = f" [{', '.join(special)}]" if special else ""

            lvl = spell.get('level') if spell.get('level') else '??'
            print(f"  - {spell['name']:30s} (Lvl {lvl:>2}, Max NPC {spell['max_level']:2d}, Resist {spell['resist_diff']:4d}){special_str}")

    print()
    print("Generating charm_spells_data.py...")
    generate_charm_spells_data()
    print("Done!")
    print()
    print("To verify, run: python3 charm_spells_data.py")

