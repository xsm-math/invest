# Gold Strategy Research · 黄金投资模型与策略研究

A reproducible research project for monthly gold allocation, with explicit execution timing, transaction costs, and rolling out-of-sample evaluation.

**研究问题：黄金趋势择时和波动率控制，是否优于简单持有或固定仓位？**

本项目使用2005—2025年的GLD日频历史数据，比较六种固定规则，并进行“过去五年训练、下一年测试”的年度滚动选参。结论保留失败结果：复杂规则没有稳定优于简单基准。仅用于历史研究与学习，不是实盘交易程序。

[完整研究报告](reports/reference/REPORT.md) · [数学与记账方法](docs/METHODOLOGY.md) · [GitHub参考来源](docs/REFERENCES.md) · [学习Notebook](notebooks/research_walkthrough.ipynb)

![年度滚动验证](reports/reference/walk_forward.png)

## 已实现

- 数据下载、严格校验、原始响应存档与SHA256复现记录。
- 长期持有、50%固定配置、趋势、波动率控制、组合规则、月度z-score均值回归。
- 逐日份额＋现金账户、下一交易日收盘执行、真实仓位漂移与精确手续费。
- 年度滚动选参、连续测试净值、每折候选分数与参数选择记录。
- 参数及成本敏感性、配对区块bootstrap区间、逐日及调仓日志。
- 自动生成中文研究报告、图表；11项离线测试；GitHub Actions测试配置。

## 关键结果

下表为2015—2025年，四个账户都从同一天现金启动；单边成本10bps、现金收益0、不加杠杆。

| 策略 | 年化收益 | 年化波动 | 最大回撤 |
|---|---:|---:|---:|
| 长期持有GLD | 12.00% | 14.74% | 22.00% |
| 固定50%黄金＋50%现金 | 6.10% | 7.42% | 11.29% |
| 固定趋势＋波动率 | 5.09% | 9.12% | 23.84% |
| 五年滚动选参组合 | 4.33% | 8.33% | 20.63% |

**滚动选参没有改善收益，也没有胜过固定50%配置的回撤。**这比只展示一条盈利净值更有研究价值：降低风险敞口、择时有效性与参数过拟合是不同问题。历史年化收益差不是未来收益承诺。

完整固定策略比较、参数轨迹和区间估计见报告；此结果来自本仓库实际运行，不来自参考项目。历史滚动测试不等于真正事前封存或实盘验证。

## 快速开始

建议Python 3.10或更新版本，在仓库根目录执行：

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -e .
python -m gold_research download
python -m gold_research run
python -m unittest discover -s tests -v
```

若使用附带本地数据的个人下载包，可跳过download。Git仓库不包含原始行情，需自行下载；接口失败会明确报错，不会切换为合成数据。测试只用明确标注的合成路径，无需行情或网络。

默认输出到`reports/generated/`，不覆盖已提交的参考结果。`configs/default.json`保存实验参数；从仓库根目录运行，路径相对于当前目录。

```bash
python -m gold_research run --config configs/default.json --out reports/generated
```

参考结果的精确依赖版本见`reports/reference/run_manifest.json`。依赖范围用于安装兼容版本，不是完整环境锁文件。若行情供应商修订历史，重新下载的哈希和结果可能不同。

## 仓库结构

| 路径 | 内容 |
|---|---|
| `src/gold_research/data.py` | 下载与数据校验 |
| `src/gold_research/strategies.py` | 未滞后的收盘目标信号 |
| `src/gold_research/engine.py` | 统一信号滞后与自融资记账 |
| `src/gold_research/walkforward.py` | 训练窗口、选参、跨年信号衔接 |
| `src/gold_research/pipeline.py` | 一键完整实验 |
| `src/gold_research/reporting.py` | 从结果生成报告与图表 |
| `src/gold_research/uncertainty.py` | 探索性配对区块bootstrap |
| `tests/` | 会计、未来信息隔离与滚动边界测试 |
| `notebooks/` | 适合逐步阅读的研究入口 |
| `reports/reference/` | 本次已运行的汇总结果与图表 |
| `configs/`、`docs/` | 参数、方法、来源及研究边界 |

## 模型与成交规则

主模型目标权重：`趋势为正 × min(1, 10% / 60日年化波动率)`。趋势为价格高于200日均线；估计波动下限1%。均值回归采用20日价格z-score低于-1.5时配置100%，否则0%。所有动态策略月度执行，非日内止损系统。

月末信号在下月首个交易日收盘成交；成交日价格变化仍由原持仓承担。基金费用不重复扣除，另计单边佣金/价差/滑点合并假设。模型不含税收、实际现金利率、期货展期或人民币汇率。

## 复现与真实性

11项测试已在本地Python3.12通过；远端Actions状态以实际运行页面为准。测试包含：未来价格不改变过去账户、未来测试年不改变训练选参、跨年第一笔调仓使用新参数、单一候选的滚动净值与连续固定策略一致。

参考了公开GitHub项目的研究组织方式和常见方法，代码独立实现，详见来源文档。没有复制未授权源码、夸大收益或将研究写成实盘业绩。未为第三方数据或参考项目授予许可证。
