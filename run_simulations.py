#!/usr/bin/env python3
"""
Portfolio Simulator - Main Simulation Runner

This script reads simulation parameters from a YAML file and executes
portfolio simulations based on those parameters. Results are stored in
a SQLite database for further analysis.
"""

import os
import sys
import argparse
import yaml
import logging
import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing
import time
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("portfolio_sim.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_market_data(data_dir="raw_data"):
    """
    Load market data from CSV files in the raw_data directory.
    
    Returns:
        dict: Dictionary containing market data DataFrames
    """
    logger.info(f"Loading market data from {data_dir}")
    
    try:
        # Load S&P 500 returns
        sp500_file = os.path.join(data_dir, "sp500_yearly.csv")
        sp500_data = pd.read_csv(sp500_file, index_col='Date', parse_dates=True)
        sp500_data = sp500_data.pct_change().dropna()
        
        # Load bond returns
        bond_file = os.path.join(data_dir, "bond_returns.csv")
        bond_data = pd.read_csv(bond_file, index_col='Date', parse_dates=True)
        
        # Load structured note parameters
        note_file = os.path.join("note_data", "growth_notes.csv")
        note_data = pd.read_csv(note_file)
        
        # Extract years from data
        sp500_data['year'] = sp500_data.index.year
        bond_data['year'] = bond_data.index.year
        
        # For inflation, use a default 2% if not available
        # In a real implementation, you would load actual inflation data
        years = sorted(list(set(sp500_data['year'].tolist())))
        inflation_data = pd.DataFrame({
            'year': years,
            'inflation_rate': [0.02] * len(years)  # Placeholder: 2% inflation
        })
        
        # Store market data in a dictionary
        market_data = {
            'sp500': sp500_data,
            'bonds': bond_data,
            'notes': note_data,
            'inflation': inflation_data,
            'years': years
        }
        
        logger.info(f"Loaded market data for {len(years)} years")
        return market_data
        
    except Exception as e:
        logger.error(f"Error loading market data: {e}")
        raise

def populate_market_conditions(db_path, market_data):
    """
    Populate the market_conditions table with historical data.
    
    Args:
        db_path (str): Path to the SQLite database
        market_data (dict): Dictionary containing market data
    """
    logger.info("Populating market conditions table")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Clear existing data
        cursor.execute("DELETE FROM market_conditions")
        
        # Extract required data
        sp500_data = market_data['sp500']
        bond_data = market_data['bonds']
        note_data = market_data['notes']
        inflation_data = market_data['inflation']
        
        # Prepare data for insertion
        market_rows = []
        for year in market_data['years']:
            # S&P 500 return for the year
            sp_return = sp500_data[sp500_data['year'] == year]['^GSPC'].iloc[0] if not sp500_data[sp500_data['year'] == year].empty else None
            
            # Bond return for the year
            bond_return = bond_data[bond_data['year'] == year]['total_return'].iloc[0] if not bond_data[bond_data['year'] == year].empty else None
            
            # Inflation rate
            inflation_rate = inflation_data[inflation_data['year'] == year]['inflation_rate'].iloc[0] if not inflation_data[inflation_data['year'] == year].empty else 0.02
            
            # Treasury rate (placeholder - in real implementation, get from data)
            treasury_rate = 0.04  # Default value
            
            # VIX level (placeholder - in real implementation, get from data)
            vix_level = 0.20  # Default value
            
            # Note participation rates
            note_params = {}
            for protection in [0.05, 0.10, 0.15, 0.20]:
                protection_str = f"{int(protection*100)}pct"
                notes_for_year = note_data[(note_data['year'] == year) & 
                                          (note_data['protection_level'] == protection)]
                
                note_params[f"note_participation_{protection_str}"] = (
                    notes_for_year['participation_rate'].iloc[0] if not notes_for_year.empty else 1.0
                )
            
            # Combine all data
            market_rows.append((
                year, 
                sp_return,
                bond_return,
                inflation_rate,
                treasury_rate,
                vix_level,
                note_params.get('note_participation_5pct', 1.0),
                note_params.get('note_participation_10pct', 1.0),
                note_params.get('note_participation_15pct', 1.0),
                note_params.get('note_participation_20pct', 1.0)
            ))
        
        # Insert into database
        cursor.executemany('''
        INSERT INTO market_conditions 
        (calendar_year, sp500_return, bond_return, inflation_rate, treasury_rate, 
         vix_level, note_participation_5pct, note_participation_10pct, 
         note_participation_15pct, note_participation_20pct)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', market_rows)
        
        conn.commit()
        conn.close()
        
        logger.info(f"Populated market conditions for {len(market_rows)} years")
        
    except Exception as e:
        logger.error(f"Error populating market conditions: {e}")
        raise

def generate_simulation_parameters(params):
    """
    Generate all combinations of simulation parameters based on the parameter file.
    
    Args:
        params (dict): Dictionary containing simulation parameters
        
    Returns:
        list: List of parameter dictionaries for each simulation
    """
    logger.info("Generating simulation parameter combinations")
    
    # Extract parameter ranges
    start_years = params['time_parameters']['start_years']
    time_horizons = params['time_parameters']['time_horizons']
    portfolio_types = params['portfolio_allocations'].keys()
    protection_levels = params['note_parameters']['protection_levels']
    withdrawal_rates = params['withdrawal_parameters']['rates']
    
    # Generate all valid combinations
    sim_params = []
    timestamp = datetime.now().isoformat()
    
    for start_year in start_years:
        for horizon in time_horizons:
            # Skip if we don't have enough data for this horizon
            if start_year + horizon > 2024:  # Assuming data ends in 2024
                continue
                
            for portfolio_type in portfolio_types:
                portfolio = params['portfolio_allocations'][portfolio_type]
                
                # For traditional portfolio with no notes, only run once (skip protection levels)
                if portfolio['notes'] == 0:
                    # Traditional portfolio doesn't use protection levels
                    for withdrawal_rate in withdrawal_rates:
                        sim_id = f"{start_year}_{portfolio_type}_traditional_{withdrawal_rate*100:.0f}pct_{horizon}yr"
                        
                        sim_params.append({
                            'sim_id': sim_id,
                            'start_year': start_year,
                            'portfolio_type': portfolio_type,
                            'equity_allocation': portfolio['equity'],
                            'note_allocation': portfolio['notes'],
                            'bond_allocation': portfolio['bonds'],
                            'protection_level': None,
                            'withdrawal_rate': withdrawal_rate,
                            'time_horizon': horizon,
                            'parameter_file': params.get('simulation_name', 'default'),
                            'run_timestamp': timestamp,
                            'starting_amount': params['initial_conditions']['starting_amount'],
                            'rebalancing_frequency': params['initial_conditions']['rebalancing_frequency']
                        })
                else:
                    # Portfolios with notes need to be run for each protection level
                    for protection_level in protection_levels:
                        for withdrawal_rate in withdrawal_rates:
                            sim_id = f"{start_year}_{portfolio_type}_{protection_level*100:.0f}pct_{withdrawal_rate*100:.0f}pct_{horizon}yr"
                            
                            sim_params.append({
                                'sim_id': sim_id,
                                'start_year': start_year,
                                'portfolio_type': portfolio_type,
                                'equity_allocation': portfolio['equity'],
                                'note_allocation': portfolio['notes'],
                                'bond_allocation': portfolio['bonds'],
                                'protection_level': protection_level,
                                'withdrawal_rate': withdrawal_rate,
                                'time_horizon': horizon,
                                'parameter_file': params.get('simulation_name', 'default'),
                                'run_timestamp': timestamp,
                                'starting_amount': params['initial_conditions']['starting_amount'],
                                'rebalancing_frequency': params['initial_conditions']['rebalancing_frequency']
                            })
    
    logger.info(f"Generated {len(sim_params)} simulation parameter combinations")
    return sim_params

def run_single_simulation(sim_params, market_data):
    """
    Run a single portfolio simulation with the given parameters.
    
    Args:
        sim_params (dict): Dictionary with simulation parameters
        market_data (dict): Dictionary containing market data
        
    Returns:
        tuple: (sim_params, yearly_results, summary_stats)
    """
    start_time = time.time()
    logger.debug(f"Starting simulation {sim_params['sim_id']}")
    
    try:
        # Extract parameters
        start_year = sim_params['start_year']
        horizon = sim_params['time_horizon']
        equity_allocation = sim_params['equity_allocation']
        note_allocation = sim_params['note_allocation']
        bond_allocation = sim_params['bond_allocation']
        protection_level = sim_params['protection_level']
        withdrawal_rate = sim_params['withdrawal_rate']
        initial_amount = sim_params['starting_amount']
        
        # Calculate initial withdrawal amount
        initial_withdrawal = initial_amount * withdrawal_rate
        
        # Initialize portfolio
        portfolio_value = initial_amount
        yearly_results = []
        
        # Get relevant market data
        sp500_data = market_data['sp500']
        bond_data = market_data['bonds']
        inflation_data = market_data['inflation']
        note_data = market_data['notes']
        
        # Run simulation for each year
        max_portfolio_value = portfolio_value
        running_max = portfolio_value
        
        for year_idx in range(horizon + 1):  # +1 to include initial state
            calendar_year = start_year + year_idx
            
            if year_idx == 0:
                # Initial state - no returns yet
                yearly_results.append({
                    'year': year_idx,
                    'calendar_year': calendar_year,
                    'starting_value': portfolio_value,
                    'ending_value': portfolio_value,
                    'withdrawal_amount': 0,
                    'equity_return': 0,
                    'note_return': 0,
                    'bond_return': 0,
                    'portfolio_return': 0,
                    'equity_value': portfolio_value * equity_allocation,
                    'note_value': portfolio_value * note_allocation,
                    'bond_value': portfolio_value * bond_allocation,
                    'inflation_rate': 0
                })
                continue
            
            # Get this year's market returns
            calendar_year = start_year + year_idx
            
            # S&P 500 return
            sp500_return = sp500_data[sp500_data['year'] == calendar_year]['^GSPC'].iloc[0] if not sp500_data[sp500_data['year'] == calendar_year].empty else 0.07
            
            # Bond return
            bond_return = bond_data[bond_data['year'] == calendar_year]['total_return'].iloc[0] if not bond_data[bond_data['year'] == calendar_year].empty else 0.04
            
            # Note return - based on S&P return and protection level
            if note_allocation > 0 and protection_level is not None:
                # Get participation rate for this year and protection level
                note_row = note_data[(note_data['year'] == calendar_year) & 
                                    (note_data['protection_level'] == protection_level)]
                
                participation_rate = note_row['participation_rate'].iloc[0] if not note_row.empty else 1.0
                
                # Calculate note return based on buffered protection
                if sp500_return > 0:
                    # Positive return with participation rate
                    note_return = sp500_return * participation_rate
                else:
                    # Negative return with protection
                    abs_return = abs(sp500_return)
                    if abs_return <= protection_level:
                        # Full protection
                        note_return = 0
                    else:
                        # Partial protection
                        note_return = -(abs_return - protection_level)
            else:
                # No notes in portfolio
                note_return = 0
            
            # Get inflation rate
            inflation_rate = inflation_data[inflation_data['year'] == calendar_year]['inflation_rate'].iloc[0] if not inflation_data[inflation_data['year'] == calendar_year].empty else 0.02
            
            # Calculate withdrawal for this year (adjust for inflation if needed)
            if year_idx == 1:
                withdrawal_amount = initial_withdrawal
            else:
                prev_withdrawal = yearly_results[-1]['withdrawal_amount']
                withdrawal_amount = prev_withdrawal * (1 + inflation_rate)
            
            # Calculate portfolio value before withdrawal
            prev_portfolio = yearly_results[-1]['ending_value']
            equity_value = prev_portfolio * equity_allocation * (1 + sp500_return)
            note_value = prev_portfolio * note_allocation * (1 + note_return)
            bond_value = prev_portfolio * bond_allocation * (1 + bond_return)
            
            pre_withdrawal_value = equity_value + note_value + bond_value
            
            # Apply withdrawal
            if pre_withdrawal_value <= withdrawal_amount:
                # Portfolio depleted
                ending_value = 0
                withdrawal_amount = pre_withdrawal_value  # Take what's left
            else:
                ending_value = pre_withdrawal_value - withdrawal_amount
            
            # Calculate overall portfolio return
            portfolio_return = (pre_withdrawal_value / prev_portfolio) - 1
            
            # Update running maximum for drawdown calculation
            running_max = max(running_max, pre_withdrawal_value)
            max_portfolio_value = max(max_portfolio_value, ending_value)
            
            # Store results for this year
            yearly_results.append({
                'year': year_idx,
                'calendar_year': calendar_year,
                'starting_value': prev_portfolio,
                'ending_value': ending_value,
                'withdrawal_amount': withdrawal_amount,
                'equity_return': sp500_return,
                'note_return': note_return,
                'bond_return': bond_return,
                'portfolio_return': portfolio_return,
                'equity_value': equity_value,
                'note_value': note_value,
                'bond_value': bond_value,
                'inflation_rate': inflation_rate
            })
            
            # Break if portfolio is depleted
            if ending_value <= 0:
                break
        
        # Calculate summary statistics
        end_value = yearly_results[-1]['ending_value']
        success_flag = 1 if end_value > 0 else 0
        
        # Calculate CAGR (Compound Annual Growth Rate)
        years_completed = yearly_results[-1]['year']
        if years_completed > 0:
            cagr = (end_value / initial_amount) ** (1 / years_completed) - 1
        else:
            cagr = 0
        
        # Calculate volatility
        returns = [r['portfolio_return'] for r in yearly_results[1:]]  # Skip first year
        volatility = np.std(returns) if returns else 0
        
        # Calculate maximum drawdown
        portfolio_values = [r['ending_value'] for r in yearly_results]
        max_drawdown = 0
        peak = portfolio_values[0]
        
        for value in portfolio_values:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak if peak > 0 else 0
            max_drawdown = max(max_drawdown, drawdown)
        
        # Adjust terminal value for inflation
        inflation_factors = [1 + r['inflation_rate'] for r in yearly_results]
        cumulative_inflation = np.prod(inflation_factors)
        inflation_adjusted_terminal = end_value / cumulative_inflation
        
        # Create summary statistics
        summary_stats = {
            'terminal_value': end_value,
            'success_flag': success_flag,
            'cagr': cagr,
            'max_drawdown': max_drawdown,
            'volatility': volatility,
            'inflation_adjusted_terminal': inflation_adjusted_terminal
        }
        
        # Update simulation parameters with summary statistics
        sim_params.update(summary_stats)
        
        elapsed_time = time.time() - start_time
        logger.debug(f"Completed simulation {sim_params['sim_id']} in {elapsed_time:.2f} seconds")
        
        return (sim_params, yearly_results)
        
    except Exception as e:
        logger.error(f"Error in simulation {sim_params['sim_id']}: {e}")
        raise

def save_simulation_results(db_path, results):
    """
    Save simulation results to the SQLite database.
    
    Args:
        db_path (str): Path to the SQLite database
        results (tuple): (sim_params, yearly_results)
    """
    sim_params, yearly_results = results
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Insert simulation parameters
        cursor.execute('''
        INSERT INTO simulations 
        (sim_id, start_year, portfolio_type, equity_allocation, note_allocation, bond_allocation,
         protection_level, withdrawal_rate, time_horizon, parameter_file, run_timestamp,
         terminal_value, success_flag, cagr, max_drawdown, volatility, inflation_adjusted_terminal)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            sim_params['sim_id'],
            sim_params['start_year'],
            sim_params['portfolio_type'],
            sim_params['equity_allocation'],
            sim_params['note_allocation'],
            sim_params['bond_allocation'],
            sim_params['protection_level'],
            sim_params['withdrawal_rate'],
            sim_params['time_horizon'],
            sim_params['parameter_file'],
            sim_params['run_timestamp'],
            sim_params['terminal_value'],
            sim_params['success_flag'],
            sim_params['cagr'],
            sim_params['max_drawdown'],
            sim_params['volatility'],
            sim_params['inflation_adjusted_terminal']
        ))
        
        # Insert yearly results
        for year_data in yearly_results:
            cursor.execute('''
            INSERT INTO yearly_results 
            (sim_id, year, calendar_year, starting_value, ending_value, withdrawal_amount,
             equity_return, note_return, bond_return, portfolio_return,
             equity_value, note_value, bond_value, inflation_rate)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                sim_params['sim_id'],
                year_data['year'],
                year_data['calendar_year'],
                year_data['starting_value'],
                year_data['ending_value'],
                year_data['withdrawal_amount'],
                year_data['equity_return'],
                year_data['note_return'],
                year_data['bond_return'],
                year_data['portfolio_return'],
                year_data['equity_value'],
                year_data['note_value'],
                year_data['bond_value'],
                year_data['inflation_rate']
            ))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        logger.error(f"Error saving simulation results: {e}")
        raise

def run_all_simulations(params, db_path, market_data, num_workers=None):
    """
    Run all simulations in parallel using a process pool.
    
    Args:
        params (dict): Dictionary containing simulation parameters
        db_path (str): Path to the SQLite database
        market_data (dict): Dictionary containing market data
        num_workers (int): Number of worker processes to use
    """
    # Generate all parameter combinations
    sim_params_list = generate_simulation_parameters(params)
    
    # Determine number of workers
    if num_workers is None:
        num_workers = max(1, multiprocessing.cpu_count() - 1)
    
    logger.info(f"Running {len(sim_params_list)} simulations with {num_workers} workers")
    start_time = time.time()
    count = 0
    
    # Use ProcessPoolExecutor for parallel execution
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        # Submit all simulations
        future_to_params = {
            executor.submit(run_single_simulation, sim_params, market_data): sim_params
            for sim_params in sim_params_list
        }
        
        # Process results as they complete
        for future in as_completed(future_to_params):
            sim_params = future_to_params[future]
            try:
                results = future.result()
                save_simulation_results(db_path, results)
                count += 1
                
                # Log progress periodically
                if count % 100 == 0 or count == len(sim_params_list):
                    elapsed = time.time() - start_time
                    logger.info(f"Completed {count}/{len(sim_params_list)} simulations ({count/len(sim_params_list)*100:.1f}%) in {elapsed:.1f} seconds")
                
            except Exception as e:
                logger.error(f"Error in simulation {sim_params['sim_id']}: {e}")
    
    total_time = time.time() - start_time
    logger.info(f"All simulations completed in {total_time:.1f} seconds")

def export_summary_csv(db_path, output_dir):
    """
    Export summary results to a CSV file.
    
    Args:
        db_path (str): Path to the SQLite database
        output_dir (str): Directory to save the CSV file
    """
    logger.info("Exporting summary results to CSV")
    
    try:
        conn = sqlite3.connect(db_path)
        
        # Query all simulation results
        query = '''
        SELECT * FROM simulations
        '''
        
        # Load into pandas DataFrame
        df = pd.read_sql_query(query, conn)
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Save to CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_path = os.path.join(output_dir, f"summary_results_{timestamp}.csv")
        df.to_csv(csv_path, index=False)
        
        conn.close()
        
        logger.info(f"Summary results exported to {csv_path}")
        
    except Exception as e:
        logger.error(f"Error exporting summary results: {e}")
        raise

def main():
    parser = argparse.ArgumentParser(description='Run portfolio simulations')
    parser.add_argument('--params', type=str, default='simulation_params.yaml',
                        help='Path to YAML parameter file')
    parser.add_argument('--workers', type=int, default=None,
                        help='Number of worker processes to use')
    parser.add_argument('--skip-setup', action='store_true',
                        help='Skip database setup step')
    args = parser.parse_args()
    
    try:
        # Load parameters
        with open(args.params, 'r') as f:
            params = yaml.safe_load(f)
        
        # Get database path from parameters
        db_path = params['output_parameters']['database_file']
        results_dir = params['output_parameters']['results_directory']
        
        # Ensure results directory exists
        os.makedirs(results_dir, exist_ok=True)
        
        # Setup database if needed
        if not args.skip_setup:
            logger.info("Setting up database")
            os.system(f"python setup_database.py --params {args.params}")
        
        # Load market data
        market_data = load_market_data()
        
        # Populate market conditions table
        populate_market_conditions(db_path, market_data)
        
        # Run simulations
        run_all_simulations(params, db_path, market_data, args.workers)
        
        # Export summary results
        export_summary_csv(db_path, results_dir)
        
        logger.info("Simulation process completed successfully")
        
    except Exception as e:
        logger.error(f"Error in simulation process: {e}")
        raise

if __name__ == "__main__":
    main() 