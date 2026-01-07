# Virtual Environment Setup

The Quarm Charm Calculator now uses a **local Python virtual environment** to keep your system clean and avoid dependency conflicts.

## What Changed

### Before:
- Dependencies installed globally with `pip3 install`
- Could conflict with system packages
- Required sudo or user-level pip permissions

### After:
- Dependencies installed in local `venv/` directory
- Completely isolated from system Python
- No sudo needed
- Easy to clean up

## How It Works

When you run `./start.sh`:

1. **First run**: Creates a new virtual environment in `venv/`
2. **Every run**:
   - Activates the virtual environment
   - Installs/updates dependencies if needed
   - Runs the Flask app from within the venv

## Benefits

✅ **Isolated**: Won't affect your system Python packages
✅ **Clean**: Easy to remove (just delete `venv/` directory)
✅ **Reproducible**: Same dependencies every time
✅ **No Conflicts**: Won't interfere with other Python projects
✅ **No Sudo**: Doesn't require root permissions

## Quick Commands

```bash
# Start the server (creates venv automatically)
./start.sh

# Clean up everything (removes venv and cache)
./cleanup.sh

# Manually recreate venv
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Troubleshooting

**Error: "No module named 'venv'"**

Install the venv module:
```bash
sudo apt install python3-venv
```

**Want to use system packages instead?**

Just run directly without the script:
```bash
pip3 install -r requirements.txt
python3 app.py
```

## File Structure

```
QuarmCharmCalculator/
├── venv/                 # Virtual environment (auto-created, git-ignored)
│   ├── bin/             # Python executables
│   ├── lib/             # Installed packages (Flask, etc.)
│   └── pyvenv.cfg       # Venv configuration
├── start.sh             # Start script (uses venv)
├── cleanup.sh           # Cleanup script (removes venv)
├── requirements.txt     # Python dependencies
└── ...
```

The `venv/` directory is automatically ignored by git (in `.gitignore`).

