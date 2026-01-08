# Quarm Charm Calculator

A web-based tool to calculate animal charm effectiveness for the Quarm EverQuest Emulator server. This tool implements the exact resist mechanics from EQMacEmu's source code to help enchanters understand charm break probabilities.

## Features

- **Initial Cast Success Rate**: Calculate the probability your charm spell will land initially
- **Charm Break Simulation**: Monte Carlo simulation showing how likely your charm is to break over time
- **Real EQMacEmu Logic**: Based directly on the `CheckResistSpell` method from `zone/spells.cpp`
- **Multiple Spell Support**: Presets for all common charm spells
- **Charisma Calculations**: Accounts for enchanter charisma bonuses (CHA > 75 reduces resist modifier)
- **Log File Analysis**: Upload your EQ log file to see real charm duration statistics (avg, min, max, P90, P95, P99)
- **Interactive Web UI**: Beautiful, modern interface with real-time calculations

## How Charm Works on Quarm

Based on the EQMacEmu source code analysis:

1. **Initial Cast**: Uses `CheckResistSpell` with normal resist mechanics
2. **Tick Checks**: Every 6 seconds (1 tick), the charm is checked for breaks:
   - 50% chance the check even occurs
   - If check occurs, runs `CheckResistSpell` with `tick_save=True` (adds +4 to caster level)
   - If the NPC resists (roll 0-200 <= resist_chance), charm breaks
3. **Six Level Rule**: If NPC is 7+ levels higher or 25%+ higher than caster, massive resist bonus applies
4. **Charisma Bonus (ENCHANTER ONLY!)**: For charm/mez spells, **ONLY ENCHANTERS** with CHA > 75 reduce resist modifier by (CHA-75)/8
   - **Druids and Necromancers do NOT get CHA bonuses for charm!**
   - This is explicitly coded: `if (caster->GetClass() == Class::Enchanter)`

## Spell Data

The calculator includes accurate charm spell data dynamically scraped from [pqdi.cc](https://www.pqdi.cc/spells):
- **6 Enchanter charms** (Charm → Command of Druzzil)
- **7 Druid animal charms** (Befriend Animal → Command of Tunare)
- **1 Necromancer undead charm** (Beguile Undead)

All spell data is automatically fetched from [pqdi.cc](https://www.pqdi.cc/spells), the authoritative database for Project Quarm/P99 era EverQuest spells.

**To update spell data**:
```bash
make refresh-spells  # Scrape latest from pqdi.cc and regenerate
```

See [SPELL_DATA.md](SPELL_DATA.md) for detailed documentation on the scraping process.

## Installation

```bash
# Clone or navigate to the directory
cd ~/workspace/QuarmCharmCalculator

# Option 1: Use the start script (recommended - uses venv automatically)
./start.sh

# Option 2: Manual installation with virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py

# Option 3: System-wide installation (not recommended)
pip3 install -r requirements.txt
python3 app.py
```

The server will start on `http://localhost:5000`

**Note**: The `start.sh` script automatically creates and uses a local virtual environment (`venv/`) to avoid impacting your system Python packages.

## Usage

1. Open your browser to `http://localhost:5000`
2. Select your charm spell from the dropdown (or enter custom resist diff)
3. Enter your level, target NPC level, and target NPC magic resist
4. Enter your charisma stat
5. Choose how many ticks to simulate (1 tick = 6 seconds)
6. Click "Calculate Charm Effectiveness"

The tool will show:
- Initial cast success probability
- Per-tick break chance
- Expected charm duration
- Detailed probability table over time
- Interactive graph of charm survival probability

### Log File Analysis

At the bottom of the page, you can upload your EQ log file to analyze your actual charm durations:

1. **Compress your log file**: First, compress your `eqlog_CharacterName_server.txt` file into a ZIP archive
   ```bash
   # On Linux/Mac
   zip eqlog_Fibbon_pq.proj.zip eqlog_Fibbon_pq.proj.txt

   # On Windows, right-click the file -> Send to -> Compressed (zipped) folder
   ```

2. Scroll to the "Analyze Your Charm Logs" section
3. Click "Choose File" and select your ZIP file
4. Click "Analyze Log File"

The tool will extract all charm cast and break events from your log and display:
- **Overall Statistics**: Average, median, min, max, P90, P95, P99 durations across all charms
- **By Spell**: Separate statistics for each charm spell you've used

This helps you compare the calculator's predictions against your actual gameplay results!

**Why ZIP?** EQ log files can be very large (multi-MB), but they're plain text and compress extremely well. A 50MB log file typically compresses to under 2MB, making uploads much faster.

**File Size Limits:**
- **Vercel Deployment**: 4MB maximum (serverless platform limit)
- **Local/Docker**: 50MB maximum
- If your compressed log is too large, create a smaller ZIP with just recent log entries

**Command Line Usage** (uses uncompressed files):
```bash
# Analyze a log file from the command line
make test-log LOG_FILE=/path/to/eqlog.txt

# Or directly with Python
python3 log_parser.py /path/to/eqlog.txt
```

## Example Results

**Level 60 Enchanter (200 CHA) vs Level 55 NPC (50 MR)**
- Using Allure (-50 resist diff)
- Initial land chance: ~95%
- Per-tick break chance: ~3.5%
- Expected duration: ~8-10 minutes

**Level 60 Enchanter (200 CHA) vs Level 60 NPC (100 MR)**
- Using Command of Druzzil (-200 resist diff)
- Initial land chance: ~75%
- Per-tick break chance: ~6%
- Expected duration: ~5-7 minutes

## Technical Details

### Resist Calculation

The resist chance calculation follows this formula (simplified):

```
resist_chance = target_MR + level_modifier + resist_modifier

level_modifier = (level_diff^2) / 2 (with sign based on diff)
resist_modifier = spell_resist_diff - (CHA-75)/8 (for enchanters on charm)

Roll: 0-200 vs resist_chance
Success if: roll > resist_chance
```

### Monte Carlo Simulation

The tool runs thousands of simulations (default 10,000) to determine statistical probabilities:
- Each simulation runs until charm breaks or max ticks reached
- Tracks at which tick the charm broke
- Calculates cumulative probability distribution
- Determines expected value (mean duration)

## Files

- `app.py` - Flask web server
- `charm_calculator.py` - Core resist calculation logic
- `charm_spells_data.py` - Generated database of all charm spells (Enchanter, Druid, Necromancer)
- `scrape_pqdi_spells.py` - Web scraper to fetch spell data from pqdi.cc
- `update_charm_spells.py` - Generates charm_spells_data.py from scraped JSON
- `pqdi_charm_spells.json` - Cached spell data from pqdi.cc
- `templates/index.html` - Web interface
- `requirements.txt` - Python dependencies
- `README.md` - This file

## Source Code Reference

This calculator is based on the EQMacEmu server source code:
- Resist logic: `zone/spells.cpp` - `Mob::CheckResistSpell()` (lines 3955-4370)
- Charm tick logic: `zone/spell_effects.cpp` - `case SE_Charm:` (lines 3031-3073)

## Credits

- Based on EQMacEmu/Quarm server source code
- Resist mechanics research from EQEmulator forums
- Created for the Quarm EverQuest server community

## License

This tool is provided as-is for the EverQuest emulator community. The resist calculation logic is derived from the open-source EQMacEmu project.

