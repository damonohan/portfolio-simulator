# Portfolio Simulator

A tool for simulating and comparing different investment portfolio strategies, including traditional stock/bond allocations and structured note-based portfolios.

## Features

- Compare traditional 60/40 portfolios with structured note portfolios
- Analyze historical performance using real market data
- Model different withdrawal strategies for retirement planning
- Calculate key performance metrics (returns, volatility, maximum drawdown)
- Generate visualizations of portfolio performance over time
- User-friendly GUI for easy parameter configuration and simulation execution

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/damonohan/portfolio-simulator.git
   cd portfolio-simulator
   ```

2. Create a virtual environment (recommended for Python 3.11.7):
   ```
   python -m venv venv
   source venv/bin/activate  # On Mac: source venv/bin/activate
                             # On Windows: venv\Scripts\activate
   ```

3. Install required packages:
   ```
   pip install -r requirements.txt
   ```

## Running the Application

Launch the GUI application:
```
python run_gui.py
```

The GUI provides an intuitive interface to configure and run portfolio simulations.

## Data Files

The simulator uses three main CSV files:

1. **S&P 500 Returns** (`data/sp500_returns.csv`): Historical annual returns of the S&P 500 index
2. **Bond Returns** (`data/bond_returns.csv`): Historical annual returns of bonds
3. **Structured Notes** (`data/structured_notes.csv`): Structured note parameters

## Data Generation Tools

This project includes tools for generating and updating the simulation data:

- **raw_data_collector.py**: Fetches market data from public sources
- **note_calculator.py**: Calculates structured note participation rates
- **cleanup_notes.py**: Utility for managing note data files

## Using the GUI

1. In the GUI:
   - Configure simulation parameters in the "Simulation Setup" tab
   - Set date ranges, initial value, and portfolio allocations
   - Configure structured note parameters and withdrawal strategies
   - Click "Run Simulation" to execute
   - View and analyze results in the "Results" tab

## Command Line Simulations

You can also run simulations from the command line:

```
python run_simulation.py --start_year 2005 --end_year 2022 --initial_value 1000000
```

For full command-line options, see the later sections of this README.

## Project Structure

- `src/`: Core simulation code
  - `data_processing.py`: Functions for loading and processing data
  - `structured_notes.py`: Classes for structured note modeling
  - `portfolio.py`: Portfolio management classes
  - `retirement.py`: Withdrawal strategy implementations
  - `simulation.py`: Core simulation engine
  - `main.py`: Main implementation of the simulator
- `data/`: Essential data files
- `images/`: Images used in the GUI
- `run_simulation.py`: Command-line entry point
- `gui.py`: Graphical user interface implementation
- `run_gui.py`: GUI entry point
- `raw_data_collector.py`: Tool to collect market data
- `note_calculator.py`: Tool to calculate structured note parameters
- `results/`: Directory for simulation outputs

## Working with GitHub

The portfolio simulator is set up for version control with Git and GitHub.

### When working on multiple computers:

1. Always pull the latest changes before starting work:
   ```
   git pull origin main
   ```

2. After making changes, commit and push them:
   ```
   git add .
   git commit -m "Description of changes"
   git push origin main
   ```

### Command Line Options for Simulations

- **Data Sources**:
  - `--sp500_file`: Path to S&P 500 returns CSV file (default: 'data/sp500_returns.csv')
  - `--bond_file`: Path to bond returns CSV file (default: 'data/bond_returns.csv')
  - `--notes_file`: Path to structured notes CSV file (default: 'data/structured_notes.csv')

- **Simulation Parameters**:
  - `--start_year`: First year of simulation (default: 2000)
  - `--end_year`: Last year of simulation (default: 2020)
  - `--initial_value`: Initial portfolio value (default: 1,000,000)

- **Portfolio Allocations**:
  - `--trad_sp500`: Traditional portfolio allocation to S&P 500 (default: 0.6)
  - `--trad_bonds`: Traditional portfolio allocation to bonds (default: 0.4)
  - `--struct_sp500`: Structured portfolio allocation to S&P 500 (default: 0.4)
  - `--struct_bonds`: Structured portfolio allocation to bonds (default: 0.3)
  - `--struct_notes`: Structured portfolio allocation to structured notes (default: 0.3)

- **Structured Note Parameters**:
  - `--protection_level`: Target protection level for structured notes (default: 0.1)

- **Withdrawal Parameters**:
  - `--withdrawal_rate`: Annual withdrawal rate (default: 0.04)
  - `--withdrawal_type`: Withdrawal strategy type: 'fixed_percent', 'fixed_dollar', or 'rmd' (default: 'fixed_percent')
  - `--initial_age`: Initial age for RMD calculations (default: 65)

- **Output Options**:
  - `--output_dir`: Directory to save results (default: 'results')
  - `--plot`: Generate and save plots 