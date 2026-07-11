import asyncio
import json
from typing import Annotated

from fastapi import Query, Request, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from common.aspect.db_seesion import DBSessionDependency
from common.aspect.pre_auth import PreAuthDependency
from common.router import APIRouterPro
from common.vo import DataResponseModel, PageResponseModel
from module_codex.entity.vo.codex_conversation_vo import (
    CodexConversationEventModel,
    CodexConversationListViewModel,
    CodexConversationMessageModel,
    CodexConversationModel,
    CodexConversationPageQueryModel,
    CodexConversationReadModel,
    CodexConversationTaskModel,
)
from module_codex.service.codex_conversation_service import CodexConversationService
from utils.response_util import ResponseUtil

codex_conversation_controller = APIRouterPro(
    prefix='/codex/conversations',
    order_num=31,
    tags=['Codex对话历史'],
    dependencies=[PreAuthDependency()],
)


def _build_stream_snapshot_signature(snapshot: dict) -> str:
    return json.dumps(snapshot, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def _encode_sse(event: str, data: dict) -> bytes:
    return f'event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n'.encode('utf-8')

@codex_conversation_controller.get(
    '',
    summary='获取Codex对话列表',
    description='从 MySQL 历史库读取历史对话列表',
    response_model=PageResponseModel[CodexConversationModel],
)
async def get_codex_conversation_list(
    request: Request,
    conversation_page_query: Annotated[CodexConversationPageQueryModel, Query()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    conversation_page_query_result = await CodexConversationService.get_conversation_list_services(
        query_db, conversation_page_query, is_page=True
    )
    return ResponseUtil.success(model_content=conversation_page_query_result)


@codex_conversation_controller.get(
    '/views',
    summary='获取Codex对话聚合列表',
    description='聚合返回列表态所需的当前执行状态和历史摘要',
    response_model=PageResponseModel[CodexConversationListViewModel],
)
async def get_codex_conversation_view_list(
    request: Request,
    conversation_page_query: Annotated[CodexConversationPageQueryModel, Query()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    conversation_page_query_result = await CodexConversationService.get_conversation_view_list_services(
        query_db, conversation_page_query, is_page=True
    )
    return ResponseUtil.success(model_content=conversation_page_query_result)


@codex_conversation_controller.get(
    '/{conversation_id}',
    summary='获取Codex对话详情',
    description='从 MySQL 历史库读取单个对话详情',
    response_model=DataResponseModel[CodexConversationModel],
)
async def get_codex_conversation_detail(
    request: Request,
    conversation_id: str,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    conversation_detail_result = await CodexConversationService.get_conversation_detail_services(query_db, conversation_id)
    return ResponseUtil.success(data=conversation_detail_result)


@codex_conversation_controller.get(
    '/{conversation_id}/messages',
    summary='获取Codex对话消息',
    description='从 MySQL 历史库读取对话完整消息',
    response_model=DataResponseModel[list[CodexConversationMessageModel]],
)
async def get_codex_conversation_messages(
    request: Request,
    conversation_id: str,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    conversation_messages_result = await CodexConversationService.get_conversation_messages_services(
        query_db, conversation_id
    )
    return ResponseUtil.success(data=conversation_messages_result)


@codex_conversation_controller.get(
    '/{conversation_id}/events',
    summary='获取Codex对话事件',
    description='从 MySQL 历史库读取对话生命周期事件',
    response_model=DataResponseModel[list[CodexConversationEventModel]],
)
async def get_codex_conversation_events(
    request: Request,
    conversation_id: str,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    conversation_events_result = await CodexConversationService.get_conversation_events_services(query_db, conversation_id)
    return ResponseUtil.success(data=conversation_events_result)


@codex_conversation_controller.get(
    '/{conversation_id}/tasks',
    summary='获取Codex对话任务',
    description='从 MySQL 历史库读取对话任务状态',
    response_model=DataResponseModel[list[CodexConversationTaskModel]],
)
async def get_codex_conversation_tasks(
    request: Request,
    conversation_id: str,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    conversation_tasks_result = await CodexConversationService.get_conversation_tasks_services(query_db, conversation_id)
    return ResponseUtil.success(data=conversation_tasks_result)


@codex_conversation_controller.get(
    '/{conversation_id}/read-model',
    summary='获取Codex对话完整读模型',
    description='聚合返回会话详情、消息、事件和任务，供页面一次性初始化',
    response_model=DataResponseModel[CodexConversationReadModel],
)
async def get_codex_conversation_read_model(
    request: Request,
    conversation_id: str,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    conversation_read_model_result = await CodexConversationService.get_conversation_read_model_services(
        query_db, conversation_id
    )
    return ResponseUtil.success(data=conversation_read_model_result)


@codex_conversation_controller.get(
    '/{conversation_id}/stream',
    summary='订阅Codex对话实时读模型',
    description='通过 SSE 订阅会话完整读模型的初始化快照和后续变化',
    response_class=StreamingResponse,
    responses={
        200: {
            'description': 'SSE 实时返回对话读模型',
            'content': {
                'text/event-stream': {},
            },
        }
    },
)
async def stream_codex_conversation_read_model(
    request: Request,
    conversation_id: str,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    poll_interval_ms: Annotated[int, Query(ge=500, le=10000, description='轮询数据库间隔，单位毫秒')] = 1000,
) -> StreamingResponse:
    async def event_stream():
        snapshot = await CodexConversationService.get_conversation_read_model_services(query_db, conversation_id)
        snapshot_signature = _build_stream_snapshot_signature(snapshot)
        yield _encode_sse('snapshot', snapshot)
        idle_elapsed_ms = 0

        while True:
            if await request.is_disconnected():
                break
            await asyncio.sleep(poll_interval_ms / 1000)
            next_snapshot = await CodexConversationService.get_conversation_read_model_services(
                query_db, conversation_id
            )
            next_signature = _build_stream_snapshot_signature(next_snapshot)
            if next_signature != snapshot_signature:
                snapshot_signature = next_signature
                idle_elapsed_ms = 0
                yield _encode_sse('update', next_snapshot)
                continue
            idle_elapsed_ms += poll_interval_ms
            if idle_elapsed_ms >= 15000:
                idle_elapsed_ms = 0
                yield _encode_sse('ping', {'conversationId': conversation_id})

    return StreamingResponse(event_stream(), media_type='text/event-stream')
