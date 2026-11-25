# RSI 平台与浏览器画布证据

用户确认四类流程的节点顺序、产物校验和定向回退规则。浏览器中的临时 RSI Flow Visual 前端呈现了四类流程的节点和连线。 [浏览器截图](qwen-canvas/)

加权 GDP 第 4 题的 Qwen 试点由 RSI Spring Boot FlowEngine 发起。后端启动请求返回运行 ID `fe6251b9-5511-47b8-baa5-8573bfbf2f91`。容器记录了四个节点推进，原版 verifier 通过 27/27，奖励为 1。 [后端响应](platform/launch-response.json) · [该题配对证据](paired-evidence/weighted-gdp-calculation-4/) · [平台运行日志](paired-evidence/weighted-gdp-calculation-4/treatment/platform-run.json)

此前九个精选试次由本地运行器发起 Qwen API 调用。以下另列原平台发起的两批运行。 [逐题结果](comparison.csv)


## 原平台测试页联调

原 `rsi-flow-platform` 项目新增 `/test/week4`。在浏览器保存四类画布后，“复核已有产物”把画布提交给真实 Spring Boot FlowEngine。后端按画布连线调用 Qwen 对既有节点产物复核，再逐题执行原版 Docker verifier。平台复核运行 `a2607d7e-fcb6-431a-b9f5-c8c31b1a84a3` 的十份官方报告均通过。部分 Qwen 自检发现旧试次缺少中间字段，逐题追踪文件保留了这些失败。 [提交的画布和十份官方报告](platform/canvas-recheck/)

“从原始输入运行十题”使用保存的画布建立逐题执行配置，在任务容器中调用 Qwen 重新生成产物。运行编号 `8cc89b7b-87d9-471f-bbae-121cb277c042`，首批结束后，地震和两道金融题取得正式失败判分，GDP 第 1、5 题执行超时，GDP 第 4 题和四道股票题因 API 502 中断。 [原始输入批次记录](platform/canvas-fresh/)

股票第 4 题从原平台补跑后，首次生成页面通过 13/16。沿用这次新生成的源码，Qwen 从交互节点定向续修两次，分别通过 15/16 和 16/16。最终运行编号 `fce9bbfe-4735-4d06-b31e-fb5a0aacba8e`，原版官方脚本奖励为 1。 [三次试次和原始官方报告](platform/stock-4/)

### Qwen 接入与判分边界

浏览器保存用户确认的节点和连线后，经原前端服务提交给 Spring Boot FlowEngine。FlowEngine 启动本地受预算约束的 Qwen API 运行器。模型为 `qwen3.5-plus`、温度为 0。业务节点执行模型生成的操作，前一节点的输出作为后续节点输入。工作簿、数据文件和网页的最终正确性由原版 Docker verifier 判定。节点格式校验和定向重试用于流程控制。

旧模型产物的 10/10 复核、有真实新生成与续修并通过的个案、原始输入批次中的失败与中断，分别保留各自的官方结果。当前证据尚无法证明十题均从原平台重新生成并通过。

金融第 3 题由原 Next.js 启动接口转交 Spring Boot，提交的是浏览器保存的画布。运行编号 `163a5035-6444-40fc-847a-8544edbe4fb1`。识别、计算和核对三个业务节点均分别调用 Qwen，使用原始 13F 数据生成新答案。官方判分 2/2，奖励为 1。 [画布、节点记录和官方报告](platform/finance-3/)
