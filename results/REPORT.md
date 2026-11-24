# 第四周复测报告

十题均从人工 Skill 失败组中选出。主批次已获得 10/10 题判定，整题通过 1 题。主批次整题修复率为 1/10（10%）。

## 逐题结果

| 任务 | 人工 Skill 基线 | 编排后 | 整题判定 |
| --- | ---: | ---: | --- |
| [地震板块 5](paired-evidence/earthquake-plate-calculation-5/) | 6/8 | 7/8 | 失败，外层超时 |
| [金融分析 1](paired-evidence/financial-analysis-1/) | 1/2 | 1/2 | 失败 |
| [金融分析 3](paired-evidence/financial-analysis-3/) | 0/2 | 1/2 | 失败 |
| [加权 GDP 1](paired-evidence/weighted-gdp-calculation-1/) | 11/27 | 13/27 | 失败 |
| [加权 GDP 5](paired-evidence/weighted-gdp-calculation-5/) | 21/25 | 11/25 | 失败 |
| [加权 GDP 4](paired-evidence/weighted-gdp-calculation-4/) | 10/27 | 27/27 | 通过 |
| [股票可视化 1](paired-evidence/stock-data-visualization-1/) | 14/15 | 8/15 | 失败 |
| [股票可视化 2](paired-evidence/stock-data-visualization-2/) | 11/15 | 8/15 | 失败 |
| [股票可视化 3](paired-evidence/stock-data-visualization-3/) | 6/15 | 8/15 | 失败 |
| [股票可视化 4](paired-evidence/stock-data-visualization-4/) | 8/16 | 15/16 | 失败 |

## 运行分析

- 在前后检查总数一致的 10 题中，通过项增加 6 题，持平 1 题，减少 3 题。
- 沿用的模型步数上限为 100。已收集的主批次轨迹中，7 题触及上限且模型未在上限内正常结束。整题判定依据实际产物和官方 verifier。
- 金融题的主要失败点是持仓数量口径和变化排序。GDP 题的失败集中在数据查找、公式计算和统计。股票题的失败断言涉及输出结构、图表渲染、数据和交互。逐项断言可查 CSV 及 CTRF。 [逐题对照](comparison.csv)
- 每个任务族复用一份流程，题目和数据由原基准实例切换。用户确认了四类顺序及命令失败恢复规则。Spring Boot FlowEngine 发起复测，子阶段在容器内运行。 [平台证据](PLATFORM.md)

## 追加地震验证

题干和输出字段指定了不同的测距参照。用确定性计算脚本复核入选板块边缘，得到 419.32 km，官方判题 8/8，reward=1。 [计算和官方判分](diagnostics/earthquake-5/)

两次平台追加试次保持同一题、模型、预算与节点顺序。先在筛选和测距阶段补充题意冲突处理规则，再把同一规则前移到准备阶段，两次均为 7/8，reward=0。模型输出的距离仍为 1732.30 km。主批次保留初版结果。 [阶段内提示](refinement/earthquake-5-stage-guidance/) · [准备阶段提示](refinement/earthquake-5/)

## 验收与贡献

- 模型为 Qwen 3.5 Plus，沿用 budget-v3。处理组向模型按阶段提供原人工 Skill 内容，并对命令错误提供一次恢复提示。各次运行记录保留实际参数和流程哈希。
- 完整且非空的官方 CTRF、所有检查通过、reward=1 和 verifier 正常退出共同构成整题通过。GDP 第 1 题用已保存的同一工作簿恢复判分，首次环境错误与重判记录均保留。 [官方判分档案](paired-evidence/)
- 十题的 32 个原始题面和 verifier 文件均逐文件核对 Git blob，与固定提交完全一致。 [上游记录](../upstream-reference/source.json)
- 用户确认流程顺序和回退规则。AI 协助实施流程适配、复测与证据整理。平台画布交互记录、人工干预基线 H0 和改进后的干预次数尚未采集。
