# Essential Files for Portfolio Simulator

This document outlines the core files and directories that are essential for the proper functioning of the Portfolio Simulator application.

## Environment Requirements

### Python Version
- **Python 3.11.7** is specifically required
- Install from [python.org](https://www.python.org/downloads/release/python-3117/) for best compatibility
- Using other Python versions may cause GUI rendering issues

### Mac-specific Requirements
- Properly installed Tcl/Tk framework (included with python.org installer)
- Use `pythonw` instead of `python` to launch GUI applications
- XQuartz may be needed for some graphical elements: https://www.xquartz.org/
- For black GUI issues:
  - Reinstall Pillow: `pip install --upgrade pillow`
  - Verify tkinter works: `python -m tkinter`

### Required Python Packages
- numpy==1.24.3
- pandas==2.0.2
- matplotlib==3.7.1
- pillow==9.5.0

## Core Application Files

- **`gui.py`**: Main GUI implementation for the application
- **`run_gui.py`**: Script to launch the GUI application
- **`requirements.txt`**: Lists all the Python package dependencies

## Core Source Code

- **`src/`**: Directory containing all simulation logic
  - `__init__.py`: Package initialization
  - `simulation.py`: Core simulation engine
  - `portfolio.py`: Portfolio management classes
  - `structured_notes.py`: Classes for structured note modeling
  - `data_processing.py`: Functions for loading and processing data
  - `retirement.py`: Withdrawal strategy implementations
  - `main.py`: Main implementation of the simulator

## Data Files

- **`data/`**: Essential data for simulations
  - `sp500_returns.csv`: Historical S&P 500 returns
  - `bond_returns.csv`: Historical bond returns
  - `structured_notes.csv`: Structured note parameters

## Data Generation and Note Calculation

*These files are crucial for generating and updating data used in simulations:*

- **`raw_data_collector.py`**: Script to fetch market data
- **`note_calculator.py`**: Calculator for structured note participation rates
- **`cleanup_notes.py`**: Utility to clean up old note data files
- **`note_participation_rates.csv`**: Note participation rate data

## Data Directories

- **`raw_data/`**: Raw market data used for calculations
- **`note_data/`**: Structured note data
- **`results/`**: Directory for simulation results (can be empty)
- **`images/`**: Contains images used in the GUI

## Documentation

- **`README.md`**: Main project documentation and usage instructions

## Running on Different Platforms

### Mac
```bash
# Verify tkinter is working
python -m tkinter

# Launch application with pythonw (recommended)
pythonw run_gui.py
```

### Windows/Linux
```bash
# Standard launch
python run_gui.py
```

## Troubleshooting

### GUI Issues
- Matplotlib backend issues - Try adding this to scripts:
  ```python
  import matplotlib
  matplotlib.use('TkAgg')  # or try 'Agg', 'Qt5Agg'
  ```
- For macOS fork safety issues:
  ```bash
  export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
  ```

## Directories that can be safely removed

- **`build/`**: Build artifacts for executable creation
- **`dist/`**: Distribution packages
- **`__pycache__/`**: Python bytecode
- **`PortfolioSimulator_OneClick/`**: Packaging experiment
- **`Portfolio_Simulator_Mac/`**: Packaging experiment

## Files that can be safely removed

- Log files (*.log)
- Temporary files
- Old simulation results
- Backup files 