import asyncio
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import patch

from module_feizhu.entity.do.file_detail_do import FileDetail, FileKeyword, FileKeywordTopic
from module_feizhu.service.file_detail_service import FileDetailService


def test_file_detail_schema_and_filter_values():
    assert FileDetail.__tablename__ == 't_file_detail'
    assert FileDetail.topic.index is True
    assert FileKeyword.keyword.unique is True
    assert FileKeywordTopic.keyword_id.index is True
    assert FileDetailService.split_values(' python,java,, ') == ['python', 'java']


def test_file_detail_reads_sqlite_and_matches_one_topic_in_a_multi_topic_row():
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / 'resources.db'
        with sqlite3.connect(path) as connection:
            connection.executescript('''
                CREATE TABLE t_file_detail (id TEXT, topic TEXT, filename TEXT, size TEXT, ext TEXT, category INTEGER, type TEXT, url TEXT, pwd TEXT, haspwd TEXT, valid TEXT, ctime TEXT, utime TEXT);
                CREATE TABLE t_file_keyword (id TEXT, keyword TEXT, sort_no INTEGER);
                CREATE TABLE t_file_keyword_topic (id TEXT, keyword_id TEXT, topic TEXT, sort_no INTEGER);
                INSERT INTO t_file_detail VALUES ('1', '外汇,期货', '期货入门', '1', 'pdf', 6, 'baidu', 'https://pan.baidu.com/s/1', '', '0', '1', '2026-01-01 00:00:00', '2026-01-02 00:00:00');
                INSERT INTO t_file_detail VALUES ('2', '外汇', '异常', '1', '资源违规提示', 6, 'baidu', 'https://pan.baidu.com/s/2', '', '0', '1', '2026-01-01 00:00:00', '2026-01-02 00:00:00');
                INSERT INTO t_file_keyword VALUES ('forex', '外汇', 0);
                INSERT INTO t_file_keyword_topic VALUES ('forex:0', 'forex', '外汇', 0);
            ''')
        with patch('module_feizhu.service.file_detail_service.RESOURCE_DB_PATH', path):
            options = asyncio.run(FileDetailService.options('forex'))
            page = asyncio.run(FileDetailService.page(1, 20, 'forex', '期货', None, None, None, '1', None, None))
        assert options.keywords[0].name == '外汇'
        assert options.topics == ['外汇']
        assert options.exts == ['pdf']
        assert (page.total, page.rows[0].id, page.rows[0].topic) == (1, '1', '外汇,期货')
