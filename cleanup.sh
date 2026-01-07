#!/bin/bash
# Cleanup script for Quarm Charm Calculator
# Removes the virtual environment and cached files

echo "Cleaning up Quarm Charm Calculator..."
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Remove virtual environment
if [ -d "venv" ]; then
    echo "Removing virtual environment..."
    rm -rf venv
    echo "  ✓ Removed venv/"
fi

# Remove Python cache
if [ -d "__pycache__" ]; then
    echo "Removing Python cache..."
    rm -rf __pycache__
    echo "  ✓ Removed __pycache__/"
fi

# Remove .pyc files
if ls *.pyc 1> /dev/null 2>&1; then
    echo "Removing .pyc files..."
    rm -f *.pyc
    echo "  ✓ Removed .pyc files"
fi

echo ""
echo "Cleanup complete!"
echo "Run ./start.sh to recreate the virtual environment."

