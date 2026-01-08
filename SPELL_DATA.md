# Charm Spell Data

## Overview

The charm spell data for this calculator is **dynamically scraped** from the **[pqdi.cc spell database](https://www.pqdi.cc/spells)**, which provides accurate spell information for the Quarm server (Project Quarm / P99 era, Classic through Velious).

## Data Source

All charm spell data is fetched directly from [pqdi.cc](https://www.pqdi.cc) using automated web scraping. This ensures:
- **Accuracy**: Data matches the actual Quarm server implementation
- **Era-appropriate**: Only includes spells available in the current Quarm era
- **Up-to-date**: Can be refreshed anytime from the live database

## Current Spell List

### Enchanter Charms (6 spells)
- **Charm** (Level 12): Max NPC 25, Resist 0
- **Beguile** (Level 24): Max NPC 37, Resist 0
- **Cajoling Whispers** (Level 39): Max NPC 46, Resist 0
- **Allure** (Level 49): Max NPC 51, Resist 0
- **Boltran's Agacerie** (Level 53): Max NPC 53, Resist -10 ⭐ (easier to land!)
- **Command of Druzzil** (Level 64): Max NPC 64, Resist 0

### Druid Animal Charms (7 spells)
- **Befriend Animal** (Level 14): Max NPC 24, Resist 0
- **Charm Animals** (Level 24): Max NPC 33, Resist 0
- **Beguile Plants** (Level 29): Max NPC 25, Resist 0
- **Beguile Animals** (Level 34): Max NPC 43, Resist 0
- **Allure of the Wild** (Level 44): Max NPC 49, Resist 0
- **Call of Karana** (Level 52): Max NPC 53, Resist 0
- **Command of Tunare** (Level 63): Max NPC 60, Resist 0

### Necromancer Undead Charms (1 spell)
- **Beguile Undead** (Level 34): Max NPC 46, Resist 0

## How to Update Spell Data

The spell data update process has two steps:

### Quick Update (Recommended)

```bash
make refresh-spells
```

This will:
1. Scrape latest data from pqdi.cc
2. Generate the Python data file
3. Verify the data loaded correctly

### Manual Update

#### Step 1: Scrape from pqdi.cc

```bash
python3 scrape_pqdi_spells.py
```

This script:
- Fetches spell lists for Enchanter, Druid, and Necromancer from pqdi.cc
- Filters to only charm spells (by name keywords)
- Fetches detailed data for each charm spell using the pqdi.cc API
- Extracts: spell level, max NPC level, resist modifier, mana cost, duration
- Saves all data to `pqdi_charm_spells.json`

#### Step 2: Generate Python Data File

```bash
python3 update_charm_spells.py
```

This script:
- Loads data from `pqdi_charm_spells.json`
- Generates `charm_spells_data.py` with the CHARM_SPELLS dictionary
- Includes all helper functions for the calculator

#### Step 3: Verify

```bash
python3 charm_spells_data.py
```

This will display all charm spells organized by class.

## Technical Details

### Scraping Process

The scraper (`scrape_pqdi_spells.py`) works as follows:

1. **Class Lists**: Fetches spell lists from:
   - Druid: `/list-spells/6`
   - Enchanter: `/list-spells/14`
   - Necromancer: `/list-spells/11`

2. **Spell Filtering**: Looks for spells with charm-related keywords in the name:
   - charm, beguile, allure, cajoling, command, etc.

3. **Detail Extraction**: For each potential charm spell:
   - Calls `/api/v1/spell/{id}` for JSON data (mana, duration, effects)
   - Parses HTML from `/spell/{id}` for spell level and resist modifier
   - Verifies it's actually a charm spell by checking effects

4. **Data Validation**: Extracts key fields:
   - **Spell Level**: From "Enchanter(12)" pattern in Classes section
   - **Max NPC Level**: From "Charm up to level X" in effects
   - **Resist Modifier**: From "Resist Adjust" field
   - **Mana Cost**: From API data
   - **Duration**: From API data (in ticks)

### Data Format

**JSON (pqdi_charm_spells.json)**:
```json
{
  "source": "pqdi.cc",
  "scraped_at": "2026-01-08 13:08:14 UTC",
  "spell_count": 14,
  "spells": [
    {
      "id": 300,
      "name": "Charm",
      "class": "Enchanter",
      "level": 12,
      "resist_diff": 0,
      "max_level": 25,
      "mana": 60,
      "duration_ticks": 205,
      "animal_only": false,
      "undead_only": false
    },
    {
      "id": 1705,
      "name": "Boltran's Agacerie",
      "class": "Enchanter",
      "level": 53,
      "resist_diff": -10,
      "max_level": 53,
      "mana": 400,
      "duration_ticks": 75
    }
  ]
}
```

**Notes on resist_diff:**
- **Negative values** make it HARDER to resist (easier to land) - better spells
- **0** = normal resist difficulty
- **Positive values** make it EASIER to resist (harder to land) - worse spells
- Example: Boltran's Agacerie at -10 is better than Charm at 0

**Python (charm_spells_data.py)**:
```python
CHARM_SPELLS = {
    300: {
        'name': 'Charm',
        'resist_diff': 0,
        'max_level': 25,
        'classes': ['Enchanter'],
        'spell_level': 12
    },
    1705: {
        'name': "Boltran's Agacerie",
        'resist_diff': -10,
        'max_level': 53,
        'classes': ['Enchanter'],
        'spell_level': 53
    }
}
```

## Advantages of Dynamic Scraping

1. **Always Current**: Fetch latest data anytime from pqdi.cc
2. **Accurate**: Uses the authoritative Quarm spell database
3. **Auditable**: JSON cache file can be reviewed before deploying
4. **Maintainable**: No manual updates needed when spells change
5. **Transparent**: All data sources and extraction logic are visible

## Build Process

The scraper is designed to be run during development/deployment:

### Local Development
```bash
make refresh-spells  # Update when needed
./start.sh           # Run the calculator
```

### Docker Build
The Dockerfile includes the scraper script and cached JSON file, allowing the image to be built without network access if `pqdi_charm_spells.json` is committed to the repo.

To refresh in Docker:
```bash
# Run scraper locally first
python3 scrape_pqdi_spells.py

# Then build Docker image with updated data
make docker-build
```

## Reference Links

- **pqdi.cc Spell Database**: https://www.pqdi.cc/spells
- **pqdi.cc API**: `https://www.pqdi.cc/api/v1/spell/{id}`
- **Enchanter Spells**: https://www.pqdi.cc/list-spells/14
- **Druid Spells**: https://www.pqdi.cc/list-spells/6
- **Necromancer Spells**: https://www.pqdi.cc/list-spells/11

## Troubleshooting

### Scraper Fails

If `scrape_pqdi_spells.py` fails:
1. Check network connectivity to pqdi.cc
2. Verify pqdi.cc website is accessible
3. Check if HTML structure changed (may need pattern updates)
4. Use cached `pqdi_charm_spells.json` if available

### Missing Spells

If expected spells are missing:
1. Check if spell name matches keywords in `is_likely_charm_spell_name()`
2. Add new keywords if needed
3. Re-run scraper

### Wrong Data

If spell data seems incorrect:
1. Manually check spell on pqdi.cc website
2. Review `pqdi_charm_spells.json` to see what was scraped
3. Check extraction patterns in `extract_spell_details()`
4. Report issue to pqdi.cc if their data is wrong

## Historical Note

Previous versions used:
- Manual curation (prone to errors and outdated)
- Client `spells_en.txt` file (wrong era, inconsistent format)
- Failed web scraping attempts (incorrect URL patterns)

The current scraper is reliable and maintainable, using both the pqdi.cc API and HTML parsing to get complete, accurate data.
