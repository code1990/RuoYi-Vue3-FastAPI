from module_exam.entity.do.exam_card_do import ExamCard, ExamCardAiSummaryVersion, ExamCategory


def test_exam_card_schema_has_independent_category_and_card_tables():
    assert ExamCategory.__tablename__ == 'exam_category'
    assert ExamCard.__tablename__ == 'exam_card'
    assert ExamCard.category_id.index is True
    assert ExamCard.ai_summary.type.python_type is str
    assert ExamCard.active_ai_summary_version_id.nullable is True
    assert ExamCardAiSummaryVersion.__tablename__ == 'exam_card_ai_summary_version'
    assert ExamCardAiSummaryVersion.card_id.index is True
    assert ExamCardAiSummaryVersion.__table_args__[0].name == 'uk_exam_card_ai_summary_version_card_version'
