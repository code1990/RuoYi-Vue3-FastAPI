# Windows 打包 Android APK

此项目已是 Vue 3 UniApp，直接用 HBuilderX 打包，不需要把 `ruoyi-uniapp.zip` 的英语学习页面或旧依赖复制进来。

1. Windows 拉取本仓库，使用 HBuilderX 导入 `ruoyi-fastapi-app` 目录。
2. 在 HBuilderX 中打开 `src/manifest.json`：需要独立应用时先申请并替换 `appid`；确认 Android 图标和版本号。
3. 选择“发行 → 原生 App-云打包”，平台选 Android，架构保留 `armeabi-v7a`、`arm64-v8a`，按需配置自己的证书后生成 APK。
4. 安装到真机验证登录、头像上传和接口访问。

开发运行时接口为 `http://localhost:9099`；生产构建自动使用 `https://vfadmin.insistence.tech/prod-api`，因此 APK 不会尝试访问手机自身的 localhost。若部署地址变更，只修改 `src/config.js` 的生产地址后重新云打包。

命令行的 `pnpm build:app` 仅生成 App 资源；最终签名 APK 仍在 HBuilderX 的原生 App 云打包流程生成。
