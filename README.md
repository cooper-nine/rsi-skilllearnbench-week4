# SkillLearnBench 第四周复测

本项目比较同一道题在原始人工 Skill 组和结构化 Skill 组的结果。两组使用相同任务输入、官方 verifier 和既有 budget-v3 协议。复测选取原人工 Skill 组已经失败的十题，覆盖地震、金融、加权 GDP 和股票可视化。

- [十题的输入、期望和失败检查](results/CASE-EVIDENCE.md)
- [前后对照 CSV](results/comparison.csv)
- [四类结构化流程](qwen/flows)
- [十题运行清单](qwen/cases.json)
- [SkillLearnBench 来源与固定提交](upstream-reference/source.json)

## 当前验收状态

地震第 5 题已得到一次结构化运行输出。Agent 正常退出，外层 verifier 运行超时，但落盘的 CTRF 包含全部 8 条检查和具体断言。事件 ID 从错误变为正确，检查通过数由 6/8 增至 7/8。距离 1732.30 km 仍偏离官方值 419.32 km，题目依然失败。剩余 9 题未完成复测，当前没有可报告的十题修复率。

流程 JSON 目前由 Qwen 复测运行器执行。rsi-flow-platform 上已验证的是另一条 Excel 演示链路。本项目四类流程仍待本人确认节点结构并在平台上搭建、接入和逐题验证。现有 JSON 属于 AI 辅助草案。

## 结构和失败反馈

地震流程将事件筛选和距离计算拆开，以便分别定位地理匹配与测距错误。金融流程先确定基金、季度和申报标识，再分析持仓或补充查询。GDP 流程分开处理模板读取、公式计算、重算验证。股票流程把输入整理、渲染与交互检查分开。同一类题共享流程，实例变更由基准输入携带。

草案的节点契约以原 Skill 文本片段为输入，并通过共享工作目录传递产物。运行器保留节点进入、完成及 shell 失败恢复记录。平台正式版本仍需逐节点定义产物名称与类型、必填校验、可恢复错误和回退条件。地震题优先复查边界选择、投影和测距方法。距离不合格须回到测距节点，保留筛选正确的事件；修复方法由实际复测验证。

## 本地复测

工作目录需已安装基准依赖和 Docker Linux 引擎，并有已准备的 budget-v3 基线状态、预算配置及 API 凭证。Windows 现有环境可按以下命令运行。

```powershell
Set-Location 'E:\SkillLearnBench-Workspace\upstream-sparse'
$env:Path = 'C:\Program Files\Docker\Docker\resources\bin;' + $env:Path
$env:DASHSCOPE_API_KEY = [Environment]::GetEnvironmentVariable('DASHSCOPE_API_KEY', 'User')
.\.venv\Scripts\python.exe .\qwen\run_rsi_retests.py
```

将本仓库的 qwen 复测文件和流程同步至基准工作目录的 qwen 目录后运行。已有有效结果按实例与流程哈希复用。外层超时且保存了完整失败断言的记录单独标记，继续后续用例。输出在 output/qwen_rsi_flow。公网上的仓库不包含 API 凭证和本机运行环境。

## 下一阶段的人在回路指标

将人手选节点、改边、补参数、人工重试和改输出的每次实际操作记为一次干预，记录题号、触发原因和时间。先在平台上跑本批十题，记录人工方案的真实次数 H0，目前没有实测值。目标是在相同输入、预算和 verifier 下保持 10/10 通过，同时将干预总数降到不超过 H0 的一半；H0 为零时目标维持零次。分别报告通过数、总干预次数、每题中位数和人工耗时，并用未参与编排的同类问题复验。任何未满 10/10 的运行都单列。
