# 十题清单与配对证据

每题保留原题、预期、人工 Skill 基线失败检查和早期 Qwen 官方报告。原平台试次的最新整题成绩与原始记录见[平台对照](platform/ACCEPTANCE.md)。 [早期试点 CSV](comparison.csv) · [实验报告](QWEN-PILOT.md)

## earthquake-plate-calculation/5

- 原平台复测　**通过，8/8**。 [逐题执行及官判](platform/canvas-retries/b8003ff6-204f-4008-8d6c-72aad006bbbd/earthquake-plate-calculation-5/)
- 输入　2024 地震事件 JSON、PB2002 边界及板块 JSON。 [原题](../upstream-reference/tasks/earthquake-plate-calculation/earthquake-plate-calculation-5/instruction.md)
- 期望　answer.json；事件 us7000myfa，距离 419.32 km（容差 0.01 km）。 [官方检查](../upstream-reference/tasks/earthquake-plate-calculation/earthquake-plate-calculation-5/tests/test_outputs.py)
- 人工 Skill 基线 **6/8，整题失败**。试次 `20261118-122708-583ff7`。 [官方报告](paired-evidence/earthquake-plate-calculation-5/baseline/ctrf.json)
- 早期 Qwen API 试点 **8/8，整题通过，奖励为 1**。试次 `20261124-215351-cde393`。 [官方报告](paired-evidence/earthquake-plate-calculation-5/treatment/ctrf.json) · [运行记录](paired-evidence/earthquake-plate-calculation-5/treatment/run.json) · [试次索引](paired-evidence/earthquake-plate-calculation-5/treatment/attempts.json)

<details>
<summary>基线失败检查</summary>

```text
test_outputs.py::TestEarthquakeTask::test_distance_within_tolerance
test_outputs.py::TestEarthquakeTask::test_earthquake_id_correct
```

</details>

## financial-analysis/1

- 原平台复测　**通过，2/2**。 [逐题执行及官判](platform/finance-1/)
- 输入　Q2/Q3 2025 SEC 13F 数据和本题问题列表。 [原题](../upstream-reference/tasks/financial-analysis/financial-analysis-1/instruction.md)
- 期望　在 /root/answers.json 交付Renaissance 的 AUM 和股票数量、Berkshire 增持额前五的 CUSIP，以及 Palantir 持仓额前三的经理，顺序及数值由官方脚本核对。 [官方检查](../upstream-reference/tasks/financial-analysis/financial-analysis-1/tests/test_outputs.py)
- 人工 Skill 基线 **1/2，整题失败**。试次 `20261118-114709-707627`。 [官方报告](paired-evidence/financial-analysis-1/baseline/ctrf.json)
- 早期 Qwen API 试点 **2/2，整题通过，奖励为 1**。试次 `20261125-004055-e951df`。 [官方报告](paired-evidence/financial-analysis-1/treatment/ctrf.json) · [运行记录](paired-evidence/financial-analysis-1/treatment/run.json) · [试次索引](paired-evidence/financial-analysis-1/treatment/attempts.json)

<details>
<summary>基线失败检查</summary>

```text
test_outputs.py::test_answer_quality
```

</details>

## financial-analysis/3

- 原平台复测　**通过，2/2**。 [逐题执行及官判](platform/finance-3/)
- 输入　Q2/Q3 2025 SEC 13F 数据和本题问题列表。 [原题](../upstream-reference/tasks/financial-analysis/financial-analysis-3/instruction.md)
- 期望　在 /root/answers.json 交付Soros 的 AUM、Pershing Square 增持额前三的 CUSIP，以及 NVIDIA 持仓额前五的经理，顺序及数值由官方脚本核对。 [官方检查](../upstream-reference/tasks/financial-analysis/financial-analysis-3/tests/test_outputs.py)
- 人工 Skill 基线 **0/2，整题失败**。试次 `20261118-123134-1043bc`。 [官方报告](paired-evidence/financial-analysis-3/baseline/ctrf.json)
- 早期 Qwen API 试点 **2/2，整题通过，奖励为 1**。试次 `20261125-004524-6b896b`。 [官方报告](paired-evidence/financial-analysis-3/treatment/ctrf.json) · [运行记录](paired-evidence/financial-analysis-3/treatment/run.json) · [试次索引](paired-evidence/financial-analysis-3/treatment/attempts.json)

<details>
<summary>基线失败检查</summary>

```text
test_outputs.py::test_file_exists
test_outputs.py::test_answer_quality
```

</details>

## weighted-gdp-calculation/1

- 原平台复测　**通过，27/27**。 [逐题执行及官判](platform/canvas-retries/1eeaee54-76a2-4def-a22d-5633040140f6/weighted-gdp-calculation-1/)
- 输入　gdp.xlsx 的 Data 表及原始 Task 模板。 [原题](../upstream-reference/tasks/weighted-gdp-calculation/weighted-gdp-calculation-1/instruction.md)
- 期望　在原模板中按题面填写查找公式、净出口及描述统计、SUMPRODUCT 加权值；通过单元格检查。 [官方检查](../upstream-reference/tasks/weighted-gdp-calculation/weighted-gdp-calculation-1/tests/test_outputs.py)
- 人工 Skill 基线 **11/27，整题失败**。试次 `20261118-124901-2690d3`。 [官方报告](paired-evidence/weighted-gdp-calculation-1/baseline/ctrf.json)
- 早期 Qwen API 试点 **27/27，整题通过，奖励为 1**。试次 `20261125-005144-c6b49e`。 [官方报告](paired-evidence/weighted-gdp-calculation-1/treatment/ctrf.json) · [运行记录](paired-evidence/weighted-gdp-calculation-1/treatment/run.json) · [试次索引](paired-evidence/weighted-gdp-calculation-1/treatment/attempts.json)

<details>
<summary>基线失败检查</summary>

```text
test_outputs.py::TestStep1LookupFormulas::test_exports_have_data
test_outputs.py::TestStep1LookupFormulas::test_imports_have_data
test_outputs.py::TestStep1DataValues::test_exports_values
test_outputs.py::TestStep1DataValues::test_imports_values
test_outputs.py::TestStep1DataValues::test_gdp_values
test_outputs.py::TestStep2NetExportsCalculation::test_net_exports_pct_have_data
test_outputs.py::TestStep2NetExportsCalculation::test_net_exports_pct_values
test_outputs.py::TestStep2Statistics::test_statistics_have_data
test_outputs.py::TestStep2Statistics::test_min_values
test_outputs.py::TestStep2Statistics::test_max_values
test_outputs.py::TestStep2Statistics::test_median_values
test_outputs.py::TestStep2Statistics::test_mean_values
test_outputs.py::TestStep2Statistics::test_percentile_values
test_outputs.py::TestStep3WeightedMean::test_weighted_mean_has_data
test_outputs.py::TestStep3WeightedMean::test_weighted_mean_values_reasonable
test_outputs.py::TestStep3WeightedMean::test_weighted_mean_values
```

</details>

## weighted-gdp-calculation/5

- 原平台复测　**通过，25/25**。 [逐题执行及官判](platform/canvas-retries/e61d8f69-f61d-4346-aee8-6efd67b2fc84/weighted-gdp-calculation-5/)
- 输入　gdp.xlsx 的 Data 表及原始 Task 模板。 [原题](../upstream-reference/tasks/weighted-gdp-calculation/weighted-gdp-calculation-5/instruction.md)
- 期望　在原模板中按题面填写查找公式、贸易余额系数及描述统计、按贸易总额进行 SUMPRODUCT 加权；通过单元格检查。 [官方检查](../upstream-reference/tasks/weighted-gdp-calculation/weighted-gdp-calculation-5/tests/test_outputs.py)
- 人工 Skill 基线 **21/25，整题失败**。试次 `20261118-150937-21cedf`。 [官方报告](paired-evidence/weighted-gdp-calculation-5/baseline/ctrf.json)
- 早期 Qwen API 试点 **25/25，整题通过，奖励为 1**。试次 `20261125-002513-f38f87`。 [官方报告](paired-evidence/weighted-gdp-calculation-5/treatment/ctrf.json) · [运行记录](paired-evidence/weighted-gdp-calculation-5/treatment/run.json) · [试次索引](paired-evidence/weighted-gdp-calculation-5/treatment/attempts.json)

<details>
<summary>基线失败检查</summary>

```text
test_outputs.py::TestStep2Statistics::test_min_values
test_outputs.py::TestStep2Statistics::test_max_values
test_outputs.py::TestStep2Statistics::test_median_values
test_outputs.py::TestStep2Statistics::test_mean_values
```

</details>

## weighted-gdp-calculation/4

- 原平台复测　**通过，27/27**。 [逐题执行及官判](platform/canvas-retries/b49640e9-305b-4b1b-a0ba-fc00ce2c4008/weighted-gdp-calculation-4/)
- 输入　gdp.xlsx 的 Data 表及原始 Task 模板。 [原题](../upstream-reference/tasks/weighted-gdp-calculation/weighted-gdp-calculation-4/instruction.md)
- 期望　在原模板中按题面填写查找公式、净出口及描述统计、SUMPRODUCT 加权值；通过单元格检查。 [官方检查](../upstream-reference/tasks/weighted-gdp-calculation/weighted-gdp-calculation-4/tests/test_outputs.py)
- 人工 Skill 基线 **10/27，整题失败**。试次 `20261118-140525-7fb55f`。 [官方报告](paired-evidence/weighted-gdp-calculation-4/baseline/ctrf.json)
- 早期 Qwen API 试点 **27/27，整题通过，奖励为 1**。试次 `20261124-202303-42cdb5`。 [官方报告](paired-evidence/weighted-gdp-calculation-4/treatment/ctrf.json) · [运行记录](paired-evidence/weighted-gdp-calculation-4/treatment/run.json) · [试次索引](paired-evidence/weighted-gdp-calculation-4/treatment/attempts.json)

<details>
<summary>基线失败检查</summary>

```text
test_outputs.py::TestStep1LookupFormulas::test_exports_have_data
test_outputs.py::TestStep1LookupFormulas::test_imports_have_data
test_outputs.py::TestStep1LookupFormulas::test_gdp_have_data
test_outputs.py::TestStep1DataValues::test_exports_values
test_outputs.py::TestStep1DataValues::test_imports_values
test_outputs.py::TestStep1DataValues::test_gdp_values
test_outputs.py::TestStep2NetExportsCalculation::test_net_exports_pct_have_data
test_outputs.py::TestStep2NetExportsCalculation::test_net_exports_pct_values
test_outputs.py::TestStep2Statistics::test_statistics_have_data
test_outputs.py::TestStep2Statistics::test_min_values
test_outputs.py::TestStep2Statistics::test_max_values
test_outputs.py::TestStep2Statistics::test_median_values
test_outputs.py::TestStep2Statistics::test_mean_values
test_outputs.py::TestStep2Statistics::test_percentile_values
test_outputs.py::TestStep3WeightedMean::test_weighted_mean_has_data
test_outputs.py::TestStep3WeightedMean::test_weighted_mean_values_reasonable
test_outputs.py::TestStep3WeightedMean::test_weighted_mean_values
```

</details>

## stock-data-visualization/1

- 原平台复测　**通过，15/15**。 [逐题执行及官判](platform/canvas-retries/025b47f6-e47d-49f4-b5d2-0d49a077225a/stock-data-visualization-1/)
- 输入　股票说明及个股历史行情目录。 [原题](../upstream-reference/tasks/stock-data-visualization/stock-data-visualization-1/instruction.md)
- 期望　用 stock-descriptions.csv 和个股行情数据交付 D3 v6 单页，显示按市值和行业分组的气泡图与 50 行表格，普通股票有悬停提示、ETF 无提示，点击双向高亮。 [官方检查](../upstream-reference/tasks/stock-data-visualization/stock-data-visualization-1/tests/test_outputs.py)
- 人工 Skill 基线 **14/15，整题失败**。试次 `20261118-134937-19d1a4`。 [官方报告](paired-evidence/stock-data-visualization-1/baseline/ctrf.json)
- 早期 Qwen API 试点 **15/15，整题通过，奖励为 1**。试次 `20261124-235639-135ea2`。 [官方报告](paired-evidence/stock-data-visualization-1/treatment/ctrf.json) · [运行记录](paired-evidence/stock-data-visualization-1/treatment/run.json) · [试次索引](paired-evidence/stock-data-visualization-1/treatment/attempts.json)

<details>
<summary>基线失败检查</summary>

```text
test_outputs.py::test_output_structure_and_files[/root/output/data/indiv-stock-indiv-stock/ directory]
```

</details>

## stock-data-visualization/2

- 原平台复测　**通过，15/15**。 [逐题执行及官判](platform/canvas-retries/025b47f6-e47d-49f4-b5d2-0d49a077225a/stock-data-visualization-2/)
- 输入　股票说明及个股历史行情目录。 [原题](../upstream-reference/tasks/stock-data-visualization/stock-data-visualization-2/instruction.md)
- 期望　用 stock-descriptions.json 和个股行情数据交付 D3 v6 单页，显示按市值和行业分组的气泡图与 50 行表格，普通股票有悬停提示、ETF 无提示，点击双向高亮。 [官方检查](../upstream-reference/tasks/stock-data-visualization/stock-data-visualization-2/tests/test_outputs.py)
- 人工 Skill 基线 **11/15，整题失败**。试次 `20261118-141811-3aa771`。 [官方报告](paired-evidence/stock-data-visualization-2/baseline/ctrf.json)
- 早期 Qwen API 试点 **15/15，整题通过，奖励为 1**。试次 `20261125-004434-2ad657`。 [官方报告](paired-evidence/stock-data-visualization-2/treatment/ctrf.json) · [运行记录](paired-evidence/stock-data-visualization-2/treatment/run.json) · [试次索引](paired-evidence/stock-data-visualization-2/treatment/attempts.json)

<details>
<summary>基线失败检查</summary>

```text
test_outputs.py::test_data_table
test_outputs.py::test_tooltips_non_etf_and_etf
test_outputs.py::test_interactive_linking
test_outputs.py::test_market_cap_formatting
```

</details>

## stock-data-visualization/3

- 原平台复测　**通过，15/15**。 [逐题执行及官判](platform/canvas-retries/c9eab40c-6e7c-408d-9f7c-7bbf5d29e100/stock-data-visualization-3/)
- 输入　股票说明及个股历史行情目录。 [原题](../upstream-reference/tasks/stock-data-visualization/stock-data-visualization-3/instruction.md)
- 期望　用 stock-descriptions.tsv 和个股行情数据交付 D3 v6 单页，显示按市值和行业分组的气泡图与 50 行表格，普通股票有悬停提示、ETF 无提示，点击双向高亮。 [官方检查](../upstream-reference/tasks/stock-data-visualization/stock-data-visualization-3/tests/test_outputs.py)
- 人工 Skill 基线 **6/15，整题失败**。试次 `20261118-145831-ff084f`。 [官方报告](paired-evidence/stock-data-visualization-3/baseline/ctrf.json)
- 早期 Qwen API 试点 **15/15，整题通过，奖励为 1**。试次 `20261124-235733-c595ab`。 [官方报告](paired-evidence/stock-data-visualization-3/treatment/ctrf.json) · [运行记录](paired-evidence/stock-data-visualization-3/treatment/run.json) · [试次索引](paired-evidence/stock-data-visualization-3/treatment/attempts.json)

<details>
<summary>基线失败检查</summary>

```text
test_outputs.py::test_output_structure_and_files[/root/output/index.html-index.html]
test_outputs.py::test_output_structure_and_files[/root/output/js/visualization.js-custom visualization.js]
test_outputs.py::test_bubble_chart_rendering
test_outputs.py::test_data_table
test_outputs.py::test_tooltips_non_etf_and_etf
test_outputs.py::test_interactive_linking
test_outputs.py::test_market_cap_formatting
test_outputs.py::test_sector_clustering
test_outputs.py::test_legend_completeness
```

</details>

## stock-data-visualization/4

- 原平台复测　**通过，16/16**。 [逐题执行及官判](platform/canvas-retries/26e05b4f-2dd5-4542-8c72-1db8013d2e5d/stock-data-visualization-4/)
- 输入　股票说明及个股历史行情目录。 [原题](../upstream-reference/tasks/stock-data-visualization/stock-data-visualization-4/instruction.md)
- 期望　用 stock-descriptions.csv 和个股行情数据交付 D3 v6 单页，显示按市值和行业分组的气泡图与 50 行表格，普通股票有悬停提示、ETF 无提示，点击双向高亮。 [官方检查](../upstream-reference/tasks/stock-data-visualization/stock-data-visualization-4/tests/test_outputs.py)
- 人工 Skill 基线 **8/16，整题失败**。试次 `20261118-152648-61d383`。 [官方报告](paired-evidence/stock-data-visualization-4/baseline/ctrf.json)
- 早期 Qwen API 试点 **16/16，整题通过，奖励为 1**。试次 `20261124-235811-ec73fc`。 [官方报告](paired-evidence/stock-data-visualization-4/treatment/ctrf.json) · [运行记录](paired-evidence/stock-data-visualization-4/treatment/run.json) · [试次索引](paired-evidence/stock-data-visualization-4/treatment/attempts.json)

<details>
<summary>基线失败检查</summary>

```text
test_outputs.py::test_bubble_chart_rendering
test_outputs.py::test_data_table
test_outputs.py::test_visualization_uses_only_target_tickers
test_outputs.py::test_tooltips_non_etf_and_etf
test_outputs.py::test_interactive_linking
test_outputs.py::test_market_cap_formatting
test_outputs.py::test_sector_clustering
test_outputs.py::test_legend_completeness
```

</details>
