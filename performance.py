"""
performance.py — Performance Analytics & Visualisation
========================================================
Computes professional hedge fund metrics and generates
a full 4-panel performance report chart.

Author: Syed Mohammad Zaheen
MSc Quantitative Finance
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')


def sharpe_ratio(returns, rf=0.02, periods=12):
    excess = returns - rf / periods
    if excess.std() == 0:
        return 0.0
    return float(excess.mean() / excess.std() * np.sqrt(periods))


def sortino_ratio(returns, rf=0.02, periods=12):
    excess   = returns - rf / periods
    downside = excess[excess < 0]
    if len(downside) == 0 or downside.std() == 0:
        return 0.0
    return float(excess.mean() / downside.std() * np.sqrt(periods))


def max_drawdown(returns):
    cum  = (1 + returns).cumprod()
    peak = cum.cummax()
    dd   = (cum - peak) / peak
    return float(dd.min())


def calmar_ratio(returns, periods=12):
    ann_ret = (1 + returns.mean()) ** periods - 1
    mdd     = abs(max_drawdown(returns))
    return float(ann_ret / mdd) if mdd > 0 else 0.0


def compute_metrics(returns, name, rf=0.02, periods=12):
    ann_ret = (1 + returns.mean()) ** periods - 1
    ann_vol = returns.std() * np.sqrt(periods)
    return {
        'Name'               : name,
        'Ann. Return (%)'    : round(ann_ret * 100, 2),
        'Ann. Volatility (%)': round(ann_vol * 100, 2),
        'Sharpe Ratio'       : round(sharpe_ratio(returns, rf), 3),
        'Sortino Ratio'      : round(sortino_ratio(returns, rf), 3),
        'Max Drawdown (%)'   : round(max_drawdown(returns) * 100, 2),
        'Calmar Ratio'       : round(calmar_ratio(returns), 3),
        'Win Rate (%)'       : round((returns > 0).mean() * 100, 1),
        'Best Month (%)'     : round(returns.max() * 100, 2),
        'Worst Month (%)'    : round(returns.min() * 100, 2),
    }


def print_report(strat, bench):
    keys = ['Ann. Return (%)', 'Ann. Volatility (%)', 'Sharpe Ratio',
            'Sortino Ratio', 'Max Drawdown (%)', 'Calmar Ratio',
            'Win Rate (%)', 'Best Month (%)', 'Worst Month (%)']
    print(f"\n  {'Metric':<25} {'Strategy':>12}  {'Benchmark':>12}")
    print(f"  {'─'*52}")
    for k in keys:
        s_val = str(strat[k])
        b_val = str(bench[k])
        print(f"  {k:<25} {s_val:>12}  {b_val:>12}")


def plot_report(strategy_returns, benchmark_returns, save=True):
    bench = benchmark_returns.reindex(strategy_returns.index).dropna()
    strat = strategy_returns.reindex(bench.index)

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Momentum Strategy — Performance Report',
                 fontsize=15, fontweight='bold')

    # ── 1. Cumulative PnL ───────────────────────────────
    ax = axes[0, 0]
    cum_s = (1 + strat).cumprod()
    cum_b = (1 + bench).cumprod()
    ax.plot(cum_s.index, cum_s.values, label='Momentum Strategy',
            color='steelblue', lw=2)
    ax.plot(cum_b.index, cum_b.values, label='EW Benchmark',
            color='gray', lw=1.5, linestyle='--')
    ax.fill_between(cum_s.index, cum_s.values, cum_b.values,
                    where=cum_s.values >= cum_b.values,
                    alpha=0.15, color='green')
    ax.fill_between(cum_s.index, cum_s.values, cum_b.values,
                    where=cum_s.values < cum_b.values,
                    alpha=0.15, color='red')
    ax.set_title('Cumulative Return (Strategy vs Benchmark)')
    ax.set_ylabel('Portfolio Value (start = 1)')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    # ── 2. Drawdown ─────────────────────────────────────
    ax = axes[0, 1]
    cum  = (1 + strat).cumprod()
    peak = cum.cummax()
    dd   = (cum - peak) / peak * 100
    ax.fill_between(dd.index, dd.values, 0, color='crimson', alpha=0.6)
    ax.set_title('Drawdown (%)')
    ax.set_ylabel('Drawdown (%)')
    ax.grid(True, alpha=0.3)

    # ── 3. Rolling 12m Sharpe ───────────────────────────
    ax = axes[1, 0]
    roll_sharpe = strat.rolling(6).apply(
        lambda x: sharpe_ratio(pd.Series(x)), raw=False)
    ax.plot(roll_sharpe.index, roll_sharpe.values,
            color='darkorange', lw=1.5)
    ax.axhline(0, color='black', lw=0.8, alpha=0.5)
    ax.axhline(1, color='green', lw=0.8, linestyle='--',
               alpha=0.6, label='Sharpe=1')
    ax.set_title('Rolling 6-Month Sharpe Ratio')
    ax.set_ylabel('Sharpe Ratio')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    # ── 4. Monthly Returns Bar Chart ────────────────────
    ax = axes[1, 1]
    colors = ['steelblue' if r >= 0 else 'crimson' for r in strat.values]
    ax.bar(range(len(strat)), strat.values * 100, color=colors, alpha=0.8)
    ax.axhline(0, color='black', lw=0.8)
    ax.set_title('Monthly Returns (%)')
    ax.set_ylabel('Return (%)')
    ax.set_xlabel('Month')
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    if save:
        plt.savefig('performance_report.png', dpi=150, bbox_inches='tight')
        print("  Saved: performance_report.png")
    plt.show()


if __name__ == '__main__':
    import sys
    sys.path.append('.')
    from data import load_prices, compute_returns, load_benchmark
    from strategy import momentum_signal
    from backtest import run_backtest, compute_benchmark

    print("=" * 55)
    print("  MOMENTUM BACKTEST — Full Performance Report")
    print("=" * 55)
    print()

    prices    = load_prices('stocks.csv')
    returns   = compute_returns(prices, freq='monthly')
    signals, _ = momentum_signal(returns, lookback=3, n_long=2, n_short=2)
    results   = run_backtest(returns, signals, transaction_cost=0.001)
    benchmark = compute_benchmark(returns)

    strat_ret = results['portfolio_returns']
    bench_ret = benchmark.reindex(strat_ret.index).dropna()

    strat_m = compute_metrics(strat_ret, 'Momentum Strategy')
    bench_m = compute_metrics(bench_ret, 'EW Benchmark')

    print_report(strat_m, bench_m)

    print(f"\n  Generating charts...")
    plot_report(strat_ret, bench_ret)
    print("\n  Full backtest complete.")
