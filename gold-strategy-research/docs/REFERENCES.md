# GitHub 参考与实现边界

检索及阅读日期：2026-09-28。固定提交号见 reference_manifest.json。以下项目是方法与组织方式的参考，不代表经过本项目验证的盈利系统。

| 项目 | 实际阅读 | 借鉴方式 | 本项目实现差异 |
|---|---|---|---|
| [lucienismael/algorithmic-trading-backtester](https://github.com/lucienismael/algorithmic-trading-backtester) | README、strategy.py、walk_forward.py | 数据、策略、账户与评价分离；均线与价格 z-score 策略；训练选参再测试 | 独立实现只做多的月度配置；五年滚动窗口；测试持仓连续；保留预热数据；所有交易由统一账户模型处理 |
| [codewithpom/GOLD-START](https://github.com/codewithpom/GOLD-START) | README、data_prep.py | 明确时间折叠、研究配置、自动化检验、结果文档化 | 使用日频 GLD 而非五分钟 XAUUSD；小参数网格而非大规模 Optuna 搜索；不采用其自动定时寻优或收益目标 |

GitHub API 在检索时未识别这两个仓库的许可证。这里只参考常见方法和设计思路，未复制源代码；没有给参考项目重新授权。新实现延续本项目上一版的原创回测代码。仓库也不沿用任何第三方收益、胜率或“生产可用”声明。

方法层面：200日趋势、历史波动率缩放、价格z-score和滚动检验都是常见研究工具，引用上述仓库不意味着这些方法最初由其提出。本项目没有复现参考仓库的完整实验，也不声称达到同等结果。

数据参考：[GLD 官方产品页](https://www.spdrgoldshares.com/usa/gld/)。价格通过 Yahoo Finance 公开历史接口获取；详见 data/README.md。CI 结构参考 [GitHub 官方 Python 工作流文档](https://docs.github.com/en/actions/tutorials/build-and-test-code/python)。
