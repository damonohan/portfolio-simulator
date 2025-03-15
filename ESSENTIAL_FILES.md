# Essential Files for Portfolio Simulator

This document outlines the core files and directories that are essential for the proper functioning of the Portfolio Simulator application.

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