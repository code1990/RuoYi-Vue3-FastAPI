from collections import defaultdict
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from common.vo import PageModel
from exceptions.exception import ServiceException
from module_codex.dao.codex_conversation_dao import CodexConversationDao
from module_codex.entity.vo.codex_conversation_vo import CodexConversationPageQueryModel


class CodexConversationService:
    """
    Codex 对话历史服务层
    """

    RUNNING_STATUS_SET = {'running', 'in_progress', 'processing', 'queued', 'submitted', 'pending', 'created', 'started'}
    SUCCESS_STATUS_SET = {'done', 'completed', 'success', 'succeeded', 'finished', 'ok'}
    ERROR_STATUS_SET = {'error', 'failed', 'failure', 'cancelled', 'canceled', 'timeout'}

    @classmethod
    def _normalize_status(cls, value: str | None) -> str | None:
        return value.lower() if value else None

    @classmethod
    def _is_running_status(cls, value: str | None) -> bool:
        return cls._normalize_status(value) in cls.RUNNING_STATUS_SET

    @classmethod
    def _is_success_status(cls, value: str | None) -> bool:
        return cls._normalize_status(value) in cls.SUCCESS_STATUS_SET

    @classmethod
    def _is_error_status(cls, value: str | None) -> bool:
        return cls._normalize_status(value) in cls.ERROR_STATUS_SET

    @classmethod
    def _latest_by(cls, items: list[dict[str, Any]], *keys: str) -> dict[str, Any] | None:
        if not items:
            return None
        return max(items, key=lambda item: tuple(item.get(key) or 0 for key in keys))

    @classmethod
    def _build_conversation_view(
        cls,
        conversation: dict[str, Any],
        messages: list[dict[str, Any]],
        events: list[dict[str, Any]],
        tasks: list[dict[str, Any]],
    ) -> dict[str, Any]:
        latest_message = cls._latest_by(messages, 'sequenceNo', 'id')
        latest_event = cls._latest_by(events, 'createdAtMs', 'id')
        latest_task = cls._latest_by(tasks, 'submittedAtMs', 'id')
        active_tasks = [task for task in tasks if cls._is_running_status(task.get('status'))]
        failed_tasks = [task for task in tasks if cls._is_error_status(task.get('status'))]
        completed_tasks = [task for task in tasks if cls._is_success_status(task.get('status'))]

        latest_message_preview = conversation.get('lastMessagePreview') or (latest_message or {}).get('content')
        latest_message_at_ms = (latest_message or {}).get('createdAtMs')
        last_activity_candidates = [
            conversation.get('updatedAtMs'),
            latest_message_at_ms,
            (latest_event or {}).get('createdAtMs'),
            (latest_task or {}).get('completedAtMs'),
            (latest_task or {}).get('submittedAtMs'),
        ]
        last_activity_at_ms = max((value for value in last_activity_candidates if value is not None), default=None)
        current_status = conversation.get('status') or (latest_task or {}).get('status') or (latest_event or {}).get('eventStatus')
        is_running = bool(active_tasks) or cls._is_running_status(current_status)
        has_error = bool(conversation.get('lastError')) or bool(failed_tasks) or cls._is_error_status(current_status)

        finished_at_candidates = [task.get('completedAtMs') for task in completed_tasks if task.get('completedAtMs') is not None]
        if not is_running and finished_at_candidates:
            finished_at_ms = max(finished_at_candidates)
        elif not is_running and conversation.get('updatedAtMs') is not None:
            finished_at_ms = conversation.get('updatedAtMs')
        else:
            finished_at_ms = None

        started_at_candidates = [
            conversation.get('createdAtMs'),
            min((item.get('createdAtMs') for item in messages if item.get('createdAtMs') is not None), default=None),
            min((item.get('createdAtMs') for item in events if item.get('createdAtMs') is not None), default=None),
            min((item.get('submittedAtMs') for item in tasks if item.get('submittedAtMs') is not None), default=None),
        ]
        started_at_ms = min((value for value in started_at_candidates if value is not None), default=None)

        return {
            'conversation': conversation,
            'currentState': {
                'status': current_status,
                'phase': (latest_event or {}).get('eventType') or (latest_message or {}).get('messageType'),
                'isRunning': is_running,
                'hasError': has_error,
                'activeTaskCount': len(active_tasks),
                'latestTaskId': (latest_task or {}).get('taskId'),
                'latestTaskStatus': (latest_task or {}).get('status'),
                'latestEventType': (latest_event or {}).get('eventType'),
                'latestEventStatus': (latest_event or {}).get('eventStatus'),
                'currentTurnId': (latest_task or {}).get('turnId')
                or (latest_event or {}).get('turnId')
                or (latest_message or {}).get('turnId'),
                'lastActivityAtMs': last_activity_at_ms,
            },
            'historySummary': {
                'messageCount': len(messages),
                'userMessageCount': sum(1 for item in messages if item.get('role') == 'user'),
                'assistantMessageCount': sum(1 for item in messages if item.get('role') == 'assistant'),
                'eventCount': len(events),
                'taskCount': len(tasks),
                'completedTaskCount': len(completed_tasks),
                'failedTaskCount': len(failed_tasks),
                'latestMessagePreview': latest_message_preview,
                'latestMessageAtMs': latest_message_at_ms,
                'startedAtMs': started_at_ms,
                'finishedAtMs': finished_at_ms,
            },
            'messages': messages,
            'events': events,
            'tasks': tasks,
        }

    @classmethod
    async def get_conversation_list_services(
        cls, query_db: AsyncSession, query_object: CodexConversationPageQueryModel, is_page: bool = False
    ) -> PageModel | list[dict[str, Any]]:
        return await CodexConversationDao.get_conversation_list(query_db, query_object, is_page)

    @classmethod
    async def get_conversation_view_list_services(
        cls, query_db: AsyncSession, query_object: CodexConversationPageQueryModel, is_page: bool = False
    ) -> PageModel | list[dict[str, Any]]:
        result = await CodexConversationDao.get_conversation_list(query_db, query_object, is_page)
        rows = result.rows if is_page else result
        conversation_ids = [row['conversationId'] for row in rows]
        messages = await CodexConversationDao.get_conversation_messages_by_ids(query_db, conversation_ids)
        events = await CodexConversationDao.get_conversation_events_by_ids(query_db, conversation_ids)
        tasks = await CodexConversationDao.get_conversation_tasks_by_ids(query_db, conversation_ids)

        messages_map: dict[str, list[dict[str, Any]]] = defaultdict(list)
        events_map: dict[str, list[dict[str, Any]]] = defaultdict(list)
        tasks_map: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for item in messages:
            messages_map[item['conversationId']].append(item)
        for item in events:
            events_map[item['conversationId']].append(item)
        for item in tasks:
            tasks_map[item['conversationId']].append(item)

        view_rows = [
            cls._build_conversation_view(
                row,
                messages_map.get(row['conversationId'], []),
                events_map.get(row['conversationId'], []),
                tasks_map.get(row['conversationId'], []),
            )
            for row in rows
        ]
        if not is_page:
            return view_rows

        result.rows = view_rows
        return result

    @classmethod
    async def get_conversation_detail_services(cls, query_db: AsyncSession, conversation_id: str) -> dict[str, Any]:
        conversation = await CodexConversationDao.get_conversation_detail(query_db, conversation_id)
        if conversation is None:
            raise ServiceException(message='会话不存在')
        return conversation

    @classmethod
    async def get_conversation_messages_services(
        cls, query_db: AsyncSession, conversation_id: str
    ) -> list[dict[str, Any]]:
        await cls.get_conversation_detail_services(query_db, conversation_id)
        return await CodexConversationDao.get_conversation_messages(query_db, conversation_id)

    @classmethod
    async def get_conversation_events_services(cls, query_db: AsyncSession, conversation_id: str) -> list[dict[str, Any]]:
        await cls.get_conversation_detail_services(query_db, conversation_id)
        return await CodexConversationDao.get_conversation_events(query_db, conversation_id)

    @classmethod
    async def get_conversation_tasks_services(cls, query_db: AsyncSession, conversation_id: str) -> list[dict[str, Any]]:
        await cls.get_conversation_detail_services(query_db, conversation_id)
        return await CodexConversationDao.get_conversation_tasks(query_db, conversation_id)

    @classmethod
    async def get_conversation_read_model_services(
        cls, query_db: AsyncSession, conversation_id: str
    ) -> dict[str, Any]:
        conversation = await cls.get_conversation_detail_services(query_db, conversation_id)
        messages = await CodexConversationDao.get_conversation_messages(query_db, conversation_id)
        events = await CodexConversationDao.get_conversation_events(query_db, conversation_id)
        tasks = await CodexConversationDao.get_conversation_tasks(query_db, conversation_id)
        return cls._build_conversation_view(conversation, messages, events, tasks)
