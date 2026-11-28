# 架构与启动

## 指定前后端逐题复测

按下文启动 Spring Boot 和前端，前端设置 `RSI_WEEK4_TOKEN` 与 `RSI_FLOW_BACKEND_URL`。后端配置同一令牌、可用的百炼 Key 和已准备的 `RSI_WEEK4_BENCHMARK_HOME`。开启 Docker Linux 引擎。然后从总交付仓库运行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run-platform-cases.ps1 -FrontendCases ..\rsi-data-platform\examples\week4 -BenchmarkHome ..\upstream-sparse
```

脚本按 case01–case10 逐题向指定前端提交 `fresh` 请求，核对 Spring Boot 返回的运行 ID 与落盘画布，等待本次运行结果。所有选中题均取得官方通过时返回退出码 0。可加 `-CaseNumber 1` 单题检查。运行阶段调用 Qwen 并执行 Docker 原版判分。归档回放及 Next.js 本地实跑入口供讲解与排查使用，正式复测使用本节的 Spring Boot 路径。

## 评审快速启动

Windows 机器安装 Git、Node.js 24 和 Python 3.11 或更新版本。在有空间的磁盘目录执行：

```powershell
git clone https://github.com/cooper-nine/rsi-skilllearnbench-week4
Set-Location rsi-skilllearnbench-week4
powershell -NoProfile -ExecutionPolicy Bypass -File .\review.ps1
```

脚本会在同一磁盘的 `.review` 下获取前端和 Visual，安装锁定的前端依赖并启动本机页面。打开 `http://127.0.0.1:3020/test/week4`，默认地震画布可直接点「回放节点归档」。页面按真实画布的连线校验顺序。展开每个节点可看子 Skill、输入输出契约和该节点的历史 Qwen 产物，并核对归档官方报告。切换任务类型可以验证其他画布。

### 重新从原始输入执行

启动 Docker Desktop，先在当前终端通过自己的脚本或凭证配置设置 `DASHSCOPE_API_KEY`，然后执行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\review.ps1 -Live
```

初次运行会准备原始基准数据、Python 环境和十题 Docker 镜像。已有准备好的环境可加 `-BenchmarkHome <基准目录>`。打开同一画布页面，保存四类画布，选择一道题并点「从原始输入运行」。页面显示运行 ID，结束后显示本次官判。逐节点产物和失败诊断写在运行 ID 对应的目录。

评审实跑由本机 Next.js 启动同一个 Python 流程运行器，再逐节点调用 Qwen 并运行原版 Docker 验收。下文另有历史正式实验使用的 Spring Boot 启动方法，适合验证 FlowEngine 接入。

评审实跑验证中，股票第 4 题重新调用 Qwen 完成四类节点，原版脚本判为 13/16，奖励为 0。未通过项为原始数据子目录、ETF 与普通股票提示框和市值格式。归档回放中该题保留先前正式验收的 16/16。 [本次四节点记录](results/reviewer-smoke/stock-4/run.json) · [本次官方报告](results/reviewer-smoke/stock-4/ctrf.json)

## 正式实验架构

1. Next.js 的 `/test/week4` 使用 Visual 画布呈现四类人工流程。页面把已保存的画布和所选题目提交给本机 Next.js 路由。
2. Next.js 把请求转给 Spring Boot 的 `/api/engine/flow`。FlowEngine 调用 `RSI_WEEK4_CANVAS`，校验本地令牌，写下画布并启动 Python 运行器，返回运行 ID。
3. Python 决定节点顺序并组装 Skill 提示词和上游产物。业务节点调用 Qwen 3.5 Plus，将模型提供的操作在题目 Docker 容器中执行。节点失败反馈给模型继续修正，运行记录按次保存。
4. Docker 在最终产物上运行固定提交的原版 `test.sh`。根据运行 ID 在基准工作区的 `output/qwen_rsi_flow/platform` 找到运行进度。正式判分证据是 CTRF 和 `reward.txt`。后端通用循环框架的实验是独立提交，四周验收所用的节点循环在 Python 运行器。

## 已有 E 盘工作区

启动 Docker Desktop，并等 `docker info` 成功。后端 IDEA 运行 `core-test` 模块的 `AppTestStarter`，具体配置见[后端启动说明](https://github.com/cooper-nine/rsi-data-spring-boot/blob/main/WEEK4.md)。设置 `RSI_WEEK4_BENCHMARK_HOME=E:/SkillLearnBench-Workspace/upstream-sparse`。前端进入现有 `rsi-flow-platform`，按[前端启动说明](https://github.com/cooper-nine/rsi-data-platform/blob/main/WEEK4.md)启动。前后端使用相同的本地随机令牌，百炼 Key 仅由后端进程读取。

## 新机器安装

使用 Java 8、Maven 3.9、Node 24.15.0、pnpm 10.34.9、Python 3.11 或更高版本、Git LFS 及 Docker Desktop Linux 容器。后端 Maven 依赖需要课程仓库的访问配置。建议在 E 盘同一个父目录执行以下命令。

```powershell
git lfs install
git clone https://github.com/cooper-nine/rsi-data-spring-boot
git clone https://github.com/cooper-nine/rsi-data-platform
git clone https://github.com/cooper-nine/rsi-data-visual rsi-flow-visual
git clone https://github.com/cooper-nine/rsi-skilllearnbench-week4
python .\rsi-skilllearnbench-week4\prepare.py --workspace .\upstream-sparse --install --build-images
```

构建首次下载十题数据和 Docker 依赖。以同级 `upstream-sparse` 的绝对路径和自己的百炼 Key 配置后端，再按两个仓库的 `WEEK4.md` 启动。默认运行预算上限为 20 元，账本位于基准工作区的 `output/qwen_budget_campaign`。历史检查点续跑需要保留原机器的运行目录。

若 GitHub 大文件下载中断，可用 `--source <已有基准仓库路径>` 从含固定提交的本地仓库准备另一个空目录。若只有 Docker 镜像构建中断，在已准备好的目录上运行 `python .\rsi-skilllearnbench-week4\prepare.py --workspace .\upstream-sparse --images-only`。

打开 `http://127.0.0.1:3020/test/week4`，保存四类画布，选一道题从原始输入运行。拿到运行 ID 后查看该目录的 `runner.log` 和 `results.json`。页面上的「复核已有产物」和历史股票补跑使用既有产物或历史检查点，首次复现请使用原始输入入口。历史实际结果见[逐题验收](results/platform/ACCEPTANCE.md)。

## 发布验证

- 从公开仓库重新克隆前端与 Visual，通过 `pnpm install --frozen-lockfile` 和 `pnpm build`。
- 从公开仓库重新克隆后端，使用已配置的课程 Maven 依赖通过 12 个模块编译并启动。通过前端路由提交画布取得 FlowEngine 运行 ID，后端写入运行目录。这次启动检查未提供模型 API Key。
- 使用归档的 Qwen 产物，重新执行股票第 4 题的原版 Docker 判分，16 项全部通过，奖励为 1。独立循环框架测试通过 5 项。十题正式验收为先前逐题完成的 10/10。
- 从本机缓存的固定基准提交准备了独立工作区，安装了锁定的 Python 依赖并核对原题文件。直接从 GitHub 下载原始大文件的首次验证遇到连接中断。
