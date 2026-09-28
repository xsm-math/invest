"""Explicit research question and numerical comparisons from measured metrics."""
from .reporting import NAMES


def comparison(summary, cfg):
    def rows(period):
        return summary[summary.Period == period].set_index('Strategy')
    def table(period):
        df = rows(period)
        lines = ['| 策略 | 年化收益 | 年化波动率 | 最大回撤幅度 | 夏普 RF=0 | 平均黄金仓位 |',
                 '|---|---:|---:|---:|---:|---:|']
        for mode in ['buy_hold', 'trend', 'vol', 'combined', 'fixed_50']:
            r = df.loc[mode]
            lines.append(f'| {NAMES[mode]} | {r.CAGR:.2%} | {r.Volatility:.2%} | {abs(r.MaxDrawdown):.2%} | {r.Sharpe_RF0:.2f} | {r.AvgWeight:.2%} |')
        return '\n'.join(lines)
    def delta(period, a, b):
        df = rows(period); x, y = df.loc[a], df.loc[b]
        return (f'| {NAMES[a]} − {NAMES[b]} | {(x.CAGR-y.CAGR)*100:+.2f} | '
                f'{(x.Volatility-y.Volatility)*100:+.2f} | '
                f'{(abs(x.MaxDrawdown)-abs(y.MaxDrawdown))*100:+.2f} | '
                f'{x.Sharpe_RF0-y.Sharpe_RF0:+.2f} |')
    pairs = [('trend','buy_hold'),('vol','buy_hold'),('vol','trend'),('combined','vol'),('combined','fixed_50')]
    delta_header = ['| 比较（前者减后者） | 收益差（百分点） | 波动差（百分点） | 回撤幅度差（百分点） | 夏普差 |',
                    '|---|---:|---:|---:|---:|']
    recent = rows('2020-2025'); full = rows('All')
    def verdict(condition):
        return '满足' if condition else '不满足'
    trend_test = all(df.loc['trend','CAGR'] >= df.loc['buy_hold','CAGR'] and
                     abs(df.loc['trend','MaxDrawdown']) < abs(df.loc['buy_hold','MaxDrawdown'])
                     for df in (full,recent))
    vol_test = all(df.loc['vol','Volatility'] < df.loc['buy_hold','Volatility'] and
                   abs(df.loc['vol','MaxDrawdown']) < abs(df.loc['buy_hold','MaxDrawdown'])
                   for df in (full,recent))
    combined_test = all(df.loc['combined','CAGR'] >= df.loc['vol','CAGR'] and
                        abs(df.loc['combined','MaxDrawdown']) < abs(df.loc['vol','MaxDrawdown'])
                        for df in (full,recent))
    examples=[]
    for sigma in [.08,.10,.15,.20,.30]:
        allocation=min(1,cfg['target_vol']/max(sigma,.01))
        examples.append(f'| {sigma:.0%} | {allocation:.2%} | 100% / 0% | {allocation:.2%} / 0% |')
    return f'''## 1. 明确研究问题

**对美元黄金ETF GLD，在相同数据、月度成交规则和交易成本下，200日趋势择时与10%目标波动率控制，谁更能降低风险？降低风险牺牲了多少收益？把两者叠加是否值得？**

主比较使用2007—2025年全样本；2020—2025年单独作为近期历史分段检查，两个区间分别列示，不混用数字。这里的“近期”仅指截至2025年的研究分段，不是当前行情。明确三个判断标准：

1. **趋势择时**：是否在年化收益不低于满仓持有的同时，降低最大回撤？
2. **波动率控制**：是否同时降低年化波动率和最大回撤？同时单独报告收益代价，不将降仓位说成超额收益。
3. **叠加趋势过滤**：相对单独波动率控制，是否在不降低年化收益的同时进一步降低最大回撤？

这是本次报告明确化后的描述性评价标准，不是事前登记的统计假设，也不是唯一可能的投资目标。

## 2. 两种方法的明确数字

| 项目 | 趋势择时（trend） | 波动率控制（vol） |
|---|---|---|
| 输入 | 收盘价与过去{cfg['ma']}个交易日均价 | 过去{cfg['vol_window']}个日收益的样本标准差×√252 |
| 触发或目标 | 收盘价严格高于均价才持有 | 目标年化波动率{cfg['target_vol']:.0%} |
| 目标黄金仓位 | 高于均价100%；低于或等于均价0% | min(100%, {cfg['target_vol']:.0%}/max(估计波动率,1%)) |
| 是否判断涨跌方向 | 是 | 否，无论趋势正负都按风险分配仓位 |
| 杠杆与现金 | 无杠杆；未投部分为现金 | 无杠杆；未投部分为现金 |

组合策略（combined）=趋势开关×波动率控制仓位。以下是**规则计算示例，不是实际回测业绩**；斜杠前后分别表示趋势为正/非正：

| 估计年化波动率 | 仅波动率控制 | 仅趋势择时（正/非正） | 组合策略（正/非正） |
|---|---:|---:|---:|
{chr(10).join(examples)}

共同条件：每月首个交易日收盘执行上一交易日信号，单边成本{cfg['cost_bps']:g}bps（{cfg['cost_bps']/100:.2f}%），现金年收益假设{cfg['cash_rate']:.0%}。持有期间仓位会自然漂移，目标仓位不等于每天的实际仓位。满仓基准只首次买入；固定50%基准每月恢复50%仓位。

**10%是仓位计算目标，不是实际波动率的保证上限。**收益率以美元计，最大回撤以下统一显示正的损失幅度，越小越好；夏普采用零无风险利率。

## 3. 先看全样本：2007—2025

{table('All')}

{chr(10).join(delta_header + [delta('All',a,b) for a,b in pairs])}

## 4. 再看近期分段：2020—2025

{table('2020-2025')}

{chr(10).join(delta_header + [delta('2020-2025',a,b) for a,b in pairs])}

差值由未四舍五入的原始指标计算。收益差为负表示少赚，波动差/回撤幅度差为负表示风险更低。“百分点”是两个百分率的差，不是相对下降百分比。两段并不独立：2020—2025包含在全样本中。

## 5. 明确结论

- **趋势择时：{verdict(trend_test)}本报告的收益不降且回撤下降标准。**全样本收益{full.loc['trend','CAGR']:.2%}、回撤{abs(full.loc['trend','MaxDrawdown']):.2%}；近期收益{recent.loc['trend','CAGR']:.2%}、回撤{abs(recent.loc['trend','MaxDrawdown']):.2%}。不能只凭全样本回撤改善就认为200日趋势过滤有效，必须同时看近期和收益代价。
- **波动率控制：{verdict(vol_test)}两个区间均降低波动和回撤的风险控制标准。**近期相对趋势择时少赚{(recent.loc['trend','CAGR']-recent.loc['vol','CAGR'])*100:.2f}个百分点年化收益，但最大回撤幅度减少{(abs(recent.loc['trend','MaxDrawdown'])-abs(recent.loc['vol','MaxDrawdown']))*100:.2f}个百分点；相对满仓持有少赚{(recent.loc['buy_hold','CAGR']-recent.loc['vol','CAGR'])*100:.2f}个百分点。因此它体现的是风险与收益的取舍，不是更高收益。
- **趋势＋波动率：{verdict(combined_test)}相对单独波动率控制的收益不降且回撤进一步下降标准。**近期组合年化收益{recent.loc['combined','CAGR']:.2%}，低于单独控制的{recent.loc['vol','CAGR']:.2%}；回撤{abs(recent.loc['combined','MaxDrawdown']):.2%}，高于单独控制的{abs(recent.loc['vol','MaxDrawdown']):.2%}。更低的日常波动不保证更浅的累计回撤。
- **简单仓位基准不能省略。**近期固定50%黄金的收益{recent.loc['fixed_50','CAGR']:.2%}、回撤{abs(recent.loc['fixed_50','MaxDrawdown']):.2%}，组合策略对应{recent.loc['combined','CAGR']:.2%}、{abs(recent.loc['combined','MaxDrawdown']):.2%}。仓位暴露不同，不能把差异当成严格风险匹配后的因果证明，但足以要求复杂模型解释其额外价值。

**就本次既定参数和历史样本：若研究目标是降低黄金持仓风险，单独波动率控制比200日趋势择时更有支持；没有证据支持再叠加该趋势过滤来改善收益—回撤组合。若目标仅为历史最高收益，满仓持有在以上比较中更高，但承担了更大风险。**这不是未来收益预测，也没有证明其他趋势参数、成交频率或市场会有相同结论。
'''
