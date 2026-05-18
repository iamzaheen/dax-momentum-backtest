"""
strategy.py — Momentum Signal Generator
=========================================
Implements cross-sectional momentum strategy.

With only 4 stocks we use a simpler but valid approach:
  - Rank all 4 stocks by past N-month return each month
  - Long top 2 (winners), short bottom 2 (losers)
  - Rebalance monthly

This is the same Jegadeesh-Titman logic used on larger universes —
the principle holds even with a small stock universe.

Author: Syed Mohammad Zaheen
MSc Quantitative Finance
"""

import pandas as pd
import numpy as np


def momentum_signal(returns, lookback=3, n_long=2, n_short=2):
    """
    Generate momentum signals for each stock at each rebalancing date.

    Parameters
    ----------
    returns  : DataFrame — monthly returns (dates x stocks)
    lookback : int — months of return history to use
               (using 3 months given ~4 years of data and 4 stocks)
    n_long   : int — number of stocks to go long
    n_short  : int — number of stocks to go short

    Returns
    -------
    signals : DataFrame — +1 (long), -1 (short), 0 (not held)
    scores  : DataFrame — raw momentum scores (cumulative return)
    """
    signals = pd.DataFrame(0, index=returns.index, columns=returns.columns)
    scores  = pd.DataFrame(np.nan, index=returns.index, columns=returns.columns)

    for i in range(lookback, len(returns)):
        # Momentum score: cumulative return over past lookback months
        window     = returns.iloc[i - lookback:i]
        cum_return = (1 + window).prod() - 1

        valid = cum_return.dropna()
        if len(valid) < n_long + n_short:
            continue

        # Rank stocks by momentum (highest = best momentum)
        ranked = valid.rank(ascending=False)

        sig = pd.Series(0, index=returns.columns)
        sig[ranked <= n_long]                    = 1   # top 2 = long
        sig[ranked >= len(valid) - n_short + 1] = -1  # bottom 2 = short

        signals.iloc[i] = sig
        scores.iloc[i]  = cum_return

    return signals, scores


def get_portfolio_weights(signals):
    """Convert signals to equal-weight portfolio weights."""
    weights = pd.DataFrame(0.0, index=signals.index, columns=signals.columns)

    for date in signals.index:
        sig          = signals.loc[date]
        long_stocks  = sig[sig == 1].index
        short_stocks = sig[sig == -1].index

        if len(long_stocks) > 0:
            weights.loc[date, long_stocks]  =  1.0 / len(long_stocks)
        if len(short_stocks) > 0:
            weights.loc[date, short_stocks] = -1.0 / len(short_stocks)

    return weights


if __name__ == '__main__':
    import sys
    sys.path.append('.')
    from data import load_prices, compute_returns

    print("=" * 55)
    print("  MOMENTUM BACKTEST — Module 2: Strategy")
    print("=" * 55)
    print()

    prices  = load_prices('stocks.csv')
    returns = compute_returns(prices, freq='monthly')
    signals, scores = momentum_signal(returns, lookback=3, n_long=2, n_short=2)

    active = signals[signals.abs().sum(axis=1) > 0]
    print(f"  Total rebalancing months: {len(active)}")
    print(f"\n  Last 5 signals:")
    print(f"  {'Date':<12} {'Stock1':>8} {'Stock2':>8} {'Stock3':>8} {'Stock4':>8}")
    for date, row in active.tail(5).iterrows():
        vals = '  '.join([f'{int(v):>8}' if v != 0 else f"{'—':>8}"
                          for v in row.values])
        print(f"  {str(date.date()):<12} {vals}")

    print(f"\n  Key: +1 = LONG, -1 = SHORT, — = not held")
    print("\n  Module 2 complete.")
