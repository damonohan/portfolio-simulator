import logging
import numpy as np

# Configure logging
logger = logging.getLogger(__name__)

class WithdrawalStrategy:
    """Base class for withdrawal strategies."""
    
    def __init__(self, params):
        """
        Initialize with strategy parameters.
        
        Parameters:
        - params: Dict containing strategy parameters
        """
        self.params = params
        self.start_year = params.get('start_year', None)
        logger.info(f"Created withdrawal strategy: {self.__class__.__name__}")
    
    def calculate_withdrawal(self, portfolio, current_year):
        """
        Calculate withdrawal amount for current year.
        
        Parameters:
        - portfolio: Portfolio object
        - current_year: Current year in the simulation
        
        Returns:
        - withdrawal_amount: Amount to withdraw
        """
        raise NotImplementedError("Subclasses must implement this method")


class FixedPercentageWithdrawal(WithdrawalStrategy):
    """Withdraw a fixed percentage of portfolio each year."""
    
    def __init__(self, params):
        """Initialize with strategy parameters."""
        super().__init__(params)
        self.rate = params.get('rate', 0.04)  # Default 4%
        self.inflation_adjusted = params.get('inflation_adjusted', False)
        self.inflation_rate = params.get('inflation_rate', 0.025)  # Default 2.5%
        self.initial_portfolio_value = None
        
        logger.info(f"Fixed percentage withdrawal: {self.rate:.2%}")
        if self.inflation_adjusted:
            logger.info(f"  Inflation adjusted ({self.inflation_rate:.2%} annually)")
    
    def calculate_withdrawal(self, portfolio, current_year):
        """
        Calculate withdrawal amount based on current portfolio value.
        
        Parameters:
        - portfolio: Portfolio object
        - current_year: Current year in the simulation
        
        Returns:
        - withdrawal_amount: Amount to withdraw
        """
        # Initialize the initial portfolio value if not set
        if self.initial_portfolio_value is None:
            self.initial_portfolio_value = portfolio.get_total_value()
        
        portfolio_value = portfolio.get_total_value()
        
        if self.inflation_adjusted:
            # Calculate initial withdrawal rate
            initial_withdrawal = self.initial_portfolio_value * self.rate
            
            # Adjust for inflation
            years_since_start = 0 if self.start_year is None else (current_year - self.start_year)
            inflation_factor = (1 + self.inflation_rate) ** years_since_start
            withdrawal = initial_withdrawal * inflation_factor
            
            logger.debug(f"Year {current_year}: Inflation-adjusted withdrawal: ${initial_withdrawal:,.2f} * {inflation_factor:.4f} = ${withdrawal:,.2f}")
        else:
            # Simple percentage of current portfolio
            withdrawal = portfolio_value * self.rate
            logger.debug(f"Year {current_year}: Fixed percentage withdrawal: {self.rate:.2%} * ${portfolio_value:,.2f} = ${withdrawal:,.2f}")
        
        # Can't withdraw more than what's available
        return min(withdrawal, portfolio_value)


class FixedDollarWithdrawal(WithdrawalStrategy):
    """Withdraw a fixed dollar amount each year."""
    
    def __init__(self, params):
        """Initialize with strategy parameters."""
        super().__init__(params)
        self.amount = params.get('amount', 40000)  # Default $40,000
        self.inflation_adjusted = params.get('inflation_adjusted', False)
        self.inflation_rate = params.get('inflation_rate', 0.025)  # Default 2.5%
        
        logger.info(f"Fixed dollar withdrawal: ${self.amount:,.2f}")
        if self.inflation_adjusted:
            logger.info(f"  Inflation adjusted ({self.inflation_rate:.2%} annually)")
    
    def calculate_withdrawal(self, portfolio, current_year):
        """
        Calculate fixed dollar withdrawal amount, possibly adjusted for inflation.
        
        Parameters:
        - portfolio: Portfolio object
        - current_year: Current year in the simulation
        
        Returns:
        - withdrawal_amount: Amount to withdraw
        """
        portfolio_value = portfolio.get_total_value()
        
        if self.inflation_adjusted:
            # Adjust for inflation
            years_since_start = 0 if self.start_year is None else (current_year - self.start_year)
            inflation_factor = (1 + self.inflation_rate) ** years_since_start
            withdrawal = self.amount * inflation_factor
            
            logger.debug(f"Year {current_year}: Inflation-adjusted fixed withdrawal: ${self.amount:,.2f} * {inflation_factor:.4f} = ${withdrawal:,.2f}")
        else:
            # Simple fixed amount
            withdrawal = self.amount
            logger.debug(f"Year {current_year}: Fixed dollar withdrawal: ${withdrawal:,.2f}")
        
        # Can't withdraw more than what's available
        return min(withdrawal, portfolio_value)


class RMDWithdrawal(WithdrawalStrategy):
    """
    Required Minimum Distribution withdrawal strategy.
    Based on IRS life expectancy tables.
    """
    
    def __init__(self, params):
        """Initialize with strategy parameters."""
        super().__init__(params)
        self.starting_age = params.get('starting_age', 72)
        self.current_age = self.starting_age
        
        # Simplified RMD factors (IRS Uniform Lifetime Table)
        self.rmd_factors = {
            72: 27.4, 73: 26.5, 74: 25.5, 75: 24.6, 76: 23.7, 77: 22.9,
            78: 22.0, 79: 21.1, 80: 20.2, 81: 19.4, 82: 18.5, 83: 17.7,
            84: 16.8, 85: 16.0, 86: 15.2, 87: 14.4, 88: 13.7, 89: 12.9,
            90: 12.2, 91: 11.5, 92: 10.8, 93: 10.1, 94: 9.5, 95: 8.9,
            96: 8.4, 97: 7.8, 98: 7.3, 99: 6.8, 100: 6.4
        }
        
        logger.info(f"RMD withdrawal starting at age {self.starting_age}")
    
    def calculate_withdrawal(self, portfolio, current_year):
        """
        Calculate RMD withdrawal amount based on age.
        
        Parameters:
        - portfolio: Portfolio object
        - current_year: Current year in the simulation
        
        Returns:
        - withdrawal_amount: Amount to withdraw
        """
        portfolio_value = portfolio.get_total_value()
        
        # Update age if start_year is defined
        if self.start_year is not None:
            self.current_age = self.starting_age + (current_year - self.start_year)
        
        # Check if RMDs apply yet
        if self.current_age < self.starting_age:
            logger.debug(f"Year {current_year} (Age {self.current_age}): No RMD required yet")
            return 0
        
        # Cap age at 100 for the factors table
        lookup_age = min(self.current_age, 100)
        
        # Get the appropriate divisor
        divisor = self.rmd_factors.get(lookup_age, 6.4)  # Default to age 100+ factor
        
        # Calculate RMD
        withdrawal = portfolio_value / divisor
        
        logger.debug(f"Year {current_year} (Age {self.current_age}): RMD calculation: ${portfolio_value:,.2f} / {divisor:.1f} = ${withdrawal:,.2f}")
        
        return withdrawal


def create_withdrawal_strategy(params):
    """
    Factory function to create the appropriate withdrawal strategy.
    
    Parameters:
    - params: Dict containing strategy parameters
    
    Returns:
    - WithdrawalStrategy: An instance of the appropriate strategy
    """
    strategy_type = params.get('strategy', 'fixed_percentage').lower()
    
    if strategy_type == 'fixed_percentage':
        return FixedPercentageWithdrawal(params)
    elif strategy_type == 'fixed_dollar':
        return FixedDollarWithdrawal(params)
    elif strategy_type == 'rmd':
        return RMDWithdrawal(params)
    else:
        logger.warning(f"Unknown withdrawal strategy: {strategy_type}. Defaulting to Fixed Percentage.")
        return FixedPercentageWithdrawal(params) 