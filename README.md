# SkillLearnBench 第四周｜人工编排与 Qwen 3.5 Plus

同一批十题的人工 Skill 基线全部未通过。采用人工确认的四类节点、输入输出契约和定向回退后，**Qwen API 复测由 0/10 提升至 10/10 整题通过**。其中两题来自同轮试点，后续八题全部通过。整题通过要求原版 Docker `test.sh` 正常退出、CTRF 报告全部通过、`reward.txt` 为 `1`。

- [十题清单：输入、期望、基线失败与 Qwen 结果](results/CASE-EVIDENCE.md)
- [同输入逐题对照 CSV](results/comparison.csv) · [原始配对证据](results/paired-evidence/)
- [实验报告、失败分析和下一阶段指标](results/QWEN-PILOT.md)
- [四类浏览器编排截图](results/qwen-canvas/) · [平台运行证据](results/PLATFORM.md)
- [节点配置](qwen/flows/) · [运行清单](qwen/cases.json) · [基准固定版本](upstream-reference/source.json)

## 运行与核验

GDP 第 4 题的 Qwen 试点由 RSI 后端发起。其余精选结果由本地运行器调用 Qwen API，保存节点产物，并在 Docker 中运行官方脚本。四张截图来自临时 RSI Flow Visual 浏览器前端，展示四类流程。原平台画布点击执行全部题目的验证仍待完成。

在仓库根目录执行 `python qwen/export_paired_evidence.py`，从已发布的原始报告、奖励文件和运行配置重新核验十份配对并生成 CSV。这一步可离线运行。

`qwen/run_rsi_retests.py` 是准备好的基准工作区使用的 Qwen 运行入口。它需要固定版本的 SkillLearnBench、Docker、已准备的基线和预算状态，以及本地配置的 DashScope API 凭证。已发布的逐题证据保留实际采用的配置、试次与模型检查点，包含从先前 Qwen 产物继续的运行。
