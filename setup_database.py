#!/usr/bin/env python3
"""
Database setup script for portfolio simulator.
Creates the SQLite database structure for storing simulation results.
"""

import os
import sqlite3
import argparse
import yaml
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def create_database(db_path):
    """Create the SQLite database with proper schema for simulation results."""
    # Ensure directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Connect to database (creates if it doesn't exist)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    logger.info(f"Creating database at {db_path}")
    
    # Create simulations table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS simulations (
        sim_id TEXT PRIMARY KEY,              -- Unique identifier (e.g., "1980_balanced_10pct_4pct_20yr")
        start_year INTEGER,                   -- Historical starting year
        portfolio_type TEXT,                  -- E.g., "balanced", "growth", "traditional"
        equity_allocation REAL,               -- Percentage in decimal form
        note_allocation REAL,                 -- Percentage in decimal form
        bond_allocation REAL,                 -- Percentage in decimal form
        protection_level REAL,                -- Note protection level (decimal)
        withdrawal_rate REAL,                 -- Initial withdrawal rate (decimal)
        time_horizon INTEGER,                 -- Simulation length in years
        parameter_file TEXT,                  -- Reference to parameter file used
        run_timestamp TEXT,                   -- When simulation was executed
        
        -- Summary statistics (for quick filtering/analysis)
        terminal_value REAL,                  -- Ending portfolio value
        success_flag INTEGER,                 -- 1 if portfolio survived, 0 if depleted
        cagr REAL,                            -- Compound annual growth rate
        max_drawdown REAL,                    -- Maximum drawdown percentage
        volatility REAL,                      -- Standard deviation of returns
        inflation_adjusted_terminal REAL      -- Terminal value adjusted for inflation
    )
    ''')
    
    # Create yearly_results table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS yearly_results (
        sim_id TEXT,                          -- References simulations table
        year INTEGER,                         -- Year number in simulation (0, 1, 2...)
        calendar_year INTEGER,                -- Actual calendar year
        starting_value REAL,                  -- Portfolio value at start of year
        ending_value REAL,                    -- Portfolio value at end of year
        withdrawal_amount REAL,               -- Amount withdrawn this year
        equity_return REAL,                   -- Return on equity portion
        note_return REAL,                     -- Return on structured note portion
        bond_return REAL,                     -- Return on bond portion
        portfolio_return REAL,                -- Overall portfolio return
        equity_value REAL,                    -- Value of equity portion at year end
        note_value REAL,                      -- Value of note portion at year end
        bond_value REAL,                      -- Value of bond portion at year end
        inflation_rate REAL,                  -- Inflation rate this year
        
        PRIMARY KEY (sim_id, year),
        FOREIGN KEY (sim_id) REFERENCES simulations (sim_id)
    )
    ''')
    
    # Create market_conditions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS market_conditions (
        calendar_year INTEGER PRIMARY KEY,    -- Calendar year
        sp500_return REAL,                    -- S&P 500 return
        bond_return REAL,                     -- Bond index return
        inflation_rate REAL,                  -- Inflation rate
        treasury_rate REAL,                   -- Treasury yield
        vix_level REAL,                       -- Average VIX level
        note_participation_5pct REAL,         -- Participation rate for 5% buffer
        note_participation_10pct REAL,        -- Participation rate for 10% buffer
        note_participation_15pct REAL,        -- Participation rate for 15% buffer
        note_participation_20pct REAL         -- Participation rate for 20% buffer
    )
    ''')
    
    # Create simulation_parameters table to store parameter file versions
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS simulation_parameters (
        parameter_file TEXT PRIMARY KEY,      -- Parameter file name/path
        file_content TEXT,                    -- Full content of parameter file
        timestamp TEXT                        -- When parameters were recorded
    )
    ''')
    
    # Create indexes for faster queries
    cursor.execute('''CREATE INDEX IF NOT EXISTS idx_yearly_sim_id ON yearly_results(sim_id)''')
    cursor.execute('''CREATE INDEX IF NOT EXISTS idx_yearly_calendar_year ON yearly_results(calendar_year)''')
    cursor.execute('''CREATE INDEX IF NOT EXISTS idx_sim_portfolio_type ON simulations(portfolio_type)''')
    cursor.execute('''CREATE INDEX IF NOT EXISTS idx_sim_start_year ON simulations(start_year)''')
    
    conn.commit()
    conn.close()
    
    logger.info("Database schema created successfully")

def save_parameters_to_db(db_path, param_file):
    """Save the parameters file content to the database for reference."""
    try:
        with open(param_file, 'r') as f:
            param_content = f.read()
            
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT OR REPLACE INTO simulation_parameters 
        (parameter_file, file_content, timestamp) 
        VALUES (?, ?, ?)
        ''', (param_file, param_content, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        logger.info(f"Parameter file {param_file} saved to database")
    except Exception as e:
        logger.error(f"Error saving parameters to database: {e}")

def main():
    parser = argparse.ArgumentParser(description='Set up database for portfolio simulations')
    parser.add_argument('--params', type=str, default='simulation_params.yaml',
                        help='Path to YAML parameter file')
    args = parser.parse_args()
    
    try:
        # Load parameters
        with open(args.params, 'r') as f:
            params = yaml.safe_load(f)
        
        # Get database path from parameters
        db_path = params['output_parameters']['database_file']
        
        # Create database
        create_database(db_path)
        
        # Save parameter file to database
        save_parameters_to_db(db_path, args.params)
        
        logger.info(f"Database setup complete: {db_path}")
        
    except Exception as e:
        logger.error(f"Error setting up database: {e}")
        raise

if __name__ == "__main__":
    main() 