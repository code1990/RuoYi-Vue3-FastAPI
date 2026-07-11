# Codex Read Model API

本文档定义 `module_codex` 对前端开放的读接口契约，以及它与 `CodexMonitor daemon -> MySQL -> FastAPI` 投影链路的边界。

## 1. 用哪个接口

默认只区分两类读接口：

- 聚合读模型：给前端页面直接消费
- 原始表读取：给排障、导出、核对投影使用

前端页面默认使用聚合接口，不要自己在前端拼 `/messages + /events + /tasks`。

## 2. 响应包裹

普通 JSON 接口统一使用项目响应包裹。

分页接口：

```json
{
  "code": 200,
  "msg": "查询成功",
  "rows": [],
  "total": 0
}
```

详情接口：

```json
{
  "code": 200,
  "msg": "操作成功",
  "data": {}
}
```

SSE 接口不使用该包裹，直接输出 `text/event-stream`。

## 3. 前端主消费接口

### 3.1 列表页

`GET /codex/conversations/views`

用途：

- 会话列表页主接口
- 一行一个 conversation
- 已包含基础信息、执行状态、历史摘要

查询参数：

- `pageNum`, `pageSize`
- `conversationId`
- `workspaceId`, `workspaceIds`
- `threadId`
- `operator`
- `title`
- `status`, `statuses`
- `hasError`
- `searchText`
- `createdAtStartMs`, `createdAtEndMs`
- `updatedAtStartMs`, `updatedAtEndMs`
- `orderByColumn`
- `isAsc`

允许的 `orderByColumn`：

- `updatedAtMs`
- `createdAtMs`
- `title`
- `status`
- `operator`
- `conversationId`

返回示例：

```json
{
  "code": 200,
  "msg": "查询成功",
  "rows": [
    {
      "conversation": {
        "conversationId": "conv-1",
        "workspaceId": "ws-1",
        "threadId": "thread-1",
        "title": "Fix login redirect",
        "requirement": "Inspect the repo and fix the redirect bug.",
        "status": "running",
        "operator": "alice",
        "lastMessagePreview": "Investigating the redirect middleware.",
        "finalSummary": null,
        "lastError": null,
        "createdAtMs": 1760000000000,
        "updatedAtMs": 1760000005000
      },
      "currentState": {
        "status": "running",
        "phase": "conversation.streaming",
        "isRunning": true,
        "hasError": false,
        "activeTaskCount": 1,
        "latestTaskId": "task-2",
        "latestTaskStatus": "running",
        "latestEventType": "conversation.streaming",
        "latestEventStatus": "ok",
        "currentTurnId": "turn-2",
        "lastActivityAtMs": 1760000005000
      },
      "historySummary": {
        "messageCount": 8,
        "userMessageCount": 3,
        "assistantMessageCount": 5,
        "eventCount": 12,
        "taskCount": 2,
        "completedTaskCount": 1,
        "failedTaskCount": 0,
        "latestMessagePreview": "Investigating the redirect middleware.",
        "latestMessageAtMs": 1760000005000,
        "startedAtMs": 1760000000000,
        "finishedAtMs": null
      }
    }
  ],
  "total": 1
}
```

列表页消费规则：

- 状态徽标读 `currentState.status` 和 `currentState.isRunning`，不要只看 `conversation.status`
- 错误态读 `currentState.hasError`
- 列表摘要读 `historySummary.latestMessagePreview`
- 主键和跳转 id 读 `conversation.conversationId`
- `conversation.threadId` 仅作调试或链路追踪，不要当业务主键

### 3.2 详情页初始化

`GET /codex/conversations/{conversationId}/read-model`

用途：

- 详情页首次加载的一次性初始化接口

`data` 内固定包含：

- `conversation`
- `currentState`
- `historySummary`
- `messages`
- `events`
- `tasks`

详情页消费规则：

- 首屏初始化优先走这个接口
- 时间线、任务区块、状态头部都从同一份 `data` 渲染
- 不要默认并发请求 `/messages`、`/events`、`/tasks` 再自己组装

### 3.3 详情页实时流

`GET /codex/conversations/{conversationId}/stream`

查询参数：

- `pollIntervalMs`：可选，默认 `1000`，范围 `500-10000`

传输：

- `text/event-stream`

事件类型：

- `snapshot`：首次全量快照，结构与 `/read-model` 的 `data` 完全一致
- `update`：后续全量替换快照，不是 patch
- `ping`：保活事件，结构固定为 `{ "conversationId": "..." }`

SSE 示例：

```text
event: snapshot
data: {"conversation":{"conversationId":"conv-1"},"currentState":{"status":"running"},"historySummary":{"messageCount":8},"messages":[],"events":[],"tasks":[]}
```

SSE 消费规则：

- `snapshot` 和 `update` 都按整包替换本地状态
- `ping` 只用于保活，不更新 UI
- 如果首屏已调用 `/read-model`，SSE 订阅后仍要接受后续 `snapshot`

## 4. 原始接口

以下接口继续保留：

- `GET /codex/conversations`
- `GET /codex/conversations/{conversationId}`
- `GET /codex/conversations/{conversationId}/messages`
- `GET /codex/conversations/{conversationId}/events`
- `GET /codex/conversations/{conversationId}/tasks`

使用场景：

- 管理后台排障
- 导出
- 核对 MySQL 投影是否和 daemon 写入一致

## 5. 字段语义

前端可以稳定依赖的字段语义：

- `conversation.conversationId`：业务主键，页面跳转、缓存 key、深链都用它
- `conversation.threadId`：底层 Codex thread id，可能被后续任务复用，不是业务主键
- `conversation.lastMessagePreview`：daemon 维护的最新摘要，前端不需要重新裁切消息内容
- `conversation.finalSummary`：会话完成后的总结，没有就为 `null`
- `conversation.lastError`：最近一次瞬时或终态错误摘要
- `currentState.phase`：优先来自最新事件类型，否则退化到最新消息类型
- `currentState.currentTurnId`：优先取最新 task，再退化到 event/message
- `historySummary.finishedAtMs`：只有会话不再 running 时才有意义
- `tasks[].createdThread`：API 中是布尔值，MySQL 存储为 `tinyint(1)`，`1=true`、`0=false`
- `messages[].payloadJson` 与 `events[].payloadJson`：原样透传 JSON 字符串，前端若要读内部字段需自行 `JSON.parse`

当前状态值说明：

- `running`、`queued`、`pending`、`submitted`、`started`、`in_progress`、`processing` 会被视为运行中
- `done`、`completed`、`success`、`succeeded`、`finished`、`ok` 会被视为成功
- `error`、`failed`、`failure`、`timeout`、`canceled`、`cancelled` 会被视为错误
- daemon 还会把部分事件归一为 `waiting_input`、`waiting_approval`、`streaming`

前端不要自己维护另一份状态归类表，统一按以上语义消费返回值。

## 6. MySQL 投影契约

FastAPI 读侧假设 daemon 会持续写入以下四张表：

- `conversation`
- `conversation_message`
- `conversation_event`
- `conversation_task`

当前字段契约如下。

`conversation`

- `conversation_id`
- `workspace_id`
- `thread_id`
- `title`
- `requirement`
- `status`
- `operator`
- `last_message_preview`
- `final_summary`
- `last_error`
- `created_at_ms`
- `updated_at_ms`

`conversation_message`

- `conversation_id`
- `thread_id`
- `turn_id`
- `role`
- `message_type`
- `content`
- `payload_json`
- `sequence_no`
- `created_at_ms`

`conversation_event`

- `conversation_id`
- `thread_id`
- `turn_id`
- `event_type`
- `event_status`
- `payload_json`
- `created_at_ms`

`conversation_task`

- `conversation_id`
- `task_id`
- `workspace_id`
- `thread_id`
- `turn_id`
- `status`
- `created_thread`
- `submitted_at_ms`
- `completed_at_ms`
- `last_error`

当前已确认：

- FastAPI ORM/VO/DAO 与 `sql/ruoyi-fastapi.sql` 中这四张表字段一致
- daemon 当前 upsert SQL 与上述字段集一致
- `created_thread` 已通过 `202607090001_fix_codex_created_thread_bool.py` 统一为布尔/`tinyint(1)` 语义

## 7. 演进规则

daemon 新增、删除、重命名任何投影字段时，必须一起改这 6 处：

1. `CodexMonitor` 的 Rust struct 和写库 SQL
2. FastAPI 的 MySQL 初始化 DDL
3. FastAPI Alembic 迁移链
4. FastAPI DO
5. FastAPI VO/DAO/Service
6. 本文档

只改一侧，等于主动制造漂移。
