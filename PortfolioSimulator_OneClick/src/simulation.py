import logging
import pandas as pd
import numpy as np
from datetime import datetime
from .portfolio import Portfolio
from .structured_notes import create_note
from .retirement import create_withdrawal_strategy

# Configure logging
logger = logging.getLogger(__name__)

class PortfolioSimulation:
    """Simulates portfolio performance over time with optional withdrawals."""
    
    def __init__(self, sp500_returns, bond_returns, notes_data, start_year, end_year, 
                 initial_value, portfolio_allocations, note_selection_params=None,
                 withdrawal_params=None, pre_selected_notes=None):
        """
        Initialize simulation with required data and parameters.
        
        Parameters:
        - sp500_returns: Dict mapping years to S&P 500 returns
        - bond_returns: Dict mapping years to bond returns
        - notes_data: DataFrame containing structured note data
        - start_year: First year in the simulation
        - end_year: Last year in the simulation
        - initial_value: Starting portfolio value
        - portfolio_allocations: Dict mapping portfolio names to allocation dicts
          e.g., {"traditional": {"sp500": 0.6, "bonds": 0.4},
                 "structured": {"sp500": 0.5, "bonds": 0.3, "notes": 0.2}}
        - note_selection_params: Dict of parameters for selecting structured notes
        - withdrawal_params: Dict of withdrawal strategy parameters
        - pre_selected_notes: Dict mapping years to note parameters (optional)
        """
        self.sp500_returns = sp500_returns
        self.bond_returns = bond_returns
        self.notes_data = notes_data
        self.start_year = start_year
        self.end_year = end_year
        self.initial_value = initial_value
        self.portfolio_allocations = portfolio_allocations
        self.note_selection_params = note_selection_params
        self.withdrawal_params = withdrawal_params
        self.pre_selected_notes = pre_selected_notes
        
        # Dictionaries to store simulation results
        self.portfolios = {}
        self.results = {}
        
        # Initialize portfolios
        self._initialize_portfolios()
        
        # Set up withdrawal strategy if provided
        self.withdrawal_strategy = None
        if withdrawal_params:
            self._initialize_withdrawal_strategy()
        
        logger.info(f"Initialized simulation: {start_year} to {end_year}")
    
    def _initialize_portfolios(self):
        """Initialize portfolio objects for each allocation strategy."""
        for name, allocations in self.portfolio_allocations.items():
            self.portfolios[name] = Portfolio(self.initial_value, allocations)
            self.results[name] = []
            logger.info(f"Created portfolio '{name}' with allocations: {allocations}")
    
    def _initialize_withdrawal_strategy(self):
        """Initialize the withdrawal strategy based on parameters."""
        if self.withdrawal_params:
            # Add start_year to params if not present
            if 'start_year' not in self.withdrawal_params:
                self.withdrawal_params['start_year'] = self.start_year
            
            self.withdrawal_strategy = create_withdrawal_strategy(self.withdrawal_params)
            logger.info(f"Created withdrawal strategy: {self.withdrawal_strategy.__class__.__name__}")
    
    def _get_note_for_year(self, year):
        """
        Get structured note parameters for the given year.
        
        Parameters:
        - year: Year to get note for
        
        Returns:
        - note_params: Dict of note parameters
        """
        logger.info(f"Selecting structured note for year {year}")
        
        # If notes were pre-selected, use them
        if self.pre_selected_notes and year in self.pre_selected_notes:
            note_params = self.pre_selected_notes[year]
            logger.info(f"Using pre-selected note for year {year}: "
                      f"{note_params['protection_level']:.0%} {note_params.get('protection_type', 'Buffer')}, "
                      f"PR: {note_params['participation_rate']:.4f}")
            return note_params
        
        # Otherwise, filter notes for this year based on selection params
        if self.notes_data is not None and self.note_selection_params:
            year_notes = self.notes_data[self.notes_data['year'] == year]
            
            if not year_notes.empty:
                logger.info(f"Found {len(year_notes)} notes available for year {year}")
                
                # Filter by protection level if specified
                if 'protection_level' in self.note_selection_params:
                    target_protection = self.note_selection_params['protection_level']
                    logger.info(f"Target protection level: {target_protection:.0%}")
                    
                    matching_notes = year_notes[year_notes['protection_level'] == target_protection]
                    
                    if not matching_notes.empty:
                        note_params = matching_notes.iloc[0].to_dict()
                        logger.info(f"Found exact match: {note_params['protection_level']:.0%} "
                                  f"{note_params.get('protection_type', 'Buffer')}, "
                                  f"PR: {note_params['participation_rate']:.4f}")
                        return note_params
                    else:
                        # Find closest match
                        logger.info(f"No exact {target_protection:.0%} buffer note found. Looking for closest match...")
                        
                        year_notes['distance'] = abs(year_notes['protection_level'] - target_protection)
                        closest_note = year_notes.sort_values('distance').iloc[0]
                        
                        logger.info(f"Selected closest match: {closest_note['protection_level']:.0%} "
                                  f"{closest_note.get('protection_type', 'Buffer')}, "
                                  f"PR: {closest_note['participation_rate']:.4f} "
                                  f"(distance: {closest_note['distance']:.0%})")
                        
                        return closest_note.to_dict()
                else:
                    # No protection level specified, use first note
                    note_params = year_notes.iloc[0].to_dict()
                    logger.info(f"No specific protection level requested. Using first available note: "
                              f"{note_params['protection_level']:.0%} {note_params.get('protection_type', 'Buffer')}, "
                              f"PR: {note_params['participation_rate']:.4f}")
                    return note_params
            else:
                logger.warning(f"No notes available for year {year}")
        
        # Default note parameters if no data available
        logger.warning(f"No structured note data available for year {year}. Using default parameters.")
        default_params = {
            'participation_rate': 1.0,
            'protection_level': 0.1,
            'protection_type': 'Buffer',
            'term': 1,
            'underlying_asset': 'S&P 500',
            'year': year
        }
        logger.info(f"Default note parameters: {default_params['protection_level']:.0%} "
                  f"{default_params['protection_type']}, PR: {default_params['participation_rate']:.2f}")
        return default_params
    
    def _get_year_returns(self, year):
        """
        Get returns for all asset classes for the given year.
        
        Parameters:
        - year: Year to get returns for
        
        Returns:
        - returns_dict: Dict mapping asset names to returns
        """
        returns_dict = {
            'sp500': self.sp500_returns.get(year, 0),
            'bonds': self.bond_returns.get(year, 0)
        }
        
        # Log market returns first
        logger.info(f"===== YEAR {year} RETURNS =====")
        logger.info(f"S&P 500: {returns_dict['sp500']:.4%}, Bond: {returns_dict['bonds']:.4%}")
        
        # Calculate structured note return if any portfolio uses them
        if any('notes' in alloc for alloc in self.portfolio_allocations.values()):
            # Get note parameters for this year
            note_params = self._get_note_for_year(year)
            
            # Create note and calculate return
            note = create_note(note_params)
            underlying_return = returns_dict['sp500']
            
            # Log structured note parameters
            logger.info(f"STRUCTURED NOTE: {note}")
            logger.info(f"- Protection Level: {note_params['protection_level']:.2%}")
            logger.info(f"- Participation Rate: {note_params['participation_rate']:.4f}")
            logger.info(f"- Protection Type: {note_params.get('protection_type', 'Buffer')}")
            
            # Calculate return - the detailed calculation logs are in the note's calculate_return method
            logger.info(f"- Underlying Asset Return: {underlying_return:.4%}")
            note_return = note.calculate_return(underlying_return)
            
            returns_dict['notes'] = note_return
            
            # Log final note return
            logger.info(f"- Final Note Return: {note_return:.4%}")
        else:
            logger.debug(f"Year {year}: No structured notes in any portfolio")
        
        return returns_dict
    
    def run_simulation(self):
        """
        Run the simulation for all portfolios and years.
        
        Returns:
        - results: Dict mapping portfolio names to lists of yearly results
        """
        logger.info(f"Running simulation from {self.start_year} to {self.end_year}")
        
        for year in range(self.start_year, self.end_year + 1):
            logger.info(f"Simulating year {year}")
            
            # Get returns for this year
            returns_dict = self._get_year_returns(year)
            
            # Process each portfolio
            for name, portfolio in self.portfolios.items():
                # Apply returns
                portfolio.apply_returns(returns_dict)
                
                # Calculate withdrawal if strategy exists
                withdrawal_amount = 0
                if self.withdrawal_strategy:
                    withdrawal_amount = self.withdrawal_strategy.calculate_withdrawal(portfolio, year)
                    portfolio.withdraw(withdrawal_amount)
                
                # Record results
                portfolio_value = portfolio.get_total_value()
                annual_return = portfolio.get_annual_return()
                
                year_result = {
                    'year': year,
                    'portfolio_value': portfolio_value,
                    'annual_return': annual_return,
                    'withdrawal': withdrawal_amount,
                    'asset_values': portfolio.get_asset_values(),
                    'asset_allocations': portfolio.get_asset_allocations()
                }
                
                self.results[name].append(year_result)
                
                logger.info(f"  Portfolio '{name}': ${portfolio_value:,.2f} (Return: {annual_return:.2%})")
                
                # Rebalance portfolio for next year
                portfolio.rebalance()
        
        logger.info("Simulation completed")
        return self.results
    
    def get_results_dataframe(self):
        """
        Convert simulation results to a pandas DataFrame.
        
        Returns:
        - df: DataFrame with simulation results
        """
        # Create a list to hold all data
        all_data = []
        
        for portfolio_name, years_data in self.results.items():
            for year_data in years_data:
                row = {
                    'portfolio': portfolio_name,
                    'year': year_data['year'],
                    'portfolio_value': year_data['portfolio_value'],
                    'annual_return': year_data['annual_return'],
                    'withdrawal': year_data['withdrawal']
                }
                
                # Add asset values as separate columns
                for asset, value in year_data['asset_values'].items():
                    row[f'{asset}_value'] = value
                
                # Add asset allocations as separate columns
                for asset, allocation in year_data['asset_allocations'].items():
                    row[f'{asset}_allocation'] = allocation
                
                all_data.append(row)
        
        # Convert to DataFrame
        df = pd.DataFrame(all_data)
        
        # Sort by portfolio and year
        if not df.empty:
            df = df.sort_values(['portfolio', 'year'])
        
        return df
    
    def calculate_summary_statistics(self):
        """
        Calculate summary statistics for each portfolio.
        
        Returns:
        - summary: Dict mapping portfolio names to summary statistics
        """
        summary = {}
        
        for name, years_data in self.results.items():
            # Extract portfolio values and returns
            values = [data['portfolio_value'] for data in years_data]
            returns = [data['annual_return'] for data in years_data]
            
            # Calculate statistics
            total_return = (values[-1] / self.initial_value) - 1 if values else 0
            cagr = (values[-1] / self.initial_value) ** (1 / len(years_data)) - 1 if values else 0
            max_drawdown = self._calculate_max_drawdown(values)
            
            # Calculate volatility
            volatility = np.std(returns) if len(returns) > 1 else 0
            
            # Create summary for this portfolio
            summary[name] = {
                'initial_value': self.initial_value,
                'final_value': values[-1] if values else 0,
                'total_return': total_return,
                'cagr': cagr,
                'volatility': volatility,
                'max_drawdown': max_drawdown,
                'years': len(years_data)
            }
        
        return summary
    
    def _calculate_max_drawdown(self, values):
        """
        Calculate maximum drawdown from a series of values.
        
        Parameters:
        - values: List of portfolio values
        
        Returns:
        - max_drawdown: Maximum drawdown as a decimal
        """
        if not values or len(values) < 2:
            return 0
        
        peak = values[0]
        max_drawdown = 0
        
        for value in values:
            if value > peak:
                peak = value
            
            drawdown = (peak - value) / peak if peak > 0 else 0
            max_drawdown = max(max_drawdown, drawdown)
        
        return max_drawdown 