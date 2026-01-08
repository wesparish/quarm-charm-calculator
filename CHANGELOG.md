# Changelog

## [Unreleased]

### Added
- **Log File Analysis**: Upload EQ log files to analyze real charm duration statistics
  - Extract charm cast and break events from logs
  - Display average, median, min, max, P90, P95, P99 durations
  - Separate statistics per charm spell
  - **Supports all classes**: Automatically detects Druid (7 spells), Enchanter (6 spells), and Necromancer (1 spell) charms
  - **Dynamically loaded from database**: No hardcoded spell lists, always in sync with spell database
  - **ZIP compression required** for web uploads (faster uploads, log files compress 20-40x)
  - Command-line tool: `python3 log_parser.py <logfile>` or `make test-log LOG_FILE=<path>`
  - Web UI upload interface at bottom of calculator page
- **Duration Statistics in Calculator**: Main calculator now shows comprehensive duration statistics
  - Average, median, min, max, P90, P95, P99 durations for simulated charms
  - Beautiful table display with both minutes and seconds
  - Helps understand the full distribution of possible charm durations
- **Pet -MR Items and Debuffs field**: New input to calculate break probability accounting for -MR debuffs cast before charming and -MR items given to charmed pet
- **Automatic class detection**: Class is now automatically determined from spell selection (removed manual "Your Class" dropdown)
- **pqdi.cc spell data**: Switched to manually curated spell data from pqdi.cc (accurate for Quarm/P99 era)
- **update_charm_spells.py**: Script to regenerate spell data from curated list
- **SPELL_DATA.md**: Comprehensive documentation on spell data sources and update process
- **Makefile**: Added convenience commands for common tasks
- **Line graph**: Visual chart showing charm survival probability over time (using Chart.js)
- **NPC level validation**: Prevents calculating with NPC level higher than spell's max level
- **Dynamic help text**: CHA and Pet MR fields show contextual help based on spell selection

### Changed
- **Default NPC MR**: Changed from 50 to 35 (more realistic default)
- **Spell data source**: Replaced spells_en.txt parsing with manually curated data from pqdi.cc
- **Break probability calculation**: Now uses effective MR (base MR - pet items) for per-tick checks
- **Initial land chance**: Still uses base NPC MR (before giving pet items)
- **CSS fixes**: Fixed `.warning` class conflict that was hiding expected duration display

### Removed
- **spell_parser.py**: Removed unreliable spells_en.txt parser
- **fetch_charm_spells.py**: Removed failed web scraping attempt
- **data/spells_en.txt**: Removed outdated client spell file
- **"Your Class" dropdown**: Now automatically determined from spell selection

### Fixed
- **Expected Duration visibility**: Fixed CSS conflict that hid the expected duration when in warning range (5-10 min)
- **Cache-control headers**: Added headers to prevent browser caching issues during development
- **Docker build**: Removed unnecessary data directory creation

## Spell Data Changes

### Confirmed Accurate (from pqdi.cc)
- ✓ Enchanter: 7 spells (Charm through Command of Druzzil)
- ✓ Druid: 4 animal charms (Charm Animals through Call of Karana)
- ✓ Necromancer: 2 undead charms (Beguile Undead and Allure of Death)

All spell data verified against https://www.pqdi.cc/spells database.

## Technical Improvements

### Build Process
- Updated Dockerfile to include update_charm_spells.py
- Removed data/ directory references
- Simplified .dockerignore

### Development
- Added Makefile with common commands
- Improved error messaging for spell selection
- Better validation and user feedback

### Documentation
- Added SPELL_DATA.md for spell update process
- Updated README.md with spell data section
- Created this CHANGELOG.md

## Migration Notes

If you have local changes:

1. **Spell data**: Old charm_spells_data.py is replaced with pqdi.cc-sourced data
2. **Deleted files**: spell_parser.py, fetch_charm_spells.py, data/ directory
3. **Docker**: Rebuild image after pulling changes

## Known Issues

None at this time.

## Future Enhancements

- [ ] Add support for resist gear on caster
- [ ] Show tick-by-tick simulation visualization
- [ ] Export results to CSV/JSON
- [ ] Compare multiple spells side-by-side
- [x] Add historical charm duration tracking (log file analysis)

