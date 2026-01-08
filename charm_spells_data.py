"""
Charm spell data for Quarm server.

Data sourced from pqdi.cc spell database (https://www.pqdi.cc/spells).
Accurate for Classic through Velious era (Quarm/P99).

To update: Run update_charm_spells.py
"""

# Charm spell database
# Format: spell_id: {name, resist_diff, max_level, classes, spell_level, ...}
CHARM_SPELLS = {
    245: {
        'name': 'Befriend Animal',
        'resist_diff': 0,
        'max_level': 24,
        'classes': ['Druid'],
        'spell_level': 14,
        'animal_only': True
    },
    260: {
        'name': 'Charm Animals',
        'resist_diff': 0,
        'max_level': 33,
        'classes': ['Druid'],
        'spell_level': 24,
        'animal_only': True
    },
    753: {
        'name': 'Beguile Plants',
        'resist_diff': 0,
        'max_level': 25,
        'classes': ['Druid'],
        'spell_level': 29,
        'animal_only': True
    },
    141: {
        'name': 'Beguile Animals',
        'resist_diff': 0,
        'max_level': 43,
        'classes': ['Druid'],
        'spell_level': 34,
        'animal_only': True
    },
    142: {
        'name': 'Allure of the Wild',
        'resist_diff': 0,
        'max_level': 49,
        'classes': ['Druid'],
        'spell_level': 44,
        'animal_only': True
    },
    1553: {
        'name': 'Call of Karana',
        'resist_diff': 0,
        'max_level': 53,
        'classes': ['Druid'],
        'spell_level': 52,
        'animal_only': True
    },
    3445: {
        'name': 'Command of Tunare',
        'resist_diff': 0,
        'max_level': 60,
        'classes': ['Druid'],
        'spell_level': 63,
        'animal_only': True
    },
    300: {
        'name': 'Charm',
        'resist_diff': 0,
        'max_level': 25,
        'classes': ['Enchanter'],
        'spell_level': 12
    },
    182: {
        'name': 'Beguile',
        'resist_diff': 0,
        'max_level': 37,
        'classes': ['Enchanter'],
        'spell_level': 24
    },
    183: {
        'name': 'Cajoling Whispers',
        'resist_diff': 0,
        'max_level': 46,
        'classes': ['Enchanter'],
        'spell_level': 39
    },
    184: {
        'name': 'Allure',
        'resist_diff': 0,
        'max_level': 51,
        'classes': ['Enchanter'],
        'spell_level': 49
    },
    1705: {
        'name': 'Boltran`s Agacerie',
        'resist_diff': -10,
        'max_level': 53,
        'classes': ['Enchanter'],
        'spell_level': 53
    },
    3355: {
        'name': 'Command of Druzzil',
        'resist_diff': 0,
        'max_level': 64,
        'classes': ['Enchanter'],
        'spell_level': 64
    },
    197: {
        'name': 'Beguile Undead',
        'resist_diff': 0,
        'max_level': 46,
        'classes': ['Necromancer'],
        'spell_level': 34,
        'undead_only': True
    },
}


def get_charm_spell(spell_id):
    """Get charm spell data by ID."""
    return CHARM_SPELLS.get(spell_id)


def get_charm_spell_by_name(name):
    """Get charm spell data by name (case-insensitive)."""
    name_lower = name.lower()
    for spell_id, data in CHARM_SPELLS.items():
        if data['name'].lower() == name_lower:
            return {**data, 'id': spell_id}
    return None


def get_all_charm_spells():
    """Get all charm spells."""
    return [{**data, 'id': spell_id} for spell_id, data in CHARM_SPELLS.items()]


def get_charm_spells_by_class(class_name):
    """Get all charm spells for a specific class."""
    return [
        {**data, 'id': spell_id}
        for spell_id, data in CHARM_SPELLS.items()
        if class_name in data.get('classes', [])
    ]


def get_player_charm_spells():
    """Get only player-usable charm spells (exclude NPC spells)."""
    return [
        {**data, 'id': spell_id}
        for spell_id, data in CHARM_SPELLS.items()
        if not data.get('npc_only', False)
    ]


if __name__ == "__main__":
    print("Quarm Charm Spells Database")
    print("=" * 80)

    for class_name in ['Enchanter', 'Druid', 'Necromancer']:
        spells = get_charm_spells_by_class(class_name)
        print(f"\n{class_name} Charms ({len(spells)}):")
        print("-" * 80)
        for spell in sorted(spells, key=lambda x: x.get('spell_level', 0)):
            special = []
            if spell.get('animal_only'):
                special.append("Animals Only")
            if spell.get('undead_only'):
                special.append("Undead Only")
            special_str = f" ({', '.join(special)})" if special else ""

            print(f"  [{spell['id']:4d}] {spell['name']:30s} "
                  f"Level {spell.get('spell_level', '?'):2} | "
                  f"Max NPC: {spell['max_level']:2d} | "
                  f"Resist: {spell['resist_diff']:4d}{special_str}")
