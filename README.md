# RuoYi-Vue3-FastAPI

本项目是量化数据 Web 平台：RuoYi 提供用户、权限、菜单和 Web API；`stock_cron` 负责行情抓取、计算和 SQLite 数据落库。

## 运行架构

```text
服务器
stock_cron ──抓取、计算、定时调度──> SQLite
                                      │ 只读
FastAPI ──MySQL（用户、权限、菜单）──> Web API ──> Nginx ──> 浏览器

Windows
Vue3 前端开发、构建 dist、发布静态文件到服务器
```

职责边界必须保持清晰：

- `stock_cron`：唯一的数据抓取与计算入口；写入 SQLite。
- `ruoyi-fastapi-backend`：只读 SQLite，为 Web 提供分页、筛选和权限保护的接口；MySQL 只保存用户、角色和菜单。
- `ruoyi-fastapi-frontend`：Windows 上开发；通过 `/prod-api` 调用服务器接口，不直接读取 SQLite。

本项目**不使用 Docker 部署**。

## 目录

```text
ruoyi-fastapi-backend/   服务器 FastAPI 服务、MySQL 菜单迁移、SQLite 只读接口
ruoyi-fastapi-frontend/  Windows Vue3 前端
../stock_cron/           服务器定时抓取、信号计算、SQLite 数据库和调度文档
```

## 服务器：数据计算与调度

`stock_cron` 是业务数据的核心。所有行情抓取、两融排名、组合排名与收益回填都在服务器运行并写入 SQLite；Web 服务不重复计算。

两融任务的当前调度示例：

```cron
15 9 * * 1-5 flock -xn /tmp/insert_stock_margin_trading.lock -c 'cd /root/project/stock_cron && mkdir -p logs && /root/.venv/bin/python insert_stock_margin_trading.py --wait-for-update --report >> logs/insert_stock_margin_trading_stdout.log 2>&1'
30 9 * * 1-5 flock -xn /tmp/update_stock_margin_rank_performance.lock -c 'cd /root/project/stock_cron && mkdir -p logs && /root/.venv/bin/python update_stock_margin_rank_performance.py --skip-performance >> logs/update_stock_margin_rank_performance_stdout.log 2>&1'
10 23 * * 1-5 flock -xn /tmp/update_stock_signal_performance.lock -c 'cd /root/project/stock_cron && mkdir -p logs && /root/.venv/bin/python update_stock_signal_performance.py --target-percent 2.0 >> logs/update_stock_signal_performance_stdout.log 2>&1'
```

完整任务说明、依赖顺序和日志位置见 [`stock_cron/develop_crontab.md`](../stock_cron/develop_crontab.md)。修改计算规则后，先在 `stock_cron` 验证 SQLite 结果，再扩展 Web 接口。

## 服务器：后端开发与部署

一键部署流程见 [`docs/deployment.md`](docs/deployment.md)。

后端运行目录为 `ruoyi-fastapi-backend`，生产配置为 `.env.prod`。SQLite 路径通过 `STOCK_STAT_DB_PATH` 配置；该路径必须指向 `stock_cron` 生成的数据文件，并对服务进程可读。

安装或更新依赖：

```bash
cd /root/project/RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend
/root/.venv/bin/pip install -r requirements.txt
```

服务由 systemd 管理：

```ini
# /etc/systemd/system/ruoyi-fastapi.service
[Service]
WorkingDirectory=/root/project/RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend
ExecStart=/root/.venv/bin/python3 app.py --env prod
Restart=always
```

后端发布流程：

```bash
cd /root/project/RuoYi-Vue3-FastAPI
git pull --ff-only origin master
cd ruoyi-fastapi-backend
/root/.venv/bin/pip install -r requirements.txt
python -m pytest -q tests/test_stock_margin_controller.py
systemctl restart ruoyi-fastapi.service
systemctl is-active ruoyi-fastapi.service
curl -fsS http://127.0.0.1:9099/docs >/dev/null
```

日志与状态：

```bash
systemctl status ruoyi-fastapi.service
journalctl -u ruoyi-fastapi.service -f
```

Nginx 将 `/prod-api/` 反向代理到 `127.0.0.1:9099/`。变更 Nginx 配置后先运行 `nginx -t`，再执行 `systemctl reload nginx`。

## Web 接口约定

后端只暴露已经由 `stock_cron` 计算完成的数据。接口使用 `/prod-api` 前缀，由 Nginx 转发。

两融组合排名接口：

```text
GET /prod-api/stock/margin/combo/list?windowDays=2&pageNum=1&pageSize=20
```

- `windowDays`：仅 `2`、`3`、`5`，对应最近 2/3/5 个交易日的综合排名。
- `startDate`、`endDate`：可选，格式 `YYYYMMDD`。
- 返回 `rows`、`total`、`pageNum`、`pageSize`、`hasNext`。
- 收益字段未完成回填时返回 `null`，前端显示 `-`。

组合的计算与页面字段约定见 [`stock_cron/docs/margin_combo_web.md`](../stock_cron/docs/margin_combo_web.md)。新增策略时优先扩展 SQLite 表和一个参数化接口，不复制表、Controller 或页面。

## Windows：前端开发与发布

Windows 只负责 `ruoyi-fastapi-frontend`。开发时配置 API 指向服务器，或用本地 Vite 代理；不在 Windows 上运行 `stock_cron` 和生产 FastAPI。

```bash
cd ruoyi-fastapi-frontend
yarn
yarn dev
```

接口封装位于 `src/api/`。新增页面先对接服务器已有接口，再提交前端代码；菜单由后端 MySQL 迁移创建，路由参数可用于复用页面，例如 `windowDays=2`、`3`、`5`。

前端发布流程：

```bash
cd ruoyi-fastapi-frontend
yarn build:prod
```

将生成的 `dist/` **内容**上传到服务器 Nginx 静态目录：

```text
/usr/share/nginx/html/fastapi/
```

上传后检查页面和 `/prod-api` 请求；静态文件更新通常不需要重启 FastAPI 或 Nginx。若修改 Nginx 配置，执行：

```bash
nginx -t && systemctl reload nginx
```

## 提交约定

- `stock_cron` 与本仓库分别提交、分别推送。
- 后端 API、MySQL 菜单迁移和前端 API 定义保持同一提交语义。
- 发布前确认工作区干净，使用 `git pull --ff-only`，避免服务器上产生合并提交。

### 服务端提交范围

服务器工作副本可提交 `ruoyi-fastapi-backend/**`（含测试）、`ruoyi-fastapi-frontend/**` 及根目录、`.github/**`、`scripts/**` 等服务器配置。前端源码在服务器开发和提交，Windows 仅负责构建并发布 `dist`；`ruoyi-fastapi-app/**`、`ruoyi-fastapi-test/**` 仍在 Windows 工作副本开发和提交。

首次在服务器安装提交检查：

```bash
./scripts/install-server-git-hooks.sh
```

该检查只阻止受限目录进入提交，不阻止查看或临时编辑。紧急修复需要明确绕过时使用 `git commit --no-verify`。
