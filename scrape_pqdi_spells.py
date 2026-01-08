#!/usr/bin/env python3
"""
Scrape charm spell data from pqdi.cc spell database.

This script dynamically fetches all charm spells from pqdi.cc for:
- Enchanters
- Druids
- Necromancers

The data is saved to pqdi_charm_spells.json for use by the calculator.
"""

import json
import re
import sys
import time
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from html.parser import HTMLParser


class LinkExtractor(HTMLParser):
    """Extract links from HTML."""

    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            attrs_dict = dict(attrs)
            if 'href' in attrs_dict:
                self.links.append(attrs_dict['href'])


def fetch_url(url, retry=3):
    """Fetch a URL with retries."""
    for attempt in range(retry):
        try:
            print(f"  Fetching {url}...", file=sys.stderr)
            req = Request(url, headers={'User-Agent': 'Mozilla/5.0 (QuarmCharmCalculator/1.0)'})
            with urlopen(req, timeout=30) as response:
                return response.read().decode('utf-8')
        except (URLError, HTTPError) as e:
            print(f"  Error (attempt {attempt + 1}/{retry}): {e}", file=sys.stderr)
            if attempt < retry - 1:
                time.sleep(2)
            else:
                raise
    return None


def get_class_spell_lists():
    """Get the spell list URLs for relevant classes."""
    print("\n=== Using known class spell list IDs ===", file=sys.stderr)

    # Known list-spells IDs for each class (from pqdi.cc website structure)
    # Druid = 6, Enchanter = 14, Necromancer = 11
    class_map = {
        'Druid': 6,
        'Enchanter': 14,
        'Necromancer': 11
    }

    for class_name, list_id in class_map.items():
        print(f"  {class_name}: /list-spells/{list_id}", file=sys.stderr)

    return class_map


def extract_spell_ids_from_class_list(class_name, list_id):
    """Extract all spell IDs and names from a class spell list page."""
    print(f"\n=== Fetching {class_name} spells ===", file=sys.stderr)

    url = f'https://www.pqdi.cc/list-spells/{list_id}'
    html = fetch_url(url)

    spells = []

    # Find all spell links with their names
    # Pattern: <a href="/spell/260" class="link">Charm Animals</a>
    spell_pattern = r'<a\s+href=["\']?/spell/(\d+)["\']?[^>]*>([^<]+)</a>'
    matches = re.findall(spell_pattern, html, re.IGNORECASE)

    print(f"  Found {len(matches)} total spells for {class_name}", file=sys.stderr)

    # Build spell list
    for spell_id, spell_name in matches:
        spell_name = spell_name.strip()
        # Skip if it's just whitespace or an icon reference
        if spell_name and not spell_name.startswith('<'):
            spells.append({
                'id': int(spell_id),
                'name': spell_name,
                'class': class_name
            })

    print(f"  Extracted {len(spells)} spell entries", file=sys.stderr)
    return spells


def is_likely_charm_spell_name(spell_name):
    """Quick check if spell name suggests it's a charm spell."""
    charm_keywords = [
        'charm', 'beguile', 'allure', 'cajoling', 'command of druzzil',
        'ordinance', 'agacerie', 'call of karana', 'command of tunare',
        'befriend'
    ]
    spell_lower = spell_name.lower()

    for keyword in charm_keywords:
        if keyword in spell_lower:
            return True

    return False


def is_charm_spell(html, spell_name):
    """Check if a spell is a charm spell by looking at its effects."""
    # Look for "Charm" in effect type or spell description
    charm_patterns = [
        r'Effect type:.*?Charm',
        r'Charm up to level',
        r'>Charm<',
    ]

    for pattern in charm_patterns:
        if re.search(pattern, html, re.IGNORECASE):
            return True

    return False


def extract_spell_details(spell_id, spell_name, class_name):
    """Extract detailed spell information from individual spell page."""
    try:
        # First try the API for clean JSON data
        api_url = f'https://www.pqdi.cc/api/v1/spell/{spell_id}'
        api_data_str = fetch_url(api_url)
        api_data = json.loads(api_data_str) if api_data_str else {}

        time.sleep(0.3)  # Be nice to the server

        # Check if this is actually a charm spell from effects
        is_charm = False
        max_level = None

        if 'effects' in api_data:
            for effect in api_data['effects']:
                if 'charm' in effect.lower():
                    is_charm = True
                    # Extract max level from "Charm up to level X"
                    match = re.search(r'up to level\s+(\d+)', effect, re.IGNORECASE)
                    if match:
                        max_level = int(match.group(1))
                    break

        if not is_charm:
            return None

        print(f"  ✓ Found charm spell: {spell_name} (ID {spell_id})", file=sys.stderr)

        # Parse duration ticks from "20 min 30 sec (205 ticks)"
        duration_ticks = None
        if 'duration' in api_data:
            duration_match = re.search(r'\((\d+)\s+ticks?\)', api_data['duration'])
            if duration_match:
                duration_ticks = int(duration_match.group(1))

        # Now fetch HTML for missing data (spell level and resist_diff)
        html_url = f'https://www.pqdi.cc/spell/{spell_id}'
        html = fetch_url(html_url)
        time.sleep(0.3)

        # Extract spell level from Classes section
        # Looking for patterns like "Enchanter(12)" or "DRU/12"
        spell_level = None
        level_patterns = [
            r'(?:Enchanter|Druid|Necromancer)\((\d+)\)',  # Full class name(level)
            r'(?:ENC|DRU|NEC)/(\d+)',  # Class abbreviation/level
            r'<kbd[^>]*>(\d+)</kbd>',  # Level in kbd tag
        ]
        for pattern in level_patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            if matches:
                spell_level = int(matches[0])
                break

        # Extract resist modifier from the raw data section
        # NOTE: Negative values make it HARDER to resist (easier to land)
        #       -10 = harder to resist, 0 = normal, +10 = easier to resist
        resist_diff = 0  # Default fallback (0 = normal difficulty)
        resist_patterns = [
            r'<strong>ResistDiff:\s*</strong><span[^>]*>(-?\d+)</span>',  # Raw data field
            r'Resist\s+Type:.*?\((-?\d+)\)',  # Resist Type: Magic (-10)
        ]
        for pattern in resist_patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                resist_diff = int(match.group(1))
                break

        details = {
            'id': spell_id,
            'name': spell_name,
            'class': class_name,
            'level': spell_level,
            'resist_diff': resist_diff,
            'max_level': max_level or 55,  # Default if not found
            'mana': api_data.get('mana'),
            'duration_ticks': duration_ticks
        }

        # Determine special flags
        if class_name == 'Druid':
            details['animal_only'] = True
        elif class_name == 'Necromancer':
            details['undead_only'] = True

        return details

    except Exception as e:
        print(f"  Error fetching spell {spell_id}: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return None


def scrape_all_charm_spells():
    """Main function to scrape all charm spells."""
    print("=" * 80, file=sys.stderr)
    print("PQDI.CC Charm Spell Scraper", file=sys.stderr)
    print("=" * 80, file=sys.stderr)

    # Get class spell list URLs
    class_map = get_class_spell_lists()

    all_charm_spells = []

    # Process each class
    for class_name, list_id in class_map.items():
        if not list_id:
            print(f"\nSkipping {class_name} - no list ID found", file=sys.stderr)
            continue

        # Get all spells for this class
        all_spells = extract_spell_ids_from_class_list(class_name, list_id)

        # Filter to only likely charm spells by name (optimization)
        likely_charm_spells = [s for s in all_spells if is_likely_charm_spell_name(s['name'])]

        print(f"\n  Filtered to {len(likely_charm_spells)} potential charm spells (from {len(all_spells)} total)", file=sys.stderr)
        print(f"  Potential charms: {', '.join([s['name'] for s in likely_charm_spells])}", file=sys.stderr)

        # Check each likely spell to confirm it's a charm spell
        for spell in likely_charm_spells:
            details = extract_spell_details(spell['id'], spell['name'], class_name)
            if details:
                all_charm_spells.append(details)

        print(f"\n  Confirmed {len([s for s in all_charm_spells if s['class'] == class_name])} charm spells for {class_name}", file=sys.stderr)

    return all_charm_spells


def save_charm_spells(charm_spells, filename='pqdi_charm_spells.json'):
    """Save charm spells to JSON file."""
    print(f"\n=== Saving to {filename} ===", file=sys.stderr)

    # Sort by class, then level
    charm_spells.sort(key=lambda x: (x['class'], x['level'] or 0))

    output = {
        'source': 'pqdi.cc',
        'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime()),
        'spell_count': len(charm_spells),
        'spells': charm_spells
    }

    with open(filename, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"  Saved {len(charm_spells)} charm spells", file=sys.stderr)

    # Print summary
    print("\n=== Summary ===", file=sys.stderr)
    for class_name in ['Enchanter', 'Druid', 'Necromancer']:
        class_spells = [s for s in charm_spells if s['class'] == class_name]
        print(f"{class_name}: {len(class_spells)} spells", file=sys.stderr)
        for spell in class_spells:
            lvl = spell['level'] if spell['level'] else '??'
            print(f"  - {spell['name']:30s} (Lvl {lvl:>2}, Max NPC {spell['max_level']:2}, Resist {spell['resist_diff']:4})", file=sys.stderr)


def main():
    """Main entry point."""
    try:
        charm_spells = scrape_all_charm_spells()

        if not charm_spells:
            print("\nERROR: No charm spells found!", file=sys.stderr)
            return 1

        save_charm_spells(charm_spells)

        print("\n" + "=" * 80, file=sys.stderr)
        print("SUCCESS! Charm spell data saved to pqdi_charm_spells.json", file=sys.stderr)
        print("=" * 80, file=sys.stderr)
        print("\nNext step: Run update_charm_spells.py to generate charm_spells_data.py", file=sys.stderr)

        return 0

    except Exception as e:
        print(f"\nFATAL ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())

