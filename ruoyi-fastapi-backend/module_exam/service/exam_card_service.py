from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from module_exam.entity.do.exam_card_do import ExamCard, ExamCategory


class ExamCardService:
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
