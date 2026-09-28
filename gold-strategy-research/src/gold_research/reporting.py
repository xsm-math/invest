"""Research tables, figures, and manuscript generation."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

NAMES={'buy_hold':'Buy and hold','fixed_50':'Fixed 50%','trend':'Trend timing',
       'vol':'Volatility targeting','combined':'Combined','mean_reversion':'Mean reversion',
       'walk_forward':'Walk-forward'}


def table(df):
    lines=['| Strategy | CAGR | Volatility | Sharpe | Max. drawdown | Annual turnover |',
           '|---|---:|---:|---:|---:|---:|']
    for _,r in df.iterrows():
        lines.append(f'| {NAMES.get(r.Strategy,r.Strategy)} | {r.CAGR:.2%} | {r.Volatility:.2%} | {r.Sharpe_RF0:.2f} | {abs(r.MaxDrawdown):.2%} | {r.TurnoverAnnual:.2f} |')
    return '\n'.join(lines)


def plot(results,path,title):
    fig,axes=plt.subplots(2,1,figsize=(11,8),sharex=True,gridspec_kw={'height_ratios':[2,1]})
    for mode,d in results.items():
        axes[0].plot(d.index,d.nav,label=NAMES.get(mode,mode),lw=1.3)
        axes[1].plot(d.index,d.nav/d.nav.cummax().clip(lower=1)-1,lw=1)
    axes[0].set_yscale('log');axes[0].set_ylabel('NAV (log scale)');axes[0].set_title(title)
    axes[0].legend(ncol=3,fontsize=9);axes[1].set_ylabel('Drawdown')
    for ax in axes: ax.grid(alpha=.2)
    fig.tight_layout();fig.savefig(path,dpi=150);plt.close(fig)


def write_report(out,summary,wf_summary,folds,interval,cfg,sha):
    from .comparison import comparison
    (out/'COMPARISON.md').write_text(comparison(summary,cfg),encoding='utf-8')
    full=summary[summary.Period=='All'];recent=summary[summary.Period=='2020-2025']
    d=recent.set_index('Strategy')
    text=f'''# Trend Timing and Volatility Targeting in Gold Allocation

## Abstract

This study evaluates monthly allocation rules for SPDR Gold Shares (GLD). A moving-average filter is compared with volatility targeting, their combination, and passive allocations. In 2020–2025, volatility targeting returned {d.loc['vol','CAGR']:.2%} annually with a maximum drawdown of {abs(d.loc['vol','MaxDrawdown']):.2%}, compared with {d.loc['trend','CAGR']:.2%} and {abs(d.loc['trend','MaxDrawdown']):.2%} for trend timing. Under the reference specification, volatility targeting reduced risk at a modest return cost relative to trend timing. Combining the two rules did not improve the recent-period return–drawdown trade-off.

## 1. Data and specification

Daily adjusted GLD closing prices cover 2005–2025; 2005–2006 provide indicator warm-up. Fixed-rule evaluation begins on {cfg['start']}. Results are denominated in USD. The analysis uses a single vendor and does not independently verify exchange data.

Trend timing allocates fully to gold when the closing price exceeds its {cfg['ma']}-session moving average and otherwise holds cash. Volatility targeting sets gold exposure to min(1, {cfg['target_vol']:.2%}/max(estimated volatility, 1%)), using the sample standard deviation of {cfg['vol_window']} daily returns, annualized by √252. The combined rule multiplies this exposure by the trend indicator. All exposures are long-only and capped at 100%.

Buy-and-hold and monthly rebalanced 50% gold/50% cash serve as benchmarks. An auxiliary mean-reversion rule holds gold when the {cfg['mr_window']}-session price z-score is below −{cfg['mr_entry']}; it is evaluated at the same monthly frequency.

Signals observed at the previous close are executed at the first trading-day close of each month. Existing holdings earn the execution-day return. Costs are {cfg['cost_bps']:g} basis points per unit of traded value, per side; cash earns a constant {cfg['cash_rate']:.2%}. Holdings drift between rebalances. Taxes, integer share constraints, and market impact beyond the cost assumption are excluded. Terminal positions are marked to market without liquidation.

## 2. Fixed-rule results

**Table 1. Full sample, 2007–2025.**

{table(full)}

**Table 2. Historical subperiod, 2020–2025.**

{table(recent)}

![Fixed-rule comparison](plain_comparison.png)

*Figure 1. Annualized return, annualized volatility, and maximum drawdown. Scales are shared within each column. Drawdown is reported as a positive loss magnitude. The subperiod is contained in the full sample; these are not independent replications.*

Relative to trend timing in 2020–2025, volatility targeting changed annualized return by {(d.loc['vol','CAGR']-d.loc['trend','CAGR'])*100:+.2f} percentage points and reduced maximum drawdown by {(abs(d.loc['trend','MaxDrawdown'])-abs(d.loc['vol','MaxDrawdown']))*100:.2f} points. The combined rule returned {d.loc['combined','CAGR']:.2%} with a {abs(d.loc['combined','MaxDrawdown']):.2%} drawdown. The fixed 50% benchmark returned {d.loc['fixed_50','CAGR']:.2%} with an {abs(d.loc['fixed_50','MaxDrawdown']):.2%} drawdown. Lower exposure therefore remains an important alternative explanation for apparent risk reduction.

![Account paths](plain_journey.png)

*Figure 2. Existing strategy accounts rebased to USD 100,000 at year-end 2019, with subperiod drawdowns below. Rebased accounts retain prior holdings; they are not newly opened portfolios. The upper panel uses a linear scale.*

## 3. Rolling parameter selection

Each test year uses parameters selected from the preceding {cfg['walk_forward']['train_years']} calendar years. Nine combinations of moving-average length and volatility target are ranked by training-period net Sharpe ratio. Parameters are frozen for the next year; test holdings and trading costs carry across year boundaries. All comparison accounts below start from cash on the same first test date.

**Table 3. Walk-forward evaluation, 2015–2025.**

{table(wf_summary)}

The paired annualized mean daily-return difference between walk-forward allocation and fixed 50% exposure is {interval['annualized_mean_daily_difference']:.2%}. A circular block bootstrap ({interval['block_size']}-session blocks; {interval['repetitions']} replications) gives a 95% percentile interval of [{interval['lower_95']:.2%}, {interval['upper_95']:.2%}]. This interval concerns arithmetic mean returns, not CAGR. It neither corrects for multiple specification searches nor repeats parameter selection within each resample.

## 4. Interpretation and limitations

The reference results support volatility targeting as an exposure-control method, rather than evidence of return predictability. The trend filter does not consistently improve the return–drawdown trade-off, and rolling optimization does not outperform the simple fixed-weight benchmark. These conclusions are conditional on the instrument, sample, execution convention, and chosen parameters.

The study is retrospective. Rolling evaluation limits direct look-ahead in parameter selection but does not eliminate researcher selection bias. Historical volatility is not a loss bound. Cash returns, currency conversion, execution frictions, and alternative parameter choices may alter the comparison. The benchmarks are not exactly risk-matched, so performance differences do not identify a causal timing effect.

## Reproducibility

CAGR uses a 252-session annualization convention. Sharpe assumes a zero risk-free rate. Subperiod drawdowns reset the running peak at the subperiod boundary. Source hash: `{sha}`. The accompanying CSV files record metrics, candidate scores, selected parameters, and sensitivity results. Data provenance and software versions are recorded in `run_manifest.json`. See [methodology](../../docs/METHODOLOGY.md) and [references](../../docs/REFERENCES.md).
'''
    (out/'REPORT.md').write_text(text,encoding='utf-8')
