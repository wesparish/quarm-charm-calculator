#!/bin/bash
# Quick start script for Quarm Charm Calculator
# Uses a local Python virtual environment to avoid impacting the system

echo "==================================="
echo "Quarm Charm Calculator"
echo "==================================="
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment"
        echo "You may need to install python3-venv:"
        echo "  sudo apt install python3-venv"
        exit 1
    fi
    echo "Virtual environment created!"
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip in venv
python -m pip install --upgrade pip -q

# Install dependencies if needed
echo "Checking dependencies..."
pip install -q -r requirements.txt

echo ""
echo "Starting web server..."
echo "Open your browser to: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the Flask app
python app.py

