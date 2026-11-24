# Qwen 3.5 Plus 单题编排复测

**6/10 整题通过。本轮续跑的八题有 4/8 整题通过。**

原人工 Skill 基线均未整题通过。整题通过依据原版 Docker test.sh 的正常退出、reward=1 和完整官方报告。节点检查点数量单列，区分官方产物判定与实际编排执行。此前的确定性修复没有计入此表。

| 同一输入的题目 | 基线试次 | Qwen 官方判定 | 官方检查 | 已记录的节点检查点 |
| --- | --- | --- | --- | ---: |
| [earthquake-plate-calculation-5](qwen-pilot/earthquake-plate-calculation-5/) | 20261118-122708-583ff7 · 失败 | 通过 | 8/8 | 4 |
| [financial-analysis-1](qwen-pilot/financial-analysis-1/) | 20261118-114709-707627 · 失败 | 未通过 | 1/2 | 3 |
| [financial-analysis-3](qwen-pilot/financial-analysis-3/) | 20261118-123134-1043bc · 失败 | 未通过 | 1/2 | 3 |
| [weighted-gdp-calculation-1](qwen-pilot/weighted-gdp-calculation-1/) | 20261118-124901-2690d3 · 失败 | 未通过 | 25/27 | 4 |
| [weighted-gdp-calculation-5](qwen-pilot/weighted-gdp-calculation-5/) | 20261118-150937-21cedf · 失败 | 通过 | 25/25 | 4 |
| [weighted-gdp-calculation-4](qwen-pilot/weighted-gdp-calculation-4/) | 20261118-140525-7fb55f · 失败 | 通过 | 27/27 | 0 |
| [stock-data-visualization-1](qwen-pilot/stock-data-visualization-1/) | 20261118-134937-19d1a4 · 失败 | 通过 | 15/15 | 4 |
| [stock-data-visualization-2](qwen-pilot/stock-data-visualization-2/) | 20261118-141811-3aa771 · 失败 | 未通过 | 14/15 | 4 |
| [stock-data-visualization-3](qwen-pilot/stock-data-visualization-3/) | 20261118-145831-ff084f · 失败 | 通过 | 15/15 | 4 |
| [stock-data-visualization-4](qwen-pilot/stock-data-visualization-4/) | 20261118-152648-61d383 · 失败 | 通过 | 16/16 | 4 |

GDP 第 4 题沿用早先的同模型平台试次。该次运行记录节点推进，早于新版 JSON 检查点协议。地震第 5 题为已验证的 JSON 检查点试点。

截图从临时 RSI Flow Visual 前端取得，展示运行配置。实际 API 试次由本地运行器启动，前端画布点击执行尚未验证。 [四类画布截图](qwen-canvas/)

## 编排设计与失败回退

用户确认了四类节点顺序以及产物校验后的定向回退。每个节点只交接下游需要的结果。例如股票先生成页面，再测试鼠标交互；页面能打开时，提示框出错只需修交互节点。GDP 校验公式时保留原始工作簿格式；金融计算前先核对基金申报编号，避免用对公式却算错基金。

节点产物检查只决定编排下一步。每题链接提供所选试次的官方报告、奖励、编排配置和已记录的节点输出。试次索引保留分数、失败项和运行中断。

下一阶段可让模型起草同样的节点契约和回退分支，以同一批输入和原版 verifier 验证。每次人工修改节点、修正产物或手工触发重试分别计一次干预。先实测当前每题干预次数，再以整题 10/10 为前提比较自动生成后的总次数和中位数，目标是每题零人工重试。
