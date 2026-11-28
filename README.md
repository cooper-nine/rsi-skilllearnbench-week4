# SkillLearnBench 第四周｜人工编排与 Qwen 3.5 Plus

## 评审快速启动

从本仓库根目录运行 `powershell -NoProfile -ExecutionPolicy Bypass -File .\review.ps1`。用 Node.js、Python 和 Git 启动原画布页面，点击「回放节点归档」即可检查拆分 Skill、节点顺序、真实 Qwen 产物与历史官判。需要重新调用 Qwen 时，使用同一脚本的 `-Live` 模式。 [评审与实跑步骤](RUN.md#评审快速启动)

## 仓库提交

- 我的后端项目 [rsi-data-spring-boot](https://github.com/cooper-nine/rsi-data-spring-boot)
- 我的前端项目 [rsi-data-platform](https://github.com/cooper-nine/rsi-data-platform)
- 我的前端编排框架 [rsi-data-visual](https://github.com/cooper-nine/rsi-data-visual) 提供原画布组件及前端可直接安装的构建文件
- 我的后端 RSI 编排框架 [rsi-flow](https://github.com/cooper-nine/rsi-flow) 含有独立的有界循环节点实验

安装和架构见[完整启动说明](RUN.md)。

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
