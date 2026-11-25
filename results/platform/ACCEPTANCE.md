# 原平台验收

**完整验收通过 7/10。** 验收使用上周原人工 Skill 基线、同一任务输入和未改动的官方 verifier。完整通过要求原平台提交的流程留下每个业务节点的 Qwen 记录，并得到官方 PASS。

| 任务 | 基线检查 | 平台复测检查 | 验收 | 证据 |
| --- | ---: | ---: | --- | --- |
| earthquake-plate-calculation-5 | 6/8 | 8/8 | 通过 | [平台记录](../platform/canvas-retries/b8003ff6-204f-4008-8d6c-72aad006bbbd/earthquake-plate-calculation-5/) |
| financial-analysis-1 | 1/2 | 2/2 | 通过 | [平台记录](../platform/finance-1/) |
| financial-analysis-3 | 0/2 | 2/2 | 通过 | [平台记录](../platform/finance-3/) |
| weighted-gdp-calculation-1 | 11/27 | 15/27 | 未通过 | [平台记录](../platform/canvas-retries/e0201826-a5af-4e45-966e-da1873ecffdf/weighted-gdp-calculation-1/) |
| weighted-gdp-calculation-5 | 21/25 | 12/25 | 未通过 | [平台记录](../platform/canvas-retries/cdee63ab-6d1e-44bc-8ff7-d95a4b6e362a/weighted-gdp-calculation-5/) [原始输入执行](../platform/canvas-retries/e0201826-a5af-4e45-966e-da1873ecffdf/weighted-gdp-calculation-5/run.json) |
| weighted-gdp-calculation-4 | 10/27 | 13/27 | 未通过 | [平台记录](../platform/canvas-retries/e0201826-a5af-4e45-966e-da1873ecffdf/weighted-gdp-calculation-4/) |
| stock-data-visualization-1 | 14/15 | 15/15 | 通过 | [平台记录](../platform/canvas-retries/025b47f6-e47d-49f4-b5d2-0d49a077225a/stock-data-visualization-1/) [原始输入执行](../platform/canvas-retries/7ef1165d-92c5-4a94-a6cc-4582b2567739/stock-data-visualization-1/run.json) |
| stock-data-visualization-2 | 11/15 | 15/15 | 通过 | [平台记录](../platform/canvas-retries/025b47f6-e47d-49f4-b5d2-0d49a077225a/stock-data-visualization-2/) [原始输入执行](../platform/canvas-retries/7ef1165d-92c5-4a94-a6cc-4582b2567739/stock-data-visualization-2/run.json) |
| stock-data-visualization-3 | 6/15 | 15/15 | 通过 | [平台记录](../platform/canvas-retries/c9eab40c-6e7c-408d-9f7c-7bbf5d29e100/stock-data-visualization-3/) [原始输入执行](../platform/canvas-retries/7ef1165d-92c5-4a94-a6cc-4582b2567739/stock-data-visualization-3/run.json) |
| stock-data-visualization-4 | 8/16 | 16/16 | 通过 | [平台记录](../platform/canvas-retries/26e05b4f-2dd5-4542-8c72-1db8013d2e5d/stock-data-visualization-4/) |

原平台从已生成的 Qwen 产物复核取得 10/10。该批保留独立证据。 [产物复核](canvas-recheck/)
