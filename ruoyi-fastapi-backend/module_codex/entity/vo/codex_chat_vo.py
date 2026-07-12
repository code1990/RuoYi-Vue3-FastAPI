from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class CodexChatStartRequestModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    workspace_id: str = Field(description='工作区ID')
    title: str = Field(description='会话标题')
    requirement: str = Field(description='首条需求')
    operator: str | None = Field(default=None, description='操作者')
    model: str | None = Field(default=None, description='模型')
    effort: str | None = Field(default=None, description='推理强度')
    service_tier: str | None = Field(default=None, description='服务层级')
    access_mode: str | None = Field(default=None, description='访问模式')
    images: list[Any] | None = Field(default=None, description='图片列表')
    app_mentions: list[str] | None = Field(default=None, description='应用提及列表')
    collaboration_mode: str | None = Field(default=None, description='协作模式')
    codex_profile: str | None = Field(default=None, description='Codex profile')
    default_prompt_template: str | None = Field(default=None, description='默认提示词模板')


class CodexChatMessageRequestModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    text: str = Field(description='追问内容')
    model: str | None = Field(default=None, description='模型')
    effort: str | None = Field(default=None, description='推理强度')
    service_tier: str | None = Field(default=None, description='服务层级')
    access_mode: str | None = Field(default=None, description='访问模式')
    images: list[Any] | None = Field(default=None, description='图片列表')
    app_mentions: list[str] | None = Field(default=None, description='应用提及列表')
    collaboration_mode: str | None = Field(default=None, description='协作模式')
    codex_profile: str | None = Field(default=None, description='Codex profile')
    default_prompt_template: str | None = Field(default=None, description='默认提示词模板')


class CodexChatAcceptedTaskModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    task_id: str | None = Field(default=None, description='任务ID')
    status: str | None = Field(default=None, description='任务状态')
    workspace_id: str | None = Field(default=None, description='工作区ID')
    thread_id: str | None = Field(default=None, description='线程ID')
    turn_id: str | None = Field(default=None, description='轮次ID')
    created_thread: bool | None = Field(default=None, description='是否新建线程')
    submitted_at_ms: int | None = Field(default=None, description='提交时间')
    completed_at_ms: int | None = Field(default=None, description='完成时间')
    last_error: str | None = Field(default=None, description='最后错误')


class CodexChatConversationSummaryModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    conversation_id: str | None = Field(default=None, description='会话ID')
    workspace_id: str | None = Field(default=None, description='工作区ID')
    thread_id: str | None = Field(default=None, description='线程ID')
    title: str | None = Field(default=None, description='标题')
    requirement: str | None = Field(default=None, description='需求')
    status: str | None = Field(default=None, description='会话状态')
    last_message_preview: str | None = Field(default=None, description='最后消息摘要')


class CodexChatActionResponseModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    conversation: CodexChatConversationSummaryModel = Field(description='会话摘要')
    task: CodexChatAcceptedTaskModel = Field(description='受理任务')
