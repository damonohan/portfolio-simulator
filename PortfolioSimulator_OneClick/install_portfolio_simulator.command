#!/bin/bash

# Portfolio Simulator Installer and Launcher
# This script automatically installs and runs the Portfolio Simulator
# The .command extension makes it double-clickable on Mac

# Clear the terminal for a cleaner interface
clear

# Move to the script's directory
cd "$(dirname "$0")"

echo "====================================="
echo "  PORTFOLIO SIMULATOR INSTALLER"
echo "====================================="
echo ""
echo "This script will set up and run Portfolio Simulator."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is required but not found."
    echo "Please install Python from python.org"
    echo ""
    echo "Opening Python download page..."
    open https://www.python.org/downloads/
    echo ""
    echo "After installing Python, double-click this file again."
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

echo "Python 3 found. Continuing with installation..."
echo ""

# Extract the portfolio simulator files
if [ -f "portfolio_simulator_files.zip" ]; then
    echo "Extracting portfolio simulator files..."
    unzip -o -q portfolio_simulator_files.zip
    echo "Extraction complete."
    echo ""
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    echo "Virtual environment created."
    echo ""
fi

# Activate virtual environment and install dependencies
echo "Setting up environment and installing dependencies..."
source .venv/bin/activate
pip install --upgrade pip > /dev/null
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt > /dev/null
else
    echo "ERROR: requirements.txt not found!"
    read -p "Press Enter to exit..."
    exit 1
fi
echo "Dependencies installed successfully."
echo ""

# Run the application
echo "Starting Portfolio Simulator..."
echo "====================================="
echo ""
python gui.py

# Deactivate virtual environment when the application closes
deactivate

# Keep terminal open if there was an error
if [ $? -ne 0 ]; then
    echo ""
    echo "An error occurred while running Portfolio Simulator."
    read -p "Press Enter to exit..."
fi 