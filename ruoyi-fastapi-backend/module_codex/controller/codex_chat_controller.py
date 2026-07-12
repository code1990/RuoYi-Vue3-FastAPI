from typing import Annotated

from fastapi import Request, Response

from common.aspect.pre_auth import PreAuthDependency
from common.router import APIRouterPro
from common.vo import DataResponseModel
from module_codex.entity.vo.codex_chat_vo import (
    CodexChatActionResponseModel,
    CodexChatMessageRequestModel,
    CodexChatStartRequestModel,
)
from module_codex.service.codex_chat_service import CodexChatService
from utils.response_util import ResponseUtil


codex_chat_controller = APIRouterPro(
    prefix='/codex/chat',
    order_num=30,
    tags=['Codex对话写接口'],
    dependencies=[PreAuthDependency()],
)


@codex_chat_controller.post(
    '/start',
    summary='创建Codex对话',
    description='代理转发到CodexMonitor daemon创建新对话',
    response_model=DataResponseModel[CodexChatActionResponseModel],
)
async def start_codex_chat(
    request: Request,
    chat_req: CodexChatStartRequestModel,
) -> Response:
    result = await CodexChatService.start_conversation_services(chat_req)
    return ResponseUtil.success(data=result)


@codex_chat_controller.post(
    '/{conversation_id}/messages',
    summary='继续Codex对话',
    description='代理转发到CodexMonitor daemon向已有对话追加消息',
    response_model=DataResponseModel[CodexChatActionResponseModel],
)
async def append_codex_chat_message(
    request: Request,
    conversation_id: str,
    chat_req: Annotated[CodexChatMessageRequestModel, ...],
) -> Response:
    result = await CodexChatService.append_message_services(conversation_id, chat_req)
    return ResponseUtil.success(data=result)
