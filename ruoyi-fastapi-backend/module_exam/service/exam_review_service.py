from datetime import date, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from module_exam.entity.do.exam_card_do import ExamCard, ExamCardReview, ExamCardReviewLog, ExamCategory


class ExamReviewService:
    @staticmethod
    def _review_required(review: ExamCardReview) -> int:
        return max(3, review.required_repetitions - max(0, (review.review_round or 1) - 4))

    @staticmethod
    def _card(row: ExamCard, review: ExamCardReview | None = None) -> dict:
        required = ExamReviewService._review_required(review) if review and review.state == 'review' else review.required_repetitions if review else max(4, row.difficulty + 2)
        return {'cardId': row.card_id, 'categoryId': row.category_id, 'question': row.question, 'aiSummary': row.ai_summary, 'keyPoints': row.key_points, 'tags': row.tags, 'difficulty': row.difficulty, 'progress': {'completed': review.completed_repetitions if review else 0, 'required': required, 'phase': review.state if review else 'learning', 'round': review.review_round if review and review.state == 'review' else None}}

    @classmethod
    async def overview(cls, db: AsyncSession, user_id: int, year: int | None = None) -> dict:
        now = datetime.now(); today = now.date(); year = year or today.year
        due = await db.scalar(select(func.count()).select_from(ExamCardReview).where(ExamCardReview.user_id == user_id, ExamCardReview.state == 'review', ExamCardReview.next_review_time <= now)) or 0
        new_count = await db.scalar(select(func.count()).select_from(ExamCard).where(ExamCard.review_enabled.is_(True), ExamCard.status == 'published', ~ExamCard.card_id.in_(select(ExamCardReview.card_id).where(ExamCardReview.user_id == user_id)))) or 0
        start, end = date(year, 1, 1), date(year + 1, 1, 1)
        rows = (await db.execute(select(func.date(ExamCardReviewLog.reviewed_time), func.count()).where(ExamCardReviewLog.user_id == user_id, ExamCardReviewLog.reviewed_time >= start, ExamCardReviewLog.reviewed_time < end).group_by(func.date(ExamCardReviewLog.reviewed_time)))).all()
        planned_rows = (await db.execute(select(func.date(ExamCardReview.next_review_time), func.count()).where(ExamCardReview.user_id == user_id, ExamCardReview.state == 'review', ExamCardReview.next_review_time > now, ExamCardReview.next_review_time >= start, ExamCardReview.next_review_time < end).group_by(func.date(ExamCardReview.next_review_time)))).all()
        heatmap = [{'date': str(day), 'count': count} for day, count in rows]
        planned_reviews = [{'date': str(day), 'count': count} for day, count in planned_rows]
        completed_today = next((item['count'] for item in heatmap if item['date'] == str(today)), 0)
        return {'dueCount': due, 'newAvailable': new_count, 'completedToday': completed_today, 'heatmap': heatmap, 'plannedReviews': planned_reviews}

    @classmethod
    async def next_card(cls, db: AsyncSession, user_id: int) -> dict | None:
        now = datetime.now()
        review = await db.scalar(select(ExamCardReview).where(ExamCardReview.user_id == user_id, ExamCardReview.state == 'review', ExamCardReview.next_review_time <= now).order_by(ExamCardReview.next_review_time))
        if review:
            return cls._card(await db.get(ExamCard, review.card_id), review)
        review = await db.scalar(select(ExamCardReview).join(ExamCard, ExamCard.card_id == ExamCardReview.card_id).join(ExamCategory, ExamCategory.category_id == ExamCard.category_id).where(ExamCardReview.user_id == user_id, ExamCardReview.state == 'learning', ExamCardReview.completed_repetitions < ExamCardReview.required_repetitions).order_by(ExamCategory.sort_no, ExamCategory.category_id, ExamCardReview.learning_batch, ExamCardReview.last_review_time))
        if review:
            return cls._card(await db.get(ExamCard, review.card_id), review)
        batch = (await db.scalar(select(func.max(ExamCardReview.learning_batch)).where(ExamCardReview.user_id == user_id)) or 0) + 1
        available_cards = (ExamCard.review_enabled.is_(True), ExamCard.status == 'published', ~ExamCard.card_id.in_(select(ExamCardReview.card_id).where(ExamCardReview.user_id == user_id)))
        category_id = await db.scalar(select(ExamCard.category_id).join(ExamCategory, ExamCategory.category_id == ExamCard.category_id).where(*available_cards).order_by(ExamCategory.sort_no, ExamCategory.category_id, ExamCard.sort_no, ExamCard.card_id).limit(1))
        cards = (await db.scalars(select(ExamCard).where(*available_cards, ExamCard.category_id == category_id).order_by(ExamCard.sort_no, ExamCard.card_id).limit(5))).all()
        if not cards:
            return None
        first_card_id = cards[0].card_id
        for card in cards:
            db.add(ExamCardReview(user_id=user_id, card_id=card.card_id, state='learning', learning_batch=batch, required_repetitions=max(4, card.difficulty + 2), completed_repetitions=0, interval_days=1))
        await db.commit()
        return cls._card(await db.get(ExamCard, first_card_id))

    @classmethod
    async def rate(cls, db: AsyncSession, user_id: int, card_id: int, rating: str) -> dict:
        card = await db.get(ExamCard, card_id)
        if not card or not card.review_enabled or card.status != 'published':
            raise ValueError('该卡片未启用复习')
        now = datetime.now()
        review = await db.scalar(select(ExamCardReview).where(ExamCardReview.user_id == user_id, ExamCardReview.card_id == card_id))
        if not review:
            review = ExamCardReview(user_id=user_id, card_id=card_id, state='learning', required_repetitions=max(4, card.difficulty + 2), completed_repetitions=0, interval_days=1); db.add(review)
            if rating == 'hard': review.required_repetitions += 1
            if rating == 'again': review.required_repetitions += 2
        if review.state == 'learning':
            if rating == 'again': review.required_repetitions = min(10, review.required_repetitions + 1)
            else: review.completed_repetitions += 1
            if review.completed_repetitions >= review.required_repetitions:
                review.state, review.completed_repetitions, review.review_round, review.interval_days, review.next_review_time = 'review', 0, 1, 1, now + timedelta(days=1)
        elif rating == 'again':
            review.state, review.completed_repetitions, review.review_round, review.next_review_time = 'learning', 0, 0, None
        else:
            review.completed_repetitions += 1
            if review.completed_repetitions >= cls._review_required(review):
                factor = {'hard': 1.2, 'good': 2.5, 'easy': 3.5}[rating]
                review.interval_days = min(180, max(1, round((review.interval_days or 1) * factor)))
                review.next_review_time = now + timedelta(days=review.interval_days)
                review.completed_repetitions = 0
                review.review_round += 1
        review.last_review_time = now; db.add(ExamCardReviewLog(user_id=user_id, card_id=card_id, rating=rating, reviewed_time=now))
        required = cls._review_required(review) if review.state == 'review' else review.required_repetitions
        result = {'state': review.state, 'completed': review.completed_repetitions, 'required': required, 'reviewRound': review.review_round, 'nextReviewTime': review.next_review_time}
        await db.commit()
        return result
