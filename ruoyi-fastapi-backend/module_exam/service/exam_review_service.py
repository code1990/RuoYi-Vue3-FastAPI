from collections import defaultdict
from datetime import date, datetime, timedelta
from math import ceil

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

    @staticmethod
    def _daily_question_counts(start: date, days: int, known_cards: set[int], rows: list[tuple[int, datetime]]) -> list[dict]:
        """Count each card once per day; its first-ever rating is new learning."""
        counts = {str(start + timedelta(days=offset)): {'newCards': set(), 'reviewedCards': set()} for offset in range(days)}
        seen_cards = set(known_cards)
        for card_id, reviewed_time in rows:
            item = counts[str(reviewed_time.date())]
            if card_id in item['newCards'] or card_id in item['reviewedCards']:
                continue
            if card_id in seen_cards:
                item['reviewedCards'].add(card_id)
            else:
                item['newCards'].add(card_id)
                seen_cards.add(card_id)
        return [
            {'date': day, 'newCards': len(item['newCards']), 'reviewedCards': len(item['reviewedCards']), 'studiedCards': len(item['newCards']) + len(item['reviewedCards'])}
            for day, item in counts.items()
        ]

    @classmethod
    async def progress(cls, db: AsyncSession, user_id: int) -> dict:
        """Question-centric learning progress; kept separate from the legacy overview API."""
        today = date.today()
        start, end = today - timedelta(days=29), today + timedelta(days=1)
        active_cards = (ExamCard.review_enabled.is_(True), ExamCard.status == 'published')
        total = await db.scalar(select(func.count()).select_from(ExamCard).where(*active_cards)) or 0
        review_rows = (await db.execute(
            select(ExamCardReview.state, ExamCardReview.review_round, func.count())
            .join(ExamCard, ExamCard.card_id == ExamCardReview.card_id)
            .where(ExamCardReview.user_id == user_id, *active_cards)
            .group_by(ExamCardReview.state, ExamCardReview.review_round)
        )).all()
        levels = {'unlearned': total, 'learning': 0, 'initialReview': 0, 'consolidating': 0, 'mastered': 0}
        for state, review_round, count in review_rows:
            levels['unlearned'] -= count
            if state == 'learning':
                levels['learning'] += count
            elif review_round <= 1:
                levels['initialReview'] += count
            elif review_round <= 3:
                levels['consolidating'] += count
            else:
                levels['mastered'] += count

        log_filters = (ExamCardReviewLog.user_id == user_id, *active_cards)
        known_cards = set((await db.scalars(
            select(ExamCardReviewLog.card_id).join(ExamCard, ExamCard.card_id == ExamCardReviewLog.card_id)
            .where(*log_filters, ExamCardReviewLog.reviewed_time < start).distinct()
        )).all())
        logs = (await db.execute(
            select(ExamCardReviewLog.card_id, ExamCardReviewLog.reviewed_time)
            .join(ExamCard, ExamCard.card_id == ExamCardReviewLog.card_id)
            .where(*log_filters, ExamCardReviewLog.reviewed_time >= start, ExamCardReviewLog.reviewed_time < end)
            .order_by(ExamCardReviewLog.reviewed_time, ExamCardReviewLog.log_id)
        )).all()
        daily = cls._daily_question_counts(start, 30, known_cards, logs)
        new_cards = sum(item['newCards'] for item in daily)
        reviewed_cards = sum(item['reviewedCards'] for item in daily)
        studied_cards = new_cards + reviewed_cards
        average_new = new_cards / 30
        estimated_days = 0 if not levels['unlearned'] else ceil(levels['unlearned'] / average_new) if average_new else None
        calendar_start = today.replace(day=1)
        next_month = (calendar_start.replace(day=28) + timedelta(days=4)).replace(day=1)
        calendar_end = (next_month.replace(day=28) + timedelta(days=4)).replace(day=1)
        calendar_known_cards = set((await db.scalars(
            select(ExamCardReviewLog.card_id).join(ExamCard, ExamCard.card_id == ExamCardReviewLog.card_id)
            .where(*log_filters, ExamCardReviewLog.reviewed_time < calendar_start).distinct()
        )).all())
        calendar_logs = (await db.execute(
            select(ExamCardReviewLog.card_id, ExamCardReviewLog.reviewed_time)
            .join(ExamCard, ExamCard.card_id == ExamCardReviewLog.card_id)
            .where(*log_filters, ExamCardReviewLog.reviewed_time >= calendar_start, ExamCardReviewLog.reviewed_time < min(calendar_end, end))
            .order_by(ExamCardReviewLog.reviewed_time, ExamCardReviewLog.log_id)
        )).all()
        planned = defaultdict(int)
        planned_rows = (await db.scalars(
            select(ExamCardReview.next_review_time).join(ExamCard, ExamCard.card_id == ExamCardReview.card_id)
            .where(ExamCardReview.user_id == user_id, ExamCardReview.state == 'review', ExamCardReview.next_review_time >= today, ExamCardReview.next_review_time < calendar_end, *active_cards)
        )).all()
        for next_review_time in planned_rows:
            planned[str(next_review_time.date())] += 1
        calendar = cls._daily_question_counts(calendar_start, (calendar_end - calendar_start).days, calendar_known_cards, calendar_logs)
        for item in calendar:
            item['plannedCards'] = planned[item['date']]
        return {
            'questionBank': {**levels, 'started': total - levels['unlearned'], 'progressPercent': round((total - levels['unlearned']) * 100 / total) if total else 0},
            'recent30Days': {
                'days': daily, 'newCards': new_cards, 'reviewedCards': reviewed_cards, 'studiedCards': studied_cards,
                'averageDailyStudied': round(studied_cards / 30, 1), 'averageDailyNew': round(average_new, 1), 'estimatedCoverageDays': estimated_days,
            },
            'calendar': calendar,
        }

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
