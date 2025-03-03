import logging
import numpy as np

# Configure logging
logger = logging.getLogger(__name__)

class Portfolio:
    """Represents a portfolio with different asset allocations."""
    
    def __init__(self, initial_value, allocations):
        """
        Initialize portfolio with starting value and allocations.
        
        Parameters:
        - initial_value: Starting portfolio value
        - allocations: Dict of asset allocations (e.g., {"sp500": 0.6, "bonds": 0.4})
        """
        self.initial_value = initial_value
        self.allocations = allocations
        self.current_value = initial_value
        self.prev_value = initial_value  # For calculating annual return
        
        # Validate allocations
        self._validate_allocations()
        
        # Initialize asset values based on allocations
        self.asset_values = {}
        self.rebalance()
        
        logger.info(f"Created portfolio with initial value ${initial_value:,.2f}")
        logger.info(f"  Allocations: {self.allocations}")
    
    def _validate_allocations(self):
        """Validate that allocations sum to approximately 1.0."""
        total = sum(self.allocations.values())
        if not np.isclose(total, 1.0, atol=1e-6):
            logger.warning(f"Allocations do not sum to 1.0: {total:.4f}")
            # Normalize allocations
            for asset in self.allocations:
                self.allocations[asset] /= total
            logger.info(f"Normalized allocations: {self.allocations}")
    
    def rebalance(self):
        """Rebalance portfolio to target allocations."""
        logger.debug(f"Rebalancing portfolio (value: ${self.current_value:,.2f})")
        
        self.asset_values = {}
        for asset, allocation in self.allocations.items():
            self.asset_values[asset] = self.current_value * allocation
            logger.debug(f"  {asset}: ${self.asset_values[asset]:,.2f} ({allocation:.2%})")
    
    def apply_returns(self, returns_dict):
        """
        Apply annual returns to each asset class.
        
        Parameters:
        - returns_dict: Dict mapping asset names to their returns
        
        Returns:
        - new_value: Updated portfolio value after applying returns
        """
        logger.debug(f"Applying returns to portfolio (value: ${self.current_value:,.2f})")
        
        # Store previous value for return calculation
        self.prev_value = self.current_value
        
        # Apply returns to each asset
        for asset, value in self.asset_values.items():
            if asset in returns_dict:
                ret = returns_dict[asset]
                new_value = value * (1 + ret)
                logger.debug(f"  {asset}: ${value:,.2f} -> ${new_value:,.2f} (return: {ret:.2%})")
                self.asset_values[asset] = new_value
            else:
                logger.warning(f"No return data for asset: {asset}")
        
        # Update current value
        self.current_value = sum(self.asset_values.values())
        logger.debug(f"New portfolio value: ${self.current_value:,.2f}")
        
        return self.current_value
    
    def withdraw(self, amount):
        """
        Withdraw a specified amount from the portfolio, proportionally from all assets.
        
        Parameters:
        - amount: Amount to withdraw
        
        Returns:
        - actual_withdrawal: Actual amount withdrawn (might be less if insufficient funds)
        """
        if amount <= 0:
            return 0
        
        # Cap withdrawal at current value
        actual_withdrawal = min(amount, self.current_value)
        
        if actual_withdrawal < amount:
            logger.warning(f"Insufficient funds for withdrawal. Requested: ${amount:,.2f}, Available: ${self.current_value:,.2f}")
        
        # Withdraw proportionally from each asset
        withdrawal_ratio = actual_withdrawal / self.current_value
        
        for asset in self.asset_values:
            asset_withdrawal = self.asset_values[asset] * withdrawal_ratio
            self.asset_values[asset] -= asset_withdrawal
            logger.debug(f"  Withdrew ${asset_withdrawal:,.2f} from {asset}")
        
        # Update current value
        self.current_value -= actual_withdrawal
        logger.debug(f"After withdrawal: ${self.current_value:,.2f}")
        
        return actual_withdrawal
    
    def get_total_value(self):
        """Return total portfolio value."""
        return self.current_value
    
    def get_annual_return(self):
        """Calculate annual return of the portfolio."""
        if np.isclose(self.prev_value, 0):
            return 0
        
        return (self.current_value / self.prev_value) - 1
    
    def get_asset_values(self):
        """Return a dictionary of asset values."""
        return self.asset_values.copy()
    
    def get_asset_allocations(self):
        """Return a dictionary of current asset allocations (as percentages)."""
        if np.isclose(self.current_value, 0):
            return {asset: 0 for asset in self.asset_values}
        
        return {asset: value / self.current_value for asset, value in self.asset_values.items()} 