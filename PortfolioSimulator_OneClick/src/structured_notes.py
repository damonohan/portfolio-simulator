import logging
import numpy as np

# Configure logging
logger = logging.getLogger(__name__)

class StructuredNote:
    """Base class for structured notes."""
    
    def __init__(self, params):
        """
        Initialize with note parameters.
        
        Parameters:
        - params: Dict containing note parameters (participation_rate, protection_level, etc.)
        """
        self.params = params
        self.participation_rate = params.get('participation_rate', 1.0)
        self.protection_level = params.get('protection_level', 0.0)
        self.term = params.get('term', 1.0)
        self.protection_type = params.get('protection_type', 'Buffer')
        self.underlying_asset = params.get('underlying_asset', 'S&P 500')
        self.year = params.get('year', None)
        
        # Optional ID for tracking notes across years
        self.note_id = params.get('note_id', None)
        
        logger.debug(f"Created structured note: {self.note_id or 'No ID'}, "
                    f"PR: {self.participation_rate:.2f}, "
                    f"Protection: {self.protection_level:.2f}, "
                    f"Year: {self.year}")
    
    def calculate_return(self, underlying_return):
        """Calculate note return based on underlying asset performance."""
        raise NotImplementedError("Subclasses must implement this method")
    
    def __str__(self):
        """String representation of the structured note."""
        return (f"{self.underlying_asset} {int(self.protection_level*100)}% "
                f"{self.protection_type} Note (PR: {self.participation_rate:.2f})")


class BufferedNote(StructuredNote):
    """Specific implementation for buffered notes."""
    
    def calculate_return(self, underlying_return):
        """
        Calculate buffered note return.
        
        For positive underlying returns:
            return = underlying_return * participation_rate
        For negative underlying returns:
            If |underlying_return| <= protection_level: return = 0
            If |underlying_return| > protection_level: return = -(|underlying_return| - protection_level)
        
        Parameters:
        - underlying_return: Annual return of the underlying asset
        
        Returns:
        - note_return: Annual return of the structured note
        """
        logger.info(f"BUFFERED NOTE CALCULATION:")
        logger.info(f"  Step 1: Analyze underlying return: {underlying_return:.4%}")
        
        # For positive returns, apply participation rate
        if underlying_return > 0:
            logger.info(f"  Step 2: Positive return detected, applying participation rate")
            logger.info(f"    Calculation: {underlying_return:.4%} × {self.participation_rate:.4f}")
            note_return = underlying_return * self.participation_rate
            logger.info(f"  Step 3: Final positive return result: {note_return:.4%}")
            return note_return
        
        # For negative returns, apply buffer logic
        else:
            # Convert to absolute value for comparison
            abs_return = abs(underlying_return)
            logger.info(f"  Step 2: Negative return detected, applying buffer protection")
            logger.info(f"    Absolute value of return: |{underlying_return:.4%}| = {abs_return:.4%}")
            logger.info(f"    Buffer protection level: {self.protection_level:.4%}")
            
            # Check if loss is within the protection buffer
            if abs_return <= self.protection_level:
                # Full protection - no loss
                logger.info(f"  Step 3: Loss is WITHIN buffer ({abs_return:.4%} ≤ {self.protection_level:.4%})")
                logger.info(f"    Full downside protection applies")
                logger.info(f"  Step 4: Final return result: 0.00%")
                return 0.0
            else:
                # Partial protection - loss beyond buffer
                logger.info(f"  Step 3: Loss EXCEEDS buffer ({abs_return:.4%} > {self.protection_level:.4%})")
                excess_loss = abs_return - self.protection_level
                logger.info(f"    Excess loss beyond buffer: {abs_return:.4%} - {self.protection_level:.4%} = {excess_loss:.4%}")
                note_return = -excess_loss
                logger.info(f"  Step 4: Final return result: {note_return:.4%}")
                return note_return


class FlooredNote(StructuredNote):
    """Implementation for floored notes (full downside protection)."""
    
    def calculate_return(self, underlying_return):
        """
        Calculate floored note return.
        
        For positive underlying returns:
            return = underlying_return * participation_rate
        For negative underlying returns:
            return = max(underlying_return, -protection_level)
        
        Parameters:
        - underlying_return: Annual return of the underlying asset
        
        Returns:
        - note_return: Annual return of the structured note
        """
        logger.info(f"FLOORED NOTE CALCULATION:")
        logger.info(f"  Step 1: Analyze underlying return: {underlying_return:.4%}")
        
        # For positive returns, apply participation rate
        if underlying_return > 0:
            logger.info(f"  Step 2: Positive return detected, applying participation rate")
            logger.info(f"    Calculation: {underlying_return:.4%} × {self.participation_rate:.4f}")
            note_return = underlying_return * self.participation_rate
            logger.info(f"  Step 3: Final positive return result: {note_return:.4%}")
            return note_return
        
        # For negative returns, apply floor logic
        else:
            # Limit the loss to the protection level
            logger.info(f"  Step 2: Negative return detected, applying floor protection")
            logger.info(f"    Underlying negative return: {underlying_return:.4%}")
            logger.info(f"    Floor protection level: -{self.protection_level:.4%}")
            
            max_loss = -self.protection_level
            logger.info(f"    Maximum allowable loss: {max_loss:.4%}")
            note_return = max(underlying_return, max_loss)
            
            if underlying_return < max_loss:
                logger.info(f"  Step 3: Underlying loss EXCEEDS floor (worse than {max_loss:.4%})")
                logger.info(f"    Floor protection applied: loss limited to {max_loss:.4%}")
            else:
                logger.info(f"  Step 3: Underlying loss WITHIN floor ({underlying_return:.4%} ≥ {max_loss:.4%})")
                logger.info(f"    Actual underlying return used (no protection needed)")
            
            logger.info(f"  Step 4: Final return result: {note_return:.4%}")
            return note_return


def create_note(params):
    """
    Factory function to create the appropriate type of structured note.
    
    Parameters:
    - params: Dict containing note parameters
    
    Returns:
    - StructuredNote: An instance of the appropriate note subclass
    """
    protection_type = params.get('protection_type', 'Buffer').lower()
    
    if protection_type == 'buffer':
        return BufferedNote(params)
    elif protection_type == 'floor':
        return FlooredNote(params)
    else:
        logger.warning(f"Unknown protection type: {protection_type}. Defaulting to Buffer.")
        return BufferedNote(params)


def simple_note_payoff(underlying_return, participation_rate, protection_level, protection_type='Buffer'):
    """
    Calculate structured note payoff using a simplified approach.
    
    Parameters:
    - underlying_return: Return of the underlying asset
    - participation_rate: Participation rate for upside returns
    - protection_level: Level of downside protection
    - protection_type: Type of protection (Buffer or Floor)
    
    Returns:
    - note_return: Return of the structured note
    """
    protection_type = protection_type.lower()
    
    # For positive returns
    if underlying_return > 0:
        return underlying_return * participation_rate
    
    # For negative returns
    if protection_type == 'buffer':
        if abs(underlying_return) <= protection_level:
            return 0
        else:
            return -(abs(underlying_return) - protection_level)
    elif protection_type == 'floor':
        return max(underlying_return, -protection_level)
    else:
        # Default to buffer
        if abs(underlying_return) <= protection_level:
            return 0
        else:
            return -(abs(underlying_return) - protection_level) 