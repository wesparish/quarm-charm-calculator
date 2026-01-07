"""
Spell File Parser for EverQuest spells_en.txt

Parses the EQ spell file format based on field definitions from:
https://github.com/rumstil/eqspellparser

Field 80 = RESIST_MOD (resist_diff)
Field 31 = RESISTTYPE (magic=2)
Field 167 = SPELL_EFFECTS (contains effect data)
"""

import re
from typing import Dict, List, Optional


class SpellParser:
    """Parser for EverQuest spells_en.txt file format."""
    
    # Spell Effect (SPA) constants
    SE_CHARM = 22  # Charm effect (SPA 22)
    
    # Resist types
    RESIST_MAGIC = 2
    RESIST_FIRE = 1
    RESIST_COLD = 3
    RESIST_POISON = 4
    RESIST_DISEASE = 5
    
    # Class IDs (for min level fields 38-53)
    CLASS_WARRIOR = 38
    CLASS_CLERIC = 39
    CLASS_PALADIN = 40
    CLASS_RANGER = 41
    CLASS_SHADOWKNIGHT = 42
    CLASS_DRUID = 43
    CLASS_MONK = 44
    CLASS_BARD = 45
    CLASS_ROGUE = 46
    CLASS_SHAMAN = 47
    CLASS_NECROMANCER = 48
    CLASS_WIZARD = 49
    CLASS_MAGICIAN = 50
    CLASS_ENCHANTER = 51
    CLASS_BEASTLORD = 52
    CLASS_BERSERKER = 53
    
    CLASS_NAMES = {
        CLASS_WARRIOR: "Warrior",
        CLASS_CLERIC: "Cleric",
        CLASS_PALADIN: "Paladin",
        CLASS_RANGER: "Ranger",
        CLASS_SHADOWKNIGHT: "Shadow Knight",
        CLASS_DRUID: "Druid",
        CLASS_MONK: "Monk",
        CLASS_BARD: "Bard",
        CLASS_ROGUE: "Rogue",
        CLASS_SHAMAN: "Shaman",
        CLASS_NECROMANCER: "Necromancer",
        CLASS_WIZARD: "Wizard",
        CLASS_MAGICIAN: "Magician",
        CLASS_ENCHANTER: "Enchanter",
        CLASS_BEASTLORD: "Beastlord",
        CLASS_BERSERKER: "Berserker",
    }
    
    def __init__(self, spell_file_path: str):
        """Initialize parser with path to spells_en.txt file."""
        self.spell_file_path = spell_file_path
        self.spells = {}
        self._parse_file()
    
    def _parse_file(self):
        """Parse the spell file and load all spells."""
        with open(self.spell_file_path, 'r', encoding='latin-1') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                    
                fields = line.split('^')
                if len(fields) < 100:  # Need at least 100 fields for basic spell data
                    continue
                
                try:
                    spell_id = int(fields[0])
                    spell_data = self._parse_spell(fields)
                    if spell_data:
                        self.spells[spell_id] = spell_data
                except (ValueError, IndexError):
                    continue
    
    def _parse_spell(self, fields: List[str]) -> Optional[Dict]:
        """Parse a single spell from its fields."""
        try:
            spell_id = int(fields[0])
            name = fields[1]
            
            # Skip empty spells
            if not name or name == "BLUE_TRAIL":
                return None
            
            # Parse basic info
            resist_type = int(fields[31]) if fields[31] else 0
            resist_mod = int(fields[80]) if fields[80] else 0
            
            # Parse class levels (fields 38-53)
            class_levels = {}
            for class_id in range(self.CLASS_WARRIOR, self.CLASS_BERSERKER + 1):
                field_idx = class_id
                level = int(fields[field_idx]) if fields[field_idx] and fields[field_idx] != '255' else None
                if level and level < 255:
                    class_name = self.CLASS_NAMES.get(class_id, f"Class{class_id}")
                    class_levels[class_name] = level
            
            # Parse spell effects
            # Based on eqspellparser format:
            # Fields 20-31: slot 1-12 base1 effect
            # Fields 32-43: slot 1-12 base2 effect  
            # Fields 44-55: slot 1-12 max effect
            # Fields 70-81: slot 1-12 calc formula data
            # Fields 86-97: slot 1-12 spa/type (effect ID)
            effects = []
            for i in range(12):  # 12 effect slots
                try:
                    spa_idx = 86 + i
                    base1_idx = 20 + i
                    base2_idx = 32 + i
                    max_idx = 44 + i
                    calc_idx = 70 + i
                    
                    if spa_idx >= len(fields):
                        break
                        
                    spa = int(fields[spa_idx]) if fields[spa_idx] else 254
                    
                    # 254 means unused slot, no more to follow
                    if spa == 254:
                        break
                    
                    base1 = int(fields[base1_idx]) if fields[base1_idx] else 0
                    base2 = int(fields[base2_idx]) if fields[base2_idx] else 0
                    max_val = int(fields[max_idx]) if fields[max_idx] else 0
                    calc = int(fields[calc_idx]) if fields[calc_idx] else 0
                    
                    effects.append({
                        'slot': i + 1,
                        'effect_id': spa,
                        'base1': base1,
                        'base2': base2,
                        'max': max_val,
                        'calc': calc
                    })
                except (ValueError, IndexError):
                    pass
            
            # Determine if this is a charm spell
            is_charm = any(e['effect_id'] == self.SE_CHARM for e in effects)
            
            # Get max level from charm effect (stored in base1)
            max_level = 0
            if is_charm:
                for effect in effects:
                    if effect['effect_id'] == self.SE_CHARM:
                        max_level = effect['base1']
                        break
            
            return {
                'id': spell_id,
                'name': name,
                'resist_type': resist_type,
                'resist_mod': resist_mod,
                'class_levels': class_levels,
                'effects': effects,
                'is_charm': is_charm,
                'max_level': max_level
            }
            
        except (ValueError, IndexError) as e:
            return None
    
    def get_charm_spells(self) -> List[Dict]:
        """Get all charm spells from the spell file."""
        charm_spells = []
        
        for spell_id, spell in self.spells.items():
            if spell['is_charm']:
                charm_spells.append(spell)
        
        # Sort by name
        charm_spells.sort(key=lambda x: x['name'])
        return charm_spells
    
    def get_spell_by_id(self, spell_id: int) -> Optional[Dict]:
        """Get a specific spell by ID."""
        return self.spells.get(spell_id)
    
    def get_spell_by_name(self, name: str) -> Optional[Dict]:
        """Get a specific spell by name (case-insensitive)."""
        name_lower = name.lower()
        for spell in self.spells.values():
            if spell['name'].lower() == name_lower:
                return spell
        return None
    
    def search_spells(self, query: str) -> List[Dict]:
        """Search for spells by name (partial match, case-insensitive)."""
        query_lower = query.lower()
        results = []
        
        for spell in self.spells.values():
            if query_lower in spell['name'].lower():
                results.append(spell)
        
        results.sort(key=lambda x: x['name'])
        return results


def main():
    """Test the spell parser."""
    import os
    
    spell_file = "/home/wes/workspace/QuarmCharmCalculator/data/spells_en.txt"
    
    if not os.path.exists(spell_file):
        print(f"Spell file not found: {spell_file}")
        return
    
    print("Parsing spell file...")
    parser = SpellParser(spell_file)
    
    print(f"\nTotal spells parsed: {len(parser.spells)}")
    
    # Get all charm spells
    charm_spells = parser.get_charm_spells()
    print(f"\nFound {len(charm_spells)} charm spells:")
    print("=" * 80)
    
    for spell in charm_spells:
        print(f"\n[{spell['id']}] {spell['name']}")
        print(f"  Resist Mod: {spell['resist_mod']}")
        print(f"  Max Level: {spell['max_level']}")
        
        if spell['class_levels']:
            classes = ", ".join([f"{cls}({lvl})" for cls, lvl in sorted(spell['class_levels'].items())])
            print(f"  Classes: {classes}")
        
        # Show charm effect details
        for effect in spell['effects']:
            if effect['effect_id'] == SpellParser.SE_CHARM:
                print(f"  Charm Effect: Max NPC Level {effect['base1']}")
    
    print("\n" + "=" * 80)
    
    # Test specific spell lookup
    print("\nTesting spell lookup:")
    allure = parser.get_spell_by_name("Allure")
    if allure:
        print(f"\nAllure spell data:")
        print(f"  ID: {allure['id']}")
        print(f"  Resist Mod: {allure['resist_mod']}")
        print(f"  Max Level: {allure['max_level']}")


if __name__ == "__main__":
    main()

