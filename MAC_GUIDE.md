# Mac-Specific Guide for Portfolio Simulator

This guide addresses common issues Mac users might encounter when running the Portfolio Simulator, particularly with the GUI interface.

## Installation Requirements

### 1. Python Version

**Use Python 3.11.7 specifically** - Download from the official Python website:
- Visit: https://www.python.org/downloads/release/python-3117/
- Download the "macOS 64-bit universal2 installer"
- Follow the installation instructions

Do NOT use Homebrew or other package managers to install Python, as they might not include the proper Tcl/Tk framework needed for tkinter.

### 2. Verify Python Installation

After installing Python, verify the installation:

```bash
# Check Python version
python --version  # Should show Python 3.11.7

# Test if tkinter is working
python -m tkinter  # Should open a small window
```

If the tkinter test doesn't open a window, the Tcl/Tk framework may not be properly installed.

## Running the Application

### Recommended Method

Use `pythonw` instead of `python` to launch the GUI on Mac:

```bash
# Navigate to the project directory
cd portfolio-simulator

# Activate virtual environment if you created one
source venv/bin/activate

# Launch with pythonw (recommended for Mac)
pythonw run_gui.py
```

## Troubleshooting Black/Blank GUI

If you see a black or blank window when launching the GUI:

### 1. Update Dependencies

```bash
# Upgrade Pillow (handles images)
pip install --upgrade pillow

# Force reinstall tkinter-related packages
pip uninstall -y tk tcl
pip install tk tcl
```

### 2. Try Different Matplotlib Backend

Create a file called `fix_mac.py` in the project directory:

```python
# Contents of fix_mac.py
import matplotlib
matplotlib.use('Agg')  # Try different backends: 'Agg', 'TkAgg', 'Qt5Agg'

# Import this file before importing matplotlib in your code
```

Then run:
```bash
pythonw -c "import fix_mac; from gui import PortfolioSimulatorGUI; import tkinter as tk; root = tk.Tk(); app = PortfolioSimulatorGUI(root); root.mainloop()"
```

### 3. Environment Variables

Some Mac versions require special environment variables:

```bash
# Run these before starting the application
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES

# Then launch the app
pythonw run_gui.py
```

### 4. Install XQuartz

Some Mac installations may need XQuartz for proper rendering:

1. Download from: https://www.xquartz.org/
2. Install and restart your computer
3. Try running the application again

## Alternative: Command Line Mode

If the GUI still doesn't work, you can use the command-line version:

```bash
python run_simulation.py --start_year 2005 --end_year 2022 --initial_value 1000000
```

## Last Resort: Python Reinstallation

If nothing else works, try completely reinstalling Python:

1. Uninstall Python 3.11.7
2. Download a fresh copy from python.org
3. During installation, make sure to check "Install Tcl/Tk"
4. Restart your computer
5. Reinstall the portfolio simulator dependencies

## Support

If you continue to have issues after trying these solutions, please submit an issue on GitHub with the following information:
- Your exact macOS version
- The output of `python --version`
- The output of `python -c "import tkinter; print(tkinter.TkVersion)"`
- Screenshots of any error messages 