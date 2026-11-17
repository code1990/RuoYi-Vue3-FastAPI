from collections import defaultdict
from datetime import date, datetime, timedelta
from math import ceil

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from module_exam.entity.do.exam_card_do import ExamCard, ExamCardReview, ExamCardReviewLog, ExamCategory


class ExamReviewService:
    MIN_ATTEMPT_SECONDS = 60
    DAILY_NEW_CARD_LIMIT = 10
    MIN_REPETITIONS = 5
    LEARNING_BATCH_SIZE = 5

    @staticmethod
    def _today_deadline(now: datetime) -> datetime:
        return datetime.combine(now.date() + timedelta(days=1), datetime.min.time())

    @classmethod
    def _attempt_seconds(cls, difficulty: int) -> int:
        return max(cls.MIN_ATTEMPT_SECONDS, max(1, difficulty) * 20)

    @staticmethod
    def _today_task(review_total: int, review_completed: int, learning_total: int, learning_completed: int, learning_remaining_rounds: int, review_remaining_seconds: int, learning_remaining_seconds: int) -> dict:
        remaining_rounds = max(0, review_total - review_completed) + learning_remaining_rounds
        return {
            'reviewTotal': review_total,
            'reviewCompleted': review_completed,
            'learningTotal': learning_total,
            'learningCompleted': learning_completed,
            'remainingRounds': remaining_rounds,
            'estimatedSeconds': review_remaining_seconds + learning_remaining_seconds,
        }

    @staticmethod
    def _learning_task(due: int, pending: int, completed: int, in_progress: int = 0) -> tuple[int, int]:
        return (0, 0) if due else (pending + completed + in_progress, completed + in_progress)

    @classmethod
    def _new_card_limit(cls, started_today: int) -> int:
        return max(0, cls.DAILY_NEW_CARD_LIMIT - started_today)

    @classmethod
    def _required_repetitions(cls, difficulty: int) -> int:
        return max(cls.MIN_REPETITIONS, difficulty + 2)

    @staticmethod
    def _review_required(review: ExamCardReview) -> int:
        return max(ExamReviewService.MIN_REPETITIONS, review.required_repetitions)

    @staticmethod
    def _card(row: ExamCard, review: ExamCardReview | None = None, last_rating: str | None = None) -> dict:
        required = ExamReviewService._review_required(review) if review and review.state == 'review' else review.required_repetitions if review else ExamReviewService._required_repetitions(row.difficulty)
        completed = review.completed_repetitions if review else 0
        return {'cardId': row.card_id, 'categoryId': row.category_id, 'question': row.question, 'aiSummary': row.ai_summary, 'keyPoints': row.key_points, 'tags': row.tags, 'difficulty': row.difficulty, 'isNew': review is None, 'isWeak': last_rating in {'again', 'hard'}, 'progress': {'completed': completed, 'required': required, 'nextRound': min(completed + 1, required), 'phase': review.state if review else 'learning', 'round': review.review_round if review and review.state == 'review' else None, 'batch': review.learning_batch if review else None}}

    @classmethod
    async def _card_for_user(cls, db: AsyncSession, user_id: int, row: ExamCard, review: ExamCardReview | None = None) -> dict:
        last_rating = await db.scalar(
            select(ExamCardReviewLog.rating)
            .where(ExamCardReviewLog.user_id == user_id, ExamCardReviewLog.card_id == row.card_id)
            .order_by(ExamCardReviewLog.reviewed_time.desc(), ExamCardReviewLog.log_id.desc())
            .limit(1)
        )
        return cls._card(row, review, last_rating)

    @classmethod
    async def overview(cls, db: AsyncSession, user_id: int, year: int | None = None) -> dict:
        now = datetime.now(); today = now.date(); year = year or today.year
        today_start = datetime.combine(today, datetime.min.time())
        tomorrow_start = cls._today_deadline(now)
        due_difficulties = (await db.scalars(select(ExamCard.difficulty).join(ExamCardReview, ExamCardReview.card_id == ExamCard.card_id).where(
            ExamCardReview.user_id == user_id,
            or_(
                and_(ExamCardReview.state == 'review', ExamCardReview.next_review_time < tomorrow_start),
                and_(ExamCardReview.state == 'learning', ExamCardReview.completed_repetitions < ExamCardReview.required_repetitions, or_(ExamCardReview.next_review_time.is_(None), ExamCardReview.next_review_time < tomorrow_start)),
            ),
        ))).all()
        due = len(due_difficulties)
        review_completed = await db.scalar(select(func.count()).select_from(ExamCardReview).where(
            ExamCardReview.user_id == user_id, ExamCardReview.state == 'review', ExamCardReview.completed_repetitions == 0,
            ExamCardReview.last_review_time >= today_start, ExamCardReview.last_review_time < tomorrow_start,
            ExamCardReview.next_review_time >= tomorrow_start,
        )) or 0
        review_in_progress = await db.scalar(select(func.count()).select_from(ExamCardReview).where(
            ExamCardReview.user_id == user_id, ExamCardReview.state == 'review',
            ExamCardReview.completed_repetitions > 0,
            ExamCardReview.last_review_time >= today_start, ExamCardReview.last_review_time < tomorrow_start,
            ExamCardReview.next_review_time >= tomorrow_start,
        )) or 0
        learning_rows = (await db.execute(select(ExamCardReview.required_repetitions, ExamCardReview.completed_repetitions, ExamCard.difficulty).join(ExamCard, ExamCard.card_id == ExamCardReview.card_id).where(ExamCardReview.user_id == user_id, ExamCardReview.state == 'learning', or_(ExamCardReview.next_review_time.is_(None), ExamCardReview.next_review_time < tomorrow_start)))).all()
        learning_pending = len(learning_rows)
        learning_remaining_rounds = learning_pending
        learning_remaining_seconds = sum(cls._attempt_seconds(difficulty) for _required, _completed, difficulty in learning_rows)
        learning_completed = await db.scalar(select(func.count()).select_from(ExamCardReview).where(
            ExamCardReview.user_id == user_id,
            ExamCardReview.state == 'review',
            ExamCardReview.review_round == 1,
            ExamCardReview.completed_repetitions == 0,
            ExamCardReview.last_review_time >= today_start, ExamCardReview.last_review_time < tomorrow_start,
            ExamCardReview.next_review_time >= tomorrow_start,
        )) or 0
        learning_in_progress = await db.scalar(select(func.count()).select_from(ExamCardReview).where(
            ExamCardReview.user_id == user_id, ExamCardReview.state == 'learning',
            ExamCardReview.completed_repetitions > 0,
            ExamCardReview.last_review_time >= today_start, ExamCardReview.last_review_time < tomorrow_start,
            ExamCardReview.next_review_time >= tomorrow_start,
        )) or 0
        if due:
            learning_remaining_rounds = 0
            learning_remaining_seconds = 0
        else:
            learning_remaining_rounds += learning_in_progress
        new_count = await db.scalar(select(func.count()).select_from(ExamCard).where(ExamCard.review_enabled.is_(True), ExamCard.status == 'published', ~ExamCard.card_id.in_(select(ExamCardReview.card_id).where(ExamCardReview.user_id == user_id)))) or 0
        start, end = date(year, 1, 1), date(year + 1, 1, 1)
        rows = (await db.execute(select(func.date(ExamCardReviewLog.reviewed_time), func.count()).where(ExamCardReviewLog.user_id == user_id, ExamCardReviewLog.reviewed_time >= start, ExamCardReviewLog.reviewed_time < end).group_by(func.date(ExamCardReviewLog.reviewed_time)))).all()
        planned_rows = (await db.execute(select(func.date(ExamCardReview.next_review_time), func.count()).where(ExamCardReview.user_id == user_id, ExamCardReview.state == 'review', ExamCardReview.next_review_time > now, ExamCardReview.next_review_time >= start, ExamCardReview.next_review_time < end).group_by(func.date(ExamCardReview.next_review_time)))).all()
        heatmap = [{'date': str(day), 'count': count} for day, count in rows]
        planned_reviews = [{'date': str(day), 'count': count} for day, count in planned_rows]
        completed_today = next((item['count'] for item in heatmap if item['date'] == str(today)), 0)
        difficult_today = await db.scalar(select(func.count()).select_from(ExamCardReviewLog).where(
            ExamCardReviewLog.user_id == user_id,
            ExamCardReviewLog.reviewed_time >= today_start,
            ExamCardReviewLog.reviewed_time < tomorrow_start,
            ExamCardReviewLog.rating.in_(('again', 'hard')),
        )) or 0
        tomorrow_due = await db.scalar(select(func.count()).select_from(ExamCardReview).where(
            ExamCardReview.user_id == user_id,
            ExamCardReview.state == 'review',
            ExamCardReview.next_review_time >= tomorrow_start,
            ExamCardReview.next_review_time < tomorrow_start + timedelta(days=1),
        )) or 0
        learning_total, learning_done = cls._learning_task(due, learning_pending, learning_completed, learning_in_progress)
        return {
            'dueCount': due,
            'newAvailable': new_count,
            'completedToday': completed_today,
            'todayTask': cls._today_task(due + review_completed + review_in_progress, review_completed, learning_total, learning_done, learning_remaining_rounds, sum(cls._attempt_seconds(difficulty) for difficulty in due_difficulties), learning_remaining_seconds),
            'dailyFeedback': {'completed': review_completed + learning_completed, 'difficult': difficult_today, 'tomorrowDue': tomorrow_due},
            'heatmap': heatmap,
            'plannedReviews': planned_reviews,
        }

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
        today_deadline = cls._today_deadline(now)
        active_batch = await db.scalar(select(func.min(ExamCardReview.learning_batch)).where(
            ExamCardReview.user_id == user_id,
            ExamCardReview.state == 'learning',
            ExamCardReview.completed_repetitions < ExamCardReview.required_repetitions,
        ))
        if active_batch is not None:
            review = await db.scalar(select(ExamCardReview).join(ExamCard, ExamCard.card_id == ExamCardReview.card_id).where(
                ExamCardReview.user_id == user_id,
                ExamCardReview.state == 'learning',
                ExamCardReview.learning_batch == active_batch,
                ExamCardReview.completed_repetitions < ExamCardReview.required_repetitions,
                or_(ExamCardReview.next_review_time.is_(None), ExamCardReview.next_review_time < today_deadline),
            ).order_by(ExamCardReview.last_review_time.asc(), ExamCardReview.card_id))
            if review:
                return await cls._card_for_user(db, user_id, await db.get(ExamCard, review.card_id), review)
            return None

        batch = (await db.scalar(select(func.max(ExamCardReview.learning_batch)).where(ExamCardReview.user_id == user_id)) or 0) + 1
        due_reviews = (await db.scalars(select(ExamCardReview).join(ExamCard, ExamCard.card_id == ExamCardReview.card_id).where(
            ExamCardReview.user_id == user_id,
            ExamCardReview.state == 'review',
            ExamCardReview.next_review_time < today_deadline,
        ).order_by(ExamCardReview.last_review_time.asc(), ExamCardReview.card_id).limit(cls.LEARNING_BATCH_SIZE))).all()
        if due_reviews:
            for review in due_reviews:
                review.state = 'learning'
                review.completed_repetitions = 0
                review.review_round = 0
                review.interval_days = 1
                review.learning_batch = batch
                review.next_review_time = None
            await db.commit()
            return await cls.next_card(db, user_id)

        started_today = await db.scalar(select(func.count()).select_from(ExamCardReview).where(
            ExamCardReview.user_id == user_id,
            ExamCardReview.create_time >= datetime.combine(now.date(), datetime.min.time()),
        )) or 0
        new_card_limit = cls._new_card_limit(started_today)
        if not new_card_limit:
            return None
        available_cards = (ExamCard.review_enabled.is_(True), ExamCard.status == 'published', ~ExamCard.card_id.in_(select(ExamCardReview.card_id).where(ExamCardReview.user_id == user_id)))
        cards = (await db.scalars(select(ExamCard).join(ExamCategory, ExamCategory.category_id == ExamCard.category_id).where(*available_cards).order_by(ExamCategory.sort_no, ExamCard.sort_no, ExamCard.card_id).limit(min(cls.LEARNING_BATCH_SIZE, new_card_limit)))).all()
        if not cards:
            return None
        for card in cards:
            db.add(ExamCardReview(user_id=user_id, card_id=card.card_id, state='learning', learning_batch=batch, required_repetitions=cls._required_repetitions(card.difficulty), completed_repetitions=0, interval_days=1))
        await db.commit()
        return await cls.next_card(db, user_id)

    @classmethod
    async def rate(cls, db: AsyncSession, user_id: int, card_id: int, rating: str) -> dict:
        card = await db.get(ExamCard, card_id)
        if not card or not card.review_enabled or card.status != 'published':
            raise ValueError('该卡片未启用复习')
        now = datetime.now()
        review = await db.scalar(select(ExamCardReview).where(ExamCardReview.user_id == user_id, ExamCardReview.card_id == card_id))
        if not review:
            review = ExamCardReview(user_id=user_id, card_id=card_id, state='learning', required_repetitions=cls._required_repetitions(card.difficulty), completed_repetitions=0, interval_days=1); db.add(review)
            if rating == 'hard': review.required_repetitions += 1
            if rating == 'again': review.required_repetitions += 2
        if review.state == 'learning':
            if rating == 'again': review.required_repetitions = min(10, review.required_repetitions + 1)
            else: review.completed_repetitions += 1
            if review.completed_repetitions >= review.required_repetitions:
                review.state, review.completed_repetitions, review.review_round, review.interval_days, review.next_review_time = 'review', 0, 1, 1, now + timedelta(days=1)
            else:
                review.next_review_time = now + timedelta(days=1)
        elif rating == 'again':
            review.state, review.completed_repetitions, review.review_round, review.next_review_time = 'learning', 0, 0, now + timedelta(days=1)
        else:
            review.completed_repetitions += 1
            if review.completed_repetitions >= cls._review_required(review):
                factor = {'hard': 1.2, 'good': 2.5, 'easy': 3.5}[rating]
                review.interval_days = min(180, max(1, round((review.interval_days or 1) * factor)))
                review.next_review_time = now + timedelta(days=review.interval_days)
                review.completed_repetitions = 0
                review.review_round += 1
            else:
                review.next_review_time = now + timedelta(days=1)
        review.last_review_time = now; db.add(ExamCardReviewLog(user_id=user_id, card_id=card_id, rating=rating, reviewed_time=now))
        required = cls._review_required(review) if review.state == 'review' else review.required_repetitions
        result = {'state': review.state, 'completed': review.completed_repetitions, 'required': required, 'reviewRound': review.review_round, 'nextReviewTime': review.next_review_time}
        await db.commit()
        return result
