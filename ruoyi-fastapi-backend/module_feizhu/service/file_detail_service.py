import os
import sqlite3
from pathlib import Path

from module_feizhu.entity.vo.file_detail_vo import FileDetailModel, FileDetailOptionsModel, FileDetailPageModel, FileKeywordTopicsModel


RESOURCE_DB_PATH = Path(os.getenv('FEIZHU_RESOURCE_DB_PATH', '/root/data/disk/ruoyi-fastapi/feizhu_resources.db'))


class FileDetailService:
    @staticmethod
    def split_values(value: str | None) -> list[str]:
        return [item.strip() for item in (value or '').split(',') if item.strip()]

    @classmethod
    async def keyword_topics(cls) -> list[FileKeywordTopicsModel]:
        if not RESOURCE_DB_PATH.exists():
            return []
        with sqlite3.connect(RESOURCE_DB_PATH) as connection:
            rows = connection.execute('''
                SELECT k.id,k.keyword,t.topic FROM t_file_keyword k
                LEFT JOIN t_file_keyword_topic t ON t.keyword_id=k.id
                ORDER BY k.sort_no,k.keyword,t.sort_no,t.topic
            ''').fetchall()
        keywords: dict[str, FileKeywordTopicsModel] = {}
        for keyword_id, keyword, topic in rows:
            item = keywords.setdefault(keyword_id, FileKeywordTopicsModel(id=keyword_id, name=keyword, topics=[]))
            if topic:
                item.topics.append(topic)
        return list(keywords.values())

    @classmethod
    async def remove_keyword_topic(cls, keyword_id: str, topic: str) -> bool:
        if not RESOURCE_DB_PATH.exists():
            return False
        with sqlite3.connect(RESOURCE_DB_PATH) as connection:
            cursor = connection.execute('DELETE FROM t_file_keyword_topic WHERE keyword_id=? AND topic=?', (keyword_id, topic))
        return cursor.rowcount > 0

    @classmethod
    async def options(cls, keyword_ids: str | None) -> FileDetailOptionsModel:
        if not RESOURCE_DB_PATH.exists():
            return FileDetailOptionsModel(keywords=[], topics=[], exts=[], categories=[], types=[], valids=[], haspwds=[])
        with sqlite3.connect(RESOURCE_DB_PATH) as connection:
            keywords = [{'id': row[0], 'name': row[1]} for row in connection.execute('SELECT id,keyword FROM t_file_keyword ORDER BY sort_no,keyword')]
            selected = cls.split_values(keyword_ids)
            allowed = [row[0] for row in connection.execute('SELECT topic FROM t_file_keyword_topic WHERE keyword_id IN (' + ','.join('?' for _ in selected) + ')', selected)] if selected else None
            topics = sorted({topic for (value,) in connection.execute('SELECT DISTINCT topic FROM t_file_detail') for topic in cls.split_values(value) if allowed is None or any(term.lower() in topic.lower() for term in allowed)})

            def values(column: str) -> list:
                result = [row[0] for row in connection.execute(f"SELECT DISTINCT {column} FROM t_file_detail WHERE {column} IS NOT NULL AND {column} <> '' ORDER BY {column}")]
                return [value for value in result if column != 'ext' or not any('\u4e00' <= char <= '\u9fff' for char in str(value))]

            return FileDetailOptionsModel(keywords=keywords, topics=topics, exts=values('ext'), categories=values('category'), types=values('type'), valids=values('valid'), haspwds=values('haspwd'))

    @classmethod
    async def page(
        cls, page_num: int, page_size: int, keyword_ids: str | None, topics: str | None,
        exts: str | None, category: int | None, resource_type: str | None, valid: str | None,
        haspwd: str | None, keyword: str | None,
    ) -> FileDetailPageModel:
        if not RESOURCE_DB_PATH.exists():
            return FileDetailPageModel(rows=[], total=0, page_num=page_num, page_size=page_size)
        conditions, params = [], []
        keyword_values = cls.split_values(keyword_ids)
        if keyword_values:
            with sqlite3.connect(RESOURCE_DB_PATH) as connection:
                expanded = [row[0] for row in connection.execute('SELECT topic FROM t_file_keyword_topic WHERE keyword_id IN (' + ','.join('?' for _ in keyword_values) + ')', keyword_values)]
            if not expanded:
                return FileDetailPageModel(rows=[], total=0, page_num=page_num, page_size=page_size)
            conditions.append('(' + ' OR '.join('topic LIKE ?' for _ in expanded) + ')')
            params.extend(f'%{topic}%' for topic in expanded)
        values = cls.split_values(topics)
        if values:
            conditions.append('(' + ' OR '.join("instr(',' || topic || ',', ',' || ? || ',') > 0" for _ in values) + ')')
            params.extend(values)
        values = cls.split_values(exts)
        if values:
            conditions.append('ext IN (' + ','.join('?' for _ in values) + ')')
            params.extend(values)
        if category is not None:
            conditions.append('category = ?')
            params.append(category)
        if resource_type:
            conditions.append('type = ?')
            params.append(resource_type)
        if valid:
            conditions.append('valid = ?')
            params.append(valid)
        if haspwd:
            conditions.append('haspwd = ?')
            params.append(haspwd)
        if keyword:
            conditions.append('(filename LIKE ? OR topic LIKE ? OR url LIKE ?)')
            params.extend([f'%{keyword}%'] * 3)
        where = ' WHERE ' + ' AND '.join(conditions) if conditions else ''
        with sqlite3.connect(RESOURCE_DB_PATH) as connection:
            connection.row_factory = sqlite3.Row
            total = connection.execute('SELECT COUNT(*) FROM t_file_detail' + where, params).fetchone()[0]
            rows = connection.execute(
                'SELECT id,topic,filename,size,ext,category,type,url,pwd,haspwd,valid,ctime,utime FROM t_file_detail'
                + where + ' ORDER BY utime DESC, id DESC LIMIT ? OFFSET ?', [*params, page_size, (page_num - 1) * page_size]
            ).fetchall()
        return FileDetailPageModel(
            rows=[FileDetailModel.model_validate(dict(row)) for row in rows],
            total=total,
            page_num=page_num,
            page_size=page_size,
        )
