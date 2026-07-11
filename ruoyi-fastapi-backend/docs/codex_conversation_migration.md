# Codex Conversation Migration

This runbook defines the upgrade path for already-deployed environments after the `conversation*` tables were added.

## Current Role

- MySQL is the FastAPI/Web read-side history store
- CodexMonitor daemon still treats local JSON snapshots as the restart source for `conversation` and `conversation_task`
- migration therefore has two steps: create schema first, then backfill daemon snapshots into MySQL

## 1. Schema Upgrade

Do not paste the `sql/ruoyi-fastapi.sql` fragment directly into a running environment as the primary path.

Use Alembic through the existing CLI:

```bash
cd ruoyi-fastapi-backend
ruoyi db check --env=prod
ruoyi db current --env=prod --output=json
ruoyi db upgrade --env=prod --revision=head --allow-prod --dry-run --yes
ruoyi db upgrade --env=prod --revision=head --allow-prod --yes
```

The migration file for this change is:

- `alembic/versions/202607080001_add_codex_conversation_tables.py`
- `alembic/versions/202607090001_fix_codex_created_thread_bool.py`

## 2. Daemon Cutover

After the schema exists, enable MySQL projection on the daemon host:

```bash
export CODEX_MONITOR_MYSQL_URL='mysql://user:password@127.0.0.1:3306/ruoyi-fastapi'
```

Then restart `codex_monitor_daemon`.

Current daemon behavior on startup:

- load `service_conversations.json` and `service_tasks.json` from the daemon data dir
- upsert those records into MySQL on startup

So the restart itself is the current backfill trigger for `conversation` and `conversation_task`.

## 3. Backfill Scope

Backfilled automatically after daemon restart:

- `conversation`
- `conversation_task`

Not backfilled automatically in current v1:

- `conversation_message`
- `conversation_event`

Reason:

- these rows are written directly to MySQL at event time
- the daemon has no local append-only log for historical message/event replay

Operational meaning:

- old snapshot state can be recovered into MySQL
- old message/event history before MySQL cutover is not guaranteed
- message/event history is reliable only from the moment MySQL projection is enabled

## 3.1 Constraint Policy

Database-level foreign keys are enabled only for:

- `conversation_message.conversation_id -> conversation.conversation_id`
- `conversation_event.conversation_id -> conversation.conversation_id`
- `conversation_task.conversation_id -> conversation.conversation_id`

All three use:

- `ON UPDATE CASCADE`
- `ON DELETE CASCADE`

Deliberately not modeled as foreign keys:

- `workspace_id`
- `thread_id`
- `turn_id`

Reason:

- those identifiers come from daemon/runtime state outside the RuoYi schema
- the current MySQL side is a read/history store, not the runtime owner of those ids

Operational requirement before upgrade:

- if an environment already contains orphan rows in child tables, clean them before applying the migration, otherwise the foreign-key step will fail

## 4. Validation

After restart, verify that MySQL is receiving snapshot backfill:

```sql
SELECT COUNT(*) AS conversation_count FROM conversation;
SELECT COUNT(*) AS task_count FROM conversation_task;
SELECT COUNT(*) AS message_count FROM conversation_message;
SELECT COUNT(*) AS event_count FROM conversation_event;
```

Expected result:

- `conversation` and `conversation_task` counts should increase to match the daemon's local snapshot
- `conversation_message` and `conversation_event` may remain low or zero until new traffic arrives

Then verify FastAPI can read the new tables through the Codex endpoints.

Recommended contract checks:

- `GET /codex/conversations/views`
- `GET /codex/conversations/{conversation_id}/read-model`
- `GET /codex/conversations/{conversation_id}/stream`

And confirm `conversation_task.created_thread` is stored as `0/1` rather than legacy string values:

```sql
SELECT task_id, created_thread
FROM conversation_task
ORDER BY id DESC
LIMIT 10;
```

## 4.1 Read-Side Consistency Checklist

If daemon continues evolving its MySQL projection, use this checklist before releasing the FastAPI read side:

1. Compare daemon structs and upsert SQL against these tables:
   - `conversation`
   - `conversation_message`
   - `conversation_event`
   - `conversation_task`
2. Confirm FastAPI DO fields still match table columns exactly.
3. Confirm FastAPI VO fields still expose every frontend-visible column.
4. Confirm `docs/codex_read_model_api.md` still describes the real payload shape.
5. Run the Codex conversation tests:

```bash
cd ruoyi-fastapi-backend
pytest tests/test_codex_conversation_controller.py
```

The current test file includes schema-contract assertions intended to fail fast when daemon/MySQL/FastAPI field sets drift.

## 5. Rollback

If the schema upgrade succeeded but daemon projection must be paused:

1. remove `CODEX_MONITOR_MYSQL_URL` from the daemon environment
2. restart the daemon

This stops new MySQL writes and returns the daemon to JSON-only runtime behavior.

Do not drop the new tables during a simple rollback unless you are also explicitly reverting the backend release.
