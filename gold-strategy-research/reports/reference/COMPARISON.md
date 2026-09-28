# Fixed-rule comparison

**Research question.** Does trend timing improve the risk–return trade-off of gold allocation relative to volatility targeting and passive exposure?

| Rule | Gold allocation |
|---|---|
| Trend timing | 100% when price exceeds the 200-session moving average; otherwise 0% |
| Volatility targeting | min(100%, 10%/max(estimated annualized volatility, 1%)); 60-return estimation window |
| Combined | Trend indicator multiplied by volatility-targeted exposure |
| Fixed 50% | 50% gold, rebalanced monthly |
| Buy and hold | Initial full allocation; no subsequent rebalancing |

All dynamic rules execute at the first trading-day close of each month using the previous close's signal. Costs are 10 bps per side. The risk target is a sizing parameter, not a guaranteed volatility or loss ceiling.

## 2007–2025

| Strategy | CAGR | Volatility | Sharpe | Max. drawdown | Annual turnover |
|---|---:|---:|---:|---:|---:|
| Buy and hold | 10.24% | 17.50% | 0.64 | 45.56% | 0.05 |
| Fixed 50% | 5.37% | 8.77% | 0.64 | 25.18% | 0.14 |
| Trend timing | 7.84% | 14.01% | 0.61 | 40.15% | 1.84 |
| Volatility targeting | 6.99% | 11.00% | 0.67 | 33.20% | 0.89 |
| Combined | 5.43% | 9.02% | 0.63 | 29.17% | 1.83 |

## 2020–2025

| Strategy | CAGR | Volatility | Sharpe | Max. drawdown | Annual turnover |
|---|---:|---:|---:|---:|---:|
| Buy and hold | 18.58% | 16.34% | 1.13 | 22.00% | 0.00 |
| Fixed 50% | 9.19% | 8.22% | 1.11 | 11.29% | 0.10 |
| Trend timing | 12.87% | 14.68% | 0.90 | 31.10% | 2.34 |
| Volatility targeting | 12.28% | 11.43% | 1.07 | 15.97% | 1.02 |
| Combined | 7.81% | 10.22% | 0.79 | 23.84% | 2.53 |

Relative to trend timing, volatility targeting changed CAGR by -0.59 percentage points, volatility by -3.25 points, and drawdown magnitude by -15.13 points. Differences are calculated before rounding.

**Conclusion.** In the reference experiment, volatility targeting delivered a more favorable risk profile than trend timing at a modest return cost. Combining the rules did not improve the recent-period return–drawdown trade-off. Fixed 50% exposure provides a competitive low-complexity benchmark. These are retrospective comparisons, not evidence of prospective outperformance.

[Full report](REPORT.md) · [Figures](BEGINNER.md)
