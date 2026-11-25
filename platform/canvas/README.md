# 原 RSI Flow Platform 画布联调

前端的 `frontend/week4` 对应原 `rsi-flow-platform/app/test/week4`。后端的 `Week4Canvas.java` 放在原 Spring Boot 项目的 `core-flow` 中，与 `Week4Resume.java` 同包。`flow-week4-canvas.json` 放在 `core-flow/src/main/resources/flow/Run`。将 `runner/` 下的两个 Python 文件放到已准备的基准工作区 `qwen` 目录。

前端开发服务配置 `RSI_FLOW_BACKEND_URL` 和 `RSI_WEEK4_TOKEN`，Spring Boot 配置相同令牌和 `RSI_WEEK4_BENCHMARK_HOME`，由后端进程读取 DashScope 凭证。当前本地联调使用前端 3020 和后端 39912。令牌仅由服务端转发。

打开 `/test/week4`，逐类保存画布，选择从原始输入运行或复核已有产物。页面返回 Spring Boot 分配的运行 ID。提交的画布、生成的执行配置和运行进度保存在基准工作区的 `output/qwen_rsi_flow/platform/<运行 ID>`。从原始输入运行的逐题记录用 `treatment_run` 关联 Qwen 试次与官方结果。

[平台运行证据](../../results/PLATFORM.md)
