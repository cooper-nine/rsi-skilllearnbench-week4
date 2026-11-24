# Qwen 3.5 Plus 单题编排复测

**10/10 整题通过。本轮续跑的八题有 8/8 整题通过。**

原人工 Skill 基线均未整题通过。整题通过依据原版 Docker test.sh 的正常退出、reward=1 和完整官方报告。节点检查点数量单列，区分官方产物判定与实际编排执行。此前的确定性修复没有计入此表。

| 同一输入的题目 | 基线试次 | Qwen 官方判定 | 官方检查 | 已记录的节点检查点 |
| --- | --- | --- | --- | ---: |
| [earthquake-plate-calculation-5](qwen-pilot/earthquake-plate-calculation-5/) | [20261118-122708-583ff7](paired-evidence/earthquake-plate-calculation-5/baseline/) · 6/8 · 失败 | 通过 | 8/8 | 4 |
| [financial-analysis-1](qwen-pilot/financial-analysis-1/) | [20261118-114709-707627](paired-evidence/financial-analysis-1/baseline/) · 1/2 · 失败 | 通过 | 2/2 | 3 |
| [financial-analysis-3](qwen-pilot/financial-analysis-3/) | [20261118-123134-1043bc](paired-evidence/financial-analysis-3/baseline/) · 0/2 · 失败 | 通过 | 2/2 | 3 |
| [weighted-gdp-calculation-1](qwen-pilot/weighted-gdp-calculation-1/) | [20261118-124901-2690d3](paired-evidence/weighted-gdp-calculation-1/baseline/) · 11/27 · 失败 | 通过 | 27/27 | 4 |
| [weighted-gdp-calculation-5](qwen-pilot/weighted-gdp-calculation-5/) | [20261118-150937-21cedf](paired-evidence/weighted-gdp-calculation-5/baseline/) · 21/25 · 失败 | 通过 | 25/25 | 4 |
| [weighted-gdp-calculation-4](qwen-pilot/weighted-gdp-calculation-4/) | [20261118-140525-7fb55f](paired-evidence/weighted-gdp-calculation-4/baseline/) · 10/27 · 失败 | 通过 | 27/27 | 0 |
| [stock-data-visualization-1](qwen-pilot/stock-data-visualization-1/) | [20261118-134937-19d1a4](paired-evidence/stock-data-visualization-1/baseline/) · 14/15 · 失败 | 通过 | 15/15 | 4 |
| [stock-data-visualization-2](qwen-pilot/stock-data-visualization-2/) | [20261118-141811-3aa771](paired-evidence/stock-data-visualization-2/baseline/) · 11/15 · 失败 | 通过 | 15/15 | 4 |
| [stock-data-visualization-3](qwen-pilot/stock-data-visualization-3/) | [20261118-145831-ff084f](paired-evidence/stock-data-visualization-3/baseline/) · 6/15 · 失败 | 通过 | 15/15 | 4 |
| [stock-data-visualization-4](qwen-pilot/stock-data-visualization-4/) | [20261118-152648-61d383](paired-evidence/stock-data-visualization-4/baseline/) · 8/16 · 失败 | 通过 | 16/16 | 4 |

GDP 第 4 题沿用早先的同模型平台试次。该次运行记录节点推进，早于新版 JSON 检查点协议。地震第 5 题为已验证的 JSON 检查点试点。

截图从临时 RSI Flow Visual 前端取得，展示运行配置。Qwen API 试次由本地运行器启动。运行器传递节点产物、执行模型生成的代码或应用模型提出的编辑。前端画布点击执行尚未验证。 [四类画布截图](qwen-canvas/)

## 编排设计与失败回退

用户确认了四类节点顺序和定向回退规则。每一步检查交给下一步的产物，发现问题就回到产生该产物的节点。

- 地震：先按题意筛选事件、确认板块，再测距。选中的事件不变时，可以只重算距离。
- 金融：先找到每个基金在正确季度的申报编号，再按同一口径算金额和排名。基金选错时，后面的数字再精确也会答错题。
- GDP：先读模板和单元格范围，再写公式，最后重算并检查错误。公式出了问题，可以保留已确认的数据范围和工作簿格式。
- 股票：先读数据、渲染页面，再检查鼠标交互。页面能打开时，提示框出错可以定位到字段映射或交互状态。

节点产物检查只决定编排下一步。每题链接提供所选试次的官方报告、奖励、编排配置和已记录的节点输出。试次索引保留分数、失败项和运行中断。

新题只要沿用相同输入类型与交付形式，就可以复用节点分工。需要替换的是题目输入和契约中的字段或范围，这轮覆盖了四类中的多个同类题。下一阶段可让模型起草同样的节点契约和回退分支，以同一批输入和原版 verifier 验证。每次人工修改节点、修正产物或手工触发重试分别计一次干预。先实测当前每题干预次数，再以整题 10/10 为前提比较自动生成后的总次数和中位数，目标是每题零人工重试。

## 试次边界

AI 协助把用户确认的结构接入运行器、根据节点失败诊断数据和公式问题，并整理证据。Qwen 完成节点动作，官方脚本独立验收。报告保留未通过和中断试次。

股票第 2 题的早期草稿把 sector 为 ETF 的记录当作普通股票。Qwen 修正字段映射后，同一产物由官方脚本补跑判分。后续试次补齐 CSS 可见状态和第四个 Qwen 检查点。早期的模型自检 JSON 错误保存在试次记录。

金融第 1 题早期选错 Renaissance 申报记录。第 3 题先混淆了 Soros 的名称，后又把 NVIDIA 发行人搜索限在一个基金的持仓里。后续保留已验证的申报编号，并从全季度持仓查发行人、按申报编号汇总排名。两题最后各通过 2/2。

GDP 第 1 题逐步从 25/27 到 26/27，再到 27/27。更换不兼容函数后，旧的 #NAME? 缓存还在。清除后，读取缓存的官方检查得到空值；最终将实际重算结果写回十个分位数公式的缓存，保留原公式和格式。
