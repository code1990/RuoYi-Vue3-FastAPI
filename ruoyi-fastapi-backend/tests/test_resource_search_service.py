import asyncio
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import patch

from module_feizhu.service.resource_search_service import ResourceSearchService


def test_topic_search_and_detail_share_detail_items():
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / 'resources.db'
        with sqlite3.connect(path) as connection:
            connection.executescript('''
                CREATE TABLE t_file_detail (id TEXT PRIMARY KEY, topic TEXT, eu TEXT, filename TEXT, size TEXT, isdir INTEGER, ext TEXT, category INTEGER, user TEXT, ctime TEXT, utime TEXT, updatetime TEXT, type TEXT, url TEXT, pwd TEXT, haspwd TEXT, valid TEXT, create_time TEXT, detail_loaded_count INTEGER, detail_complete INTEGER);
                CREATE TABLE t_file_detail_item (resource_id TEXT, path TEXT, filename TEXT, size INTEGER, ext TEXT, isdir INTEGER, sort_no INTEGER);
                INSERT INTO t_file_detail VALUES ('one', '外贸,报关', 'eu', '外贸实务.pdf', '1024', 0, 'pdf', 4, '', '', '', '2026-11-18 00:00:00', 'baidu', 'https://example.test', '1234', '1', '1', '', 1, 0);
                INSERT INTO t_file_detail_item VALUES ('one', '/资料', '外贸实务.pdf', 1024, 'pdf', 0, 0);
            ''')
        with patch('module_feizhu.service.resource_search_service.RESOURCE_DB_PATH', path):
            topics = asyncio.run(ResourceSearchService.topics())
            search = asyncio.run(ResourceSearchService.search('外贸', 1, 15, 'baidu'))
            detail = asyncio.run(ResourceSearchService.detail('one'))
        assert topics == ['外贸', '报关']
        assert search['total'] == 1
        assert search['resources'][0]['res']['filelist'][0]['filename'] == '外贸实务.pdf'
        assert search['resources'][0]['res']['available'] is True
        assert detail['filelist'][0]['path'] == '/资料'


def test_search_pages_duplicate_group_once_and_detail_returns_other_share():
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / 'resources.db'
        with sqlite3.connect(path) as connection:
            connection.executescript('''
                CREATE TABLE t_file_detail (id TEXT PRIMARY KEY, topic TEXT, eu TEXT, filename TEXT, size TEXT, isdir INTEGER, ext TEXT, category INTEGER, user TEXT, ctime TEXT, utime TEXT, updatetime TEXT, type TEXT, url TEXT, pwd TEXT, haspwd TEXT, valid TEXT, create_time TEXT, detail_loaded_count INTEGER, detail_complete INTEGER);
                CREATE TABLE t_file_detail_item (resource_id TEXT, path TEXT, filename TEXT, size INTEGER, ext TEXT, isdir INTEGER, sort_no INTEGER);
                CREATE TABLE t_file_detail_group_relation (resource_id TEXT, topic TEXT, duplicate_group TEXT, topic_fit REAL, relevance_score REAL, file_similarity REAL, match_type TEXT, updated_at TEXT);
                INSERT INTO t_file_detail VALUES ('one', '量化交易', '', '量化交易课程', '1', 0, '', 0, '', '', '', '2026-11-18 00:00:00', 'baidu', 'https://one', '', '0', '1', '', 2, 0);
                INSERT INTO t_file_detail VALUES ('two', '量化交易', '', '量化交易课程', '1', 0, '', 0, '', '', '', '2026-11-17 00:00:00', 'baidu', 'https://two', '', '0', '1', '', 2, 0);
                INSERT INTO t_file_detail_item VALUES ('one', '', '课件.pdf', 1, 'pdf', 0, 0);
                INSERT INTO t_file_detail_item VALUES ('two', '', '课件.pdf', 1, 'pdf', 0, 0);
                INSERT INTO t_file_detail_group_relation VALUES ('one', '量化交易', 'grp_1', 1, .9, 1, 'same_name_similar_files', '2026-11-18');
                INSERT INTO t_file_detail_group_relation VALUES ('two', '量化交易', 'grp_1', 1, .8, 1, 'same_name_similar_files', '2026-11-18');
            ''')
        with patch('module_feizhu.service.resource_search_service.RESOURCE_DB_PATH', path):
            search = asyncio.run(ResourceSearchService.search('量化交易', 1, 15))
            detail = asyncio.run(ResourceSearchService.detail('one'))
        assert (search['total'], search['resources'][0]['res']['id']) == (1, 'one')
        assert detail['similar_shares'][0]['id'] == 'two'
