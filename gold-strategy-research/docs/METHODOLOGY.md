# Methodology

## Allocation rules

Let P_t denote the adjusted closing price and r_t = P_t/P_(t−1) − 1. The trend indicator is I_t = 1{P_t > MA_200,t}. Estimated volatility is the sample standard deviation of the preceding 60 daily returns, multiplied by √252.

The volatility-targeted weight is a_t = min(1, 0.10/max(σ_t, 0.01)). Trend, volatility, and combined allocations are I_t, a_t, and I_t a_t, respectively. The auxiliary mean-reversion rule allocates fully when the 20-session price z-score is below −1.5 and holds cash otherwise.

## Execution and accounting

Targets are observed at the prior close and executed at the first trading-day close of each month. Signal lagging occurs once, inside the execution engine. Shares remain constant between rebalances; portfolio weights therefore drift with prices.

For pre-trade wealth V, existing gold value A, post-trade gold value X, target weight w, and proportional cost c, self-financing requires X = w(V − c|X−A|). Thus:

- Purchases: X = w(V+cA)/(1+wc).
- Sales: X = w(V−cA)/(1−wc).

Cash after trading is V−X−c|X−A|. Initial purchases incur costs; terminal positions are marked to market without liquidation. Fractional shares are permitted.

## Evaluation

CAGR uses 252 trading sessions per year. Sharpe uses arithmetic daily mean returns, sample standard deviation, and a zero risk-free rate. Maximum drawdown includes initial wealth and resets its running peak at each reported subperiod boundary. Subperiod returns retain existing positions.

For each test year, nine combined-rule specifications are scored over the preceding five calendar years by net Sharpe. Earlier observations are used only for indicator warm-up. Ties favor shorter moving averages, then lower volatility targets. Parameters are frozen for the next year, and test holdings carry continuously across years.

A paired circular block bootstrap describes uncertainty in annualized mean daily-return differences. It does not estimate a CAGR confidence interval, account for multiple specification searches, or re-estimate the selection procedure in each resample.

## Scope

This is a retrospective single-asset study. Rolling selection reduces direct look-ahead but does not eliminate researcher selection bias. Benchmarks are not exactly risk-matched; differences cannot be interpreted as causal timing effects. The prose interpretation refers to the committed reference experiment and should be reassessed after configuration changes.
