# Web 展示层设计补充

## 1. 背景与约束

- 当前对话环境缺少可运行的 `ruoyi-fastapi` Web 前端和 `codex-monitor` / FastAPI 后端服务。
- `RuoYi-Vue3-FastAPI` 仓库内只有 `ruoyi-fastapi-app`，它是 `uni-app` 载体，不等同于传统后台 Web 管理端。
- 由于服务器内存不足，前端实际开发不在服务器进行，而是在 Windows 机器上完成。
- 因此这里输出的是“可在其他对话直接复用的前端设计说明”，不是当前环境内直接联调实现。

## 2. 现状判断

### 2.1 已有后端能力

FastAPI 后端已经具备这些接口能力：

- `GET /codex/conversations/views`
- `GET /codex/conversations/{conversationId}/read-model`
- `GET /codex/conversations/{conversationId}/stream`
- `GET /codex/conversations`
- `GET /codex/conversations/{conversationId}`
- `GET /codex/conversations/{conversationId}/messages`
- `GET /codex/conversations/{conversationId}/events`
- `GET /codex/conversations/{conversationId}/tasks`
- `GET /stock/xg/night-super/cards`

并且已经有文档：

- `RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/docs/codex_read_model_api.md`
- `RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/docs/codex_conversation_migration.md`

### 2.2 缺失前端能力

当前仓库内没看到这些消费层代码：

- codex conversation 列表页
- codex conversation 详情页
- codex message / task / event 展示页
- codex 实时状态展示层
- 夜盘统计卡片页
- 菜单、路由、权限点接入
- 联调验收记录

## 3. 前端载体结论

### 3.1 推荐结论

新增独立的 Web 管理端载体，不建议把这套页面直接塞进现有 `ruoyi-fastapi-app`。

推荐载体：

- 新建 `ruoyi-fastapi-frontend` 或独立前端仓库
- 技术栈保持 Vue3 + Vite + RuoYi Web 管理端风格
- 在 Windows 机器开发、打包、联调

### 3.2 原因

`ruoyi-fastapi-app` 当前是 `uni-app` 结构，更偏移动端 / 小程序 / H5 多端容器，不适合作为这批后台管理页面的主载体，主要问题：

- SSE 支持和调试体验不如标准 Web 管理端稳定
- 列表页、详情页、表格、抽屉、多 Tab 这种后台交互在 uni-app 上维护成本更高
- 菜单、权限、后台布局体系不完整

### 3.3 保留方案

如果必须复用 `ruoyi-fastapi-app`，只建议做“只读简化版”：

- codex 列表页
- codex 详情页
- 夜盘卡片页

不建议在 `uni-app` 里优先做复杂的实时 SSE 管理页。

## 4. 页面设计

### 4.1 Codex 会话列表页

页面目标：

- 展示会话列表
- 支持分页、筛选、排序、关键字搜索
- 支持状态驱动展示
- 支持跳转会话详情

接口：

- 首选 `GET /codex/conversations/views`

表格列建议：

- 标题 `conversation.title`
- 会话ID `conversation.conversationId`
- 工作区 `conversation.workspaceId`
- 线程ID `conversation.threadId`
- 当前状态 `currentState.status`
- 当前阶段 `currentState.phase`
- 错误标记 `currentState.hasError`
- 活跃任务数 `currentState.activeTaskCount`
- 最新摘要 `historySummary.latestMessagePreview`
- 消息数 `historySummary.messageCount`
- 任务数 `historySummary.taskCount`
- 创建时间 `historySummary.startedAtMs` 或 `conversation.createdAtMs`
- 最后活跃时间 `currentState.lastActivityAtMs`
- 操作者 `conversation.operator`

筛选项建议：

- `workspaceId` / `workspaceIds`
- `operator`
- `status` / `statuses`
- `hasError`
- `searchText`
- `createdAtStartMs` / `createdAtEndMs`
- `updatedAtStartMs` / `updatedAtEndMs`

排序项建议：

- `updatedAtMs`
- `createdAtMs`
- `title`
- `status`
- `operator`
- `conversationId`

交互建议：

- 行点击进入详情页
- `hasError=true` 时高亮
- `isRunning=true` 时展示动态状态点
- 支持“仅看进行中”“仅看失败”“仅看有错误”

### 4.2 Codex 会话详情页

页面目标：

- 一次性展示 conversation 全量读模型
- 持续接收实时状态更新
- 支持按消息 / 任务 / 事件分区浏览

接口：

- 初始化：`GET /codex/conversations/{conversationId}/read-model`
- 实时更新：`GET /codex/conversations/{conversationId}/stream`

页面结构建议：

- 顶部摘要区
- 中部 Tab 区
- 右侧或底部状态区

顶部摘要区字段：

- 标题
- 会话状态
- 当前阶段
- 是否运行中
- 是否有错误
- 最新任务ID
- 最新事件类型
- 最后活跃时间
- 最终总结
- 最后错误

Tab 建议：

- `概览`
- `消息`
- `任务`
- `事件`
- `原始数据`

`概览` 展示：

- `conversation`
- `currentState`
- `historySummary`

`消息` 展示：

- 时间线
- 角色区分 `user/assistant/system`
- `messageType`
- `turnId`
- `payloadJson` 折叠展开

`任务` 展示：

- `taskId`
- `status`
- `createdThread`
- `submittedAtMs`
- `completedAtMs`
- `lastError`

`事件` 展示：

- `eventType`
- `eventStatus`
- `turnId`
- `createdAtMs`
- `payloadJson`

`原始数据` 展示：

- 直接显示 `/read-model` 返回 JSON
- 用于排查聚合逻辑和投影异常

### 4.3 Codex 消息页 / 任务页 / 事件页

不建议独立做三级菜单页面，优先作为会话详情页内部 Tab。

只有在这些场景才拆独立页：

- 数据量很大，需要独立查询和导出
- 需要跨 conversation 检索任务或事件
- 需要运维排查视图

### 4.4 夜盘统计卡片页

页面目标：

- 展示夜盘三维度超额统计卡片

接口：

- `GET /stock/xg/night-super/cards`

查询项：

- `tradeDate`
- `limit`

页面结构建议：

- 顶部日期切换
- 顶部数量切换 `3 / 10`
- 中部按 `signalName` 渲染卡片行
- 每行固定渲染 `240 / 60 / 300`

卡片字段：

- 是否存在 `exists`
- 维度标签 `label`
- 达标率 `okRate`
- 超额率 `superRate`
- 达标数量 `okCount`
- 超额数量 `superCount`
- 总数 `totalCount`
- 更新时间 `updatedAt`
- 空态原因 `emptyReason`

交互建议：

- 按 `rankScore` 默认降序展示
- 缺失维度卡片显示空态，不隐藏
- 提供“切换日期”和“展开更多”能力

## 5. 实时状态展示设计

### 5.1 首选方案

详情页使用 SSE。

消费接口：

- `GET /codex/conversations/{conversationId}/stream`

事件类型：

- `snapshot`
- `update`
- `ping`

前端处理原则：

- `snapshot` 作为首帧全量初始化
- `update` 作为全量替换，不做 patch 合并
- `ping` 仅更新时间或连接状态，不参与渲染

### 5.2 降级方案

如果浏览器环境、网关、代理或开发阶段不方便使用 SSE，则降级为轮询：

- 详情页轮询 `/read-model`
- 轮询间隔建议 `3s`
- 页面失焦后退化为 `10s`
- 页面隐藏时暂停

### 5.3 列表页实时策略

列表页不建议给每行开 SSE。

建议：

- 默认轮询 `/codex/conversations/views`
- 间隔 `10s`
- 提供“手动刷新”
- 只有详情页进入 SSE

## 6. API 契约接线设计

### 6.1 前端 API 模块拆分

建议目录：

- `src/api/codex/conversation.ts`
- `src/api/stock/nightSuper.ts`

建议方法：

- `getConversationViewList(params)`
- `getConversationDetail(conversationId)`
- `getConversationReadModel(conversationId)`
- `getConversationMessages(conversationId)`
- `getConversationTasks(conversationId)`
- `getConversationEvents(conversationId)`
- `createConversationStream(conversationId, options)`
- `getNightSuperCards(params)`

### 6.2 前端类型定义

建议目录：

- `src/types/codex.ts`
- `src/types/stock.ts`

重点类型：

- `CodexConversation`
- `CodexConversationCurrentState`
- `CodexConversationHistorySummary`
- `CodexConversationListRow`
- `CodexConversationReadModel`
- `CodexConversationMessage`
- `CodexConversationTask`
- `CodexConversationEvent`
- `StockNightSuperCards`

### 6.3 已确认字段契约

这几个字段必须按当前后端文档消费：

- `currentState.isRunning` 是布尔
- `currentState.hasError` 是布尔
- `historySummary.*Count` 是数值
- `tasks[].createdThread` 是布尔

不要再按旧语义把 `createdThread` 当字符串或线程 ID。

## 7. 菜单、路由、权限设计

### 7.1 菜单建议

一级菜单：

- `Codex监控`
- `股票统计`

二级菜单：

- `Codex会话`
- `夜盘统计`

### 7.2 路由建议

- `/codex/conversations`
- `/codex/conversations/:conversationId`
- `/stock/night-super`

### 7.3 权限点建议

菜单权限建议最小集：

- `codex:conversation:list`
- `codex:conversation:detail`
- `codex:conversation:stream`
- `stock:xgNight:view`

按钮级权限如果后续需要再加，不要一开始过度设计。

### 7.4 路由守卫

需要接入现有 Web 框架的：

- 登录态校验
- 动态菜单注入
- 权限点校验
- 404 / 无权限页

## 8. Windows 开发与无后端联调方案

### 8.1 本地开发建议

开发机器：

- Windows 本地

代码组织：

- 前端独立 repo 或独立目录
- 后端接口契约文档单独引用，不依赖服务器运行

### 8.2 无后端时的 Mock 策略

建议直接用静态 JSON mock，不引入额外复杂依赖。

建议目录：

- `src/mock/codex/conversation-views.json`
- `src/mock/codex/conversation-read-model.json`
- `src/mock/stock/night-super-cards.json`

策略：

- API 层加 `mock` 开关
- 开发初期先接静态 JSON
- 后续切到真实网关地址

### 8.3 SSE Mock 策略

没有真实 SSE 时：

- 用定时器模拟 `snapshot -> update -> ping`
- 本地生成状态变更样例
- 验证页面刷新、重连、错误态展示

## 9. 联调验收清单

### 9.1 Codex 列表页验收

- 能打开列表页
- 能分页
- 能按状态筛选
- 能按关键字搜索
- 能按最后活跃时间排序
- 有错误会话能高亮
- 进入详情页跳转正确

### 9.2 Codex 详情页验收

- 首次加载能完整拿到 `/read-model`
- SSE 首帧能渲染
- `update` 到达后页面能替换最新状态
- `ping` 不会导致页面闪烁
- 消息 / 任务 / 事件三个 Tab 展示正确
- `createdThread` 显示为“新建/复用”，不是字符串原样输出

### 9.3 夜盘卡片页验收

- 默认可展示最新交易日
- 切换 `tradeDate` 正常
- 切换 `limit` 正常
- 缺失维度卡片有空态展示

### 9.4 发布验收

- Windows 本地打包成功
- 发布脚本路径和产物目录明确
- 路由刷新不 404
- 菜单、权限点正常生效

## 10. 与 MySQL 新表的一致性要求

前端消费必须遵循后端投影契约，不直接猜字段。

已知需要重点关注的表：

- `conversation`
- `conversation_message`
- `conversation_event`
- `conversation_task`

当 daemon 写库字段发生变化时，必须同步检查：

1. FastAPI SQL DDL
2. Alembic migration
3. DO 模型
4. VO 模型
5. 聚合读模型文档
6. 前端类型定义
7. 前端展示文案

当前已知已修正的一致性点：

- `conversation_task.created_thread` 语义为布尔标记，不是线程 ID 字符串

## 11. 后续对话可直接复用的任务拆分

如果在另一个对话里继续做前端，可以直接按下面顺序推进：

1. 确认前端载体：独立 `ruoyi-fastapi-frontend`
2. 搭 API 模块和 TS 类型
3. 先用 mock JSON 跑通列表页
4. 接详情页和本地假 SSE
5. 接夜盘卡片页
6. 接路由、菜单、权限
7. 切真实 FastAPI 接口
8. 最后再接真实 codex-monitor SSE / 轮询联调

## 12. 结论

这批功能缺的不是后端接口，而是完整的 Web 消费层设计和载体决策。

最小正确路径不是在当前服务器硬补前端，而是：

- 在 Windows 上新建独立 Web 管理端
- 按已有 FastAPI 读模型文档接线
- 先 mock，后联调
- 详情页走 SSE，列表页走轮询
- 菜单、权限、路由按后台系统标准接入
