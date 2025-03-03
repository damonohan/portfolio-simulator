import os
import stat
import time
import logging
import requests
import warnings
import yfinance as yf
import pandas as pd
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_fred_api_access():
    """
    Test FRED API access with a simple request
    """
    print("\nTesting FRED API access...")
    api_key = '89e86be5e7783447661a3da157cd0de5'
    test_series = 'TEDRATE'
    url = f'https://api.stlouisfed.org/fred/series?series_id={test_series}&api_key={api_key}&file_type=json'
    
    print("Making test request to FRED API...")
    try:
        response = requests.get(url, verify=False)
        print(f"Response status code: {response.status_code}")
        print(f"Response content: {response.text[:200]}...")
        
        if response.status_code == 200:
            print("✓ API key is valid and working")
            return True
        else:
            print(f"✗ API request failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Error testing API access: {e}")
        return False

def fetch_and_save_raw_data(start_date="1976-01-01", end_date="2025-01-01", max_retries=3, timeout=30):
    """
    Fetch raw historical data for S&P 500, Treasury, and VIX, retrying on failure, and overwrite CSV files
    with fixed names in raw_data/ using an absolute path.
    """
    # Get absolute path for raw_data directory
    raw_data_dir = os.path.join(os.getcwd(), "raw_data")
    print(f"Working directory: {os.getcwd()}")
    
    # Ensure raw_data directory exists with write permissions
    if not os.path.exists(raw_data_dir):
        print(f"Creating directory: {raw_data_dir}")
        os.makedirs(raw_data_dir, exist_ok=True)
    else:
        print(f"Directory {raw_data_dir} already exists.")
        try:
            os.chmod(raw_data_dir, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)  # Full permissions
        except PermissionError as e:
            print(f"Permission error on {raw_data_dir}: {e}. Setting user-only permissions.")
            try:
                os.chmod(raw_data_dir, stat.S_IRWXU)
            except Exception as e2:
                print(f"Failed to set permissions: {e2}. Proceeding with existing permissions.")
    
    # Fetch data with retries
    for attempt in range(max_retries):
        try:
            sp500 = yf.download("^GSPC", start=start_date, end=end_date, progress=False, timeout=timeout)["Close"]
            treasury = yf.download("^TNX", start=start_date, end=end_date, progress=False, timeout=timeout)["Close"] / 100  # Convert to decimal
            vix = yf.download("^VIX", start="1990-01-01", end=end_date, progress=False, timeout=timeout)["Close"] / 100  # Convert to decimal
            break
        except Exception as e:
            print(f"Attempt {attempt + 1}/{max_retries} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
            else:
                print("Max retries reached, using default data.")
                default_dates = pd.date_range(start=start_date, end=end_date, freq='YE')
                sp500 = pd.Series([100 + i * 10 for i in range(len(default_dates))], index=default_dates, name="Close")
                treasury = pd.Series(0.041, index=default_dates, name="Close")  # Default 4.1%
                vix = pd.Series(0.20, index=default_dates, name="Close")  # Default 20%

    # Resample data
    yearly_sp500 = sp500.resample("YE").last()
    yearly_treasury = treasury.resample("YE").mean()
    yearly_vix = vix.resample("YE").mean()

    # Debug prints
    print("Raw S&P 500 (Yearly End) Data:")
    print(yearly_sp500.dropna())
    print("Raw Treasury Yield (Yearly Average) Data:")
    print(yearly_treasury.dropna())
    print("Raw VIX (Yearly Average) Data:")
    print(yearly_vix.dropna())

    # Save to CSV with headers
    yearly_sp500.to_csv(os.path.join(raw_data_dir, "sp500_yearly.csv"), index=True, header=True)
    yearly_treasury.to_csv(os.path.join(raw_data_dir, "treasury_yearly.csv"), index=True, header=True)
    yearly_vix.to_csv(os.path.join(raw_data_dir, "vix_yearly.csv"), index=True, header=True)

    print(f"Raw data overwritten with fixed names in {raw_data_dir}/.")

def fetch_bank_funding_spreads():
    try:
        print("\nFetching BBB Corporate Bond spread data...")
        
        api_key = '89e86be5e7783447661a3da157cd0de5'
        series_id = 'BAMLC0A4CBBB'  # ICE BofA BBB US Corporate Index Option-Adjusted Spread
        url = f'https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={api_key}&file_type=json'
        
        print(f"Fetching series {series_id}...")
        response = requests.get(url, verify=False)
        
        if response.status_code == 200:
            data = response.json()
            observations = data['observations']
            
            # Print series info
            print("\nSeries Information:")
            print(f"Title: {data.get('title', 'N/A')}")
            print(f"Units: {data.get('units', 'N/A')}")
            print(f"Frequency: {data.get('frequency', 'N/A')}")
            
            # Convert to pandas series
            dates = []
            values = []
            for obs in observations:
                try:
                    if obs['value'] != '.':
                        dates.append(obs['date'])
                        values.append(float(obs['value']) / 100)  # Convert basis points to decimal
                except ValueError as e:
                    print(f"Skipping invalid value: {obs['value']} on {obs['date']}")
                    continue
            
            spreads = pd.Series(values, index=pd.DatetimeIndex(dates))
            
            # Show key crisis periods
            print("\nSample of BBB spreads:")
            print(spreads.head())
            
            if 2008 in spreads.index.year:
                print("\n2008 Financial Crisis spreads:")
                print(spreads['2008'].describe())
                print(f"Max spread in 2008: {spreads['2008'].max():.2%}")
            
            if 2020 in spreads.index.year:
                print("\n2020 COVID Crisis spreads:")
                print(spreads['2020'].describe())
                print(f"Max spread in 2020: {spreads['2020'].max():.2%}")
            
            # Calculate yearly averages
            yearly_spreads = spreads.groupby(spreads.index.year).mean()
            yearly_spreads.index = pd.to_datetime(yearly_spreads.index.astype(str) + '-12-31')
            
            # Save to CSV
            raw_data_dir = os.path.join(os.getcwd(), "raw_data")
            output_path = os.path.join(raw_data_dir, "bank_funding_spreads.csv")
            yearly_spreads.to_frame('TEDRATE').to_csv(output_path)
            
            return yearly_spreads
            
        else:
            print(f"FRED API request failed with status code: {response.status_code}")
            print(f"Error message: {response.text}")
            raise Exception(f"FRED API request failed: {response.text}")
            
    except Exception as e:
        print(f"Error fetching bank funding spreads: {e}")
        return None

def fetch_spy_dividend_yields(start_date="1976-01-01", end_date="2025-01-01"):
    """
    Fetch historical SPY ETF dividend yields from Yahoo Finance
    """
    try:
        print("\nFetching SPY dividend yield data...")
        spy = yf.Ticker("SPY")
        
        # Get all dividend and price data
        data = spy.history(period="max")
        dividends = data['Dividends']
        prices = data['Close']
        
        # Calculate trailing 12-month dividend yield
        annual_div = dividends.rolling(window=252, min_periods=1).sum()
        div_yield = (annual_div / prices).resample('YE').last()
        
        print("\nSample of SPY dividend yields:")
        print(div_yield.head())
        
        if 2008 in div_yield.index.year:
            print("\n2008 Financial Crisis dividend yield:")
            print(f"2008 dividend yield: {div_yield.loc['2008'].iloc[0]:.2%}")  # Fixed float warning
        
        if 2020 in div_yield.index.year:
            print("\n2020 COVID Crisis dividend yield:")
            print(f"2020 dividend yield: {div_yield.loc['2020'].iloc[0]:.2%}")  # Fixed float warning
            
        # Save to CSV with column name
        raw_data_dir = os.path.join(os.getcwd(), "raw_data")
        output_path = os.path.join(raw_data_dir, "spy_dividend_yields.csv")
        div_yield.to_frame('Dividend_Yield').to_csv(output_path)
        
        return div_yield
        
    except Exception as e:
        print(f"Error fetching SPY dividend yields: {e}")
        print("Using default 2% dividend yield")
        default_dates = pd.date_range(start=start_date, end=end_date, freq='YE')
        return pd.Series(0.02, index=default_dates)

def fetch_bond_returns(start_date="1976-01-01", end_date="2025-01-01"):
    """
    Fetch bond total return data using multiple sources to get the most accurate
    representation of the Bloomberg US Aggregate Bond Index returns
    """
    try:
        print("\nFetching bond total return data...")
        
        # Dictionary to collect all bond returns
        all_returns = {}
        
        # Try to get VBMFX (Vanguard Total Bond Market Index) data which goes back to 1986
        try:
            print("Fetching VBMFX (Vanguard Total Bond Market Index) data...")
            vbmfx_data = yf.download("VBMFX", start="1986-01-01", end=end_date, progress=False)
            if 'Adj Close' in vbmfx_data.columns:
                price_col = 'Adj Close'
            else:
                price_col = 'Close'
                print("Using 'Close' prices for VBMFX as 'Adj Close' not available")
                
            vbmfx = vbmfx_data[price_col]
            vbmfx_returns = vbmfx.pct_change()
            yearly_vbmfx = vbmfx_returns.resample("YE").apply(lambda x: (1 + x).prod() - 1)
            print(f"Successfully fetched VBMFX data: {len(yearly_vbmfx)} years")
            
            # Add VBMFX data for 1986-2006
            vbmfx_start_year = 1986
            vbmfx_end_year = 2007
            
            for date_idx in yearly_vbmfx.index:
                year = date_idx.year
                if vbmfx_start_year <= year < vbmfx_end_year:
                    # Store as a simple float value
                    all_returns[date_idx] = float(yearly_vbmfx.loc[date_idx])
                
        except Exception as e:
            print(f"Error fetching VBMFX data: {e}")
        
        # For most recent data, try BND ETF (Vanguard Total Bond Market ETF)
        try:
            print("Fetching BND (Vanguard Total Bond Market ETF) data...")
            bnd_data = yf.download("BND", start="2007-01-01", end=end_date, progress=False)
            if 'Adj Close' in bnd_data.columns:
                price_col = 'Adj Close'
            else:
                price_col = 'Close'
                print("Using 'Close' prices for BND as 'Adj Close' not available")
                
            bnd = bnd_data[price_col]
            bnd_returns = bnd.pct_change()
            yearly_bnd = bnd_returns.resample("YE").apply(lambda x: (1 + x).prod() - 1)
            print(f"Successfully fetched BND data: {len(yearly_bnd)} years")
            
            # Add BND data for 2007+
            bnd_start_year = 2007
            
            for date_idx in yearly_bnd.index:
                year = date_idx.year
                if year >= bnd_start_year:
                    # Store as a simple float value
                    all_returns[date_idx] = float(yearly_bnd.loc[date_idx])
                
        except Exception as e:
            print(f"Error fetching BND data: {e}")
            
            # Fall back to AGG if BND fails
            try:
                print("Falling back to AGG (iShares Core US Aggregate Bond ETF)...")
                agg_data = yf.download("AGG", start="2003-01-01", end=end_date, progress=False)
                if 'Adj Close' in agg_data.columns:
                    price_col = 'Adj Close'
                else:
                    price_col = 'Close'
                    
                agg = agg_data[price_col]
                agg_returns = agg.pct_change()
                yearly_agg = agg_returns.resample("YE").apply(lambda x: (1 + x).prod() - 1)
                
                # Add AGG data for 2007+ that are missing
                agg_start_year = 2007
                
                for date_idx in yearly_agg.index:
                    year = date_idx.year
                    if year >= agg_start_year and date_idx not in all_returns:
                        # Store as a simple float value
                        all_returns[date_idx] = float(yearly_agg.loc[date_idx])
                    
            except Exception as e2:
                print(f"Error fetching AGG data: {e2}")
        
        # For pre-1986 data, use a variable-spread model based on treasury yields
        try:
            print("Generating pre-1986 bond returns...")
            # Get treasury yields data
            treasury = yf.download("^TNX", start=start_date, end="1986-01-01", progress=False)["Close"]
            treasury_yearly = treasury.resample("YE").mean() / 100  # Convert to decimal
            
            # Apply variable spread based on yield level
            def variable_spread(yield_value):
                if yield_value > 0.10:  # Very high yield environment (>10%)
                    return 0.030  # 3.0% spread
                elif yield_value > 0.07:  # High yield (7-10%)
                    return 0.025  # 2.5% spread
                elif yield_value > 0.05:  # Moderate yield (5-7%)
                    return 0.020  # 2.0% spread
                else:  # Low yield (<5%)
                    return 0.015  # 1.5% spread
            
            # Apply the variable spread model
            early_cutoff_year = 1986
            
            # Process each yield separately to avoid Series truth value ambiguity
            for date_idx in treasury_yearly.index:
                year = date_idx.year
                if year < early_cutoff_year:
                    # Get single yield value (as float)
                    yield_value = float(treasury_yearly.loc[date_idx])
                    # Calculate return as yield + spread and store as simple float
                    all_returns[date_idx] = yield_value + variable_spread(yield_value)
            
            print(f"Generated data for {sum(1 for date in all_returns if pd.to_datetime(date).year < 1986)} pre-1986 years")
                
        except Exception as e:
            print(f"Error generating pre-1986 bond returns: {e}")
        
        # Check if we have data
        if not all_returns:
            raise ValueError("Failed to collect any bond return data")
            
        # Convert dictionary to Series and sort by date
        yearly_returns = pd.Series(all_returns).sort_index()
        yearly_returns.name = "total_return"
        
        # Save to CSV
        raw_data_dir = os.path.join(os.getcwd(), "raw_data")
        output_path = os.path.join(raw_data_dir, "bond_returns.csv")
        
        # Create a DataFrame with a single column named 'total_return'
        bond_df = pd.DataFrame({'total_return': yearly_returns})
        bond_df.index.name = 'Date'
        
        # Ensure all values are simple floats before saving
        bond_df['total_return'] = bond_df['total_return'].astype(float)
        
        bond_df.to_csv(output_path)
        
        print(f"Bond returns saved to {output_path}: {len(yearly_returns)} years")
        print("\nSample of bond returns:")
        print(yearly_returns.head())
        
        print("\nSaved to raw_data/bond_returns.csv")
        
        return yearly_returns
        
    except Exception as e:
        print(f"ERROR: Failed to fetch bond returns: {e}")
        print("No fallback data was generated. Please fix the issue before proceeding.")
        print("Portfolio simulation cannot proceed without accurate bond return data.")
        return None

def check_directory_structure():
    """
    Check if all required directories exist and create them if needed
    """
    required_dirs = ['raw_data', 'note_data']
    
    for dir_name in required_dirs:
        dir_path = os.path.join(os.getcwd(), dir_name)
        if not os.path.exists(dir_path):
            print(f"Creating {dir_name} directory...")
            os.makedirs(dir_path)
            print(f"✓ Created {dir_name}/")
        else:
            print(f"✓ {dir_name}/ exists")

if __name__ == "__main__":
    if test_fred_api_access():
        fetch_and_save_raw_data()
        print("\nFetching bank funding spreads...")
        spreads = fetch_bank_funding_spreads()
        print("\nBank funding spreads data:")
        print(spreads.head())
        print("\nSaved to raw_data/bank_funding_spreads.csv")
        
        print("\nFetching SPY dividend yields...")
        div_yields = fetch_spy_dividend_yields()
        print("\nSPY dividend yields data:")
        print(div_yields.head())
        print("\nSaved to raw_data/spy_dividend_yields.csv")
        
        print("\nFetching bond returns...")
        bond_returns = fetch_bond_returns()
        print("\nBond returns data:")
        print(bond_returns.head())
        print("\nSaved to raw_data/bond_returns.csv")
        
        print("\nChecking directory structure...")
        check_directory_structure()