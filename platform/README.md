# RSI 平台复测入口

适配器在 Spring Boot 后端注册 `RSI_WEEK4_RESUME`。FlowEngine 路由到 `launch-week4-campaign`，启动固定的本地复测程序。程序加载四份已确认的 Skill 流程，在 Qwen 容器中推进阶段，最后由官方 verifier 评分。每个新试次记录 `platform_run_id`，与后端返回的运行 ID 对应。

1. 将 `Week4Resume.java` 放入 `rsi-flow-spring-boot/core-flow/src/main/java/com/horsecoder/common/whuTalent/core/flow/Run/code/`。将 `flow-week4-resume.json` 放入 `core-flow/src/main/resources/flow/Run/`。构建时确认 `core-flow/target/classes` 在其他带有 `flow` 资源目录的类路径项之前。
2. 将本仓库最新 Qwen 运行器文件同步至已准备的基准工作区。配置现有 `budget-v3` 状态、Docker Linux 引擎和 API 凭证。
3. 在启动后端的本机环境中设置 `RSI_WEEK4_BENCHMARK_HOME` 为基准工作区，设置 `RSI_WEEK4_TOKEN` 为随机生成的至少 32 字符的会话令牌，并传入 `DASHSCOPE_API_KEY`。本次验证在 `AppTestStarter` 传入 `--server.address=127.0.0.1 --server.port=39911`。
4. 在有相同 `RSI_WEEK4_TOKEN` 的终端运行 `./platform/Invoke-Week4.ps1`。响应中的 `data.value.platformRunId` 对应基准工作区的 `output/qwen_rsi_flow/platform/<id>.log`。重复请求在活动任务存续时返回相同运行 ID。
5. 通过 `output/qwen_rsi_flow/paired-results.csv` 检查逐题状态。使用 `python qwen/export_paired_evidence.py <基准工作区>` 导出报告和官方 CTRF。

有效试次按任务、实例和流程哈希复用。复用记录保留原始运行来源。旧命令行试次由 `treatment_origin=cli` 标识。
