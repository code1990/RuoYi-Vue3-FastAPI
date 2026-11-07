from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions.exception import ServiceException
from module_exam.entity.do.exam_card_do import ExamCard, ExamCardAiSummaryVersion, ExamCategory


class ExamCardService:
    @staticmethod
    def _summary_version(row: ExamCardAiSummaryVersion) -> dict:
        return {
            'summary_version_id': row.summary_version_id,
            'version_no': row.version_no,
            'title': row.title,
            'ai_summary': row.ai_summary,
            'create_time': row.create_time,
            'update_time': row.update_time,
        }

    @classmethod
    async def categories(cls, db: AsyncSession) -> list[dict]:
        rows = (await db.scalars(select(ExamCategory).where(ExamCategory.status == 'published').order_by(ExamCategory.sort_no, ExamCategory.category_id))).all()
        return [
            {'category_id': row.category_id, 'parent_id': row.parent_id, 'name': row.name, 'sort_no': row.sort_no}
            for row in rows
        ]

    @classmethod
    async def cards(cls, db: AsyncSession, category_id: int | None = None) -> list[dict]:
        statement = select(ExamCard).where(ExamCard.status == 'published')
        if category_id:
            statement = statement.where(ExamCard.category_id == category_id)
        rows = (await db.scalars(statement.order_by(ExamCard.category_id, ExamCard.sort_no, ExamCard.card_id))).all()
        return [
            {
                'card_id': row.card_id,
                'category_id': row.category_id,
                'question': row.question,
                'answer': row.answer,
                'ai_summary': row.ai_summary,
                'key_points': row.key_points,
                'tags': row.tags,
                'card_type': row.card_type,
                'difficulty': row.difficulty,
            }
            for row in rows
        ]

    @classmethod
    async def ai_summary_versions(cls, db: AsyncSession, card_id: int) -> dict:
        card = await db.get(ExamCard, card_id)
        if not card:
            raise ServiceException(message='题目不存在')
        rows = (await db.scalars(
            select(ExamCardAiSummaryVersion)
            .where(ExamCardAiSummaryVersion.card_id == card_id)
            .order_by(ExamCardAiSummaryVersion.version_no)
        )).all()
        return {
            'active_summary_version_id': card.active_ai_summary_version_id,
            'versions': [cls._summary_version(row) for row in rows],
        }

    @classmethod
    async def add_ai_summary_version(cls, db: AsyncSession, card_id: int, title: str, ai_summary: str) -> dict:
        title = title.strip()
        ai_summary = ai_summary.strip()
        if not title or not ai_summary:
            raise ServiceException(message='方案名称和AI总结不能为空')
        card = await db.get(ExamCard, card_id, with_for_update=True)
        if not card:
            raise ServiceException(message='题目不存在')
        try:
            version_no = (await db.scalar(
                select(ExamCardAiSummaryVersion.version_no)
                .where(ExamCardAiSummaryVersion.card_id == card_id)
                .order_by(desc(ExamCardAiSummaryVersion.version_no))
                .limit(1)
            ) or 0) + 1
            version = ExamCardAiSummaryVersion(
                card_id=card_id,
                version_no=version_no,
                title=title,
                ai_summary=ai_summary,
            )
            db.add(version)
            await db.commit()
            await db.refresh(version)
            return cls._summary_version(version)
        except Exception:
            await db.rollback()
            raise

    @classmethod
    async def activate_ai_summary_version(cls, db: AsyncSession, card_id: int, summary_version_id: int) -> dict:
        card = await db.get(ExamCard, card_id, with_for_update=True)
        if not card:
            raise ServiceException(message='题目不存在')
        version = await db.get(ExamCardAiSummaryVersion, summary_version_id)
        if not version or version.card_id != card_id:
            raise ServiceException(message='AI总结版本不属于该题目')
        try:
            card.active_ai_summary_version_id = version.summary_version_id
            card.ai_summary = version.ai_summary
            await db.commit()
            return {'active_summary_version_id': version.summary_version_id, 'ai_summary': version.ai_summary}
        except Exception:
            await db.rollback()
            raise
