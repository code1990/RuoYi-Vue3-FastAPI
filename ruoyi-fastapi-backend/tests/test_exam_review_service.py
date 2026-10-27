from types import SimpleNamespace

from module_exam.service.exam_review_service import ExamReviewService


def test_review_repetitions_stay_normal_for_four_rounds_then_decrease_to_three():
    review = SimpleNamespace(required_repetitions=5)

    assert [ExamReviewService._review_required(SimpleNamespace(**review.__dict__, review_round=round_)) for round_ in range(1, 9)] == [5, 5, 5, 5, 4, 3, 3, 3]
