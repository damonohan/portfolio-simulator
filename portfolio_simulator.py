import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PortfolioSimulator:
    """
    Portfolio simulator that reads market data files and structured note data
    to simulate portfolio performance with different allocation strategies.
    """
    
    def __init__(self, data_dir="raw_data", note_dir="note_data"):
        """Initialize the simulator with paths to required data files"""
        self.data_dir = data_dir
        self.note_dir = note_dir
        
        # Data containers
        self.sp500_data = None
        self.treasury_data = None
        self.bond_data = None
        self.growth_notes = None
        
        # Load data
        self.load_market_data()
        self.load_note_data()
        
    def load_market_data(self):
        """Load market data from CSV files"""
        logger.info("Loading market data...")
        
        # Load S&P 500 yearly prices
        sp500_path = os.path.join(self.data_dir, "sp500_yearly.csv")
        if os.path.exists(sp500_path):
            self.sp500_data = pd.read_csv(sp500_path, index_col='Date', parse_dates=True)
            logger.info(f"Loaded S&P 500 data: {len(self.sp500_data)} years")
        else:
            logger.warning(f"S&P 500 data file not found: {sp500_path}")
        
        # Load Treasury yields
        treasury_path = os.path.join(self.data_dir, "treasury_yearly.csv")
        if os.path.exists(treasury_path):
            self.treasury_data = pd.read_csv(treasury_path, index_col='Date', parse_dates=True)
            logger.info(f"Loaded Treasury data: {len(self.treasury_data)} years")
        else:
            logger.warning(f"Treasury data file not found: {treasury_path}")
        
        # Try to load bond returns if available
        bond_path = os.path.join(self.data_dir, "bond_returns.csv")
        if os.path.exists(bond_path):
            self.bond_data = pd.read_csv(bond_path, index_col='Date', parse_dates=True)
            logger.info(f"Loaded bond return data: {len(self.bond_data)} years")
        else:
            logger.info(f"Bond returns file not found: {bond_path} (may need to be generated)")
    
    def load_note_data(self):
        """Load structured note data"""
        logger.info("Loading structured note data...")
        
        # Load growth notes
        notes_path = os.path.join(self.note_dir, "growth_notes.csv")
        if os.path.exists(notes_path):
            self.growth_notes = pd.read_csv(notes_path)
            logger.info(f"Loaded growth notes: {len(self.growth_notes)} notes")
        else:
            logger.warning(f"Growth notes file not found: {notes_path}")
    
    def display_data_summary(self):
        """Display summary of loaded data"""
        print("\n=== Data Summary ===")
        
        if self.sp500_data is not None:
            print(f"\nS&P 500 Data ({len(self.sp500_data)} years):")
            print(f"  Date range: {self.sp500_data.index.min()} to {self.sp500_data.index.max()}")
            print(f"  Sample data:\n{self.sp500_data.head()}")
        
        if self.treasury_data is not None:
            print(f"\nTreasury Data ({len(self.treasury_data)} years):")
            print(f"  Date range: {self.treasury_data.index.min()} to {self.treasury_data.index.max()}")
            print(f"  Sample data:\n{self.treasury_data.head()}")
        
        if self.growth_notes is not None:
            print(f"\nGrowth Notes ({len(self.growth_notes)} notes):")
            print(f"  Sample notes:\n{self.growth_notes.head()}")
            
            # Show distribution of note characteristics
            if len(self.growth_notes) > 0:
                print("\nStructured Note Characteristics:")
                print(f"  Participation rates: {self.growth_notes['participation_rate'].describe()}")
                print(f"  Barriers: {self.growth_notes['barrier'].describe() if 'barrier' in self.growth_notes.columns else 'N/A'}")

if __name__ == "__main__":
    # Create and initialize the simulator
    simulator = PortfolioSimulator()
    
    # Display summary of loaded data
    simulator.display_data_summary() 