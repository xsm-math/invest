"""Generate reviewable markdown and figures directly from research output."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

NAMES={'buy_hold':'长期持有','fixed_50':'固定50%黄金','trend':'趋势择时','vol':'波动率控制',
       'combined':'趋势＋波动率','mean_reversion':'月度均值回归','walk_forward':'滚动选参组合'}

def table(df):
    lines=['| 策略 | 年化收益 | 年化波动 | 夏普 RF=0 | 最大回撤 | 年化换手 |',
           '|---|---:|---:|---:|---:|---:|']
    for _,r in df.iterrows():
        lines.append(f'| {NAMES.get(r.Strategy,r.Strategy)} | {r.CAGR:.2%} | {r.Volatility:.2%} | {r.Sharpe_RF0:.2f} | {r.MaxDrawdown:.2%} | {r.TurnoverAnnual:.2f} |')
    return '\n'.join(lines)

def plot(results,path,title):
    fig,ax=plt.subplots(2,1,figsize=(11,8),sharex=True,gridspec_kw={'height_ratios':[2,1]})
    for mode,d in results.items():
        ax[0].plot(d.index,d.nav,label=mode,lw=1.3)
        ax[1].plot(d.index,d.nav/d.nav.cummax().clip(lower=1)-1,lw=1)
    ax[0].set_yscale('log');ax[0].set_ylabel('NAV (log)');ax[0].set_title(title)
    ax[0].legend(ncol=3,fontsize=9);ax[1].set_ylabel('Drawdown')
    for a in ax:a.grid(alpha=.2)
    fig.tight_layout();fig.savefig(path,dpi=150);plt.close(fig)

def write_report(out,summary,wf_summary,folds,interval,cfg,sha):
    hold=summary[summary.Period=='2020-2025']; full=summary[summary.Period=='All']
    text=f'''# 黄金策略研究：模块化与滚动检验版

本报告由本次程序输出生成；价格截至 {cfg['end_exclusive']}（不含），数据 SHA256：`{sha}`。

## 研究方法

研究标的是美元黄金 ETF GLD，采用复权收盘价。预热数据从 2005 年开始，固定策略从 {cfg['start']} 开始。单边成本 {cfg['cost_bps']} bps，现金年利率假设 {cfg['cash_rate']:.2%}。不做空、不加杠杆、不模拟税收和整数份额限制。

所有策略使用同一月度执行规则：上一交易日形成信号，在每月首个交易日收盘调仓。旧份额承担成交日价格变化，新份额从成交后起作用；调仓成本根据漂移后的实际仓位计算。期末按市值计价，不假设清仓。

主模型：价格高于 {cfg['ma']} 日均线时，黄金仓位为 min(1, {cfg['target_vol']:.2%}/估计波动率)，否则为零；波动率由过去 {cfg['vol_window']} 日收益估计，估计值下限为1%。风险目标不是实际风险上限。

月度均值回归作为另一类假设：若收盘价的 {cfg['mr_window']} 日价格 z-score 小于 -{cfg['mr_entry']}，下次月度执行时持仓100%，否则空仓；中途不执行止损或回归均值退出。它是月度超跌配置，不是高频黄金交易系统。

## 固定策略结果

{table(full)}

### 2020—2025 历史分段

{table(hold)}

![固定策略](fixed_strategies.png)

这六个规则没有根据此表重新挑选参数。历史分段不是事前封存样本；新增均值回归是在已看过历史表现后提出，仍属于探索性分析。对比固定50%仓位有助于区分减少敞口与择时，但不构成严格的风险匹配或因果归因。

## 年度滚动选参

从 {cfg['walk_forward']['first_test_year']} 年开始，每年只使用过去 {cfg['walk_forward']['train_years']} 个自然年的数据，在9个趋势＋风险参数组合中选择训练期扣费夏普最高者，下一年冻结参数。训练模拟每次从现金启动，不收期末清仓费；测试组合跨年延续份额，并在下一年第一次月度执行时计入切换成本。

训练截止于上一年最后一个交易日；该日收盘后选择参数，使用该日信号于下一年首个交易日收盘成交。指标预热允许使用训练窗口前已知价格，训练打分仅用窗口内收益。并列时依次选择较小均线窗口、较低风险目标，规则明确可复现。

下列基准和滚动策略均在首次测试日从现金启动，均计入初始买入费用，不拼接每年重置为1的净值。

{table(wf_summary)}

![滚动选参](walk_forward.png)

完整参数选择见 walk_forward_folds.csv；每年全部候选分数见 training_candidates.csv。下一年的历史会在再下一次训练时变为可用数据，这符合滚动过程；不能因此将整个测试序列描述为一直未见的单一封存样本。

## 不确定性

滚动策略相对固定50%基准的“平均日收益差×252”为 {interval['annualized_mean_daily_difference']:.2%}。配对循环区块 bootstrap 的95%百分位区间为 [{interval['lower_95']:.2%}, {interval['upper_95']:.2%}]，区块长度 {interval['block_size']}，重复 {interval['repetitions']} 次，随机种子 {interval['seed']}。

这是收益差均值的不确定性描述，不是 CAGR 差的区间，不是盈利概率。区块法依赖近似平稳假设，没有校正多次尝试，也没有在每次重采样中重跑选参；不能据此证明未来存在显著超额收益。

## 审计与局限

每个策略输出逐日净值、信号、目标仓位、真实仓位、份额、现金及成交金额；trades/ 记录实际非零调仓，而非虚构成一笔笔完整开平仓胜率。源数据哈希和实际依赖版本见 run_manifest.json。

参数敏感性在历史2020—2025阶段事后展示，不能再以最优参数冒充独立测试。成本敏感性针对固定组合模型；改变成本后滚动选参需另行完整重跑。现金假设为常数，没有替代为实际历史短债工具。价格未做第二来源核验，收盘价成交与滑点是简化。GLD不直接代表人民币黄金ETF、期货展期或现货保证金产品。

本次新增方法参考公开项目的模块拆分、walk-forward 和研究记录方式，代码独立实现。来源、阅读范围和固定提交号见 ../../docs/REFERENCES.md 与 reference_manifest.json。没有复制参考仓库的收益声明，也没有将历史研究说成实盘业绩。
'''
    (out/'REPORT.md').write_text(text,encoding='utf-8')
