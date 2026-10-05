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

## Windows 开发与 APK 打包

1. 安装 Node.js 20.19+ 和最新版 HBuilderX，使用终端进入本目录后执行 `corepack enable`、`pnpm install`。
2. 先执行 `pnpm build:app`。该命令成功才继续使用 HBuilderX 云打包；它只生成 App 资源，不生成签名 APK。
3. 用 HBuilderX 导入 `ruoyi-fastapi-app` 目录，打开 `src/manifest.json`，选择“发行 → 原生 App-云打包 → Android”。首次发布前替换自己的 AppID 和签名证书。
4. 生产 APK 接口为 `http://101.34.90.245/prod-api`。云打包时需在 Android 配置中允许 HTTP 明文网络访问；该服务接入 HTTPS 后应改回 HTTPS。

### 编译失败排查

- 仅显示“项目编译失败”不能定位原因。请在 HBuilderX 底部“控制台”展开本次任务，复制第一条 `ERROR` 及其后完整堆栈。
- 删除 Windows 本机 `node_modules` 后重新执行 `pnpm install`，不要把 `node_modules` 提交到 Git。
- 确认 HBuilderX 使用的 Node.js 路径为 Node 20.19+，并重新执行 `pnpm build:app`；若命令失败，优先按命令输出修复。
- 若 HBuilderX 仍提示图标文件不存在，确认已拉取提交 `6925be4` 或更新版本，并在项目根目录检查 `src/static/logo.png` 是否存在。

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
