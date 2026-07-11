from typing import Literal

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class CodexConversationModel(BaseModel):
    """
    Codex 对话模型
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        from_attributes=True,
        populate_by_name=True,
        json_schema_extra={
            'example': {
                'conversationId': 'conv-1',
                'workspaceId': 'ws-1',
                'threadId': 'thread-1',
                'title': 'Fix login redirect',
                'requirement': 'Inspect the repo and fix the redirect bug.',
                'status': 'running',
                'operator': 'alice',
                'lastMessagePreview': 'Investigating the redirect middleware.',
                'finalSummary': None,
                'lastError': None,
                'createdAtMs': 1760000000000,
                'updatedAtMs': 1760000005000,
            }
        },
    )

    id: int | None = Field(default=None, description='主键ID')
    conversation_id: str | None = Field(default=None, description='会话ID')
    workspace_id: str | None = Field(default=None, description='工作区ID')
    thread_id: str | None = Field(default=None, description='线程ID')
    title: str | None = Field(default=None, description='标题')
    requirement: str | None = Field(default=None, description='需求内容')
    status: str | None = Field(default=None, description='会话状态')
    operator: str | None = Field(default=None, description='操作者')
    last_message_preview: str | None = Field(default=None, description='最后一条消息预览')
    final_summary: str | None = Field(default=None, description='最终总结')
    last_error: str | None = Field(default=None, description='最后错误')
    created_at_ms: int | None = Field(default=None, description='创建时间毫秒时间戳')
    updated_at_ms: int | None = Field(default=None, description='更新时间毫秒时间戳')


class CodexConversationMessageModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    id: int | None = Field(default=None, description='主键ID')
    conversation_id: str | None = Field(default=None, description='会话ID')
    thread_id: str | None = Field(default=None, description='线程ID')
    turn_id: str | None = Field(default=None, description='轮次ID')
    role: str | None = Field(default=None, description='消息角色')
    message_type: str | None = Field(default=None, description='消息类型')
    content: str | None = Field(default=None, description='消息内容')
    payload_json: str | None = Field(default=None, description='扩展负载JSON')
    sequence_no: int | None = Field(default=None, description='消息顺序号')
    created_at_ms: int | None = Field(default=None, description='创建时间毫秒时间戳')


class CodexConversationEventModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    id: int | None = Field(default=None, description='主键ID')
    conversation_id: str | None = Field(default=None, description='会话ID')
    thread_id: str | None = Field(default=None, description='线程ID')
    turn_id: str | None = Field(default=None, description='轮次ID')
    event_type: str | None = Field(default=None, description='事件类型')
    event_status: str | None = Field(default=None, description='事件状态')
    payload_json: str | None = Field(default=None, description='事件负载JSON')
    created_at_ms: int | None = Field(default=None, description='创建时间毫秒时间戳')


class CodexConversationTaskModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        from_attributes=True,
        populate_by_name=True,
        json_schema_extra={
            'example': {
                'taskId': 'task-2',
                'workspaceId': 'ws-1',
                'threadId': 'thread-1',
                'turnId': 'turn-2',
                'status': 'running',
                'createdThread': False,
                'submittedAtMs': 1760000004000,
                'completedAtMs': None,
                'lastError': None,
            }
        },
    )

    id: int | None = Field(default=None, description='主键ID')
    conversation_id: str | None = Field(default=None, description='会话ID')
    task_id: str | None = Field(default=None, description='任务ID')
    workspace_id: str | None = Field(default=None, description='工作区ID')
    thread_id: str | None = Field(default=None, description='线程ID')
    turn_id: str | None = Field(default=None, description='轮次ID')
    status: str | None = Field(default=None, description='任务状态')
    created_thread: bool | None = Field(default=None, description='是否为本次任务新建线程；true=新建，false=复用')
    submitted_at_ms: int | None = Field(default=None, description='提交时间毫秒时间戳')
    completed_at_ms: int | None = Field(default=None, description='完成时间毫秒时间戳')
    last_error: str | None = Field(default=None, description='最后错误')


class CodexConversationCurrentStateModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    status: str | None = Field(default=None, description='当前执行状态')
    phase: str | None = Field(default=None, description='当前阶段')
    is_running: bool = Field(default=False, description='是否执行中')
    has_error: bool = Field(default=False, description='是否存在错误')
    active_task_count: int = Field(default=0, description='活跃任务数')
    latest_task_id: str | None = Field(default=None, description='最新任务ID')
    latest_task_status: str | None = Field(default=None, description='最新任务状态')
    latest_event_type: str | None = Field(default=None, description='最新事件类型')
    latest_event_status: str | None = Field(default=None, description='最新事件状态')
    current_turn_id: str | None = Field(default=None, description='当前轮次ID')
    last_activity_at_ms: int | None = Field(default=None, description='最后活跃时间毫秒时间戳')


class CodexConversationHistorySummaryModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    message_count: int = Field(default=0, description='消息总数')
    user_message_count: int = Field(default=0, description='用户消息数')
    assistant_message_count: int = Field(default=0, description='助手消息数')
    event_count: int = Field(default=0, description='事件总数')
    task_count: int = Field(default=0, description='任务总数')
    completed_task_count: int = Field(default=0, description='完成任务数')
    failed_task_count: int = Field(default=0, description='失败任务数')
    latest_message_preview: str | None = Field(default=None, description='最新消息摘要')
    latest_message_at_ms: int | None = Field(default=None, description='最新消息时间毫秒时间戳')
    started_at_ms: int | None = Field(default=None, description='开始时间毫秒时间戳')
    finished_at_ms: int | None = Field(default=None, description='结束时间毫秒时间戳')


class CodexConversationListViewModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        from_attributes=True,
        populate_by_name=True,
        json_schema_extra={
            'example': {
                'conversation': {
                    'conversationId': 'conv-1',
                    'workspaceId': 'ws-1',
                    'threadId': 'thread-1',
                    'title': 'Fix login redirect',
                    'requirement': 'Inspect the repo and fix the redirect bug.',
                    'status': 'running',
                    'operator': 'alice',
                    'lastMessagePreview': 'Investigating the redirect middleware.',
                    'finalSummary': None,
                    'lastError': None,
                    'createdAtMs': 1760000000000,
                    'updatedAtMs': 1760000005000,
                },
                'currentState': {
                    'status': 'running',
                    'phase': 'conversation.streaming',
                    'isRunning': True,
                    'hasError': False,
                    'activeTaskCount': 1,
                    'latestTaskId': 'task-2',
                    'latestTaskStatus': 'running',
                    'latestEventType': 'conversation.streaming',
                    'latestEventStatus': 'ok',
                    'currentTurnId': 'turn-2',
                    'lastActivityAtMs': 1760000005000,
                },
                'historySummary': {
                    'messageCount': 8,
                    'userMessageCount': 3,
                    'assistantMessageCount': 5,
                    'eventCount': 12,
                    'taskCount': 2,
                    'completedTaskCount': 1,
                    'failedTaskCount': 0,
                    'latestMessagePreview': 'Investigating the redirect middleware.',
                    'latestMessageAtMs': 1760000005000,
                    'startedAtMs': 1760000000000,
                    'finishedAtMs': None,
                },
            }
        },
    )

    conversation: CodexConversationModel = Field(description='会话主信息')
    current_state: CodexConversationCurrentStateModel = Field(description='当前执行状态聚合')
    history_summary: CodexConversationHistorySummaryModel = Field(description='历史摘要聚合')


class CodexConversationReadModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        from_attributes=True,
        populate_by_name=True,
        json_schema_extra={
            'example': {
                'conversation': {
                    'conversationId': 'conv-1',
                    'workspaceId': 'ws-1',
                    'threadId': 'thread-1',
                    'title': 'Fix login redirect',
                    'requirement': 'Inspect the repo and fix the redirect bug.',
                    'status': 'running',
                    'operator': 'alice',
                    'lastMessagePreview': 'Investigating the redirect middleware.',
                    'finalSummary': None,
                    'lastError': None,
                    'createdAtMs': 1760000000000,
                    'updatedAtMs': 1760000005000,
                },
                'currentState': {
                    'status': 'running',
                    'phase': 'conversation.streaming',
                    'isRunning': True,
                    'hasError': False,
                    'activeTaskCount': 1,
                    'latestTaskId': 'task-2',
                    'latestTaskStatus': 'running',
                    'latestEventType': 'conversation.streaming',
                    'latestEventStatus': 'ok',
                    'currentTurnId': 'turn-2',
                    'lastActivityAtMs': 1760000005000,
                },
                'historySummary': {
                    'messageCount': 8,
                    'userMessageCount': 3,
                    'assistantMessageCount': 5,
                    'eventCount': 12,
                    'taskCount': 2,
                    'completedTaskCount': 1,
                    'failedTaskCount': 0,
                    'latestMessagePreview': 'Investigating the redirect middleware.',
                    'latestMessageAtMs': 1760000005000,
                    'startedAtMs': 1760000000000,
                    'finishedAtMs': None,
                },
                'messages': [],
                'events': [],
                'tasks': [],
            }
        },
    )

    conversation: CodexConversationModel = Field(description='会话主信息')
    current_state: CodexConversationCurrentStateModel = Field(description='当前执行状态聚合')
    history_summary: CodexConversationHistorySummaryModel = Field(description='历史摘要聚合')
    messages: list[CodexConversationMessageModel] = Field(default_factory=list, description='会话消息')
    events: list[CodexConversationEventModel] = Field(default_factory=list, description='会话事件')
    tasks: list[CodexConversationTaskModel] = Field(default_factory=list, description='会话任务')


class CodexConversationQueryModel(BaseModel):
    """
    Codex 对话查询模型
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        from_attributes=True,
        populate_by_name=True,
        json_schema_extra={
            'example': {
                'workspaceId': 'ws-1',
                'statuses': ['running', 'completed'],
                'hasError': False,
                'searchText': 'redirect middleware',
                'orderByColumn': 'updatedAtMs',
                'isAsc': 'descending',
            }
        },
    )

    conversation_id: str | None = Field(default=None, description='会话ID')
    workspace_id: str | None = Field(default=None, description='工作区ID')
    workspace_ids: list[str] | None = Field(default=None, description='工作区ID列表')
    thread_id: str | None = Field(default=None, description='线程ID')
    operator: str | None = Field(default=None, description='操作者')
    title: str | None = Field(default=None, description='标题')
    search_text: str | None = Field(default=None, description='全文检索，匹配会话ID/线程ID/标题/需求/消息摘要/总结/错误')
    status: str | None = Field(default=None, description='状态')
    statuses: list[str] | None = Field(default=None, description='状态列表')
    has_error: bool | None = Field(default=None, description='是否存在错误')
    created_at_start_ms: int | None = Field(default=None, description='创建时间起始毫秒时间戳')
    created_at_end_ms: int | None = Field(default=None, description='创建时间结束毫秒时间戳')
    updated_at_start_ms: int | None = Field(default=None, description='更新时间起始毫秒时间戳')
    updated_at_end_ms: int | None = Field(default=None, description='更新时间结束毫秒时间戳')
    order_by_column: Literal[
        'updatedAtMs',
        'createdAtMs',
        'title',
        'status',
        'operator',
        'conversationId',
    ] | None = Field(default=None, description='排序字段')
    is_asc: Literal['ascending', 'descending'] | None = Field(default=None, description='排序方式')


class CodexConversationPageQueryModel(CodexConversationQueryModel):
    """
    Codex 对话分页查询模型
    """

    page_num: int = Field(default=1, description='当前页码')
    page_size: int = Field(default=10, description='每页记录数')
