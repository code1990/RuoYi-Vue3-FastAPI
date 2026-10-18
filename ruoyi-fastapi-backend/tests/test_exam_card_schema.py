from module_exam.entity.do.exam_card_do import ExamCard, ExamCategory


def test_exam_card_schema_has_independent_category_and_card_tables():
    assert ExamCategory.__tablename__ == 'exam_category'
    assert ExamCard.__tablename__ == 'exam_card'
    assert ExamCard.category_id.index is True
    assert ExamCard.ai_summary.type.python_type is str
