# Portfolio Simulator - Technical Documentation

## Overview

This document provides a detailed explanation of the Portfolio Simulator project, focusing on the data collection processes, calculations, and methodologies used. The simulator models investment portfolios that include structured notes, equities, and bonds, and analyzes their performance across different market conditions.

## Table of Contents

1. [Raw Data Collection](#1-raw-data-collection)
   - S&P 500 Returns
   - Treasury Yields
   - VIX Volatility Index
   - Bank Funding Spreads
   - Bond Total Returns
   - Dividend Yields

2. [Structured Notes Calculation](#2-structured-notes-calculation)
   - Note Types and Structures
   - Participation Rate Calculation
   - Black-Scholes Option Pricing
   - Protection Levels

3. [Portfolio Simulation](#3-portfolio-simulation)
   - Asset Allocation
   - Return Calculation
   - Performance Metrics

## 1. Raw Data Collection

The simulator relies on historical market data collected through the `raw_data_collector.py` module. This module fetches, processes, and stores several key market indicators:

### S&P 500 Returns

- **Source**: Yahoo Finance (symbol: ^GSPC)
- **Process**:
  1. Historical daily closing prices are downloaded using the yfinance library
  2. Daily prices are resampled to yearly data (year-end closing prices)
  3. Data is saved to `raw_data/sp500_yearly.csv`
  4. These values serve as the basis for equity returns and structured note underlying performance

```python
sp500 = yf.download("^GSPC", start=start_date, end=end_date, progress=False, timeout=timeout)["Close"]
yearly_sp500 = sp500.resample("YE").last()
```

### Treasury Yields

- **Source**: Yahoo Finance (symbol: ^TNX)
- **Process**:
  1. 10-year Treasury yield data is downloaded and converted to decimal format (divided by 100)
  2. Daily yields are resampled to yearly averages
  3. Data is saved to `raw_data/treasury_yearly.csv`
  4. These values represent risk-free rates used in option pricing and bond yield calculations

```python
treasury = yf.download("^TNX", start=start_date, end=end_date, progress=False, timeout=timeout)["Close"] / 100
yearly_treasury = treasury.resample("YE").mean()
```

### VIX Volatility Index

- **Source**: Yahoo Finance (symbol: ^VIX)
- **Process**:
  1. VIX data is downloaded starting from 1990 (when it became available) and converted to decimal format
  2. Daily values are resampled to yearly averages
  3. Data is saved to `raw_data/vix_yearly.csv`
  4. These values serve as volatility inputs for option pricing in structured note calculations

```python
vix = yf.download("^VIX", start="1990-01-01", end=end_date, progress=False, timeout=timeout)["Close"] / 100
yearly_vix = vix.resample("YE").mean()
```

### Bank Funding Spreads

- **Source**: FRED API (Federal Reserve Economic Data)
- **Series**: `BAMLC0A4CBBB` (ICE BofA BBB US Corporate Index Option-Adjusted Spread)
- **Process**:
  1. BBB corporate bond spread data is fetched from the FRED API
  2. Values are converted from basis points to decimal format
  3. Daily values are resampled to yearly averages
  4. Data is saved to `raw_data/bank_funding_spreads.csv`
  5. These values represent the funding cost spread that banks face above the risk-free rate

```python
spreads = pd.Series(values, index=pd.DatetimeIndex(dates))
yearly_spreads = spreads.groupby(spreads.index.year).mean()
```

### Bond Total Returns

- **Source**: Multiple sources combined for comprehensive coverage
  - VBMFX (Vanguard Total Bond Market Index) for 1986-2007
  - BND (Vanguard Total Bond Market ETF) for 2007 onwards, with AGG as fallback
  - Model-based estimates for pre-1986 data using Treasury yields and variable spread
- **Process**:
  1. Price data is collected from each source
  2. Returns are calculated and resampled to yearly values
  3. For pre-1986 data, a variable spread model is applied to Treasury yields:
     ```python
     def variable_spread(yield_value):
         if yield_value > 0.10:      # Very high yield environment (>10%)
             return 0.030            # 3.0% spread
         elif yield_value > 0.07:    # High yield (7-10%)
             return 0.025            # 2.5% spread
         elif yield_value > 0.05:    # Moderate yield (5-7%)
             return 0.020            # 2.0% spread
         else:                       # Low yield (<5%)
             return 0.015            # 1.5% spread
     ```
  4. Data from all sources is combined, converted to a pandas Series, and saved to `raw_data/bond_returns.csv`

### Dividend Yields

- **Source**: Yahoo Finance (SPY ETF)
- **Process**:
  1. SPY dividend data is downloaded
  2. Trailing 12-month dividend yield is calculated (dividends / price)
  3. Values are resampled to year-end data
  4. Data is saved to `raw_data/spy_dividend_yields.csv`
  5. These values are used in option pricing to adjust for dividend effects

```python
annual_div = dividends.rolling(window=252, min_periods=1).sum()
div_yield = (annual_div / prices).resample('YE').last()
```

## 2. Structured Notes Calculation

Structured notes are complex financial instruments that combine elements of bonds and options. The project models these notes in the `src/structured_notes.py` module and calculates their parameters in `note_calculator.py`.

### Note Types and Structures

The system supports two main types of structured notes:

1. **Buffered Notes** (`BufferedNote` class):
   - For positive underlying returns: `return = underlying_return * participation_rate`
   - For negative underlying returns:
     - If loss is within buffer (`|underlying_return| <= protection_level`): `return = 0`
     - If loss exceeds buffer: `return = -(|underlying_return| - protection_level)`

2. **Floored Notes** (`FlooredNote` class):
   - For positive underlying returns: `return = underlying_return * participation_rate`
   - For negative underlying returns: `return = max(underlying_return, -protection_level)`

### Participation Rate Calculation

The participation rate is a key parameter that determines the note's exposure to the underlying asset's upside. It's calculated using the Black-Scholes option pricing model in `note_calculator.py`:

```python
def calculate_participation_rate(start_price, rf_rate, sigma, protection_level, term=1.0, iv_factor=0.90, funding_spread=0.015, div_yield=0.02):
    # Separate funding cost from dividend yield in option pricing
    funding_rf = rf_rate + funding_spread  # Funding cost
    
    # Calculate bond price using funding cost
    bond_price = 1.0 / (1 + funding_rf) ** term
    bond_capital = 1.0 - bond_price
    
    # Option calculations using separate rates
    K_put = start_price * (1 - protection_level)
    put_premium = black_scholes_put(start_price, K_put, term, rf_rate, sigma, div_yield, iv_factor)
    call_price = black_scholes_call(start_price, start_price, term, rf_rate, sigma, div_yield, iv_factor)
    
    # Calculate total capital available and participation
    total_available = bond_capital + (put_premium / start_price)
    participation = total_available / (call_price / start_price)
    participation = min(participation, 2.0)  # Cap at 200%
    
    return participation
```

The calculation involves these key steps:

1. Calculate the bond price based on risk-free rate and funding spread
2. Determine available capital from bond discount
3. Calculate put option premium for downside protection using Black-Scholes
4. Calculate at-the-money call option price using Black-Scholes
5. Determine participation rate as (bond discount + put premium) / call price
6. Cap the participation rate at 2.0 (200%)

### Black-Scholes Option Pricing

The Black-Scholes formulas are implemented for both call and put options, adjusted for dividends:

```python
def black_scholes_call(S, K, T, r, sigma, div_yield, iv_factor=1.0):
    adjusted_sigma = sigma * iv_factor
    # Adjust stock price for dividends
    S_adj = S * np.exp(-div_yield * T)  # Present value of stock ex-dividends
    
    d1 = (np.log(S_adj / K) + (r + 0.5 * adjusted_sigma**2) * T) / (adjusted_sigma * np.sqrt(T))
    d2 = d1 - adjusted_sigma * np.sqrt(T)
    
    call_price = S_adj * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    return call_price
```

### Protection Levels

The system evaluates multiple protection levels for each year:
- 5% protection
- 10% protection
- 15% protection
- 20% protection

For each protection level, the appropriate participation rate is calculated based on:
- The year's risk-free rate
- VIX volatility
- Bank funding spread
- Dividend yield

These calculations produce the `note_data/growth_notes.csv` file, which maps years to structured note parameters.

## 3. Portfolio Simulation

The portfolio simulation is handled by `portfolio_sim.py` and the modules in the `src` directory.

### Asset Allocation

The default portfolio allocation used in the simulation is:
- 40% S&P 500 (Equity)
- 30% Structured Notes
- 30% Bonds

### Return Calculation

For each year in the simulation:

1. Load the appropriate market data for the year
2. Calculate the S&P 500 return for the year
3. Determine the structured note return based on:
   - S&P 500 performance
   - Note participation rate
   - Protection level
4. Calculate the bond return from the historical bond data
5. Apply returns to each asset class in the portfolio
6. Add any new contributions
7. Calculate the new portfolio value

```python
equity_value = portfolio_value * 0.4 * (1 + sp_return)
note_value = portfolio_value * 0.3 * (1 + note_return)
bond_value = portfolio_value * 0.3 * (1 + bond_return)
portfolio_value = equity_value + note_value + bond_value + contrib
```

### Performance Metrics

The simulation calculates key performance metrics:

- **Total Return**: `(final_portfolio_value - (initial_investment + total_contributions)) / initial_investment`
- **Annualized Return**: `((final_portfolio_value / initial_investment) ^ (1 / horizon)) - 1`

These metrics are saved to CSV files in the `simulations` directory for analysis and comparison.

## Conclusion

The Portfolio Simulator provides a comprehensive framework for analyzing investment strategies that incorporate structured notes alongside traditional asset classes. By using historical market data and financial modeling techniques, it offers insights into how these strategies might have performed across different market conditions and time periods.

The project's modular structure allows for easy extension to support additional asset classes, note structures, or investment strategies in the future. 