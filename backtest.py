"""
backtest.py — Backtesting Engine
==================================
Simulates trading the momentum strategy month by month,
tracking PnL, turnover, and transaction costs.

Author: Syed Mohammad Zaheen
MSc Quantitative Finance
"""

import pandas as pd
import numpy as np
import sys
sys.path.append('.')


def run_backtest(returns, signals, transaction_cost=0.001):
    """
    Simulate the momentum strategy and compute portfolio returns.

    Parameters
    ----------
    returns          : DataFrame — monthly stock returns
    signals          : DataFrame — +1 long, -1 short, 0 not held
    transaction_cost : float — cost per trade (0.001 = 10bps)

    Returns
    -------
    results : dict with portfolio_returns, gross_returns, turnover
    """
    from strategy import get_portfolio_weights
    weights = get_portfolio_weights(signals)

    portfolio_returns = []
    gross_returns     = []
    turnovers         = []
    dates             = []
    positions         = []

    prev_weights = pd.Series(0.0, index=returns.columns)

    for i in range(1, len(returns)):
        date          = returns.index[i]
        curr_weights  = weights.iloc[i - 1]
        month_returns = returns.iloc[i]

        if curr_weights.abs().sum() == 0:
            continue

        # Gross return
        gross_ret = (curr_weights * month_returns).sum()

        # Turnover and transaction cost
        weight_change = (curr_weights - prev_weights).abs().sum()
        turnover      = weight_change / 2
        cost          = turnover * transaction_cost
        net_ret       = gross_ret - cost

        portfolio_returns.append(net_ret)
        gross_returns.append(gross_ret)
        turnovers.append(turnover)
        dates.append(date)
        positions.append(curr_weights.to_dict())

        prev_weights = curr_weights.copy()

    results = {
        'portfolio_returns': pd.Series(portfolio_returns, index=dates, name='Strategy'),
        'gross_returns':     pd.Series(gross_returns, index=dates, name='Gross'),
        'turnover':          pd.Series(turnovers, index=dates, name='Turnover'),
        'positions':         pd.DataFrame(positions, index=dates),
    }
    return results


def compute_benchmark(returns):
    """Equal-weight benchmark — buy all 4 stocks equally each month."""
    bench = returns.mean(axis=1)
    bench.name = 'Equal-Weight Benchmark'
    return bench


if __name__ == '__main__':
    from data import load_prices, compute_returns
    from strategy import momentum_signal

    print("=" * 55)
    print("  MOMENTUM BACKTEST — Module 3: Backtest Engine")
    print("=" * 55)
    print()

    prices   = load_prices('stocks.csv')
    returns  = compute_returns(prices, freq='monthly')
    signals, _ = momentum_signal(returns, lookback=3, n_long=2, n_short=2)
    results  = run_backtest(returns, signals, transaction_cost=0.001)

    ret = results['portfolio_returns']
    print(f"  Backtest period  : {ret.index[0].date()} to {ret.index[-1].date()}")
    print(f"  Trading months   : {len(ret)}")
    print(f"  Avg monthly ret  : {ret.mean()*100:.3f}%")
    print(f"  Avg turnover     : {results['turnover'].mean()*100:.1f}% per month")
    print(f"  Best month       : {ret.max()*100:.2f}%")
    print(f"  Worst month      : {ret.min()*100:.2f}%")
    print("\n  Module 3 complete.")
