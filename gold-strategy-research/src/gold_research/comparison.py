"""Compact comparison of fixed allocation rules."""
from .reporting import table


def comparison(summary,cfg):
    modes=['buy_hold','trend','vol','combined','fixed_50']
    subset=summary[summary.Strategy.isin(modes)]
    d=subset[subset.Period=='2020-2025'].set_index('Strategy')
    return f'''# Fixed-rule comparison

**Research question.** Does trend timing improve the risk–return trade-off of gold allocation relative to volatility targeting and passive exposure?

| Rule | Gold allocation |
|---|---|
| Trend timing | 100% when price exceeds the {cfg['ma']}-session moving average; otherwise 0% |
| Volatility targeting | min(100%, {cfg['target_vol']:.0%}/max(estimated annualized volatility, 1%)); {cfg['vol_window']}-return estimation window |
| Combined | Trend indicator multiplied by volatility-targeted exposure |
| Fixed 50% | 50% gold, rebalanced monthly |
| Buy and hold | Initial full allocation; no subsequent rebalancing |

All dynamic rules execute at the first trading-day close of each month using the previous close's signal. Costs are {cfg['cost_bps']:g} bps per side. The risk target is a sizing parameter, not a guaranteed volatility or loss ceiling.

## 2007–2025

{table(subset[subset.Period=='All'])}

## 2020–2025

{table(subset[subset.Period=='2020-2025'])}

Relative to trend timing, volatility targeting changed CAGR by {(d.loc['vol','CAGR']-d.loc['trend','CAGR'])*100:+.2f} percentage points, volatility by {(d.loc['vol','Volatility']-d.loc['trend','Volatility'])*100:+.2f} points, and drawdown magnitude by {(abs(d.loc['vol','MaxDrawdown'])-abs(d.loc['trend','MaxDrawdown']))*100:+.2f} points. Differences are calculated before rounding.

**Conclusion.** In the reference experiment, volatility targeting delivered a more favorable risk profile than trend timing at a modest return cost. Combining the rules did not improve the recent-period return–drawdown trade-off. Fixed 50% exposure provides a competitive low-complexity benchmark. These are retrospective comparisons, not evidence of prospective outperformance.

[Full report](REPORT.md) · [Figures](BEGINNER.md)
'''
