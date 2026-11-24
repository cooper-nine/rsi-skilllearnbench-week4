# 十题清单与配对证据

加权 GDP 第 2 题的历史 CTRF 收集到 0 条测试。本次根据可核验性换入同类第 5 题。保留原始历史调度 CSV，后续运行以 qwen/cases.json 为准。

## earthquake-plate-calculation/5

- 输入　2024 地震事件 JSON、PB2002 边界及板块 JSON。 [原题](../upstream-reference/tasks/earthquake-plate-calculation/earthquake-plate-calculation-5/instruction.md)
- 期望　answer.json；事件 us7000myfa，距离 419.32 km（容差 0.01 km）。 [官方检查](../upstream-reference/tasks/earthquake-plate-calculation/earthquake-plate-calculation-5/tests/test_outputs.py)
- 基线　运行 20261118-122708-583ff7，reward=0。失败检查如下。

```text
test_outputs.py::TestEarthquakeTask::test_distance_within_tolerance
test_outputs.py::TestEarthquakeTask::test_earthquake_id_correct
```

复测输出的事件 ID 已匹配。距离为 1732.30 km。逐项从 6/8 变为 7/8，距离仍失败。外层运行器报告 verifier 超时。 [复测判分](earthquake-5-ctrf.json)

## financial-analysis/1

- 输入　Q2/Q3 2025 SEC 13F 数据和本题问题列表。 [原题](../upstream-reference/tasks/financial-analysis/financial-analysis-1/instruction.md)
- 期望　按本题 expected_output.json 生成 answers.json，逐题匹配官方预期。 [官方检查](../upstream-reference/tasks/financial-analysis/financial-analysis-1/tests/test_outputs.py)
- 基线　运行 20261118-114709-707627，reward=0。失败检查如下。

```text
test_outputs.py::test_answer_quality
```

改编后 1/2，官方 reward=0。已生成答案文件，基金持仓数量的断言仍失败。 [配对证据](paired-evidence/financial-analysis-1/)

## financial-analysis/3

- 输入　Q2/Q3 2025 SEC 13F 数据和本题问题列表。 [原题](../upstream-reference/tasks/financial-analysis/financial-analysis-3/instruction.md)
- 期望　按本题 expected_output.json 生成 answers.json，逐题匹配官方预期。 [官方检查](../upstream-reference/tasks/financial-analysis/financial-analysis-3/tests/test_outputs.py)
- 基线　运行 20261118-123134-1043bc，reward=0。失败检查如下。

```text
test_outputs.py::test_file_exists
test_outputs.py::test_answer_quality
```

改编前 0/2，改编后 1/2，官方 reward=0。文件存在检查已通过，持仓变化排序的断言仍失败。 [配对证据](paired-evidence/financial-analysis-3/)

## weighted-gdp-calculation/1

- 输入　gdp.xlsx 的 Data 表及原始 Task 模板。 [原题](../upstream-reference/tasks/weighted-gdp-calculation/weighted-gdp-calculation-1/instruction.md)
- 期望　在原模板中按题面填写查找公式、净出口及描述统计、SUMPRODUCT 加权值；通过单元格检查。 [官方检查](../upstream-reference/tasks/weighted-gdp-calculation/weighted-gdp-calculation-1/tests/test_outputs.py)
- 基线　运行 20261118-124901-2690d3，reward=0。失败检查如下。

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

改编前 11/27，改编后 13/27，官方 reward=0。首次判题下载 `uv` 失败。保留首次环境错误，对同一份工作簿运行未改动的官方 verifier 得到后续判分。 [配对证据](paired-evidence/weighted-gdp-calculation-1/)

## weighted-gdp-calculation/5

- 输入　gdp.xlsx 的 Data 表及原始 Task 模板。 [原题](../upstream-reference/tasks/weighted-gdp-calculation/weighted-gdp-calculation-5/instruction.md)
- 期望　在原模板中按题面填写查找公式、贸易余额系数及描述统计、按贸易总额进行 SUMPRODUCT 加权；通过单元格检查。 [官方检查](../upstream-reference/tasks/weighted-gdp-calculation/weighted-gdp-calculation-5/tests/test_outputs.py)
- 基线　运行 20261118-150937-21cedf，reward=0。失败检查如下。

```text
test_outputs.py::TestStep2Statistics::test_min_values
test_outputs.py::TestStep2Statistics::test_max_values
test_outputs.py::TestStep2Statistics::test_median_values
test_outputs.py::TestStep2Statistics::test_mean_values
```

改编前 21/25，改编后 11/25，官方 reward=0。数据值、净出口比例、统计和加权均值仍有检查失败。 [配对证据](paired-evidence/weighted-gdp-calculation-5/)

## weighted-gdp-calculation/4

- 输入　gdp.xlsx 的 Data 表及原始 Task 模板。 [原题](../upstream-reference/tasks/weighted-gdp-calculation/weighted-gdp-calculation-4/instruction.md)
- 期望　在原模板中按题面填写查找公式、净出口及描述统计、SUMPRODUCT 加权值；通过单元格检查。 [官方检查](../upstream-reference/tasks/weighted-gdp-calculation/weighted-gdp-calculation-4/tests/test_outputs.py)
- 基线　运行 20261118-140525-7fb55f，reward=0。失败检查如下。

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

改编前 10/27，改编后 27/27。官方 verifier 退出码为 0，reward=1。平台试次使用和基线相同的 Qwen 模型、预算协议与容器镜像。 [基线 CTRF](paired-evidence/weighted-gdp-calculation-4/baseline/ctrf.json) · [复测 CTRF](paired-evidence/weighted-gdp-calculation-4/treatment/ctrf.json) · [奖励](paired-evidence/weighted-gdp-calculation-4/treatment/reward.txt) · [运行记录](paired-evidence/weighted-gdp-calculation-4/treatment/run.json)

## stock-data-visualization/1

- 输入　股票说明及个股历史行情目录。 [原题](../upstream-reference/tasks/stock-data-visualization/stock-data-visualization-1/instruction.md)
- 期望　D3 v6 单页、资源与数据文件，逐项通过对应题目的布局、图表、交互或数据检查。 [官方检查](../upstream-reference/tasks/stock-data-visualization/stock-data-visualization-1/tests/test_outputs.py)
- 基线　运行 20261118-134937-19d1a4，reward=0。失败检查如下。

```text
test_outputs.py::test_output_structure_and_files[/root/output/data/indiv-stock-indiv-stock/ directory]
```

改编前 14/15，改编后 8/15，官方 reward=0。输出结构通过，气泡图、表格、提示和联动等浏览器检查失败。 [配对证据](paired-evidence/stock-data-visualization-1/)

## stock-data-visualization/2

- 输入　股票说明及个股历史行情目录。 [原题](../upstream-reference/tasks/stock-data-visualization/stock-data-visualization-2/instruction.md)
- 期望　D3 v6 单页、资源与数据文件，逐项通过对应题目的布局、图表、交互或数据检查。 [官方检查](../upstream-reference/tasks/stock-data-visualization/stock-data-visualization-2/tests/test_outputs.py)
- 基线　运行 20261118-141811-3aa771，reward=0。失败检查如下。

```text
test_outputs.py::test_data_table
test_outputs.py::test_tooltips_non_etf_and_etf
test_outputs.py::test_interactive_linking
test_outputs.py::test_market_cap_formatting
```

改编前 11/15，改编后 8/15，官方 reward=0。图表渲染、数据表、悬停提示和联动等检查失败。 [配对证据](paired-evidence/stock-data-visualization-2/)

## stock-data-visualization/3

- 输入　股票说明及个股历史行情目录。 [原题](../upstream-reference/tasks/stock-data-visualization/stock-data-visualization-3/instruction.md)
- 期望　D3 v6 单页、资源与数据文件，逐项通过对应题目的布局、图表、交互或数据检查。 [官方检查](../upstream-reference/tasks/stock-data-visualization/stock-data-visualization-3/tests/test_outputs.py)
- 基线　运行 20261118-145831-ff084f，reward=0。失败检查如下。

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

改编前 6/15，改编后 8/15，官方 reward=0。输出文件检查改善，渲染和交互仍有失败。 [配对证据](paired-evidence/stock-data-visualization-3/)

## stock-data-visualization/4

- 输入　股票说明及个股历史行情目录。 [原题](../upstream-reference/tasks/stock-data-visualization/stock-data-visualization-4/instruction.md)
- 期望　D3 v6 单页、资源与数据文件，逐项通过对应题目的布局、图表、交互或数据检查。 [官方检查](../upstream-reference/tasks/stock-data-visualization/stock-data-visualization-4/tests/test_outputs.py)
- 基线　运行 20261118-152648-61d383，reward=0。失败检查如下。

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

改编前 8/16，改编后 15/16，官方 reward=0。唯一失败为非 ETF 悬停未显示可见的提示框。 [配对证据](paired-evidence/stock-data-visualization-4/)
