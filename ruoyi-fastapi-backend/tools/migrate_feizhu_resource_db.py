"""Migrate the existing 飞舟盘 SQLite resource database to detail-item storage."""

from __future__ import annotations

import argparse
import json
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path


DEFAULT_DB = Path('/root/data/disk/ruoyi-fastapi/feizhu_resources.db')
DETAIL_COLUMNS = {
    'isdir': 'INTEGER',
    'updatetime': 'TEXT',
    'detail_synced_at': 'TEXT',
    'detail_loaded_count': 'INTEGER NOT NULL DEFAULT 0',
    'detail_complete': 'INTEGER NOT NULL DEFAULT 0',
}


def migrate(db_path: Path, apply: bool = False, backup_before_apply: bool = True) -> dict[str, int | str]:
    if not db_path.exists():
        raise FileNotFoundError(db_path)
    backup = ''
    if apply and backup_before_apply:
        backup_path = db_path.with_name(f'{db_path.name}.before-detail-items-{datetime.now():%Y%m%d%H%M%S}.bak')
        shutil.copy2(db_path, backup_path)
        backup = str(backup_path)
    with sqlite3.connect(db_path) as connection:
        if connection.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
            raise RuntimeError('SQLite integrity_check failed')
        columns = {row[1] for row in connection.execute('PRAGMA table_info(t_file_detail)')}
        missing = [name for name in DETAIL_COLUMNS if name not in columns]
        if apply:
            for name in missing:
                connection.execute(f'ALTER TABLE t_file_detail ADD COLUMN {name} {DETAIL_COLUMNS[name]}')
            connection.executescript('''
                CREATE TABLE IF NOT EXISTS t_file_detail_item (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    resource_id TEXT NOT NULL,
                    path TEXT,
                    filename TEXT NOT NULL,
                    size INTEGER,
                    ext TEXT,
                    isdir INTEGER NOT NULL DEFAULT 0,
                    sort_no INTEGER NOT NULL,
                    UNIQUE(resource_id, sort_no)
                );
                CREATE INDEX IF NOT EXISTS idx_file_detail_item_resource_sort
                    ON t_file_detail_item(resource_id, sort_no);
                CREATE INDEX IF NOT EXISTS idx_file_detail_type_updatetime
                    ON t_file_detail(type, updatetime DESC, id DESC);
            ''')
            connection.execute('UPDATE t_file_detail SET isdir=CASE WHEN category=6 THEN 1 ELSE 0 END WHERE isdir IS NULL')
            connection.execute('UPDATE t_file_detail SET updatetime=COALESCE(updatetime,update_time,utime) WHERE updatetime IS NULL')
            migrated = 0
            for resource_id, file_list in connection.execute('SELECT id,file_list FROM t_file_detail WHERE file_list IS NOT NULL AND file_list <> ""'):
                if connection.execute('SELECT 1 FROM t_file_detail_item WHERE resource_id=? LIMIT 1', (resource_id,)).fetchone():
                    continue
                try:
                    items = json.loads(file_list)
                except json.JSONDecodeError:
                    continue
                if not isinstance(items, list):
                    continue
                rows = []
                for sort_no, item in enumerate(items):
                    if not isinstance(item, dict) or not item.get('filename'):
                        continue
                    size = item.get('size')
                    rows.append((resource_id, item.get('path'), str(item['filename']), int(size) if str(size).isdigit() else None, item.get('ext'), 1 if item.get('isdir') in (1, True) else 0, sort_no))
                if rows:
                    connection.executemany('INSERT INTO t_file_detail_item(resource_id,path,filename,size,ext,isdir,sort_no) VALUES (?,?,?,?,?,?,?)', rows)
                    connection.execute('UPDATE t_file_detail SET detail_loaded_count=?, detail_complete=0 WHERE id=?', (len(rows), resource_id))
                    migrated += 1
            connection.execute("UPDATE t_file_detail SET detail_synced_at=COALESCE(detail_synced_at,update_time) WHERE detail_loaded_count > 0")
        resource_count = connection.execute('SELECT COUNT(*) FROM t_file_detail').fetchone()[0]
        item_count = connection.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='t_file_detail_item'").fetchone()[0]
    return {'resources': resource_count, 'missing_columns': len(missing), 'detail_item_table': item_count, 'backup': backup}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--db-path', type=Path, default=DEFAULT_DB)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    print(json.dumps(migrate(args.db_path, args.apply), ensure_ascii=False))
