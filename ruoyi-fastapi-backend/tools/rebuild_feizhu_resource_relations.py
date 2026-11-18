"""Calculate topic relevance and duplicate groups for local 飞舟盘 resources."""

from __future__ import annotations

import argparse
import hashlib
import re
import sqlite3
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from migrate_feizhu_resource_db import DEFAULT_DB, migrate


def normalize(value: str | None) -> str:
    value = (value or '').lower()
    value = re.sub(r'\.(zip|rar|7z|pdf|docx?|xlsx?|pptx?|mp4|mkv|avi|mp3|flac)$', '', value)
    return re.sub(r'[\s\W_]+', '', value, flags=re.UNICODE)


def topics(value: str | None) -> list[str]:
    return list(dict.fromkeys(item.strip() for item in (value or '').split(',') if item.strip()))


def similarity(left: set[str], right: set[str]) -> float:
    return len(left & right) / len(left | right) if left and right else 0.0


def rebuild(db_path: Path) -> dict[str, int]:
    migrate(db_path, apply=True, backup_before_apply=False)
    with sqlite3.connect(db_path) as connection:
        connection.row_factory = sqlite3.Row
        resources = connection.execute('SELECT id,topic,filename,valid FROM t_file_detail').fetchall()
        files_by_resource: dict[str, set[str]] = defaultdict(set)
        for row in connection.execute('SELECT resource_id,filename FROM t_file_detail_item'):
            name = normalize(row['filename'])
            if name:
                files_by_resource[row['resource_id']].add(name)

        entries, by_name = [], defaultdict(list)
        for row in resources:
            name = normalize(row['filename'])
            item = {'id': row['id'], 'topics': topics(row['topic']), 'name': name, 'files': files_by_resource[row['id']], 'valid': str(row['valid']) in ('1', 'true', 'True')}
            entries.append(item)
            if name and item['files']:
                by_name[name].append(item)

        parent = {item['id']: item['id'] for item in entries}

        def find(value: str) -> str:
            while parent[value] != value:
                parent[value] = parent[parent[value]]
                value = parent[value]
            return value

        def union(left: str, right: str) -> None:
            left, right = find(left), find(right)
            if left != right:
                parent[right] = left

        pair_similarity: dict[tuple[str, str], float] = {}
        for candidates in by_name.values():
            for index, left in enumerate(candidates):
                for right in candidates[index + 1:]:
                    score = similarity(left['files'], right['files'])
                    if score >= 0.75:
                        union(left['id'], right['id'])
                        pair_similarity[tuple(sorted((left['id'], right['id'])))] = score

        groups: dict[str, list[str]] = defaultdict(list)
        for item in entries:
            groups[find(item['id'])].append(item['id'])
        group_id = {root: f"grp_{hashlib.sha1('|'.join(sorted(members)).encode()).hexdigest()[:16]}" for root, members in groups.items() if len(members) > 1}

        now, rows = datetime.now().isoformat(timespec='seconds'), []
        for item in entries:
            related = groups[find(item['id'])]
            best_similarity = max((score for pair, score in pair_similarity.items() if item['id'] in pair), default=0.0)
            for topic in item['topics']:
                topic_name = normalize(topic)
                title_match = bool(topic_name and topic_name in item['name'])
                file_matches = sum(topic_name in filename for filename in item['files']) if topic_name else 0
                topic_fit = 1.0 if title_match else min(file_matches / max(len(item['files']), 1), 1.0)
                completeness = min(len(item['files']) / 10, 1.0)
                relevance = round(0.7 * topic_fit + 0.2 * completeness + 0.1 * item['valid'], 3)
                rows.append((item['id'], topic, group_id.get(find(item['id'])), topic_fit, relevance, best_similarity, 'same_name_similar_files' if len(related) > 1 else None, now))
        connection.execute('DELETE FROM t_file_detail_group_relation')
        connection.executemany('''INSERT INTO t_file_detail_group_relation
            (resource_id,topic,duplicate_group,topic_fit,relevance_score,file_similarity,match_type,updated_at)
            VALUES (?,?,?,?,?,?,?,?)''', rows)
    return {'resources': len(entries), 'relations': len(rows), 'duplicate_groups': len(group_id)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--db-path', type=Path, default=DEFAULT_DB)
    args = parser.parse_args()
    print(rebuild(args.db_path))
