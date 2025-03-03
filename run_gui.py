#!/usr/bin/env python3
"""
Portfolio Simulator GUI Launcher

This script launches the graphical user interface for the Portfolio Simulator.
It checks for required dependencies and installs them if missing.
"""

import sys
import subprocess
import importlib.util
import os
import tkinter as tk

def check_dependency(package_name):
    """Check if a package is installed."""
    return importlib.util.find_spec(package_name) is not None

def install_dependencies():
    """Install required dependencies for the Portfolio Simulator."""
    required_packages = ["numpy", "pandas", "matplotlib", "pillow"]
    missing_packages = [pkg for pkg in required_packages if not check_dependency(pkg)]
    
    if missing_packages:
        print(f"Installing missing dependencies: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_packages)
            print("Dependencies installed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"Error installing dependencies: {e}")
            return False
    return True

if __name__ == "__main__":
    print("Starting Portfolio Simulator GUI...")
    
    # Check and install dependencies if needed
    if not install_dependencies():
        print("Failed to install required dependencies. The GUI may not work properly.")
        input("Press Enter to continue anyway, or Ctrl+C to exit...")
    
    # Import the GUI module (only after dependencies are checked)
    from gui import PortfolioSimulatorGUI
    
    # Create data directories if they don't exist
    os.makedirs("data", exist_ok=True)
    os.makedirs("results", exist_ok=True)
    
    # Start the GUI
    root = tk.Tk()
    app = PortfolioSimulatorGUI(root)
    root.mainloop() 