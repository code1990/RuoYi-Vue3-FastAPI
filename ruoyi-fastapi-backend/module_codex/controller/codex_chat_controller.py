from typing import Annotated

from fastapi import Query, Request, Response
from fastapi.responses import StreamingResponse

from common.aspect.pre_auth import CurrentUserDependency, PreAuthDependency
from common.router import APIRouterPro
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_codex.entity.vo.codex_chat_vo import (
    CodexChatConversationMessageModel,
    CodexChatConversationQueryModel,
    CodexChatConversationStartModel,
    CodexChatServerRequestRespondModel,
)
from module_codex.service.codex_chat_service import CodexChatService
from utils.response_util import ResponseUtil

codex_chat_controller = APIRouterPro(
    prefix='/codex/chat',
    order_num=32,
    tags=['Codex Chat'],
    dependencies=[PreAuthDependency()],
)


@codex_chat_controller.get('/health', summary='CodexMonitor health')
async def get_codex_chat_health(request: Request) -> Response:
    return ResponseUtil.success(data=await CodexChatService.get_health_services())


@codex_chat_controller.get('/workspaces', summary='Codex workspaces')
async def get_codex_chat_workspaces(request: Request) -> Response:
    return ResponseUtil.success(data=await CodexChatService.list_workspaces_services())


@codex_chat_controller.get('/conversations', summary='Codex conversations')
async def get_codex_chat_conversations(
    request: Request, query_object: Annotated[CodexChatConversationQueryModel, Query()]
) -> Response:
    return ResponseUtil.success(data=await CodexChatService.list_conversations_services(query_object.workspace_id))


@codex_chat_controller.post('/conversations', summary='Start Codex conversation')
async def create_codex_chat_conversation(
    request: Request,
    conversation: CodexChatConversationStartModel,
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    return ResponseUtil.success(data=await CodexChatService.start_conversation_services(conversation, current_user))


@codex_chat_controller.post('/start', summary='Start Codex conversation (compat)')
async def create_codex_chat_conversation_compat(
    request: Request,
    conversation: CodexChatConversationStartModel,
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    return ResponseUtil.success(data=await CodexChatService.start_conversation_services(conversation, current_user))


@codex_chat_controller.get('/conversations/{conversation_id}', summary='Codex conversation detail')
async def get_codex_chat_conversation_detail(request: Request, conversation_id: str) -> Response:
    return ResponseUtil.success(data=await CodexChatService.get_conversation_services(conversation_id))


@codex_chat_controller.get('/conversations/{conversation_id}/messages', summary='Codex conversation messages')
async def get_codex_chat_conversation_messages(request: Request, conversation_id: str) -> Response:
    return ResponseUtil.success(data=await CodexChatService.get_conversation_messages_services(conversation_id))


@codex_chat_controller.post('/conversations/{conversation_id}/messages', summary='Send Codex message')
async def post_codex_chat_conversation_message(
    request: Request, conversation_id: str, message: CodexChatConversationMessageModel
) -> Response:
    return ResponseUtil.success(
        data=await CodexChatService.send_conversation_message_services(conversation_id, message)
    )


@codex_chat_controller.post('/{conversation_id}/messages', summary='Send Codex message (compat)')
async def post_codex_chat_conversation_message_compat(
    request: Request, conversation_id: str, message: CodexChatConversationMessageModel
) -> Response:
    return ResponseUtil.success(
        data=await CodexChatService.send_conversation_message_services(conversation_id, message)
    )


@codex_chat_controller.get(
    '/conversations/{conversation_id}/events',
    summary='Codex conversation events',
    response_class=StreamingResponse,
    responses={200: {'description': 'SSE stream', 'content': {'text/event-stream': {}}}},
)
async def stream_codex_chat_conversation_events(request: Request, conversation_id: str) -> StreamingResponse:
    stream = await CodexChatService.stream_conversation_events_services(conversation_id)
    return StreamingResponse(
        stream,
        media_type='text/event-stream',
        headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'},
    )


@codex_chat_controller.post('/server-requests/respond', summary='Respond to Codex server request')
async def respond_codex_server_request(
    request: Request, server_request: CodexChatServerRequestRespondModel
) -> Response:
    return ResponseUtil.success(data=await CodexChatService.respond_to_server_request_services(server_request))
