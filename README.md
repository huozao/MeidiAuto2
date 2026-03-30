# MeidiAuto2

用于在 GitHub Actions 或本地执行的库存自动化流水线。

## 目录结构

- `main.py`：统一编排入口，按顺序执行各子脚本。
- `script/`：业务脚本（下载邮件、合并 Excel、计算与着色、生成 HTML、发送邮件）。
- `.github/workflows/run-daily.yml`：标准化 CI 运行工作流（支持手动+定时）。
- `requirements.txt`：Python 依赖。

## 运行方式

### 本地运行

```bash
python -m pip install -r requirements.txt
python main.py --check
python main.py --data-dir data --stop-on-error --report-file data/run-report.json
```

推荐按“由浅到深”验证：

1. `python main.py --check`：检查脚本是否齐全、环境变量是否就绪。
2. `python main.py --dry-run`：确认执行顺序和参数无误。
3. `python main.py --data-dir data-local --stop-on-error --report-file data-local/run-report.json`：做一次完整联调并保留报告。

## 新手说明：`--dry-run` 到底是什么？

你可以把 `--dry-run` 理解成“**演习模式**”：

- 会把“将要执行哪些步骤”打印出来；
- **不会真正执行**下载邮件、处理 Excel、发邮件等动作；
- 适合第一次上手时确认流程是否正确。

对比：

- `python main.py --dry-run`：只看计划，不改任何文件；
- `python main.py --check`：检查环境变量和脚本是否存在；
- `python main.py ...`（不带 `--dry-run`）：真正执行流程。

建议新手顺序：先 `--check`，再 `--dry-run`，最后正式执行。

如果你要手动清理测试产物或自动运行后的冗余文件，可用：

- `python main.py --clean-only`：只执行 `script/010 clean.py`；
- `python main.py --clean-after-run --stop-on-error`：主流程结束后追加执行 `010 clean.py`。

运行结果重点看 3 个点：

- 进程退出码是否为 `0`；
- 汇总区是否出现失败步骤；
- `run-report.json` 中 `success` 是否为 `true`、`failed_steps` 是否为空数组。

### Windows 编码问题说明（UnicodeDecodeError: gbk）

若在 Windows/PyCharm 中看到 `UnicodeDecodeError: 'gbk' codec can't decode ...`，通常是子脚本输出编码与父进程解码编码不一致导致。当前 `main.py` 已改为二进制捕获并自动尝试 `utf-8`/`gbk` 解码，减少该类报错对联调的干扰。

### Docker 运行（推荐用于环境一致性验证）

可以。把项目拉到 Docker 后同样能跑，且更接近 CI 环境。示例：

```bash
docker run --rm -it \
  -v "$PWD":/app \
  -w /app \
  -e EMAIL_ADDRESS_QQ=xxx \
  -e EMAIL_PASSWORD_QQ=xxx \
  -e IMAP_SERVER=imap.qq.com \
  python:3.12 bash -lc "pip install -r requirements.txt && python main.py --check && python main.py --data-dir data-docker --stop-on-error --report-file data-docker/run-report.json"
```

### 新手版：Docker 从拉取到运行（一步一步）

1. **拉取 Python 镜像**

```bash
docker pull python:3.12
```

2. **进入项目目录**（里面要有 `main.py` 和 `requirements.txt`）

```bash
cd MeidiAuto2
```

3. **运行容器并执行流水线**

```bash
docker run --rm -it \
  -v "$PWD":/app \
  -w /app \
  -e EMAIL_ADDRESS_QQ=你的邮箱 \
  -e EMAIL_PASSWORD_QQ=你的授权码 \
  -e IMAP_SERVER=imap.qq.com \
  python:3.12 bash -lc "pip install -r requirements.txt && python main.py --check && python main.py --dry-run"
```

4. **确认无误后再执行正式跑**

```bash
docker run --rm -it \
  -v "$PWD":/app \
  -w /app \
  -e EMAIL_ADDRESS_QQ=你的邮箱 \
  -e EMAIL_PASSWORD_QQ=你的授权码 \
  -e IMAP_SERVER=imap.qq.com \
  python:3.12 bash -lc "pip install -r requirements.txt && python main.py --data-dir data-docker --stop-on-error --clean-after-run --report-file data-docker/run-report.json"
```

5. **查看结果文件**

- `data-docker/run-report.json`：最终成功/失败报告；
- 若启用了 `--clean-after-run`，会在主流程后执行 `010 clean.py` 做清理。

若需要在容器中一并清理产物，可在末尾追加：

```bash
python main.py --data-dir data-docker --stop-on-error --clean-after-run --report-file data-docker/run-report.json
```

### GitHub Actions 自动运行

仓库已提供 `.github/workflows/run-daily.yml`，支持两种触发方式：

- `workflow_dispatch`：在 Actions 页面手动点击运行；
- `schedule`：按 cron 自动定时运行（当前配置是每天 UTC 11:00）。

首次启用前，请在仓库 `Settings -> Secrets and variables -> Actions` 中配置：

- `EMAIL_ADDRESS_QQ`
- `EMAIL_PASSWORD_QQ`（或兼容旧变量 `EMAIL_PASSWOR_QQ`）
- `IMAP_SERVER`（可选）

### GitHub Actions 与本地是否可同时运行

可以同时进行：

- 远端 GitHub Actions 在 GitHub Runner 上执行；
- 本地运行在你自己的电脑上执行。

两者互不阻塞，但建议注意以下事项：

- 两边都在读同一邮箱时，可能出现重复下载/重复处理；
- 建议本地测试时使用独立 `--data-dir`（例如 `data-local`）；
- 若需避免同一时段重复发送邮件，可将本地运行设置为 `--dry-run` 先验证流程。

### 仅查看执行计划

```bash
python main.py --dry-run
```

## 必需环境变量

- `EMAIL_ADDRESS_QQ`
- `EMAIL_PASSWORD_QQ`（兼容历史变量 `EMAIL_PASSWOR_QQ`）
- `IMAP_SERVER`（可选，默认 `imap.qq.com`）

## `.env` 安全与联调建议

不建议把真实 `.env` 文件直接发给任何人（包括我），避免密码与邮箱凭据泄露。

你截图这个页面（`Settings -> Secrets and variables -> Actions`）**不是上传 `.env` 文件本身**，而是把 `.env` 里的每个键值拆开，分别配置成 GitHub Secrets（这是正确位置）。

推荐做法：

1. 本地创建 `.env` 并自行保管（加入 `.gitignore`，不要提交到仓库）。
2. 我可以基于你提供的**脱敏样例**帮你检查格式是否正确，例如：

```env
EMAIL_ADDRESS_QQ=demo@example.com
EMAIL_PASSWORD_QQ=********
IMAP_SERVER=imap.qq.com
```

3. 本地验证时先跑：

```bash
python main.py --check
python main.py --dry-run
```

4. 再执行完整链路（建议先用独立数据目录）：

```bash
python main.py --data-dir data-local --stop-on-error --report-file data-local/run-report.json
```

5. 若要云端验证，把同名变量配置到 GitHub Secrets，然后手动触发 `run-daily.yml` 的 `workflow_dispatch`。

可按下列映射填写：

- `.env` 的 `EMAIL_ADDRESS_QQ=xxx` -> GitHub Secret 名称：`EMAIL_ADDRESS_QQ`
- `.env` 的 `EMAIL_PASSWORD_QQ=xxx` -> GitHub Secret 名称：`EMAIL_PASSWORD_QQ`
- `.env` 的 `IMAP_SERVER=imap.qq.com` -> GitHub Secret 名称：`IMAP_SERVER`（可选）

## 设计原则

- 以 `main.py` 作为单一入口，避免多入口导致流程分叉。
- 工作流统一使用一个 YAML，避免重复/失效配置。
- 数据目录集中为 `data/`，所有脚本通过参数共享同一输出目录。

## 代码质量简评

整体评价：**中上（7.5/10）**，已经具备可维护流水线项目的核心骨架。

优点：

- 有统一编排入口（`main.py`），步骤顺序清晰，避免“脚本各跑各的”。  
- 参数化较完整（`--check` / `--dry-run` / `--stop-on-error` / `--report-file`），便于本地与 CI 共用。  
- 有最基本的可观测性：步骤耗时、失败列表、JSON 报告。  
- 兼容历史环境变量名（`EMAIL_PASSWORD_QQ|EMAIL_PASSWOR_QQ`），降低迁移成本。  

可改进点：

- 当前步骤间通过“文件约定”耦合，建议逐步补充输入/输出契约文档。  
- 缺少自动化测试（至少应补 1 组 smoke test 和 1 组失败场景测试）。  
- 失败重试策略还比较薄弱（网络/邮箱抖动时可加可配置重试）。  
- 日志结构化程度一般，后续可考虑标准 logging + 统一字段。  

## `main.py` 为什么要这样写

`main.py` 采用“编排器（orchestrator）”模式，核心目的不是承载业务细节，而是把多脚本流水线的**执行顺序、错误策略、运行入口**统一起来：

1. **单一入口，减少分叉**  
   通过 `PIPELINE_STEPS` 固化步骤顺序，避免本地、CI、临时脚本三套流程不一致。

2. **检查与执行分离**  
   `--check` 只做前置校验，`--dry-run` 只看计划，正式执行再真正跑子脚本，便于快速定位问题来源。

3. **统一错误处理策略**  
   每步都走同一套 `run_step`，可在 `--stop-on-error` 下快速失败，也可完整跑完后统一汇总失败列表。

4. **统一数据目录与报告出口**  
   所有步骤共享 `--data-dir`，并可输出 `--report-file`，方便本地复现与 CI 归档。

5. **兼容历史系统**  
   环境变量读取支持新旧键名，既保证演进，也避免“一次性切换”造成线上失败。


## 兼容说明

- 已保留历史脚本与备用 workflow（`run_script.yml`）用于回归验证。
- 默认生产链路仍以 `main.py` + `run-daily.yml` 为准，历史脚本不在默认编排步骤内。


## 运行前检查

```bash
python main.py --check
```

用于验证：
- 核心脚本是否存在；
- 必需环境变量是否已配置。

## 运行报告

可通过 `--report-file` 输出一次运行的 JSON 报告，便于追踪失败步骤。

## 常见问题：出现 `Accept current/incoming/both changes` 是什么？

这是 **Git 合并冲突（merge conflict）**，不是运行错误。通常出现在你本地分支和远端分支都改了同一段代码时。

- `Accept current change`：保留你当前分支的代码；
- `Accept incoming change`：保留对方（要合并进来）分支的代码；
- `Accept both changes`：两边都保留（随后通常还要手动整理一次）。

你**不需要去网页上“确认提交代码”**，而是要先在本地把冲突处理完，再提交：

```bash
git add <冲突文件>
git commit -m "resolve merge conflict"
git push
```

建议流程（新手版）：

1. 先看冲突文件里 `<<<<<<<`, `=======`, `>>>>>>>` 三段标记；
2. 选 current / incoming / both 其中一种；
3. 删除冲突标记并保证代码可运行；
4. 再执行一次 `python main.py --dry-run` 和 `python main.py --check`；
5. 最后 `git add` + `git commit` + `git push`。
