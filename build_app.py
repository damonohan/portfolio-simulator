#!/usr/bin/env python3
"""
Build script for creating a standalone executable of the Portfolio Simulator

This script uses PyInstaller to create a standalone executable for the Portfolio Simulator
that includes all dependencies and data files. The resulting executable can be shared
with others without requiring them to install Python or dependencies.
"""

import os
import sys
import subprocess
import shutil
from datetime import datetime

def main():
    print("Building Portfolio Simulator executable...")
    
    # Create version identifier based on date
    version = datetime.now().strftime("%Y%m%d")
    
    # Create a dist directory for the output
    if not os.path.exists("dist"):
        os.makedirs("dist")
    
    # Build the executable with PyInstaller
    build_cmd = [
        "pyinstaller",
        "--name=HALO_Portfolio_Simulator_" + version,
        "--windowed",  # Use GUI mode (no console window)
        "--onefile",   # Create a single executable file
        "--add-data=data/*:data",  # Bundle data files
        "--add-data=src/*:src",    # Bundle source files
        "run_gui.py"    # Main entry point
    ]
    
    # Add platform-specific options
    if sys.platform == "darwin":  # macOS
        build_cmd.extend([
            "--icon=images/halo_icon.icns",
            "--osx-bundle-identifier=com.halo.portfoliosimulator"
        ])
    elif sys.platform == "win32":  # Windows
        build_cmd.extend([
            "--icon=images/halo_icon.ico"
        ])
    
    # Run PyInstaller
    subprocess.run(build_cmd)
    
    # Create a zip file of the data directory for portability
    print("Creating data package...")
    shutil.make_archive(f"dist/portfolio_data_{version}", "zip", "data")
    
    print(f"Build complete! Executable saved to dist/HALO_Portfolio_Simulator_{version}")
    print(f"Data package saved to dist/portfolio_data_{version}.zip")
    print("\nTo share this application:")
    print("1. Share the executable file")
    print("2. Share the data package (zip file)")
    print("3. Instruct users to extract the data package to a 'data' folder in the same directory as the executable")

if __name__ == "__main__":
    main() 