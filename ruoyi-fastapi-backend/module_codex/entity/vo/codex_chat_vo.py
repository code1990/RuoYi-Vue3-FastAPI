from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class CodexChatConversationStartModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    workspace_id: str = Field(description='workspace id')
    title: str | None = Field(default=None, description='conversation title')
    requirement: str = Field(description='conversation requirement')
    operator: str | None = Field(default=None, description='operator')
    model: str | None = Field(default=None, description='model')
    effort: str | None = Field(default=None, description='effort')
    service_tier: str | None = Field(default=None, description='service tier')
    access_mode: str | None = Field(default=None, description='access mode')
    images: list[str] | None = Field(default=None, description='images')
    app_mentions: list[dict[str, Any]] | None = Field(default=None, description='app mentions')
    collaboration_mode: dict[str, Any] | None = Field(default=None, description='collaboration mode')
    codex_profile: str | None = Field(default=None, description='codex profile')
    default_prompt_template: str | None = Field(default=None, description='default prompt template')


class CodexChatConversationMessageModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    text: str = Field(description='message text')
    model: str | None = Field(default=None, description='model')
    effort: str | None = Field(default=None, description='effort')
    service_tier: str | None = Field(default=None, description='service tier')
    access_mode: str | None = Field(default=None, description='access mode')
    images: list[str] | None = Field(default=None, description='images')
    app_mentions: list[dict[str, Any]] | None = Field(default=None, description='app mentions')
    collaboration_mode: dict[str, Any] | None = Field(default=None, description='collaboration mode')


class CodexChatConversationQueryModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    workspace_id: str | None = Field(default=None, description='workspace id')


class CodexChatServerRequestRespondModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    workspace_id: str = Field(description='workspace id')
    request_id: int | str = Field(description='request id')
    result: dict[str, Any] = Field(description='request result')
