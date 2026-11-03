import json
import sqlite3
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / 'tools'))
from import_feizhu_zip import import_archive


class ImportFeizhuZipTest(unittest.TestCase):
    def test_merges_page_topics_into_one_detail_row(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive_path, db_path = root / 'resources.zip', root / 'resources.db'
            resource = {'id': 'resource-1', 'eu': 'eu-1', 'type': 'baidu', 'user': 'user-1', 'filelist': [{'filename': 'a.pdf'}]}
            detail = {'id': 'resource-1', 'filename': '资源', 'size': 10, 'ext': 'pdf', 'url': 'https://pan.baidu.com/s/x', 'pwd': '1234', 'haspwd': True, 'valid': 1}
            with zipfile.ZipFile(archive_path, 'w') as archive:
                archive.writestr('外汇/1.json', json.dumps({'resources': [{'res': resource}]}))
                archive.writestr('期货/1.json', json.dumps({'resources': [{'res': resource}]}))
                archive.writestr('detail/resource-1.json', json.dumps(detail))

            self.assertEqual(1, import_archive(archive_path, db_path)['imported_resources'])
            self.assertEqual(1, import_archive(archive_path, db_path)['imported_resources'])
            with sqlite3.connect(db_path) as connection:
                row = connection.execute('SELECT topic,eu,url,pwd,haspwd,valid,file_list FROM t_file_detail').fetchone()
            self.assertEqual(('外汇,期货', 'eu-1', 'https://pan.baidu.com/s/x', '1234', '1', '1', '[{"filename": "a.pdf"}]'), row)

    def test_excludes_empire_topics_without_losing_other_topic_hits(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive_path, db_path = root / 'resources.zip', root / 'resources.db'
            def resource(resource_id): return {'id': resource_id, 'eu': resource_id, 'type': 'baidu'}
            def detail(resource_id): return {'id': resource_id, 'filename': resource_id, 'url': 'https://pan.baidu.com', 'valid': 1}
            with zipfile.ZipFile(archive_path, 'w') as archive:
                archive.writestr('帝国时代/1.json', json.dumps({'resources': [{'res': resource('only-empire')}, {'res': resource('shared')}]}))
                archive.writestr('外汇/1.json', json.dumps({'resources': [{'res': resource('shared')}]}))
                archive.writestr('detail/only-empire.json', json.dumps(detail('only-empire')))
                archive.writestr('detail/shared.json', json.dumps(detail('shared')))

            import_archive(archive_path, db_path)
            with sqlite3.connect(db_path) as connection:
                self.assertEqual([('shared', '外汇')], connection.execute('SELECT id,topic FROM t_file_detail').fetchall())

    def test_does_not_restore_a_removed_default_topic_on_reimport(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive_path, db_path = root / 'resources.zip', root / 'resources.db'
            with zipfile.ZipFile(archive_path, 'w') as archive:
                archive.writestr('外汇/1.json', json.dumps({'resources': [{'res': {'id': 'resource', 'eu': 'resource'}}]}))
                archive.writestr('detail/resource.json', json.dumps({'id': 'resource'}))

            import_archive(archive_path, db_path)
            with sqlite3.connect(db_path) as connection:
                connection.execute("DELETE FROM t_file_keyword_topic WHERE keyword_id='forex' AND topic='MQL'")
            import_archive(archive_path, db_path)
            with sqlite3.connect(db_path) as connection:
                self.assertIsNone(connection.execute("SELECT 1 FROM t_file_keyword_topic WHERE keyword_id='forex' AND topic='MQL'").fetchone())


if __name__ == '__main__':
    unittest.main()
