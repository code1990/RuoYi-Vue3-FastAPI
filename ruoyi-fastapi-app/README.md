# RuoYi-FastAPI-App

基于 `uni-app` 的 `vite` + `vue3` + `tailwindcss` 开发。

## 特性

- ⚡️ [Vue 3](https://github.com/vuejs/core), [Vite](https://github.com/vitejs/vite), [pnpm](https://pnpm.io/) - 快 & 稳定

- 🎨 [TailwindCSS](https://tailwindcss.com/) - 世界上最流行，生态最好的原子化CSS框架

- 😃 [集成 Iconify](https://github.com/egoist/tailwindcss-icons) - [icones.js.org](https://icones.js.org/) 中的所有图标都为你所用

- 📥 [API 自动加载](https://github.com/antfu/unplugin-auto-import) - 直接使用 Composition API 无需引入

- 🧬 [uni-app 条件编译样式](https://tw.icebreaker.top/docs/quick-start/uni-app-css-macro) - 帮助你在多端更灵活的使用 `TailwindCSS`

- 🦾 [TypeScript](https://www.typescriptlang.org/) & [ESLint](https://eslint.org/) & [Stylelint](https://stylelint.io/) - 样式，类型，统一的校验与格式化规则，保证你的代码风格和质量

## 快速开始

> [!IMPORTANT]
> 推荐使用 `"node": "^20.19.0 || >=22.12.0"` 的 Node.js 版本进行开发!
>
> 另外谨慎升级 `package.json` 中锁定的 `pinia`/`vue`/`@vue/*` 相关包的版本，新版本可能 `uni-app` 没有兼容，造成一些奇怪的 bug

## Windows 开发与 APK 打包（可直接复制）

### 0. 只需安装一次

1. 安装 [Node.js 20 LTS](https://nodejs.org/)，安装后关闭并重新打开 PowerShell。
2. 安装最新版 [HBuilderX](https://www.dcloud.io/hbuilderx.html)。

在 PowerShell 执行，输出的 Node 版本必须是 `v20.19.0` 或更高：

```powershell
node -v
corepack enable
```

### 1. 拉取代码并安装依赖

**不要在 `src` 目录执行 `npm install`。** 必须在 `ruoyi-fastapi-app` 根目录使用 pnpm。你的目录可直接复制以下命令：

```powershell
$project = "D:\dev\RuoYi-Vue3-FastAPI\ruoyi-fastapi-app"
Set-Location $project
git pull origin master
corepack pnpm@10.28.1 install
```

出现 `ERR_PNPM`、`node 不是内部或外部命令` 或安装失败时，不要进入 HBuilderX；先将完整错误复制出来处理。

### 2. 先在命令行验证编译

仍在同一个 PowerShell 窗口执行：

```powershell
pnpm build:app
```

必须看到命令正常结束（退出码为 `0`）才进行云打包。此命令只生成 App 资源，**不会**生成 APK。

如果依赖损坏或切换过 Node 版本，使用下面整段重装后，再执行 `pnpm build:app`：

```powershell
Set-Location "D:\dev\RuoYi-Vue3-FastAPI\ruoyi-fastapi-app"
Remove-Item -Recurse -Force node_modules
Remove-Item -Force pnpm-lock.yaml -ErrorAction SilentlyContinue
corepack pnpm@10.28.1 install
pnpm build:app
```

不要提交 `node_modules` 或本机生成的 `dist`、`unpackage` 目录。

### 3. HBuilderX 云打包 APK

1. 打开 HBuilderX，选择“文件 → 导入 → 从本地目录导入”，选择 `ruoyi-fastapi-app` 文件夹，**不要**选择 `src` 文件夹。
2. 在项目中打开 `src/manifest.json`，确认 Android 图标路径均为 `src/static/logo.png`，并确认该文件存在。
3. 若发布为独立 App，在 `src/manifest.json` 替换 `appid` 为自己申请的 DCloud AppID；测试可保留现有 AppID。
4. 选择“发行 → 原生 App-云打包 → Android”，架构勾选 `armeabi-v7a` 和 `arm64-v8a`；正式发布时填入自己的 Android 签名证书。
5. 项目接口地址已经固定为 `http://101.34.90.245/prod-api`。如 HBuilderX 出现 Android 网络安全/HTTP 明文访问选项，请开启它；服务器接入 HTTPS 后应将 `src/config.js` 改回 HTTPS 地址并关闭该选项。
6. 下载 APK，安装到手机，验证登录、首页、头像上传及接口访问。

### 4. HBuilderX 显示“编译失败”时

“项目编译失败”是状态行，不能说明故障原因。按下面顺序处理：

1. 先执行上面的 `pnpm build:app`。若失败，复制 PowerShell 从第一条 `ERROR` 开始的全部内容。
2. 若命令成功但 HBuilderX 失败，打开 HBuilderX 底部“控制台”，展开最后一次“发行/运行”任务，复制第一条 `ERROR` 及其后的完整堆栈。
3. 如果错误是图标不存在，执行：

```powershell
Test-Path "D:\dev\RuoYi-Vue3-FastAPI\ruoyi-fastapi-app\src\static\logo.png"
```

输出必须为 `True`；否则先执行 `git pull origin master`。
4. 不要只复制“项目编译失败”这一行；它没有包含可修复的信息。

### vscode

使用 `vscode` 的开发者，请先安装 [Tailwind CSS IntelliSense](https://marketplace.visualstudio.com/items?itemName=bradlc.vscode-tailwindcss) 智能提示与感应插件

其他 IDE 请参考: <https://tw.icebreaker.top/docs/quick-start/intelliSense>

### 更换 Appid

把 `src/manifest.json` 中的 `appid`, 更换为你自己的 `appid`, 比如 `uni-app` / `mp-weixin` 平台。

## 升级依赖

- `pnpm up:pkg` 升级除了 `uni-app` 相关的其他依赖
- `pnpm up:uniapp` 升级 `uni-app` 相关的依赖

推荐先使用 `pnpm up:pkg` 升级, 再使用 `pnpm up:uniapp` 进行升级，因为 `pnpm up:uniapp` 很有可能会进行版本的降级已达到和 `uni-app` 版本匹配的效果

## 切换镜像源

默认情况下，走的是淘宝镜像源 : `registry.npmmirror.com`

假如你需要修改镜像源，请修改目录下的 `.npmrc` 文件，然后重新进行 `pnpm i` 安装包即可

## 包管理器

本项目默认使用 `pnpm@10` 进行管理，当然你也可以切换到其他包管理器，比如 `yarn`, `npm`

你只需要把 `pnpm-lock.yaml` 删掉，然后把 `package.json` 中的 `packageManager` 字段去除或者换成你具体的包管理器版本，然后重新安装即可

### weapp-ide-cli

本项目已经集成 `weapp-ide-cli` 可以通过 `cli` 对 `ide` 进行额外操作

- `pnpm open:dev` 打开微信开发者工具，引入 `dist/dev/mp-weixin`
- `pnpm open:build` 打开微信开发者工具，引入 `dist/build/mp-weixin`

[详细信息](https://www.npmjs.com/package/weapp-ide-cli)

## tailwindcss 生态

详见：<https://github.com/aniftyco/awesome-tailwindcss>

你可以在这里找到许多现成的UI，组件模板。

## 单位转换

- `rem` -> `rpx` (默认开启, 见 `vite.config.ts` 中 `uvtw` 插件的 `rem2rpx` 选项)
- `px` -> `rpx` (默认不开启，可在 `postcss.config.ts` 中引入 `postcss-pxtransform` 开启配置)

## Tips

- 升级 `uni-app` 依赖的方式为 `npx @dcloudio/uvm` 后，选择对应的 `Package Manager` 即可。而升级其他包的方式，可以使用 `pnpm up -Li`，这个是 `pnpm` 自带的方式。
- 使用 `vscode` 记得安装官方插件 `stylelint`,`tailwindcss`, 已在 `.vscode/extensions.json` 中设置推荐
