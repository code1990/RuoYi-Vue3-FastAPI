from datetime import date, datetime, timedelta
from types import SimpleNamespace

from module_exam.service.exam_review_service import ExamReviewService


def test_review_repetitions_stay_normal_for_four_rounds_then_decrease_to_three():
    review = SimpleNamespace(required_repetitions=5)

    assert [ExamReviewService._review_required(SimpleNamespace(**review.__dict__, review_round=round_)) for round_ in range(1, 9)] == [5, 5, 5, 5, 4, 3, 3, 3]


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
