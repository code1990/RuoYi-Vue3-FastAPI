# Codex Conversation Stream API

## 接口

`GET /codex/conversations/{conversationId}/stream`

## 用途

- Codex 会话详情页实时状态流
- 与 `/read-model` 配套

## 查询参数

- `pollIntervalMs`
  - 可选
  - 默认 `1000`
  - 范围 `500-10000`

## 响应类型

- `text/event-stream`

## 事件类型

### `snapshot`

- 首帧全量快照
- 结构与 `GET /codex/conversations/{conversationId}/read-model` 的 `data` 一致

### `update`

- 后续全量替换快照
- 不是 patch

### `ping`

- 保活事件
- 固定结构：

```json
{
  "conversationId": "conv-1"
}
```

## snapshot / update 数据结构

- `conversation`
- `currentState`
- `historySummary`
- `messages`
- `events`
- `tasks`

## SSE 示例

```text
event: snapshot
data: {"conversation":{"conversationId":"conv-1"},"currentState":{"status":"running"},"historySummary":{"messageCount":8},"messages":[],"events":[],"tasks":[]}
```

## 消费规则

- `snapshot` 和 `update` 都按整包替换本地状态
- `ping` 不更新业务 UI
- 如果 SSE 不可用，可退化为轮询 `/read-model`
