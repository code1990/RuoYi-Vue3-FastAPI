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


if __name__ == '__main__':
    unittest.main()
