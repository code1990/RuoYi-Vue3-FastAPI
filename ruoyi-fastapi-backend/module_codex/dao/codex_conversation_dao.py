from typing import Any

from sqlalchemy import asc, desc, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from common.vo import PageModel
from module_codex.entity.do.codex_conversation_do import (
    CodexConversation,
    CodexConversationEvent,
    CodexConversationMessage,
    CodexConversationTask,
)
from module_codex.entity.vo.codex_conversation_vo import CodexConversationPageQueryModel
from utils.common_util import CamelCaseUtil
from utils.page_util import PageUtil


class CodexConversationDao:
    """
    Codex 对话历史数据库操作层
    """

    @classmethod
    async def get_conversation_list(
        cls, db: AsyncSession, query_object: CodexConversationPageQueryModel, is_page: bool = False
    ) -> PageModel | list[dict[str, Any]]:
        order_column_map = {
            'updatedAtMs': CodexConversation.updated_at_ms,
            'createdAtMs': CodexConversation.created_at_ms,
            'title': CodexConversation.title,
            'status': CodexConversation.status,
            'operator': CodexConversation.operator,
            'conversationId': CodexConversation.conversation_id,
        }
        order_column = order_column_map.get(query_object.order_by_column, CodexConversation.updated_at_ms)
        if query_object.is_asc == 'ascending':
            order_by = asc(order_column)
        else:
            order_by = desc(order_column)

        search_text = query_object.search_text.strip() if query_object.search_text else None
        statuses = query_object.statuses or ([query_object.status] if query_object.status else None)
        workspace_ids = query_object.workspace_ids or ([query_object.workspace_id] if query_object.workspace_id else None)
        query = (
            select(CodexConversation)
            .where(
                CodexConversation.conversation_id == query_object.conversation_id
                if query_object.conversation_id
                else True,
                CodexConversation.workspace_id.in_(workspace_ids) if workspace_ids else True,
                CodexConversation.thread_id == query_object.thread_id if query_object.thread_id else True,
                CodexConversation.operator == query_object.operator if query_object.operator else True,
                CodexConversation.status.in_(statuses) if statuses else True,
                CodexConversation.last_error.is_not(None) if query_object.has_error is True else True,
                CodexConversation.last_error.is_(None) if query_object.has_error is False else True,
                CodexConversation.created_at_ms >= query_object.created_at_start_ms
                if query_object.created_at_start_ms is not None
                else True,
                CodexConversation.created_at_ms <= query_object.created_at_end_ms
                if query_object.created_at_end_ms is not None
                else True,
                CodexConversation.updated_at_ms >= query_object.updated_at_start_ms
                if query_object.updated_at_start_ms is not None
                else True,
                CodexConversation.updated_at_ms <= query_object.updated_at_end_ms
                if query_object.updated_at_end_ms is not None
                else True,
                CodexConversation.title.like(f'%{query_object.title}%') if query_object.title else True,
                or_(
                    CodexConversation.conversation_id.like(f'%{search_text}%'),
                    CodexConversation.thread_id.like(f'%{search_text}%'),
                    CodexConversation.title.like(f'%{search_text}%'),
                    CodexConversation.requirement.like(f'%{search_text}%'),
                    CodexConversation.last_message_preview.like(f'%{search_text}%'),
                    CodexConversation.final_summary.like(f'%{search_text}%'),
                    CodexConversation.last_error.like(f'%{search_text}%'),
                )
                if search_text
                else True,
            )
            .order_by(order_by, desc(CodexConversation.id))
        )
        return await PageUtil.paginate(db, query, query_object.page_num, query_object.page_size, is_page)

    @classmethod
    async def get_conversation_detail(cls, db: AsyncSession, conversation_id: str) -> dict[str, Any] | None:
        result = await db.execute(
            select(CodexConversation).where(CodexConversation.conversation_id == conversation_id).limit(1)
        )
        record = result.scalar_one_or_none()
        return CamelCaseUtil.transform_result(record) if record else None

    @classmethod
    async def get_conversation_messages(cls, db: AsyncSession, conversation_id: str) -> list[dict[str, Any]]:
        result = await db.execute(
            select(CodexConversationMessage)
            .where(CodexConversationMessage.conversation_id == conversation_id)
            .order_by(asc(CodexConversationMessage.sequence_no), asc(CodexConversationMessage.id))
        )
        return CamelCaseUtil.transform_result(result.scalars().all())

    @classmethod
    async def get_conversation_messages_by_ids(
        cls, db: AsyncSession, conversation_ids: list[str]
    ) -> list[dict[str, Any]]:
        if not conversation_ids:
            return []
        result = await db.execute(
            select(CodexConversationMessage)
            .where(CodexConversationMessage.conversation_id.in_(conversation_ids))
            .order_by(
                asc(CodexConversationMessage.conversation_id),
                asc(CodexConversationMessage.sequence_no),
                asc(CodexConversationMessage.id),
            )
        )
        return CamelCaseUtil.transform_result(result.scalars().all())

    @classmethod
    async def get_conversation_events(cls, db: AsyncSession, conversation_id: str) -> list[dict[str, Any]]:
        result = await db.execute(
            select(CodexConversationEvent)
            .where(CodexConversationEvent.conversation_id == conversation_id)
            .order_by(asc(CodexConversationEvent.created_at_ms), asc(CodexConversationEvent.id))
        )
        return CamelCaseUtil.transform_result(result.scalars().all())

    @classmethod
    async def get_conversation_events_by_ids(
        cls, db: AsyncSession, conversation_ids: list[str]
    ) -> list[dict[str, Any]]:
        if not conversation_ids:
            return []
        result = await db.execute(
            select(CodexConversationEvent)
            .where(CodexConversationEvent.conversation_id.in_(conversation_ids))
            .order_by(
                asc(CodexConversationEvent.conversation_id),
                asc(CodexConversationEvent.created_at_ms),
                asc(CodexConversationEvent.id),
            )
        )
        return CamelCaseUtil.transform_result(result.scalars().all())

    @classmethod
    async def get_conversation_tasks(cls, db: AsyncSession, conversation_id: str) -> list[dict[str, Any]]:
        result = await db.execute(
            select(CodexConversationTask)
            .where(CodexConversationTask.conversation_id == conversation_id)
            .order_by(desc(CodexConversationTask.submitted_at_ms), desc(CodexConversationTask.id))
        )
        return CamelCaseUtil.transform_result(result.scalars().all())

    @classmethod
    async def get_conversation_tasks_by_ids(
        cls, db: AsyncSession, conversation_ids: list[str]
    ) -> list[dict[str, Any]]:
        if not conversation_ids:
            return []
        result = await db.execute(
            select(CodexConversationTask)
            .where(CodexConversationTask.conversation_id.in_(conversation_ids))
            .order_by(
                asc(CodexConversationTask.conversation_id),
                desc(CodexConversationTask.submitted_at_ms),
                desc(CodexConversationTask.id),
            )
        )
        return CamelCaseUtil.transform_result(result.scalars().all())
