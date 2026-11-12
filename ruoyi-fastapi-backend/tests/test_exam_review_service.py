from datetime import date, datetime, timedelta

import pytest
import pytest_asyncio
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from exceptions.exception import ServiceException
from module_exam.entity.do.exam_card_do import ExamCard, ExamCardAiSummaryVersion, ExamCardReview, ExamCardReviewLog, ExamCategory
from module_exam.service.exam_card_service import ExamCardService
from module_exam.service import exam_review_service
from module_exam.service.exam_review_service import ExamReviewService


@pytest_asyncio.fixture
async def exam_db_session():
    engine = create_async_engine('sqlite+aiosqlite:///:memory:')
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with engine.begin() as conn:
        await conn.run_sync(ExamCard.metadata.create_all)
    async with session_factory() as session:
        yield session
    await engine.dispose()


def test_today_deadline_includes_all_reviews_due_before_midnight():
    assert ExamReviewService._today_deadline(datetime(2026, 11, 4, 7, 30)) == datetime(2026, 11, 5)


def test_daily_question_counts_new_and_reviewed_cards_without_duplicate_ratings():
    start = date(2026, 10, 1)
    rows = [
        (2, datetime(2026, 10, 1, 9)), (2, datetime(2026, 10, 1, 10)),
        (1, datetime(2026, 10, 1, 11)), (2, datetime(2026, 10, 2, 9)),
    ]

    days = ExamReviewService._daily_question_counts(start, 2, {1}, rows)

    assert days == [
        {'date': '2026-10-01', 'newCards': 1, 'reviewedCards': 1, 'studiedCards': 2},
        {'date': '2026-10-02', 'newCards': 0, 'reviewedCards': 1, 'studiedCards': 1},
    ]


def test_today_task_counts_remaining_learning_attempts_and_difficulty_time():
    assert ExamReviewService._today_task(6, 2, 5, 1, 11, 240, 840) == {
        'reviewTotal': 6,
        'reviewCompleted': 2,
        'learningTotal': 5,
        'learningCompleted': 1,
        'remainingRounds': 15,
        'estimatedSeconds': 1080,
    }


def test_attempt_seconds_has_a_one_minute_minimum_and_scales_with_difficulty():
    assert ExamReviewService._attempt_seconds(1) == 60
    assert ExamReviewService._attempt_seconds(3) == 60
    assert ExamReviewService._attempt_seconds(6) == 120


def test_due_reviews_pause_new_learning_task():
    assert ExamReviewService._learning_task(54, 5, 0) == (0, 0)
    assert ExamReviewService._learning_task(0, 5, 1) == (6, 1)


def test_new_cards_are_limited_to_ten_per_day():
    assert ExamReviewService._new_card_limit(0) == 10
    assert ExamReviewService._new_card_limit(6) == 4
    assert ExamReviewService._new_card_limit(10) == 0


@pytest.mark.asyncio
async def test_new_card_is_a_pretest_and_prefers_a_different_category(exam_db_session):
    exam_db_session.add_all([
        ExamCategory(category_id=1, name='first'),
        ExamCategory(category_id=2, name='second'),
        ExamCard(card_id=10, category_id=1, question='old', answer='a', review_enabled=True),
        ExamCard(card_id=11, category_id=2, question='new', answer='a', review_enabled=True),
        ExamCardReviewLog(log_id=10, user_id=1, card_id=10, rating='good', reviewed_time=datetime.now()),
    ])
    await exam_db_session.commit()

    card = await ExamReviewService.next_card(exam_db_session, 1)

    assert card['cardId'] == 11
    assert card['isNew'] is True
    assert await exam_db_session.scalar(select(func.count()).select_from(ExamCardReview)) == 0


@pytest.mark.asyncio
async def test_due_review_is_scheduled_after_one_retrieval(exam_db_session, monkeypatch):
    card = ExamCard(card_id=1, category_id=1, question='q', answer='a', difficulty=3, review_enabled=True)
    review = ExamCardReview(review_id=1, user_id=1, card_id=1, state='review', required_repetitions=5, review_round=1, interval_days=1, next_review_time=datetime.now() - timedelta(days=1))
    exam_db_session.add_all([card, review])
    await exam_db_session.commit()
    monkeypatch.setattr(exam_review_service, 'ExamCardReviewLog', lambda **kwargs: ExamCardReviewLog(log_id=1, **kwargs))

    first = await ExamReviewService.rate(exam_db_session, 1, 1, 'good')

    assert first['state'] == 'review'
    assert first['completed'] == 0
    assert first['reviewRound'] == 2
    assert first['nextReviewTime'] > datetime.now() + timedelta(days=1)


@pytest.mark.asyncio
async def test_learning_card_is_not_returned_again_until_tomorrow(exam_db_session, monkeypatch):
    card = ExamCard(card_id=4, category_id=1, question='q', answer='a', review_enabled=True)
    review = ExamCardReview(review_id=4, user_id=1, card_id=4, state='learning', required_repetitions=5, completed_repetitions=0)
    exam_db_session.add_all([card, review])
    await exam_db_session.commit()
    monkeypatch.setattr(exam_review_service, 'ExamCardReviewLog', lambda **kwargs: ExamCardReviewLog(log_id=4, **kwargs))
    result = await ExamReviewService.rate(exam_db_session, 1, 4, 'good')
    monkeypatch.setattr(exam_review_service, 'ExamCardReviewLog', ExamCardReviewLog)

    assert result['state'] == 'learning'
    assert result['nextReviewTime'] > datetime.now() + timedelta(hours=23)
    assert await ExamReviewService.next_card(exam_db_session, 1) is None


@pytest.mark.asyncio
async def test_again_returns_a_review_card_to_learning_tomorrow(exam_db_session, monkeypatch):
    card = ExamCard(card_id=5, category_id=1, question='q', answer='a', review_enabled=True)
    review = ExamCardReview(review_id=5, user_id=1, card_id=5, state='review', required_repetitions=5, review_round=2, next_review_time=datetime.now() - timedelta(days=1))
    exam_db_session.add_all([card, review])
    await exam_db_session.commit()
    monkeypatch.setattr(exam_review_service, 'ExamCardReviewLog', lambda **kwargs: ExamCardReviewLog(log_id=5, **kwargs))
    result = await ExamReviewService.rate(exam_db_session, 1, 5, 'again')
    monkeypatch.setattr(exam_review_service, 'ExamCardReviewLog', ExamCardReviewLog)

    assert result['state'] == 'learning'
    assert result['nextReviewTime'] > datetime.now() + timedelta(hours=23)
    assert await ExamReviewService.next_card(exam_db_session, 1) is None


@pytest.mark.asyncio
async def test_new_ai_summary_version_is_immediately_activated(exam_db_session):
    card = ExamCard(
        card_id=2,
        category_id=1,
        question='q',
        answer='reference',
        ai_summary='v1',
        active_ai_summary_version_id=1,
    )
    original = ExamCardAiSummaryVersion(
        summary_version_id=1,
        card_id=2,
        version_no=1,
        title='原始总结',
        ai_summary='v1',
    )
    exam_db_session.add_all([card, original])
    await exam_db_session.commit()

    version = await ExamCardService.add_ai_summary_version(exam_db_session, 2, '原理推导版', 'v2')

    assert version['version_no'] == 2
    assert version['active_summary_version_id'] == version['summary_version_id']
    updated_card = await exam_db_session.get(ExamCard, 2)

    assert updated_card.active_ai_summary_version_id == version['summary_version_id']
    assert updated_card.ai_summary == 'v2'
    assert await exam_db_session.scalar(select(func.count()).select_from(ExamCardAiSummaryVersion)) == 2


@pytest.mark.asyncio
async def test_ai_summary_version_rejects_whitespace_content(exam_db_session):
    exam_db_session.add(ExamCard(card_id=3, category_id=1, question='q', answer='a'))
    await exam_db_session.commit()

    with pytest.raises(ServiceException):
        await ExamCardService.add_ai_summary_version(exam_db_session, 3, ' ', ' ')
