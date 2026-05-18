# DAX Momentum Backtesting Engine

A systematic momentum strategy backtested on DAX 40 constituents (2015–2024), implementing the Jegadeesh-Titman (1993) cross-sectional momentum factor.

**Market:** German equities (DAX 40)  
**Strategy:** 12-1 momentum — long top 5 stocks, short bottom 5  
**Backtest period:** 2015–2024 (9 years, monthly rebalancing)

---

## Modules

| File | Description |
|---|---|
| `data.py` | Downloads DAX 40 price data via yfinance, computes returns |
| `strategy.py` | Generates 12-1 momentum signals and portfolio weights |
| `backtest.py` | Event-driven engine with transaction costs and PnL tracking |
| `performance.py` | Sharpe, Sortino, drawdown, Calmar, monthly heatmap |

---

## Quickstart

```bash
pip install yfinance pandas numpy matplotlib scipy
python performance.py   # runs full backtest and generates charts
```

---

## Strategy Logic

### Jegadeesh-Titman Momentum (12-1)

At the end of each month:

1. Compute each stock's cumulative return over the past 12 months, skipping the most recent month
2. Rank all DAX stocks by this momentum score
3. **Long** the top 5 (winners) — equal weighted
4. **Short** the bottom 5 (losers) — equal weighted
5. Hold for one month, then rebalance

```
Momentum score = cumulative return over months [t-12, t-1]

Portfolio at month t:
  Long  = top 5 stocks by momentum score
  Short = bottom 5 stocks by momentum score
```

### Why skip the most recent month?

Short-term (1-month) returns exhibit mean reversion due to microstructure effects. Including the most recent month degrades performance — this is the key Jegadeesh-Titman insight.

### Transaction costs

Each rebalancing incurs a 10bps (0.10%) cost per unit of turnover — a conservative but realistic estimate for liquid large-cap stocks.

---

## Performance metrics

| Metric | Description |
|---|---|
| Sharpe Ratio | Annualised excess return / annualised volatility |
| Sortino Ratio | Like Sharpe, but only penalises downside volatility |
| Max Drawdown | Worst peak-to-trough loss over the backtest period |
| Calmar Ratio | Annualised return / absolute max drawdown |
| Win Rate | Percentage of months with positive return |

---

## Charts generated

Running `performance.py` produces `performance_report.png` containing:

- **Cumulative PnL** — strategy vs equal-weight DAX benchmark
- **Drawdown chart** — underwater equity curve
- **Rolling 12-month Sharpe** — consistency of risk-adjusted returns
- **Monthly returns heatmap** — year-by-year, month-by-month breakdown

---

## Key concepts

**Cross-sectional momentum** ranks stocks against each other at each point in time, unlike time-series momentum which compares a stock against its own history. This strategy is market-neutral by construction — the long and short sides roughly cancel out market beta.

**The momentum anomaly** is one of the most robust findings in empirical finance, documented across asset classes and geographies (Asness et al., 2013). It persists despite being widely known, likely due to behavioural biases (underreaction, herding) and structural constraints on arbitrage.

---

## References

- Jegadeesh, N. & Titman, S. (1993). *Returns to Buying Winners and Selling Losers*. Journal of Finance.
- Asness, C., Moskowitz, T. & Pedersen, L. (2013). *Value and Momentum Everywhere*. Journal of Finance.

---

## Author

Syed Mohammad Zaheen  
MSc Quantitative Finance  
GitHub: [iamzaheen](https://github.com/iamzaheen)
