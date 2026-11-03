import os
import sqlite3
from pathlib import Path

from module_feizhu.entity.vo.file_detail_vo import FileDetailModel, FileDetailOptionsModel, FileDetailPageModel


RESOURCE_DB_PATH = Path(os.getenv('FEIZHU_RESOURCE_DB_PATH', '/root/data/disk/ruoyi-fastapi/feizhu_resources.db'))


class FileDetailService:
    @staticmethod
    def split_values(value: str | None) -> list[str]:
        return [item.strip() for item in (value or '').split(',') if item.strip()]

    @classmethod
    async def options(cls, _keyword_ids: str | None) -> FileDetailOptionsModel:
        if not RESOURCE_DB_PATH.exists():
            return FileDetailOptionsModel(keywords=[], topics=[], exts=[], categories=[], types=[], valids=[], haspwds=[])
        with sqlite3.connect(RESOURCE_DB_PATH) as connection:
            topics = sorted({topic for (value,) in connection.execute('SELECT DISTINCT topic FROM t_file_detail') for topic in cls.split_values(value)})

            def values(column: str) -> list:
                return [row[0] for row in connection.execute(f"SELECT DISTINCT {column} FROM t_file_detail WHERE {column} IS NOT NULL AND {column} <> '' ORDER BY {column}")]

            return FileDetailOptionsModel(keywords=[], topics=topics, exts=values('ext'), categories=values('category'), types=values('type'), valids=values('valid'), haspwds=values('haspwd'))

    @classmethod
    async def page(
        cls, page_num: int, page_size: int, _keyword_ids: str | None, topics: str | None,
        exts: str | None, category: int | None, resource_type: str | None, valid: str | None,
        haspwd: str | None, keyword: str | None,
    ) -> FileDetailPageModel:
        if not RESOURCE_DB_PATH.exists():
            return FileDetailPageModel(rows=[], total=0, page_num=page_num, page_size=page_size)
        conditions, params = [], []
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
