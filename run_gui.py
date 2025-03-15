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
import platform
import tkinter as tk

# Fix for Mac GUI rendering issues - Set matplotlib backend
try:
    import matplotlib
    # Use TkAgg backend on Mac for better compatibility
    if platform.system() == 'Darwin':  # macOS
        matplotlib.use('TkAgg')
        # Also disable fork safety on macOS if needed
        os.environ['OBJC_DISABLE_INITIALIZE_FORK_SAFETY'] = 'YES'
except ImportError:
    pass

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

def check_tkinter():
    """Check if tkinter is working properly."""
    try:
        # Try to create a simple tkinter window as a test
        test_root = tk.Tk()
        test_root.title("Testing Tkinter")
        # Create a label to ensure rendering works
        label = tk.Label(test_root, text="Tkinter is working!")
        label.pack(padx=20, pady=20)
        
        # Only show for a moment then destroy
        test_root.after(500, test_root.destroy)
        test_root.mainloop()
        return True
    except Exception as e:
        print(f"Warning: Tkinter may not be working properly: {e}")
        return False

if __name__ == "__main__":
    print("Starting Portfolio Simulator GUI...")
    print(f"Python version: {platform.python_version()}")
    print(f"Operating system: {platform.system()} {platform.release()}")
    
    # Check and install dependencies if needed
    if not install_dependencies():
        print("Failed to install required dependencies. The GUI may not work properly.")
        input("Press Enter to continue anyway, or Ctrl+C to exit...")
    
    # Check tkinter functionality
    if platform.system() == 'Darwin':  # If on macOS
        print("macOS detected - checking tkinter functionality...")
        check_tkinter()
        print("Note: If GUI appears black, try using 'pythonw run_gui.py' instead")
    
    # Import the GUI module (only after dependencies are checked)
    from gui import PortfolioSimulatorGUI
    
    # Create data directories if they don't exist
    os.makedirs("data", exist_ok=True)
    os.makedirs("results", exist_ok=True)
    
    # Start the GUI
    root = tk.Tk()
    
    # Additional Mac-specific settings
    if platform.system() == 'Darwin':
        # Force update the window
        root.update_idletasks()
        # Set theme to light mode to help with visibility
        root.tk_setPalette(background='#f0f0f0', foreground='black')
    
    app = PortfolioSimulatorGUI(root)
    root.mainloop() 