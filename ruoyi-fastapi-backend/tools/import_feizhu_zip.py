"""Import 飞猪盘 search pages and resource details into one SQLite table."""

from __future__ import annotations

import argparse
import json
import sqlite3
import zipfile
from collections import defaultdict
from pathlib import Path
from typing import Any


DEFAULT_DB_PATH = Path('/root/data/disk/ruoyi-fastapi/feizhu_resources.db')
KEYWORD_TOPICS = {'forex': ('外汇', ('外汇', 'MT4', 'MT5', 'MQL'))}


def archive_name(info: zipfile.ZipInfo) -> str:
    if info.flag_bits & 0x800:
        return info.filename
    try:
        return info.filename.encode('cp437').decode('gbk')
    except UnicodeError:
        return info.filename


def source_rows(archive_path: Path) -> tuple[dict[str, dict[str, Any]], dict[str, list[str]], dict[str, dict[str, Any]]]:
    resources: dict[str, dict[str, Any]] = {}
    topics: dict[str, list[str]] = defaultdict(list)
    details: dict[str, dict[str, Any]] = {}
    with zipfile.ZipFile(archive_path) as archive:
        for info in archive.infolist():
            name = archive_name(info)
            parts = name.split('/')
            if len(parts) != 2 or not name.endswith('.json'):
                continue
            try:
                payload = json.loads(archive.read(info))
            except (UnicodeDecodeError, json.JSONDecodeError):
                continue
            if parts[0] == 'detail':
                if isinstance(payload, dict) and payload.get('id'):
                    details[str(payload['id'])] = payload
                continue
            if not isinstance(payload, dict):
                continue
            for item in payload.get('resources') or []:
                resource = item.get('res') if isinstance(item, dict) else None
                if not isinstance(resource, dict) or not resource.get('id'):
                    continue
                resource_id = str(resource['id'])
                resources.setdefault(resource_id, resource)
                if parts[0] not in topics[resource_id]:
                    topics[resource_id].append(parts[0])
    return resources, topics, details


def text_bool(value: object) -> str | None:
    if value is None:
        return None
    return '1' if value is True or value == 1 else '0' if value is False or value == 0 else str(value)


def rows_for_import(archive_path: Path) -> tuple[list[dict[str, str | None]], dict[str, int]]:
    resources, topics, details = source_rows(archive_path)
    rows = []
    for resource_id, detail in details.items():
        resource = resources.get(resource_id)
        if not resource:
            continue
        file_list = detail.get('filelist', resource.get('filelist'))
        rows.append({
            'id': resource_id,
            'topic': ','.join(topics[resource_id]),
            'eu': str(resource.get('eu') or ''),
            'filename': str(detail.get('filename') or resource.get('filename') or ''),
            'size': str(detail.get('size', resource.get('size', ''))),
            'ctime': detail.get('ctime') or resource.get('ctime'),
            'utime': detail.get('utime') or resource.get('utime'),
            'ext': str(detail.get('ext', resource.get('ext', ''))),
            'category': detail.get('category', resource.get('category')),
            'user': str(resource.get('user') or ''),
            'type': str(resource.get('type') or ''),
            'file_list': json.dumps(file_list, ensure_ascii=False) if file_list is not None else None,
            'url': detail.get('url'),
            'pwd': detail.get('pwd'),
            'haspwd': text_bool(detail.get('haspwd')),
            'valid': text_bool(detail.get('valid')),
            'create_time': detail.get('createtime'),
            'update_time': detail.get('updatetime'),
        })
    return rows, {
        'search_resources': len(resources),
        'detail_resources': len(details),
        'imported_resources': len(rows),
        'search_resources_without_detail': len(set(resources) - set(details)),
    }


def create_table(connection: sqlite3.Connection) -> None:
    connection.execute('''
        CREATE TABLE IF NOT EXISTS t_file_detail (
            id TEXT PRIMARY KEY, topic TEXT NOT NULL, eu TEXT NOT NULL, filename TEXT, size TEXT,
            ctime TEXT, utime TEXT, ext TEXT, category INTEGER, user TEXT, type TEXT,
            file_list TEXT, url TEXT, pwd TEXT, haspwd TEXT, valid TEXT,
            create_time TEXT, update_time TEXT
        )
    ''')
    connection.execute('CREATE TABLE IF NOT EXISTS t_file_keyword (id TEXT PRIMARY KEY, keyword TEXT NOT NULL UNIQUE, sort_no INTEGER NOT NULL DEFAULT 0)')
    connection.execute('CREATE TABLE IF NOT EXISTS t_file_keyword_topic (id TEXT PRIMARY KEY, keyword_id TEXT NOT NULL, topic TEXT NOT NULL, sort_no INTEGER NOT NULL DEFAULT 0, UNIQUE(keyword_id, topic))')
    for keyword_id, (keyword, topics) in KEYWORD_TOPICS.items():
        connection.execute('INSERT OR IGNORE INTO t_file_keyword(id,keyword,sort_no) VALUES (?,?,?)', (keyword_id, keyword, 0))
        connection.execute('DELETE FROM t_file_keyword_topic WHERE keyword_id=?', (keyword_id,))
        connection.executemany('INSERT OR IGNORE INTO t_file_keyword_topic(id,keyword_id,topic,sort_no) VALUES (?,?,?,?)', [(f'{keyword_id}:{index}', keyword_id, topic, index) for index, topic in enumerate(topics)])


def import_archive(archive_path: Path, db_path: Path, dry_run: bool = False) -> dict[str, int]:
    rows, summary = rows_for_import(archive_path)
    if dry_run:
        return summary
    db_path.parent.mkdir(parents=True, exist_ok=True)
    columns = tuple(rows[0]) if rows else ()
    with sqlite3.connect(db_path) as connection:
        create_table(connection)
        if rows:
            names = ','.join(columns)
            values = ','.join(f':{column}' for column in columns)
            updates = ','.join(f'{column}=excluded.{column}' for column in columns if column != 'id')
            connection.executemany(
                f'INSERT INTO t_file_detail ({names}) VALUES ({values}) ON CONFLICT(id) DO UPDATE SET {updates}', rows
            )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description='Import 飞猪盘 ZIP resources into SQLite.')
    parser.add_argument('archive', type=Path)
    parser.add_argument('--db-path', type=Path, default=DEFAULT_DB_PATH)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    summary = import_archive(args.archive, args.db_path, args.dry_run)
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))


if __name__ == '__main__':
    main()
