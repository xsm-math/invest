# Trend Timing and Volatility Targeting in Gold Allocation

This project examines whether monthly trend timing improves gold allocation relative to volatility targeting and passive exposure. Daily adjusted GLD prices cover 2005–2025, with fixed-rule evaluation over 2007–2025 and annual rolling evaluation over 2015–2025.

[Report](reports/reference/REPORT.md) · [Comparison](reports/reference/COMPARISON.md) · [Figures](reports/reference/BEGINNER.md) · [Methodology](docs/METHODOLOGY.md) · [References](docs/REFERENCES.md)

## Specification

- **Trend timing:** full gold exposure when price exceeds its 200-session moving average; cash otherwise.
- **Volatility targeting:** exposure equals 10% divided by estimated annualized volatility, capped at 100%. Volatility is estimated from 60 daily returns and floored at 1%.
- **Combined:** the trend indicator multiplied by volatility-targeted exposure.
- **Benchmarks:** buy-and-hold and monthly rebalanced 50% gold/50% cash.

Signals observed at the previous close execute at the first trading-day close of each month. Costs are 10 bps per side; cash earns zero. The portfolio is long-only and unlevered. The volatility target is a sizing parameter, not a loss limit.

## Results

**2020–2025 historical subperiod; net of assumed trading costs.**

| Strategy | CAGR | Volatility | Maximum drawdown |
|---|---:|---:|---:|
| Buy and hold | 18.58% | 16.34% | 22.00% |
| Trend timing | 12.87% | 14.68% | 31.10% |
| Volatility targeting | 12.28% | 11.43% | 15.97% |
| Combined | 7.81% | 10.22% | 23.84% |
| Fixed 50% | 9.19% | 8.22% | 11.29% |

![Performance comparison](reports/reference/plain_comparison.png)

*Annualized return, volatility, and maximum drawdown for the full sample and recent subperiod. Scales are shared within columns; drawdowns are positive loss magnitudes.*

Volatility targeting reduced drawdown relative to trend timing at a 0.59-percentage-point annual return cost in the recent subperiod. Combining the rules did not improve that trade-off. Over the full sample, the combination reduced drawdown further but also reduced returns. Annual rolling parameter selection did not outperform the fixed-weight benchmark. These retrospective findings do not establish return predictability or prospective outperformance.

## Reproduction

From this directory, using Python 3.10 or later:

```bash
python -m pip install -e .
python -m gold_research download
python -m gold_research run
python -m unittest discover -s tests -v
```

The download command retrieves the historical price window. Raw market data is excluded from Git; retrieval failures are not replaced with synthetic data. Configuration is stored in `configs/default.json`. New outputs are written to `reports/generated/`; committed reference results reside in `reports/reference/`. The manifest records the data hash and software versions.

## Implementation

`strategies.py` defines target exposures; `engine.py` maintains a self-financing shares-and-cash account; `walkforward.py` selects parameters using only pre-cutoff data. Reporting modules generate tables and figures. Eleven offline tests cover accounting, signal timing, future-data isolation, and year-boundary continuity.

The analysis excludes taxes, currency conversion, and execution frictions beyond the cost assumption. It is a research implementation, not a live trading system.
