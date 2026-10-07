# 英语乐园 App

儿童平板英语学习端。服务器只提供课本、单词、MP3 和动画；本目录只在 Windows 本地运行和打包。

## 本地获取

```powershell
cd D:\dev\RuoYi-Vue3-FastAPI
git pull origin master
```

项目目录：`D:\dev\RuoYi-Vue3-FastAPI\ruoyi-english-app`。

## 安装工具

安装最新版 [HBuilderX](https://www.dcloud.io/hbuilderx.html) 和 Node.js 20 LTS，然后检查：

```powershell
node -v
npm -v
```

当前第一版只使用 uni-app 原生组件，HBuilderX 可直接运行，**不需要执行 `npm install`**。将来新增第三方包时才执行：

```powershell
npm install <包名> --save
```

不要复制或提交 `node_modules`、`unpackage`、APK 和签名文件。

## H5 与真机运行

1. 在 HBuilderX 选择“文件 → 导入 → 从本地目录导入”，选择本目录。
2. 确认首个页面是 `pages/learn/index`。
3. 选择“运行 → 运行到浏览器 → Chrome”测试 H5。
4. 选择“运行 → 运行到手机或模拟器”测试 Android。

检查乐园、学单词、小游戏、成长四个 Tab，并检查横屏、竖屏与重启后本地学习进度。

## 后端英语内容接口

后端前缀：`http://<服务器>/prod-api/english`

```text
GET /books
GET /units?bookId={bookId}
GET /words?unitId={unitId}
GET /media/{mediaId}
```

H5 开发时应配置本地代理避免跨域；APK 直接使用 HTTPS 线上地址。接口地址必须集中维护在英语 API 配置文件，不能散落在页面中。

## Android APK 打包

先修改 `manifest.json` 的名称、AppId、版本、图标、Android 包名和签名。之后在 HBuilderX：

```text
发行 → 原生 App-云打包 → Android
```

安装后验证：课本加载、MP3 播放、动画、缓存、横竖屏和重启后的学习进度。

## 提交

```bash
git add ruoyi-english-app
git commit -m "feat(english): 描述本次修改"
git push origin master
```

服务器不安装前端依赖、不编译、不打 APK。
