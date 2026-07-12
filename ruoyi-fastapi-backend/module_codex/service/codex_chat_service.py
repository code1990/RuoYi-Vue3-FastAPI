from __future__ import annotations

from typing import Any

import httpx

from config.env import CodexChatProxyConfig
from exceptions.exception import ServiceException
from module_codex.entity.vo.codex_chat_vo import CodexChatMessageRequestModel, CodexChatStartRequestModel


class CodexChatService:
    """
    Codex chat代理服务
    """

    @classmethod
    async def start_conversation_services(cls, payload: CodexChatStartRequestModel) -> dict[str, Any]:
        return await cls._post('/api/v1/conversations/start', payload.model_dump(by_alias=True, exclude_none=True))

    @classmethod
    async def append_message_services(
        cls, conversation_id: str, payload: CodexChatMessageRequestModel
    ) -> dict[str, Any]:
        return await cls._post(
            f'/api/v1/conversations/{conversation_id}/messages',
            payload.model_dump(by_alias=True, exclude_none=True),
        )

    @classmethod
    async def _post(cls, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        base_url = CodexChatProxyConfig.codex_chat_proxy_base_url.rstrip('/')
        headers = {'Content-Type': 'application/json'}
        token = CodexChatProxyConfig.codex_chat_proxy_token.strip()
        if token:
            headers['Authorization'] = f'Bearer {token}'
        try:
            async with httpx.AsyncClient(timeout=CodexChatProxyConfig.codex_chat_proxy_timeout_seconds) as client:
                response = await client.post(f'{base_url}{path}', json=payload, headers=headers)
        except httpx.HTTPError as exc:
            raise ServiceException(message=f'Codex daemon不可用: {exc!s}') from exc

        payload_json = cls._parse_json(response)
        if response.status_code >= 400 or not payload_json.get('ok', False):
            error = payload_json.get('error') or {}
            message = error.get('message') or f'Codex daemon请求失败: HTTP {response.status_code}'
            raise ServiceException(message=message)

        data = payload_json.get('data')
        if not isinstance(data, dict):
            raise ServiceException(message='Codex daemon返回结构非法')
        return data

    @staticmethod
    def _parse_json(response: httpx.Response) -> dict[str, Any]:
        try:
            data = response.json()
        except ValueError as exc:
            raise ServiceException(message='Codex daemon返回非JSON响应') from exc
        if not isinstance(data, dict):
            raise ServiceException(message='Codex daemon返回结构非法')
        return data
