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
   git clone https://github.com/yourusername/portfolio_simulator.git
   cd portfolio_simulator
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install required packages:
   ```
   pip install -r requirements.txt
   ```

## Data Files

The simulator requires three CSV files:

1. **S&P 500 Returns** (`data/sp500_returns.csv`): Historical annual returns of the S&P 500 index
2. **Bond Returns** (`data/bond_returns.csv`): Historical annual returns of bonds
3. **Structured Notes** (`data/structured_notes.csv`): Historical structured note parameters

## Using the GUI

The Portfolio Simulator includes a graphical user interface for easier use:

1. Launch the GUI:
   ```
   python run_gui.py
   ```
   or
   ```
   ./run_gui.py
   ```

2. In the GUI:
   - Configure simulation parameters in the "Simulation Setup" tab
   - Set date ranges, initial value, and portfolio allocations
   - Configure structured note parameters and withdrawal strategies
   - Click "Run Simulation" to execute
   - View and analyze results in the "Results" tab

## Running Simulations from Command Line

### Basic Usage

Run a basic simulation with default parameters:

```
python run_simulation.py
```

### Customizing Simulations

You can customize various simulation parameters:

```
python run_simulation.py --start_year 2005 --end_year 2022 --initial_value 1000000 --protection_level 0.1 --withdrawal_rate 0.04
```

### Command Line Options

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

## Output

Simulation results are saved to the specified output directory:

- **Detailed Results**: CSV file with year-by-year data for each portfolio
- **Summary Statistics**: CSV file with aggregate performance metrics
- **Plots** (if enabled): Portfolio values and annual returns over time

## Example

Compare a traditional 60/40 portfolio with a structured note portfolio during retirement:

```
python run_simulation.py --start_year 2000 --end_year 2020 --initial_value 1000000 --withdrawal_rate 0.04 --withdrawal_type fixed_percent --protection_level 0.1 --plot
```

## Project Structure

- `src/data_processing.py`: Functions for loading and processing data
- `src/structured_notes.py`: Classes for structured note modeling
- `src/portfolio.py`: Portfolio management classes
- `src/retirement.py`: Withdrawal strategy implementations
- `src/simulation.py`: Core simulation engine
- `src/main.py`: Main implementation of the simulator
- `run_simulation.py`: Command-line entry point
- `gui.py`: Graphical user interface implementation
- `run_gui.py`: GUI entry point 