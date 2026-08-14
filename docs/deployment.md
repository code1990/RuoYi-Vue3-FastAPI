# 部署说明

生产环境不使用 Docker。Nginx 静态目录为 `/usr/share/nginx/html/fastapi`，`/prod-api/` 代理到 `127.0.0.1:9099`；`ruoyi-fastapi.service` 运行后端。

## 前端（Windows 构建，服务器发布）

Windows 拉取最新代码后，在仓库根目录运行：

```bat
build_frontend_pro_zip.bat
```

将 `%USERPROFILE%\Downloads\ruoyi-fastapi-frontend-dist.zip` 上传到服务器 `/root/project/ruoyi-fastapi-frontend-dist.zip`，然后运行：

```bash
cd /root/project/RuoYi-Vue3-FastAPI
chmod +x deploy_fastapi_frontend.sh
./deploy_fastapi_frontend.sh
```

脚本兼容 Windows `Compress-Archive` 生成的 ZIP 路径，完成后校验首页和 `/prod-api`，并删除已成功发布的 ZIP。若位置不同，使用 `ZIP_FILE=/path/to/package.zip ./deploy_fastapi_frontend.sh`。

## 后端（服务器发布）

确认 `.env.prod` 中的生产配置、MySQL/Redis 可用且 `STOCK_STAT_DB_PATH` 对服务进程可读，然后运行：

```bash
cd /root/project/RuoYi-Vue3-FastAPI
chmod +x deploy_fastapi_backend.sh
./deploy_fastapi_backend.sh
```

脚本会快进拉取 `master`、安装 `requirements.txt`、重启并直接校验 `ruoyi-fastapi.service`。默认 Python 是 `/root/.venv/bin/python`；需要覆盖时：

```bash
PYTHON=/path/to/python SERVICE_NAME=ruoyi-fastapi.service ./deploy_fastapi_backend.sh
```

日志查看：

```bash
journalctl -u ruoyi-fastapi.service -f
```
