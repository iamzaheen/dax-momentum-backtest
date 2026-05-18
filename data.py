"""
data.py — Market Data Module
=============================
Loads and prepares stock price data from local CSV files.

Dataset:
  stocks.csv    — 4 stocks, 1000 daily observations (~4 years)
  DAX_sample.csv — DAX index, 254 daily observations (used as benchmark)

Author: Syed Mohammad Zaheen
MSc Quantitative Finance
"""

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')


def load_prices(filepath='stocks.csv'):
    """
    Load stock price data from CSV.

    Returns
    -------
    prices : DataFrame — daily prices, stocks as columns
    """
    df = pd.read_csv(filepath)
    df.columns = ['Stock1', 'Stock2', 'Stock3', 'Stock4']

    # Create a business-day date index (~4 years ending today)
    n = len(df)
    dates = pd.bdate_range(end='2024-01-01', periods=n)
    df.index = dates

    print(f"  Loaded {df.shape[1]} stocks, {df.shape[0]} trading days")
    print(f"  Date range : {df.index[0].date()} to {df.index[-1].date()}")
    for col in df.columns:
        print(f"  {col}: start={df[col].iloc[0]:.2f}  end={df[col].iloc[-1]:.2f}  "
              f"total return={((df[col].iloc[-1]/df[col].iloc[0])-1)*100:.1f}%")
    return df


def load_benchmark(filepath='DAX_sample.csv'):
    """
    Load DAX index as benchmark.

    Returns
    -------
    dax : Series — daily DAX index levels
    """
    df = pd.read_csv(filepath, header=0)
    df.columns = ['DAX']
    n = len(df)
    dates = pd.bdate_range(end='2024-01-01', periods=n)
    df.index = dates
    return df['DAX']


def compute_returns(prices, freq='monthly'):
    """
    Compute returns from price data.

    Parameters
    ----------
    freq : 'daily' or 'monthly'
    """
    if freq == 'monthly':
        monthly = prices.resample('ME').last()
        returns = monthly.pct_change().dropna()
    else:
        returns = prices.pct_change().dropna()
    return returns


if __name__ == '__main__':
    print("=" * 55)
    print("  MOMENTUM BACKTEST — Module 1: Data")
    print("=" * 55)
    print()
    prices  = load_prices('stocks.csv')
    returns = compute_returns(prices, freq='monthly')
    bench   = load_benchmark('DAX_sample.csv')
    print(f"\n  Monthly returns shape: {returns.shape}")
    print(f"  Sample monthly returns (last 4 months):")
    print(returns.tail(4).round(4).to_string())
    print("\n  Module 1 complete.")
