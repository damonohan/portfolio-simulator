import pandas as pd
import numpy as np
import os
from scipy.stats import norm
import logging
import matplotlib.pyplot as plt
import seaborn as sns

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("note_calculator.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()

# Black-Scholes functions (unchanged)
def black_scholes_call(S, K, T, r, sigma, div_yield, iv_factor=1.0):
    """
    Black-Scholes call option price with continuous dividend yield
    S: Stock price
    K: Strike price
    T: Time to maturity (1 year for our notes)
    r: Risk-free rate
    sigma: Volatility
    div_yield: Continuous dividend yield
    """
    adjusted_sigma = sigma * iv_factor
    # Adjust stock price for dividends
    S_adj = S * np.exp(-div_yield * T)  # Present value of stock ex-dividends
    
    d1 = (np.log(S_adj / K) + (r + 0.5 * adjusted_sigma**2) * T) / (adjusted_sigma * np.sqrt(T))
    d2 = d1 - adjusted_sigma * np.sqrt(T)
    
    call_price = S_adj * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    logger.debug(f"Call Price: S={S}, K={K}, T={T}, r={r}, sigma={adjusted_sigma}, call_price={call_price}")
    return call_price

def black_scholes_put(S, K, T, r, sigma, div_yield, iv_factor=1.0):
    """
    Black-Scholes put option price with continuous dividend yield
    """
    adjusted_sigma = sigma * iv_factor
    # Adjust stock price for dividends
    S_adj = S * np.exp(-div_yield * T)  # Present value of stock ex-dividends
    
    d1 = (np.log(S_adj / K) + (r + 0.5 * adjusted_sigma**2) * T) / (adjusted_sigma * np.sqrt(T))
    d2 = d1 - adjusted_sigma * np.sqrt(T)
    
    put_price = K * np.exp(-r * T) * norm.cdf(-d2) - S_adj * norm.cdf(-d1)
    logger.debug(f"Put Price: S={S}, K={K}, T={T}, r={r}, sigma={adjusted_sigma}, put_price={put_price}")
    return put_price

def calculate_participation_rate(start_price, rf_rate, sigma, protection_level, term=1.0, iv_factor=0.90, funding_spread=0.015, div_yield=0.02):
    """
    Calculate participation rate using Black-Scholes and funding costs
    """
    # Separate funding cost from dividend yield in option pricing
    funding_rf = rf_rate + funding_spread  # Funding cost
    
    # Log input parameters
    logger.info(f"\nCalculating participation rate:")
    logger.info(f"  RF Rate: {rf_rate:.4f}")
    logger.info(f"  Funding Spread: {funding_spread:.4f}")
    logger.info(f"  Dividend Yield: {div_yield:.4f}")
    logger.info(f"  Total Funding: {funding_rf:.4f}")
    
    # Calculate bond price using funding cost
    bond_price = 1.0 / (1 + funding_rf) ** term
    bond_capital = 1.0 - bond_price
    
    # Option calculations using separate rates
    K_put = start_price * (1 - protection_level)
    put_premium = black_scholes_put(start_price, K_put, term, rf_rate, sigma, div_yield, iv_factor)
    call_price = black_scholes_call(start_price, start_price, term, rf_rate, sigma, div_yield, iv_factor)
    
    # Dynamic IV factor based on market conditions
    crisis_iv_factor = min(1.0, 0.90 + max(0, (sigma - 0.20) * 0.5))  # Increase IV factor during high vol
    
    total_available = bond_capital + (put_premium / start_price)
    participation = total_available / (call_price / start_price)
    participation = min(participation, 2.0)
    
    return participation

def simple_note_payoff(start_price, end_price, participation_rate, protection_level):
    underlying_return = (end_price - start_price) / start_price
    if underlying_return > 0:
        return underlying_return * participation_rate
    elif underlying_return >= -protection_level:
        return 0
    else:
        return underlying_return + protection_level

def calculate_note_payoffs():
    try:
        # Load all required data
        raw_data_dir = os.path.join(os.getcwd(), "raw_data")
        
        # Load data with proper column names and index
        sp500_df = pd.read_csv(os.path.join(raw_data_dir, "sp500_yearly.csv"))
        sp500_df['Date'] = pd.to_datetime(sp500_df['Date'])
        sp500_df.set_index('Date', inplace=True)
        sp500 = sp500_df['^GSPC']
        
        treasury_df = pd.read_csv(os.path.join(raw_data_dir, "treasury_yearly.csv"))
        treasury_df['Date'] = pd.to_datetime(treasury_df['Date'])
        treasury_df.set_index('Date', inplace=True)
        treasury = treasury_df['^TNX']
        
        vix_df = pd.read_csv(os.path.join(raw_data_dir, "vix_yearly.csv"))
        vix_df['Date'] = pd.to_datetime(vix_df['Date'])
        vix_df.set_index('Date', inplace=True)
        vix = vix_df['^VIX']
        
        funding_spreads = pd.read_csv(os.path.join(raw_data_dir, "bank_funding_spreads.csv"), 
                                    index_col=0, parse_dates=True)["TEDRATE"]
        div_yields = pd.read_csv(os.path.join(raw_data_dir, "spy_dividend_yields.csv"), 
                                index_col=0, parse_dates=True)["Dividend_Yield"]
        
        logger.info("Successfully loaded all market data including dividend yields")
        
        # Calculate for each year and protection level
        note_data = []
        for start_date in sp500.index:
            year = start_date.year  # Now this will work because start_date is a datetime
            start_price = sp500[start_date]
            rf_rate = treasury[start_date]
            sigma = vix[start_date] if start_date in vix.index else 0.20
            funding_spread = funding_spreads[start_date] if start_date in funding_spreads.index else 0.015
            div_yield = div_yields[start_date] if start_date in div_yields.index else 0.02
            
            for protection_level in [0.05, 0.10, 0.15, 0.20]:
                participation = calculate_participation_rate(
                    start_price, rf_rate, sigma, protection_level, 
                    term=1.0, iv_factor=0.90, funding_spread=funding_spread,
                    div_yield=div_yield
                )
                note_data.append({
                    "protection_level": protection_level,
                    "term": 1.0,
                    "underlying_asset": "S&P 500",
                    "protection_type": "Buffer",
                    "participation_rate": participation,
                    "year": year,
                    "volatility": sigma,
                    "interest_rate": rf_rate,
                    "funding_spread": funding_spread,
                    "funding_source": "FRED TED" if start_date in funding_spreads.index else "default"
                })

        # Change the output directory to be within the current directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(script_dir, "note_data")  # Removed the ".." to keep it in same directory
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "growth_notes.csv")
        
        # Debugging
        logger.info(f"Current working directory: {os.getcwd()}")
        logger.info(f"Attempting to save to: {output_path}")
        
        note_data_df = pd.DataFrame(note_data)
        note_data_df.to_csv(output_path, index=False)
        
        print(f"Participation rates calculated and stored in '{output_path}'.")
        logger.info(f"Calculation complete. Results saved to '{output_path}'.")
    except Exception as e:
        logger.error(f"Error calculating note payoffs: {e}")

def analyze_participation_rates():
    # Read the data
    notes_df = pd.read_csv("note_data/growth_notes.csv")
    
    # Calculate total borrowing cost
    notes_df['total_cost'] = notes_df['interest_rate'] + notes_df['funding_spread']
    
    # Create visualization
    plt.figure(figsize=(12, 8))
    
    # Plot for each protection level
    for protection in notes_df['protection_level'].unique():
        mask = notes_df['protection_level'] == protection
        plt.scatter(notes_df[mask]['total_cost'], 
                   notes_df[mask]['participation_rate'],
                   label=f'Protection {protection*100}%',
                   alpha=0.6)
    
    plt.xlabel('Total Borrowing Cost (RF + Funding Spread)')
    plt.ylabel('Participation Rate')
    plt.title('Participation Rates vs Total Borrowing Cost')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Add some key period annotations
    for year in [2008, 2020]:
        year_data = notes_df[notes_df['year'] == year]
        if not year_data.empty:
            plt.annotate(f'{year}', 
                        (year_data['total_cost'].iloc[0], 
                         year_data['participation_rate'].iloc[0]))
    
    plt.savefig('participation_analysis.png')
    plt.close()

if __name__ == "__main__":
    calculate_note_payoffs()
    analyze_participation_rates()