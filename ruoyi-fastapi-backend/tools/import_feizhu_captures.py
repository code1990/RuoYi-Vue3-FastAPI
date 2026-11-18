"""Import mitmproxy captures saved by feizhupan/dump_response.py into SQLite."""

from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import datetime
from pathlib import Path

from migrate_feizhu_resource_db import DEFAULT_DB, migrate
from rebuild_feizhu_resource_relations import rebuild


def text_bool(value):
    return '1' if value is True or value == 1 else '0' if value is False or value == 0 else value


def load_json(path: Path):
    try:
        with path.open(encoding='utf-8') as source:
            return json.load(source)
    except (OSError, json.JSONDecodeError):
        return None


def merge_topic(current: str, topic: str) -> str:
    return ','.join(dict.fromkeys([item.strip() for item in f'{current},{topic}'.split(',') if item.strip()]))


def replace_items(connection: sqlite3.Connection, resource_id: str, files: list[dict]) -> None:
    connection.execute('DELETE FROM t_file_detail_item WHERE resource_id=?', (resource_id,))
    rows = [(resource_id, item.get('path'), str(item['filename']), int(item['size']) if str(item.get('size', '')).isdigit() else None, item.get('ext'), 1 if item.get('isdir') in (1, True) else 0, index) for index, item in enumerate(files) if isinstance(item, dict) and item.get('filename')]
    connection.executemany('INSERT INTO t_file_detail_item(resource_id,path,filename,size,ext,isdir,sort_no) VALUES (?,?,?,?,?,?,?)', rows)
    connection.execute('UPDATE t_file_detail SET detail_synced_at=?,detail_loaded_count=?,detail_complete=0 WHERE id=?', (datetime.now().isoformat(timespec='seconds'), len(rows), resource_id))


def import_captures(capture_dir: Path, db_path: Path) -> dict[str, int]:
    migrate(db_path, apply=True, backup_before_apply=False)
    search_files = list((capture_dir / 'search').glob('*/*.json'))
    detail_files = list((capture_dir / 'detail').glob('*.json'))
    imported_search = imported_detail = 0
    with sqlite3.connect(db_path) as connection:
        for path in search_files:
            payload, topic = load_json(path), path.parent.name
            for item in (payload or {}).get('resources') or []:
                resource = item.get('res') if isinstance(item, dict) else None
                if not isinstance(resource, dict) or not resource.get('id'):
                    continue
                resource_id = str(resource['id'])
                existing = connection.execute('SELECT topic FROM t_file_detail WHERE id=?', (resource_id,)).fetchone()
                values = (resource_id, merge_topic(existing[0] if existing else '', topic), str(resource.get('eu') or ''), resource.get('filename'), str(resource.get('size') or ''), 1 if resource.get('isdir') in (1, True) else 0, resource.get('ext'), resource.get('category'), resource.get('user'), resource.get('type'), resource.get('ctime'), resource.get('utime'), resource.get('updatetime'))
                connection.execute('''INSERT INTO t_file_detail(id,topic,eu,filename,size,isdir,ext,category,user,type,ctime,utime,updatetime)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET topic=excluded.topic,eu=excluded.eu,filename=excluded.filename,size=excluded.size,isdir=excluded.isdir,ext=excluded.ext,category=excluded.category,user=excluded.user,type=excluded.type,ctime=excluded.ctime,utime=excluded.utime,updatetime=excluded.updatetime''', values)
                imported_search += 1
        for path in detail_files:
            detail = load_json(path)
            if not isinstance(detail, dict) or not detail.get('id'):
                continue
            resource_id = str(detail['id'])
            cursor = connection.execute('''UPDATE t_file_detail SET filename=COALESCE(?,filename),size=COALESCE(?,size),isdir=COALESCE(?,isdir),ext=COALESCE(?,ext),category=COALESCE(?,category),url=?,pwd=?,haspwd=?,valid=?,ctime=COALESCE(?,ctime),utime=COALESCE(?,utime),updatetime=COALESCE(?,updatetime) WHERE id=?''', (detail.get('filename'), str(detail['size']) if detail.get('size') is not None else None, 1 if detail.get('isdir') in (1, True) else 0 if detail.get('isdir') is not None else None, detail.get('ext'), detail.get('category'), detail.get('url'), detail.get('pwd'), text_bool(detail.get('haspwd')), text_bool(detail.get('valid')), detail.get('ctime'), detail.get('utime'), detail.get('updatetime'), resource_id))
            if cursor.rowcount:
                replace_items(connection, resource_id, detail.get('filelist') or [])
                imported_detail += 1
    relation_result = rebuild(db_path)
    return {'search_rows': imported_search, 'detail_rows': imported_detail, 'relations': relation_result['relations']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--captures', type=Path, required=True)
    parser.add_argument('--db-path', type=Path, default=DEFAULT_DB)
    args = parser.parse_args()
    print(json.dumps(import_captures(args.captures, args.db_path), ensure_ascii=False))
