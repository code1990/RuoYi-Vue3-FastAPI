import asyncio
import json
from collections.abc import AsyncGenerator
from typing import Any
from urllib.parse import urlparse

import httpx

from config.env import CodexMonitorConfig
from exceptions.exception import ServiceException
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_codex.entity.vo.codex_chat_vo import (
    CodexChatConversationMessageModel,
    CodexChatConversationStartModel,
    CodexChatServerRequestRespondModel,
)


class CodexChatService:
    @classmethod
    def _base_url(cls) -> str:
        return CodexMonitorConfig.codex_monitor_base_url.rstrip('/')

    @classmethod
    def _headers(cls, *, accept: str = 'application/json') -> dict[str, str]:
        headers = {'Accept': accept}
        token = CodexMonitorConfig.codex_monitor_token.strip()
        if token:
            headers['Authorization'] = f'Bearer {token}'
            headers['x-codex-token'] = token
        return headers

    @classmethod
    def _timeout(cls) -> httpx.Timeout:
        return httpx.Timeout(
            timeout=CodexMonitorConfig.codex_monitor_http_timeout_seconds,
            connect=CodexMonitorConfig.codex_monitor_connect_timeout_seconds,
        )

    @classmethod
    def _stream_timeout(cls) -> httpx.Timeout:
        return httpx.Timeout(
            timeout=None,
            connect=CodexMonitorConfig.codex_monitor_connect_timeout_seconds,
            read=CodexMonitorConfig.codex_monitor_stream_timeout_seconds,
            write=CodexMonitorConfig.codex_monitor_http_timeout_seconds,
        )

    @classmethod
    def _build_url(cls, path: str) -> str:
        return f'{cls._base_url()}{path}'

    @classmethod
    def _get_operator(cls, current_user: CurrentUserModel | None) -> str | None:
        if not current_user or not current_user.user:
            return None
        return current_user.user.nick_name or current_user.user.user_name

    @classmethod
    async def _request_json(
        cls,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> Any:
        try:
            async with httpx.AsyncClient(timeout=cls._timeout()) as client:
                response = await client.request(
                    method,
                    cls._build_url(path),
                    headers=cls._headers(),
                    params=params,
                    json=json_body,
                )
        except httpx.HTTPError as exc:
            raise ServiceException(message=f'CodexMonitor request failed: {exc}') from exc
        return cls._parse_response(response)

    @classmethod
    def _parse_response(cls, response: httpx.Response) -> Any:
        try:
            payload = response.json()
        except ValueError:
            payload = None

        if response.status_code >= 400:
            raise ServiceException(message=cls._extract_error_message(payload, response))

        if isinstance(payload, dict) and payload.get('ok') is False:
            raise ServiceException(message=cls._extract_error_message(payload, response))

        if isinstance(payload, dict) and payload.get('ok') is True and 'data' in payload:
            return payload['data']

        return payload

    @classmethod
    def _extract_error_message(cls, payload: Any, response: httpx.Response) -> str:
        if isinstance(payload, dict):
            error = payload.get('error')
            if isinstance(error, dict):
                message = error.get('message')
                if isinstance(message, str) and message.strip():
                    return message.strip()
            for key in ('message', 'msg'):
                message = payload.get(key)
                if isinstance(message, str) and message.strip():
                    return message.strip()
        text = response.text.strip()
        if text:
            return text
        return f'CodexMonitor returned HTTP {response.status_code}'

    @classmethod
    async def get_health_services(cls) -> dict[str, Any]:
        payload = await cls._request_json('GET', '/api/v1/health')
        return payload if isinstance(payload, dict) else {'value': payload}

    @classmethod
    async def list_workspaces_services(cls) -> list[dict[str, Any]]:
        payload = await cls._request_json('GET', '/api/workspaces')
        if isinstance(payload, dict) and isinstance(payload.get('workspaces'), list):
            return payload['workspaces']
        return []

    @classmethod
    async def list_conversations_services(cls, workspace_id: str | None = None) -> dict[str, Any]:
        params = {'workspaceId': workspace_id} if workspace_id else None
        payload = await cls._request_json('GET', '/api/v1/conversations', params=params)
        if isinstance(payload, dict):
            return payload
        if isinstance(payload, list):
            return {'items': payload}
        return {'items': []}

    @classmethod
    async def get_conversation_services(cls, conversation_id: str) -> dict[str, Any]:
        payload = await cls._request_json('GET', f'/api/v1/conversations/{conversation_id}')
        if not isinstance(payload, dict):
            raise ServiceException(message='Invalid CodexMonitor conversation response')
        return payload

    @classmethod
    async def get_conversation_messages_services(cls, conversation_id: str) -> dict[str, Any]:
        payload = await cls._request_json('GET', f'/api/v1/conversations/{conversation_id}/messages')
        if not isinstance(payload, dict):
            raise ServiceException(message='Invalid CodexMonitor messages response')
        return payload

    @classmethod
    async def start_conversation_services(
        cls, request: CodexChatConversationStartModel, current_user: CurrentUserModel | None
    ) -> dict[str, Any]:
        payload = request.model_dump(by_alias=True, exclude_none=True)
        payload['title'] = (request.title or '').strip() or request.requirement.strip()[:60] or 'New conversation'
        payload['requirement'] = request.requirement.strip()
        payload.setdefault('operator', cls._get_operator(current_user))
        if payload.get('operator') is None:
            payload.pop('operator', None)
        result = await cls._request_json('POST', '/api/v1/conversations/start', json_body=payload)
        if not isinstance(result, dict):
            raise ServiceException(message='Invalid CodexMonitor start response')
        return result

    @classmethod
    async def send_conversation_message_services(
        cls, conversation_id: str, request: CodexChatConversationMessageModel
    ) -> dict[str, Any]:
        result = await cls._request_json(
            'POST',
            f'/api/v1/conversations/{conversation_id}/messages',
            json_body=request.model_dump(by_alias=True, exclude_none=True),
        )
        if not isinstance(result, dict):
            raise ServiceException(message='Invalid CodexMonitor message response')
        return result

    @classmethod
    async def stream_conversation_events_services(cls, conversation_id: str) -> AsyncGenerator[bytes, None]:
        client = httpx.AsyncClient(timeout=cls._stream_timeout())
        try:
            response = await client.send(
                client.build_request(
                    'GET',
                    cls._build_url(f'/api/v1/conversations/{conversation_id}/events'),
                    headers=cls._headers(accept='text/event-stream'),
                ),
                stream=True,
            )
        except httpx.HTTPError as exc:
            await client.aclose()
            raise ServiceException(message=f'CodexMonitor stream failed: {exc}') from exc

        if response.status_code >= 400:
            message = response.text.strip() or f'CodexMonitor returned HTTP {response.status_code}'
            await response.aclose()
            await client.aclose()
            raise ServiceException(message=message)

        async def event_stream() -> AsyncGenerator[bytes, None]:
            try:
                async for chunk in response.aiter_bytes():
                    if chunk:
                        yield chunk
            except httpx.HTTPError as exc:
                yield cls._encode_sse('error', {'message': f'CodexMonitor stream interrupted: {exc}'})
            finally:
                await response.aclose()
                await client.aclose()

        return event_stream()

    @classmethod
    async def respond_to_server_request_services(
        cls, request: CodexChatServerRequestRespondModel
    ) -> dict[str, Any]:
        payload = await cls._tcp_rpc_call(
            'respond_to_server_request',
            {
                'workspaceId': request.workspace_id,
                'requestId': request.request_id,
                'result': request.result,
            },
        )
        return payload if isinstance(payload, dict) else {'result': payload}

    @classmethod
    def _encode_sse(cls, event: str, data: dict[str, Any]) -> bytes:
        return f'event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n'.encode('utf-8')

    @classmethod
    def _tcp_host(cls) -> str:
        host = CodexMonitorConfig.codex_monitor_tcp_host.strip()
        if host:
            return host
        parsed = urlparse(cls._base_url())
        return parsed.hostname or '127.0.0.1'

    @classmethod
    async def _tcp_rpc_call(cls, method: str, params: dict[str, Any]) -> Any:
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(cls._tcp_host(), CodexMonitorConfig.codex_monitor_tcp_port),
                timeout=CodexMonitorConfig.codex_monitor_connect_timeout_seconds,
            )
        except (OSError, asyncio.TimeoutError) as exc:
            raise ServiceException(message=f'CodexMonitor TCP connect failed: {exc}') from exc

        try:
            request_id = 1
            token = CodexMonitorConfig.codex_monitor_token.strip()
            if token:
                await cls._write_rpc(writer, {'id': request_id, 'method': 'auth', 'params': {'token': token}})
                await cls._read_rpc_response(reader, request_id)
                request_id += 1
            await cls._write_rpc(writer, {'id': request_id, 'method': method, 'params': params})
            return await cls._read_rpc_response(reader, request_id)
        except (json.JSONDecodeError, OSError, asyncio.TimeoutError) as exc:
            raise ServiceException(message=f'CodexMonitor TCP request failed: {exc}') from exc
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except OSError:
                pass

    @classmethod
    async def _write_rpc(cls, writer: asyncio.StreamWriter, payload: dict[str, Any]) -> None:
        writer.write((json.dumps(payload, ensure_ascii=False) + '\n').encode('utf-8'))
        await writer.drain()

    @classmethod
    async def _read_rpc_response(cls, reader: asyncio.StreamReader, request_id: int) -> Any:
        while True:
            raw = await asyncio.wait_for(
                reader.readline(), timeout=CodexMonitorConfig.codex_monitor_http_timeout_seconds
            )
            if not raw:
                raise ServiceException(message='CodexMonitor TCP connection closed unexpectedly')
            payload = json.loads(raw.decode('utf-8').strip())
            if payload.get('id') != request_id:
                continue
            if 'error' in payload:
                error = payload['error']
                if isinstance(error, dict) and isinstance(error.get('message'), str):
                    raise ServiceException(message=error['message'])
                raise ServiceException(message='CodexMonitor TCP request returned an error')
            return payload.get('result')
