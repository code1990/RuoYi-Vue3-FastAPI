from module_feizhu.entity.do.file_detail_do import FileDetail, FileKeyword, FileKeywordTopic
from module_feizhu.service.file_detail_service import FileDetailService


def test_file_detail_schema_and_filter_values():
    assert FileDetail.__tablename__ == 't_file_detail'
    assert FileDetail.topic.index is True
    assert FileKeyword.keyword.unique is True
    assert FileKeywordTopic.keyword_id.index is True
    assert FileDetailService.split_values(' python,java,, ') == ['python', 'java']
