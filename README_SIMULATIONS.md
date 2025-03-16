# Portfolio Simulator - Parameter-Based Simulation Framework

This framework allows for comprehensive backtesting of portfolio strategies involving structured notes alongside traditional assets across different historical periods.

## Overview

The simulation framework consists of:

1. A parameter-based configuration system (YAML files)
2. A database for storing simulation results
3. Simulation execution engine
4. Analysis utilities

## Components

- `simulation_params.yaml` - Configuration file defining simulation parameters
- `setup_database.py` - Script to initialize the SQLite database
- `run_simulations.py` - Main script for running portfolio simulations
- `analyze_results.py` - Utilities for analyzing simulation results

## Requirements

- Python 3.7+
- Required packages: pandas, numpy, matplotlib, seaborn, pyyaml, sqlite3

Install dependencies:
```bash
pip install pandas numpy matplotlib seaborn pyyaml
```

## Usage

### 1. Setup

First, create a parameters file or use the provided `simulation_params.yaml`. Then set up the database:

```bash
python setup_database.py --params simulation_params.yaml
```

### 2. Run Simulations

Run all simulations defined in the parameters file:

```bash
python run_simulations.py --params simulation_params.yaml
```

Optional arguments:
- `--workers N` - Number of worker processes to use (default: CPU count - 1)
- `--skip-setup` - Skip database setup step

### 3. Analyze Results

Analyze the simulation results:

```bash
python analyze_results.py --db ./simulation_results/historical_retirement_2024_03/simulation_db.sqlite --output ./analysis_results
```

Optional arguments:
- `--plot-growth` - Plot portfolio growth curves
- `--compare-protection` - Compare different protection levels
- `--compare-portfolios` - Compare different portfolio types
- `--all` - Run all analyses

## Parameter Configuration

The `simulation_params.yaml` file defines all parameters for the simulations. Key sections include:

- `time_parameters` - Starting years and time horizons
- `portfolio_allocations` - Different portfolio allocations to test
- `note_parameters` - Structured note protection levels
- `withdrawal_parameters` - Withdrawal rates and methods
- `initial_conditions` - Starting amount and rebalancing frequency
- `output_parameters` - Results directory and database file

## Extending the Framework

To extend the framework:

1. **Add new portfolio allocations** - Add new entries to the `portfolio_allocations` section
2. **Test different withdrawal strategies** - Modify the withdrawal calculation in `run_single_simulation()`
3. **Add new analysis methods** - Create new functions in `analyze_results.py`

## Example Workflow

1. Define parameters in `simulation_params.yaml`
2. Run `python setup_database.py --params simulation_params.yaml`
3. Run `python run_simulations.py --params simulation_params.yaml`
4. Analyze results with `python analyze_results.py --db ./simulation_results/historical_retirement_2024_03/simulation_db.sqlite --output ./analysis_results --all`
5. Review the generated analysis files and visualizations

## Data Requirements

The framework expects the following data files:

- `raw_data/sp500_yearly.csv` - Yearly S&P 500 price data
- `raw_data/bond_returns.csv` - Yearly bond return data
- `note_data/growth_notes.csv` - Structured note parameters for each year/protection level

Make sure these files exist before running simulations. 