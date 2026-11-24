# 产物校验与定向回退复测

用户确认沿用原十题，在原有检查节点校验产物，失败回到相应生成节点。以原版官方 test.sh 及其整题奖励为验收依据。初版与追加批次的逐题结果分别留存。 同一批十题目前有 7/10 道留下了平台运行及官方整题通过的证据。

| 案例 | 人工 Skill 基线 | 追加验证 |
| --- | --- | --- |
| earthquake-plate-calculation-5 | [失败](paired-evidence/earthquake-plate-calculation-5/baseline/) | [通过](artifact-repair/earthquake-plate-calculation-5/) |
| financial-analysis-1 | [失败](paired-evidence/financial-analysis-1/baseline/) | [失败](artifact-repair/financial-analysis-1/) |
| financial-analysis-3 | [失败](paired-evidence/financial-analysis-3/baseline/) | [通过](artifact-repair/financial-analysis-3/) |
| weighted-gdp-calculation-1 | [失败](paired-evidence/weighted-gdp-calculation-1/baseline/) | [失败](artifact-repair/weighted-gdp-calculation-1/) |
| weighted-gdp-calculation-5 | [失败](paired-evidence/weighted-gdp-calculation-5/baseline/) | [失败](artifact-repair/weighted-gdp-calculation-5/) |
| weighted-gdp-calculation-4 | [失败](paired-evidence/weighted-gdp-calculation-4/baseline/) | 沿用[已通过的原平台试次](paired-evidence/weighted-gdp-calculation-4/) |
| stock-data-visualization-1 | [失败](paired-evidence/stock-data-visualization-1/baseline/) | [通过](artifact-repair/stock-data-visualization-1/) |
| stock-data-visualization-2 | [失败](paired-evidence/stock-data-visualization-2/baseline/) | [通过](artifact-repair/stock-data-visualization-2/) |
| stock-data-visualization-3 | [失败](paired-evidence/stock-data-visualization-3/baseline/) | [通过](artifact-repair/stock-data-visualization-3/) |
| stock-data-visualization-4 | [失败](paired-evidence/stock-data-visualization-4/baseline/) | [通过](artifact-repair/stock-data-visualization-4/) |

股票流程共用渲染和交互代码，按各题原始 CSV、JSON 或 TSV 切换输入。气泡提示框的可见状态与辅助技术状态一起更新。地震流程按入选板块计算测距，并用板块多边形和边界线段交叉复核。

Spring Boot 后端发起修复，容器回传节点事件、产物摘要和官方判分。前端画布的人工编辑记录及 H0 干预次数有待另行采集。
