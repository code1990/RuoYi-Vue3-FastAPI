import importlib
import json
import sys
import types

import pytest
from fastapi import Depends

from config.env import CodexMonitorConfig
from exceptions.exception import ServiceException
from module_codex.entity.vo.codex_chat_vo import CodexChatConversationMessageModel, CodexChatConversationStartModel
from module_codex.service.codex_chat_service import CodexChatService


def _load_controller_module():
    fake_pre_auth = types.ModuleType('common.aspect.pre_auth')
    fake_pre_auth.PreAuthDependency = lambda: Depends(lambda: None)
    fake_pre_auth.CurrentUserDependency = lambda: Depends(lambda: None)
    sys.modules['common.aspect.pre_auth'] = fake_pre_auth
    sys.modules.pop('module_codex.controller.codex_chat_controller', None)
    return importlib.import_module('module_codex.controller.codex_chat_controller')


class _FakeResponse:
    def __init__(self, status_code: int, payload: dict):
        self.status_code = status_code
        self._payload = payload
        self.text = json.dumps(payload, ensure_ascii=False)

    def json(self):
        return self._payload


class _FakeAsyncClient:
    def __init__(self, recorder: dict):
        self.recorder = recorder

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def request(self, method: str, url: str, headers: dict, params=None, json=None):
        self.recorder['method'] = method
        self.recorder['url'] = url
        self.recorder['json'] = json
        self.recorder['headers'] = headers
        self.recorder['params'] = params
        return _FakeResponse(
            202,
            {
                'ok': True,
                'data': {
                    'conversation': {
                        'conversationId': 'conv-1',
                        'workspaceId': 'ws-1',
                        'threadId': 'thread-1',
                        'status': 'accepted',
                    },
                    'task': {
                        'taskId': 'task-1',
                        'status': 'running',
                        'workspaceId': 'ws-1',
                        'threadId': 'thread-1',
                        'turnId': 'turn-1',
                        'createdThread': True,
                    },
                },
            },
        )


@pytest.mark.asyncio
async def test_codex_chat_service_posts_to_daemon(monkeypatch):
    recorder: dict = {}
    monkeypatch.setattr('module_codex.service.codex_chat_service.httpx.AsyncClient', lambda timeout: _FakeAsyncClient(recorder))
    monkeypatch.setattr(CodexMonitorConfig, 'codex_monitor_base_url', 'http://127.0.0.1:4733')
    monkeypatch.setattr(CodexMonitorConfig, 'codex_monitor_token', 'daemon-token')
    monkeypatch.setattr(CodexMonitorConfig, 'codex_monitor_http_timeout_seconds', 30.0)
    monkeypatch.setattr(CodexMonitorConfig, 'codex_monitor_connect_timeout_seconds', 10.0)

    result = await CodexChatService.start_conversation_services(
        CodexChatConversationStartModel(workspaceId='ws-1', title='t', requirement='r'),
        None,
    )

    assert recorder['method'] == 'POST'
    assert recorder['url'] == 'http://127.0.0.1:4733/api/v1/conversations/start'
    assert recorder['json']['workspaceId'] == 'ws-1'
    assert recorder['headers']['Authorization'] == 'Bearer daemon-token'
    assert result['conversation']['conversationId'] == 'conv-1'


@pytest.mark.asyncio
async def test_codex_chat_service_raises_on_daemon_error(monkeypatch):
    class _ErrorClient(_FakeAsyncClient):
        async def request(self, method: str, url: str, headers: dict, params=None, json=None):
            return _FakeResponse(
                404,
                {
                    'ok': False,
                    'error': {'code': 'conversation_not_found', 'message': 'conversation not found'},
                },
            )

    monkeypatch.setattr('module_codex.service.codex_chat_service.httpx.AsyncClient', lambda timeout: _ErrorClient({}))

    with pytest.raises(ServiceException) as exc_info:
        await CodexChatService.send_conversation_message_services(
            'missing', CodexChatConversationMessageModel(text='hi')
        )

    assert exc_info.value.message == 'conversation not found'


@pytest.mark.asyncio
async def test_codex_chat_controller_compat_start_returns_wrapped_success():
    controller_module = _load_controller_module()

    async def fake_start(_conversation, _current_user):
        return {
            'conversation': {'conversationId': 'conv-1', 'workspaceId': 'ws-1', 'threadId': 'thread-1'},
            'task': {'taskId': 'task-1', 'status': 'running'},
        }

    controller_module.CodexChatService.start_conversation_services = fake_start
    response = await controller_module.create_codex_chat_conversation_compat(
        request=None,
        conversation=CodexChatConversationStartModel(workspaceId='ws-1', title='t', requirement='r'),
        current_user=None,
    )
    payload = json.loads(response.body)

    assert payload['code'] == 200
    assert payload['data']['conversation']['conversationId'] == 'conv-1'
