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

## 设计原则

- 以 `main.py` 作为单一入口，避免多入口导致流程分叉。
- 工作流统一使用一个 YAML，避免重复/失效配置。
- 数据目录集中为 `data/`，所有脚本通过参数共享同一输出目录。


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
