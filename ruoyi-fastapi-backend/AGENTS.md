# 服务端开发范围

前后端源码均可在服务器工作副本开发和提交，包括后端测试与 `ruoyi-fastapi-frontend/**`。

前端不在服务器安装依赖或构建；由 Windows 拉取前端源码后执行构建，并将 `dist` 发布到服务器。`ruoyi-fastapi-app/**` 与 `ruoyi-fastapi-test/**` 仍仅在 Windows 工作副本开发。
