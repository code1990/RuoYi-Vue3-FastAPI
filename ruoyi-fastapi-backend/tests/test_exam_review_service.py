from datetime import date, datetime

from module_exam.service.exam_review_service import ExamReviewService


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
