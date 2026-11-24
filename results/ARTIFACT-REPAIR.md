# 产物校验与定向回退复测

用户确认沿用原十题，在原有检查节点校验产物，失败回到相应生成节点。以原版官方 test.sh 及其整题奖励为验收依据。初版与追加批次的逐题结果分别留存。 同一批十题目前有 10/10 道留下了平台运行及官方整题通过的证据。

| 案例 | 人工 Skill 基线 | 追加验证 |
| --- | --- | --- |
| earthquake-plate-calculation-5 | [失败](paired-evidence/earthquake-plate-calculation-5/baseline/) | [通过](artifact-repair/earthquake-plate-calculation-5/) |
| financial-analysis-1 | [失败](paired-evidence/financial-analysis-1/baseline/) | [通过](artifact-repair/financial-analysis-1/) |
| financial-analysis-3 | [失败](paired-evidence/financial-analysis-3/baseline/) | [通过](artifact-repair/financial-analysis-3/) |
| weighted-gdp-calculation-1 | [失败](paired-evidence/weighted-gdp-calculation-1/baseline/) | [通过](artifact-repair/weighted-gdp-calculation-1/) |
| weighted-gdp-calculation-5 | [失败](paired-evidence/weighted-gdp-calculation-5/baseline/) | [通过](artifact-repair/weighted-gdp-calculation-5/) |
| weighted-gdp-calculation-4 | [失败](paired-evidence/weighted-gdp-calculation-4/baseline/) | 沿用[已通过的原平台试次](paired-evidence/weighted-gdp-calculation-4/) |
| stock-data-visualization-1 | [失败](paired-evidence/stock-data-visualization-1/baseline/) | [通过](artifact-repair/stock-data-visualization-1/) |
| stock-data-visualization-2 | [失败](paired-evidence/stock-data-visualization-2/baseline/) | [通过](artifact-repair/stock-data-visualization-2/) |
| stock-data-visualization-3 | [失败](paired-evidence/stock-data-visualization-3/baseline/) | [通过](artifact-repair/stock-data-visualization-3/) |
| stock-data-visualization-4 | [失败](paired-evidence/stock-data-visualization-4/baseline/) | [通过](artifact-repair/stock-data-visualization-4/) |

股票流程共用渲染和交互代码，按各题原始 CSV、JSON 或 TSV 切换输入。气泡提示框的可见状态与辅助技术状态一起更新。地震流程按入选板块计算测距，并用板块多边形和边界线段交叉复核。

Spring Boot 后端发起修复，容器回传节点事件、产物摘要和官方判分。前端画布的人工编辑记录及 H0 干预次数有待另行采集。

## 失败回退记录

- 金融第 1 题的正常申报修订标记为空，早期筛选漏掉申报。计算节点改为排除明确标为修订的记录，并验证申报编号在持仓表中存在。金融第 3 题复用同一持仓分类、季度差值和申报机构排序。
- GDP 第 1、5 题的模板年份行为空。计算节点从 Data 页恢复年份引用所需的表头，并保留 Task 页原有行号和样式，使公式及官方重算后的坐标一致。
- 原命令行或平台试次失败仍保留在主批次报告。追加通过采用确定性代码执行已确认的编排，结果按官方整题通过计入。
- 人工决定为原十题、检查产物和定向回退。AI 实现修复模块，并以原版官方判题和平台启动回执核实。下一阶段的干预次数测量方式见[方案](../docs/artifact-repair.md)。
