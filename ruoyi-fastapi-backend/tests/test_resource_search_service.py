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
        assert detail['filelist'][0]['path'] == '/资料'
