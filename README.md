# SkillLearnBench 第四周复测

本项目比较同一道题在原始人工 Skill 组和结构化 Skill 组的结果。两组使用相同任务输入、官方 verifier 和既有 budget-v3 协议。复测选取原人工 Skill 组已经失败的十题，覆盖地震、金融、加权 GDP 和股票可视化。

- [十题的输入、期望和失败检查](results/CASE-EVIDENCE.md)
- [前后对照 CSV](results/comparison.csv)
- [官方判分与运行证据](results/paired-evidence)
- [RSI 平台运行记录](results/PLATFORM.md)
- [四类结构化流程](qwen/flows)
- [十题运行清单](qwen/cases.json)
- [SkillLearnBench 来源与固定提交](upstream-reference/source.json)

## 当前验收状态

同模型配对复测以官方 verifier 为准。整题通过须同时满足 verifier 正常退出、CTRF 非空且所有检查通过、`reward.txt` 为 `1`。通过数和失败断言见[逐题对照](results/comparison.csv)。

加权 GDP 第 4 题是已确认的整题修复案例。原人工 Skill 基线通过 10/27 项，RSI 平台发起的同模型复测通过 27/27 项，奖励为 1。 [两组官方判分与平台运行记录](results/paired-evidence/weighted-gdp-calculation-4/)

地震第 5 题的原同模型复测由 6/8 增至 7/8。题干与输出字段指定了不同的测距对象。补充诊断以数据选中的板块边缘为准，计算得 419.32 km，运行原版 verifier 后通过全部 8 项。该次由确定性脚本执行，独立列于[测距修复证据](results/diagnostics/earthquake-5)。

用户已确认四类流程顺序和回退规则。Spring Boot FlowEngine 接收平台运行请求，启动复测程序。Qwen 适配器在任务容器中执行流程节点，官方 verifier 在产物生成后评分。 [平台运行方式](platform/README.md)

## 结构和失败反馈

地震流程将事件筛选和距离计算拆开，以便分别定位地理匹配与测距错误。金融流程先确定基金、季度和申报标识，再分析持仓或补充查询。GDP 流程分开处理模板读取、公式计算、重算验证。股票流程把输入整理、渲染与交互检查分开。同一类题共享流程，实例变更由基准输入携带。

节点以原 Skill 文本片段指导模型，并通过共享工作目录传递产物。运行器保留节点进入、完成及命令失败恢复记录。四类流程同样使用一次失败恢复提示。节点完成由模型工具调用推进，逐题报告可见实际走过的节点。

## 本地复测

工作目录需已安装基准依赖和 Docker Linux 引擎，并有已准备的 budget-v3 基线状态、预算配置及 API 凭证。Windows 现有环境可按以下命令运行。

```powershell
Set-Location 'E:\SkillLearnBench-Workspace\upstream-sparse'
$env:Path = 'C:\Program Files\Docker\Docker\resources\bin;' + $env:Path
$env:DASHSCOPE_API_KEY = [Environment]::GetEnvironmentVariable('DASHSCOPE_API_KEY', 'User')
.\.venv\Scripts\python.exe .\qwen\run_rsi_retests.py
```

将本仓库的 qwen 复测文件和流程同步至基准工作目录的 qwen 目录后运行。已有有效结果按实例与流程哈希复用。续跑优先沿用基线记录中的本地镜像。外层超时且保存了完整失败断言的记录单独标记。输出在 `output/qwen_rsi_flow`。用 `python qwen/export_paired_evidence.py <基准工作区>` 导出前后对照与原版判分文件。

## 下一阶段的人在回路指标

将人手选节点、改边、补参数、人工重试和改输出的每次实际操作记为一次干预，记录题号、触发原因和时间。先在平台上跑本批十题，记录人工方案的真实次数 H0，目前没有实测值。目标是在相同输入、预算和 verifier 下保持 10/10 通过，同时将干预总数降到不超过 H0 的一半；H0 为零时目标维持零次。分别报告通过数、总干预次数、每题中位数和人工耗时，并用未参与编排的同类问题复验。任何未满 10/10 的运行都单列。
