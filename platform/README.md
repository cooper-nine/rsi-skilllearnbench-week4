# RSI FlowEngine 启动接口

这个目录保留 Qwen 复测的 RSI 后端启动器。加权 GDP 第 4 题使用过该启动链路。 [已验证的运行记录](../results/PLATFORM.md)

在配置好的 RSI Spring Boot 环境加载 `flow-week4-resume.json` 和 `Week4Resume.java`，为后端进程配置 `RSI_WEEK4_BENCHMARK_HOME` 与 `RSI_WEEK4_TOKEN`。基准工作区需要 Docker、Qwen 运行依赖和本地 API 凭证。在客户端终端设置同一个启动令牌后执行 `./platform/Invoke-Week4.ps1`，响应包含平台运行 ID。
