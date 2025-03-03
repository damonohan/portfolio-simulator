import os
import pandas as pd
import numpy as np
import logging

# Configure logging
logger = logging.getLogger(__name__)

def load_sp500_data(filepath, start_year=None, end_year=None):
    """
    Load S&P 500 data and convert to annual returns
    
    Parameters:
    - filepath: Path to the SP500 yearly CSV file
    - start_year: Optional filter for start year (inclusive)
    - end_year: Optional filter for end year (inclusive)
    
    Returns:
    - Dictionary mapping years to annual returns
    """
    logger.info(f"Loading S&P 500 data from {filepath}")
    
    try:
        # Load raw price data
        df = pd.read_csv(filepath, index_col='Date', parse_dates=True)
        
        # Extract year from the index
        df['Year'] = df.index.year
        
        # Convert prices to returns
        df['Return'] = df['^GSPC'].pct_change()
        
        # Drop the first row (NaN return)
        df = df.dropna()
        
        # Create a dictionary mapping years to returns
        returns_dict = {}
        for _, row in df.iterrows():
            year = row['Year']
            ret = row['Return']
            
            # Filter by year range if specified
            if start_year is not None and year < start_year:
                continue
            if end_year is not None and year > end_year:
                continue
                
            returns_dict[year] = ret
        
        logger.info(f"Loaded S&P 500 returns for {len(returns_dict)} years")
        return returns_dict
    
    except Exception as e:
        logger.error(f"Error loading S&P 500 data: {str(e)}")
        return {}

def load_bond_returns(filepath, start_year=None, end_year=None):
    """
    Load bond return data
    
    Parameters:
    - filepath: Path to the bond returns CSV file
    - start_year: Optional filter for start year (inclusive)
    - end_year: Optional filter for end year (inclusive)
    
    Returns:
    - Dictionary mapping years to bond returns
    """
    logger.info(f"Loading bond return data from {filepath}")
    
    try:
        # Load bond return data
        df = pd.read_csv(filepath, index_col='Date', parse_dates=True)
        
        # Extract year from the index
        df['Year'] = df.index.year
        
        # Create a dictionary mapping years to returns
        returns_dict = {}
        for _, row in df.iterrows():
            year = row['Year']
            ret = row['total_return']
            
            # Filter by year range if specified
            if start_year is not None and year < start_year:
                continue
            if end_year is not None and year > end_year:
                continue
                
            returns_dict[year] = ret
        
        logger.info(f"Loaded bond returns for {len(returns_dict)} years")
        return returns_dict
    
    except Exception as e:
        logger.error(f"Error loading bond return data: {str(e)}")
        return {}

def load_structured_notes(filepath, filter_params=None):
    """
    Load structured note data with optional filtering
    
    Parameters:
    - filepath: Path to the growth notes CSV file
    - filter_params: Optional dictionary of parameters to filter notes
      e.g., {"protection_level": 0.1, "term": 1.0}
    
    Returns:
    - DataFrame containing structured note data
    """
    logger.info(f"Loading structured note data from {filepath}")
    
    try:
        # Load note data
        df = pd.read_csv(filepath)
        
        # Apply filters if specified
        if filter_params:
            for param, value in filter_params.items():
                if param in df.columns:
                    df = df[df[param] == value]
        
        logger.info(f"Loaded {len(df)} structured notes")
        return df
    
    except Exception as e:
        logger.error(f"Error loading structured note data: {str(e)}")
        return pd.DataFrame()

def select_structured_notes(notes_data, protection_level, start_year, end_year):
    """
    Select structured notes with the specified protection level for each year.
    
    Parameters:
    - notes_data: DataFrame of available structured notes
    - protection_level: The desired protection level (e.g., 0.1 for 10% buffer)
    - start_year: First year in the simulation
    - end_year: Last year in the simulation
    
    Returns:
    - selected_notes: Dict mapping each year to its corresponding note
    """
    logger.info(f"Selecting structured notes with {protection_level*100}% protection from {start_year} to {end_year}")
    
    selected_notes = {}
    
    for year in range(start_year, end_year + 1):
        # Filter notes for this year with the specified protection level
        year_notes = notes_data[
            (notes_data['year'] == year) & 
            (notes_data['protection_level'] == protection_level)
        ]
        
        if year_notes.empty:
            # Try to find closest protection level
            year_all_notes = notes_data[notes_data['year'] == year]
            if not year_all_notes.empty:
                year_all_notes['distance'] = abs(year_all_notes['protection_level'] - protection_level)
                closest_note = year_all_notes.sort_values('distance').iloc[0]
                selected_notes[year] = closest_note.to_dict()
                logger.warning(f"No exact {protection_level*100}% buffer note found for {year}. Using {closest_note['protection_level']*100}% buffer instead.")
            else:
                logger.error(f"No structured notes available for year {year}")
                raise ValueError(f"No structured notes available for year {year}")
        else:
            # Use the exact matching note
            selected_notes[year] = year_notes.iloc[0].to_dict()
    
    logger.info(f"Selected notes for {len(selected_notes)} years")
    return selected_notes

def align_data(sp500_returns, bond_returns, notes_data, start_year, end_year):
    """
    Ensure all data is available and aligned for the simulation period.
    
    Parameters:
    - sp500_returns: Dict of S&P 500 annual returns
    - bond_returns: Dict of bond annual returns
    - notes_data: DataFrame of structured notes data
    - start_year: First year in the simulation
    - end_year: Last year in the simulation
    
    Returns:
    - tuple: (valid_years, aligned_sp500, aligned_bonds, aligned_notes)
    """
    logger.info(f"Aligning data from {start_year} to {end_year}")
    
    # Find years with data in all sources
    sp500_years = set(sp500_returns.keys())
    bond_years = set(bond_returns.keys())
    note_years = set(notes_data['year'].unique())
    
    # Find intersection of all years
    valid_years = sorted(list(sp500_years.intersection(bond_years).intersection(note_years)))
    
    # Filter to requested range
    valid_years = [year for year in valid_years if start_year <= year <= end_year]
    
    if not valid_years:
        logger.error(f"No overlapping data available for years {start_year} to {end_year}")
        raise ValueError(f"No overlapping data available for years {start_year} to {end_year}")
    
    logger.info(f"Found overlapping data for {len(valid_years)} years: {min(valid_years)} to {max(valid_years)}")
    
    # Create aligned dictionaries
    aligned_sp500 = {year: sp500_returns[year] for year in valid_years}
    aligned_bonds = {year: bond_returns[year] for year in valid_years}
    
    # Filter notes to valid years
    aligned_notes = notes_data[notes_data['year'].isin(valid_years)]
    
    return valid_years, aligned_sp500, aligned_bonds, aligned_notes

def add_note_ids(notes_data):
    """
    Add a unique Note ID to each note based on its core parameters.
    
    Parameters:
    - notes_data: DataFrame of structured notes
    
    Returns:
    - notes_data: Updated DataFrame with Note ID column
    """
    logger.info("Adding note IDs to structured notes data")
    
    # Define parameters that make a note "the same" across years
    id_params = ['protection_level', 'term', 'underlying_asset', 'protection_type']
    
    # Create a Note ID based on these parameters
    def create_note_id(row):
        # Example: "SPX-10BUF-1Y" for a 10% buffered 1-year S&P note
        asset = row['underlying_asset'].replace(' ', '').replace('&', '')[:3].upper()
        protection = int(row['protection_level'] * 100)
        protection_type = row['protection_type'][:3].upper()
        term = int(row['term'])
        return f"{asset}-{protection}{protection_type}-{term}Y"
    
    # Apply the function to create the ID column
    notes_data['note_id'] = notes_data.apply(create_note_id, axis=1)
    
    logger.info(f"Added note IDs to {len(notes_data)} notes")
    return notes_data 