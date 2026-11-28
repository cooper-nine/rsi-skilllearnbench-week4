# 架构与启动

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
