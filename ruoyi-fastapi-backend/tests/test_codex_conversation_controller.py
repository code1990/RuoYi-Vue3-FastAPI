import importlib
import json
import sys
import types
from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from fastapi import Depends
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from exceptions.exception import ServiceException
from module_codex.dao.codex_conversation_dao import CodexConversationDao
from module_codex.entity.do.codex_conversation_do import (
    CodexConversation,
    CodexConversationEvent,
    CodexConversationMessage,
    CodexConversationTask,
)
from module_codex.entity.vo.codex_conversation_vo import (
    CodexConversationEventModel,
    CodexConversationMessageModel,
    CodexConversationModel,
    CodexConversationPageQueryModel,
    CodexConversationTaskModel,
)
from module_codex.service.codex_conversation_service import CodexConversationService


def _load_controller_module():
    fake_pre_auth = types.ModuleType('common.aspect.pre_auth')
    fake_pre_auth.PreAuthDependency = lambda: Depends(lambda: None)
    sys.modules['common.aspect.pre_auth'] = fake_pre_auth
    sys.modules.pop('module_codex.controller.codex_conversation_controller', None)
    return importlib.import_module('module_codex.controller.codex_conversation_controller')


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine('sqlite+aiosqlite:///:memory:')
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(CodexConversation.metadata.create_all)

    async with session_factory() as session:
        session.add_all(
            [
                CodexConversation(
                    id=1,
                    conversation_id='conv-1',
                    workspace_id='ws-1',
                    thread_id='thread-1',
                    title='First conversation',
                    status='done',
                    operator='alice',
                    requirement='build realtime read model',
                    last_message_preview='assistant reply',
                    final_summary='summary-1',
                    last_error='mysql retry pending',
                    created_at_ms=1000,
                    updated_at_ms=3000,
                ),
                CodexConversation(
                    id=2,
                    conversation_id='conv-2',
                    workspace_id='ws-2',
                    thread_id='thread-2',
                    title='Second conversation',
                    status='running',
                    operator='bob',
                    requirement='night task',
                    created_at_ms=2000,
                    updated_at_ms=2000,
                ),
                CodexConversationMessage(
                    id=1,
                    conversation_id='conv-1',
                    thread_id='thread-1',
                    turn_id='turn-1',
                    role='assistant',
                    message_type='final',
                    content='second',
                    sequence_no=2,
                    created_at_ms=2200,
                ),
                CodexConversationMessage(
                    id=2,
                    conversation_id='conv-1',
                    thread_id='thread-1',
                    turn_id='turn-1',
                    role='user',
                    message_type='prompt',
                    content='first',
                    sequence_no=1,
                    created_at_ms=2100,
                ),
                CodexConversationEvent(
                    id=1,
                    conversation_id='conv-1',
                    thread_id='thread-1',
                    turn_id='turn-1',
                    event_type='started',
                    event_status='ok',
                    payload_json='{\"step\":1}',
                    created_at_ms=1100,
                ),
                CodexConversationEvent(
                    id=2,
                    conversation_id='conv-1',
                    thread_id='thread-1',
                    turn_id='turn-1',
                    event_type='finished',
                    event_status='ok',
                    payload_json='{\"step\":2}',
                    created_at_ms=1200,
                ),
                CodexConversationTask(
                    id=1,
                    conversation_id='conv-1',
                    task_id='task-1',
                    workspace_id='ws-1',
                    thread_id='thread-1',
                    turn_id='turn-1',
                    status='done',
                    created_thread=True,
                    submitted_at_ms=1200,
                    completed_at_ms=1300,
                ),
                CodexConversationTask(
                    id=2,
                    conversation_id='conv-1',
                    task_id='task-2',
                    workspace_id='ws-1',
                    thread_id='thread-1',
                    turn_id='turn-2',
                    status='running',
                    created_thread=False,
                    submitted_at_ms=1400,
                ),
            ]
        )
        await session.commit()
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_dao_lists_conversations_with_filters_and_sorting(db_session):
    result = await CodexConversationDao.get_conversation_list(
        db_session,
        CodexConversationPageQueryModel(workspace_id='ws-1', page_num=1, page_size=10),
        is_page=True,
    )

    assert result.total == 1
    assert result.rows[0]['conversationId'] == 'conv-1'
    assert result.rows[0]['updatedAtMs'] == 3000


def test_codex_mysql_projection_schema_matches_daemon_contract():
    assert set(CodexConversation.__table__.columns.keys()) == {
        'id',
        'conversation_id',
        'workspace_id',
        'thread_id',
        'title',
        'requirement',
        'status',
        'operator',
        'last_message_preview',
        'final_summary',
        'last_error',
        'created_at_ms',
        'updated_at_ms',
    }
    assert set(CodexConversationMessage.__table__.columns.keys()) == {
        'id',
        'conversation_id',
        'thread_id',
        'turn_id',
        'role',
        'message_type',
        'content',
        'payload_json',
        'sequence_no',
        'created_at_ms',
    }
    assert set(CodexConversationEvent.__table__.columns.keys()) == {
        'id',
        'conversation_id',
        'thread_id',
        'turn_id',
        'event_type',
        'event_status',
        'payload_json',
        'created_at_ms',
    }
    assert set(CodexConversationTask.__table__.columns.keys()) == {
        'id',
        'conversation_id',
        'task_id',
        'workspace_id',
        'thread_id',
        'turn_id',
        'status',
        'created_thread',
        'submitted_at_ms',
        'completed_at_ms',
        'last_error',
    }
    assert str(CodexConversationTask.__table__.columns.created_thread.type).lower() == 'boolean'


def test_codex_vo_fields_cover_mysql_projection_schema():
    assert set(CodexConversationModel.model_fields.keys()) == {
        'id',
        'conversation_id',
        'workspace_id',
        'thread_id',
        'title',
        'requirement',
        'status',
        'operator',
        'last_message_preview',
        'final_summary',
        'last_error',
        'created_at_ms',
        'updated_at_ms',
    }
    assert set(CodexConversationMessageModel.model_fields.keys()) == {
        'id',
        'conversation_id',
        'thread_id',
        'turn_id',
        'role',
        'message_type',
        'content',
        'payload_json',
        'sequence_no',
        'created_at_ms',
    }
    assert set(CodexConversationEventModel.model_fields.keys()) == {
        'id',
        'conversation_id',
        'thread_id',
        'turn_id',
        'event_type',
        'event_status',
        'payload_json',
        'created_at_ms',
    }
    assert set(CodexConversationTaskModel.model_fields.keys()) == {
        'id',
        'conversation_id',
        'task_id',
        'workspace_id',
        'thread_id',
        'turn_id',
        'status',
        'created_thread',
        'submitted_at_ms',
        'completed_at_ms',
        'last_error',
    }


@pytest.mark.asyncio
async def test_dao_lists_conversations_with_search_status_error_and_time_filters(db_session):
    result = await CodexConversationDao.get_conversation_list(
        db_session,
        CodexConversationPageQueryModel(
            search_text='realtime',
            statuses=['done', 'queued'],
            has_error=True,
            created_at_start_ms=900,
            created_at_end_ms=1500,
            page_num=1,
            page_size=10,
        ),
        is_page=True,
    )

    assert result.total == 1
    assert result.rows[0]['conversationId'] == 'conv-1'


@pytest.mark.asyncio
async def test_dao_lists_conversations_with_order_by_whitelist(db_session):
    result = await CodexConversationDao.get_conversation_list(
        db_session,
        CodexConversationPageQueryModel(
            order_by_column='createdAtMs',
            is_asc='ascending',
            page_num=1,
            page_size=10,
        ),
        is_page=True,
    )

    assert [item['conversationId'] for item in result.rows] == ['conv-1', 'conv-2']


@pytest.mark.asyncio
async def test_dao_returns_messages_in_sequence_order(db_session):
    result = await CodexConversationDao.get_conversation_messages(db_session, 'conv-1')

    assert [item['content'] for item in result] == ['first', 'second']


@pytest.mark.asyncio
async def test_service_raises_when_conversation_missing(db_session):
    with pytest.raises(ServiceException) as exc_info:
        await CodexConversationService.get_conversation_detail_services(db_session, 'missing')
    assert exc_info.value.message == '会话不存在'


@pytest.mark.asyncio
async def test_controller_returns_paginated_conversation_list(db_session):
    controller = _load_controller_module()

    response = await controller.get_codex_conversation_list(
        None,
        CodexConversationPageQueryModel(page_num=1, page_size=10),
        db_session,
    )
    payload = json.loads(response.body)

    assert payload['rows'][0]['conversationId'] == 'conv-1'
    assert payload['rows'][1]['conversationId'] == 'conv-2'
    assert payload['total'] == 2


@pytest.mark.asyncio
async def test_controller_returns_detail_messages_events_and_tasks(db_session):
    controller = _load_controller_module()

    detail_response = await controller.get_codex_conversation_detail(None, 'conv-1', db_session)
    messages_response = await controller.get_codex_conversation_messages(None, 'conv-1', db_session)
    events_response = await controller.get_codex_conversation_events(None, 'conv-1', db_session)
    tasks_response = await controller.get_codex_conversation_tasks(None, 'conv-1', db_session)

    detail_payload = json.loads(detail_response.body)
    messages_payload = json.loads(messages_response.body)
    events_payload = json.loads(events_response.body)
    tasks_payload = json.loads(tasks_response.body)

    assert detail_payload['data']['finalSummary'] == 'summary-1'
    assert [item['content'] for item in messages_payload['data']] == ['first', 'second']
    assert [item['eventType'] for item in events_payload['data']] == ['started', 'finished']
    assert [item['taskId'] for item in tasks_payload['data']] == ['task-2', 'task-1']
    assert [item['createdThread'] for item in tasks_payload['data']] == [False, True]


@pytest.mark.asyncio
async def test_controller_returns_aggregated_read_model(db_session):
    controller = _load_controller_module()

    response = await controller.get_codex_conversation_read_model(None, 'conv-1', db_session)
    payload = json.loads(response.body)

    assert payload['data']['conversation']['conversationId'] == 'conv-1'
    assert payload['data']['currentState']['status'] == 'done'
    assert payload['data']['currentState']['latestTaskId'] == 'task-2'
    assert payload['data']['currentState']['latestEventType'] == 'finished'
    assert payload['data']['historySummary']['messageCount'] == 2
    assert payload['data']['historySummary']['completedTaskCount'] == 1
    assert [item['content'] for item in payload['data']['messages']] == ['first', 'second']
    assert [item['eventType'] for item in payload['data']['events']] == ['started', 'finished']
    assert [item['taskId'] for item in payload['data']['tasks']] == ['task-2', 'task-1']


@pytest.mark.asyncio
async def test_controller_returns_aggregated_conversation_view_list(db_session):
    controller = _load_controller_module()

    response = await controller.get_codex_conversation_view_list(
        None,
        CodexConversationPageQueryModel(page_num=1, page_size=10),
        db_session,
    )
    payload = json.loads(response.body)

    assert payload['rows'][0]['conversation']['conversationId'] == 'conv-1'
    assert payload['rows'][0]['currentState']['lastActivityAtMs'] == 3000
    assert payload['rows'][0]['historySummary']['latestMessagePreview'] == 'assistant reply'
    assert payload['rows'][1]['conversation']['conversationId'] == 'conv-2'
    assert payload['rows'][1]['currentState']['isRunning'] is True
    assert payload['rows'][1]['historySummary']['messageCount'] == 0


class _DisconnectedRequest:
    def __init__(self) -> None:
        self._checks = 0

    async def is_disconnected(self) -> bool:
        self._checks += 1
        return self._checks > 1


async def _read_first_chunk(iterator: AsyncIterator[bytes]) -> bytes:
    return await anext(iterator)


@pytest.mark.asyncio
async def test_controller_stream_returns_snapshot_event(db_session):
    controller = _load_controller_module()

    response = await controller.stream_codex_conversation_read_model(
        _DisconnectedRequest(),
        'conv-1',
        db_session,
        poll_interval_ms=500,
    )
    first_chunk = await _read_first_chunk(response.body_iterator)
    payload = first_chunk.decode('utf-8')

    assert 'event: snapshot' in payload
    assert '"conversationId": "conv-1"' in payload
    assert '"messages": [{' in payload
