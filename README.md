# SkillLearnBench 第四周｜人工编排与 Qwen 3.5 Plus

十个典型案例按 case01–case10 对齐，每条都有前端画布请求、后端执行图、正式运行结果及逐题解释。仓库保留选中实例的题目与判分文件，基准输入按固定版本准备。 [十案例交付索引](results/cases/)

正式复测从指定前端进入 Spring Boot，再执行 Qwen 节点和原版 Docker 官判。逐题复测脚本与配置见[指定前后端逐题复测](RUN.md#指定前后端逐题复测)。

## 评审快速启动

从本仓库根目录运行 `powershell -NoProfile -ExecutionPolicy Bypass -File .\review.ps1`。用 Node.js、Python 和 Git 启动原画布页面，点击「回放节点归档」即可检查拆分 Skill、节点顺序、真实 Qwen 产物与历史官判。需要重新调用 Qwen 时，使用同一脚本的 `-Live` 模式。 [评审与实跑步骤](RUN.md#评审快速启动)

## 仓库提交

- 我的后端项目 [rsi-data-spring-boot](https://github.com/cooper-nine/rsi-data-spring-boot)
- 我的前端项目 [rsi-data-platform](https://github.com/cooper-nine/rsi-data-platform)
- 我的前端编排框架 [rsi-data-visual](https://github.com/cooper-nine/rsi-data-visual) 增加了可直接安装的构建产物和构建说明，供评审脚本装载原画布组件。
- 我的后端 RSI 编排框架 [rsi-flow](https://github.com/cooper-nine/rsi-flow) 增加了独立的 Java 有界 Skill 循环节点、测试和示例。十题正式实验由 Spring Boot 的 FlowEngine 调度 Python 运行器，逐节点执行由 Python 负责。

安装和架构见[完整启动说明](RUN.md)。

## 数据集与实验边界

每类任务 $i$ 使用固定版本的 SkillLearnBench 四元组 $(x_i, Q_i, v_i, S_i)$。本实验从四类任务的实例集中挑出十个已有失败基线的实例。下表的题号指实例编号。

| 组成 | 含义与用途 |
| --- | --- |
| $x_i$ | 任务说明，定义要完成的工作和交付格式。运行时使用所选实例自带的 `instruction.md`。 |
| $Q_i$ | 同类任务下的一批实例，各实例带自己的数据和任务环境。同一个实例的基线与编排复测使用同一份原始输入。 |
| $v_i$ | 只读验收规则。每个实例使用固定提交里的原版 `tests/test.sh` 及其关联测试。业务节点执行时隔离测试，最终验收阶段由 Docker 挂载并运行原版脚本，读取 CTRF 和 `reward.txt`。 |
| $S_i$ | 论文基准规定的人工参考 Skill，即任务作者提供的 `skills/human_authored/<任务族>/` 下的原始 Skill。同一任务族可以有多份文件，例如金融同时使用基金名称搜索与 13F 分析。 |

基线使用原始完整人工 Skill。编排版先从同一份 $S_i$ 按职责切分，再添加节点输入输出契约、连线和重试反馈。导出脚本记录当时工作区中原文件的 SHA-256。片段按原顺序拼回后与导出时读取的文件逐字节一致。将 Windows 与 Git 的换行统一后，拼回文本与固定提交中的原始 Skill 一致。运行时 Qwen 可读取任务说明、该节点的参考片段、原始数据和上游检查点。任务提示、节点契约和分阶段调用都是本次编排的一部分。 [固定基准版本](upstream-reference/source.json) · [原始人工参考 Skill](https://github.com/cxcscmu/SkillLearnBench/tree/726e1f79b96b0cb3d729d0e55a1c847e0b5353ae/skills/human_authored) · [切分脚本](qwen/export_rsi_flows.py)

## 四类编排

| 任务及实例 | 人工参考 Skill | 节点顺序与交接 |
| --- | --- | --- |
| 地震板块 5 | `geospatial-analysis` | **检查输入 → 筛选地震 → 计算距离 → 组装并检查答案**。先确认记录字段和坐标，再交接板块、事件及坐标。测距节点用板块边界生成距离，最后核对事件标识和结果格式，输出 `answer.json`。 |
| 金融分析 1、3 | `fuzzy-name-search`、`13f-analyzer` | **确认基金申报 → 计算持仓与变化 → 组装并检查答案**。先把基金名对应到各季度申报编号，再按题目要求计算规模、持仓和排名，最后检查答案字段与列表，输出 `answers.json`。 |
| 加权 GDP 1、4、5 | `xlsx` | **确认工作簿要求 → 定位数据与年份 → 写公式与加权 → 重算并检查**。先明确目标单元格、公式和模板约束，再交接数据块与年份映射。计算节点填写公式，检查节点定位引用和兼容性错误，输出 `gdp.xlsx`。 |
| 股票可视化 1、2、3、4 | `d3-visualization` | **检查数据与依赖 → 画气泡图和表格 → 实现悬停和联动 → 浏览器检查**。先交接文件、字段和输出要求，再生成页面、气泡图与表格。交互节点在渲染产物上补上提示框与联动，最后检查网页、数据和交互产物。 |

节点失败时，把错误反馈给负责该产物的节点，并保留可复用的上游检查点。四类流程的最后一步都是运行相应实例的官方判分。 [节点配置](qwen/flows/) · [平台画布截图](results/qwen-canvas/) · [逐题运行和回退证据](results/PLATFORM.md)

### 结果口径

正式结果来自同一批十题的逐题对照，包括定向补跑。这个样本按已有失败基线选取，结果适用于这十个实例。分阶段提示、产物校验和补跑共同参与了改善，现有记录支持同题对照。评审回放读取历史产物，新的 `-Live` 运行单独报告当次真实结果。 [十题验收](results/platform/ACCEPTANCE.md) · [评审实跑样例](results/reviewer-smoke/stock-4/ctrf.json)

同一批十题的人工 Skill 基线 **0/10**，原平台编排与补跑后 **10/10 官方整题通过**。四类流程在原 `rsi-flow-platform` 画布配置，由原前端和 Spring Boot 发起，业务节点调用 Qwen 3.5 Plus。整题结果以 Docker 容器内原版 `test.sh` 产生的官方记录为准。

- [原平台逐题验收与基线对照](results/platform/ACCEPTANCE.md) · [CSV](results/platform/comparison.csv)
- [十题清单与早期试点](results/CASE-EVIDENCE.md)
- [早期 Qwen 试点对照 CSV](results/comparison.csv) · [原始配对证据](results/paired-evidence/)
- [实验报告、失败分析和下一阶段指标](results/QWEN-PILOT.md)
- [四类浏览器编排截图](results/qwen-canvas/) · [平台运行证据](results/PLATFORM.md)
- [节点配置](qwen/flows/) · [运行清单](qwen/cases.json) · [基准固定版本](upstream-reference/source.json)

## 运行与核验

原平台测试页为 `/test/week4`。选择任务类型并保存画布，可从原始输入运行。后端为每次执行返回运行 ID，可用该 ID 对照画布、节点记录和官方报告。 [原平台联调记录](results/PLATFORM.md)

在仓库根目录执行 `python qwen/export_paired_evidence.py`，从已发布的原始报告、奖励文件和运行配置重新核验十份配对并生成 CSV。这一步可离线运行。

`qwen/run_rsi_retests.py` 是准备好的基准工作区使用的 Qwen 运行入口。它需要固定版本的 SkillLearnBench、Docker、已准备的基线和预算状态，以及本地配置的 DashScope API 凭证。已发布的逐题证据保留实际采用的配置、试次与模型检查点，包含从先前 Qwen 产物继续的运行。
