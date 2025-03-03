#!/bin/bash

echo "HALO Portfolio Simulator Installation and Setup"
echo "==============================================="
echo
echo "This script will set up everything needed to run the Portfolio Simulator."
echo

# Check if Python is installed
echo "Step 1: Checking if Python is installed..."
if ! command -v python3 &> /dev/null; then
    echo "Python is not installed. The script will download and install it for you."
    echo
    
    # Create temporary directory
    echo "Creating temporary directory..."
    mkdir -p temp_python_installer
    cd temp_python_installer
    
    # Download Python installer
    echo "Downloading Python installer..."
    curl -L https://www.python.org/ftp/python/3.11.7/python-3.11.7-macos11.pkg -o python_installer.pkg
    
    if [ ! -f "python_installer.pkg" ]; then
        echo "Failed to download Python installer."
        echo "Please install Python manually from https://www.python.org/downloads/"
        echo
        read -p "Press Enter to exit..."
        cd ..
        exit 1
    fi
    
    # Install Python
    echo "Installing Python... (This may take a few minutes)"
    echo "You may be prompted for your password and to accept security prompts."
    sudo installer -pkg python_installer.pkg -target /
    
    if [ $? -ne 0 ]; then
        echo "Failed to install Python."
        echo "Please try installing Python manually from https://www.python.org/downloads/"
        echo
        read -p "Press Enter to exit..."
        cd ..
        exit 1
    fi
    
    echo "Python installation completed!"
    cd ..
    
    echo
    echo "Python has been installed! Continuing setup..."
else
    echo "Python is already installed! Continuing setup..."
fi

echo

# Set up virtual environment
echo "Step 2: Setting up virtual environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo "Failed to create virtual environment."
        echo "Please contact the person who shared this with you."
        echo
        read -p "Press Enter to exit..."
        exit 1
    fi
fi

# Activate virtual environment
echo "Step 3: Activating virtual environment..."
source .venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Failed to activate virtual environment."
    echo "Please contact the person who shared this with you."
    echo
    read -p "Press Enter to exit..."
    exit 1
fi

# Install required packages
echo "Step 4: Installing required packages..."
echo "This may take a few minutes..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Failed to install required packages."
    echo "Please contact the person who shared this with you."
    echo
    read -p "Press Enter to exit..."
    exit 1
fi

echo
echo "All setup completed successfully!"
echo
echo "Starting HALO Portfolio Simulator..."
echo
echo "(When you're done using the simulator, you can close its window.)"

# Run the application
python gui.py

echo
echo "Thank you for using HALO Portfolio Simulator!"
echo "To run it again, just double-click this file."
echo
read -p "Press Enter to exit..." 