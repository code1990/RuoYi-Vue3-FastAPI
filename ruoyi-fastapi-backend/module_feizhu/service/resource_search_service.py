import html
import os
import sqlite3
from pathlib import Path


RESOURCE_DB_PATH = Path(os.getenv('FEIZHU_RESOURCE_DB_PATH', '/root/data/disk/ruoyi-fastapi/feizhu_resources.db'))


class ResourceSearchService:
    @staticmethod
    def _topics(connection: sqlite3.Connection) -> list[str]:
        return sorted({topic.strip() for (value,) in connection.execute("SELECT topic FROM t_file_detail WHERE topic <> ''") for topic in value.split(',') if topic.strip()})

    @classmethod
    async def topics(cls) -> list[str]:
        if not RESOURCE_DB_PATH.exists():
            return []
        with sqlite3.connect(RESOURCE_DB_PATH) as connection:
            return cls._topics(connection)

    @staticmethod
    def _highlight(value: str, keyword: str) -> str:
        escaped = html.escape(value or '')
        if not keyword:
            return escaped
        return escaped.replace(html.escape(keyword), f'<mark>{html.escape(keyword)}</mark>')

    @classmethod
    async def search(cls, kw: str, page: int, line: int, res_type: str | None) -> dict:
        if not RESOURCE_DB_PATH.exists() or not kw:
            return {'resources': [], 'total': 0}
        with sqlite3.connect(RESOURCE_DB_PATH) as connection:
            connection.row_factory = sqlite3.Row
            where, params = ["instr(',' || topic || ',', ',' || ? || ',') > 0"], [kw]
            if res_type:
                where.append('type=?')
                params.append(res_type)
            clause = ' WHERE ' + ' AND '.join(where)
            total = connection.execute('SELECT COUNT(*) FROM t_file_detail' + clause, params).fetchone()[0]
            rows = connection.execute(
                'SELECT id,eu,filename,size,isdir,ext,category,user,ctime,utime,updatetime,type FROM t_file_detail'
                + clause + ' ORDER BY COALESCE(updatetime,utime) DESC,id DESC LIMIT ? OFFSET ?',
                [*params, line, (page - 1) * line],
            ).fetchall()
            resources = []
            for row in rows:
                files = connection.execute('SELECT path,filename,size,ext,isdir FROM t_file_detail_item WHERE resource_id=? ORDER BY sort_no', (row['id'],)).fetchall()
                res = {key: row[key] for key in row.keys() if row[key] is not None}
                res['filelist'] = [{key: item[key] for key in item.keys() if item[key] is not None} for item in files]
                if res.get('size') is not None:
                    res['size'] = str(res['size'])
                resources.append({'highs': {'filename': [cls._highlight(row['filename'] or '', kw)]}, 'res': res})
        return {'resources': resources, 'total': total}

    @classmethod
    async def detail(cls, resource_id: str) -> dict | None:
        if not RESOURCE_DB_PATH.exists():
            return None
        with sqlite3.connect(RESOURCE_DB_PATH) as connection:
            connection.row_factory = sqlite3.Row
            row = connection.execute('SELECT id,url,filename,size,isdir,haspwd,ext,pwd,ctime,utime,category,create_time,updatetime,valid,detail_loaded_count,detail_complete FROM t_file_detail WHERE id=?', (resource_id,)).fetchone()
            if not row:
                return None
            files = connection.execute('SELECT path,filename,size,ext,isdir FROM t_file_detail_item WHERE resource_id=? ORDER BY sort_no', (resource_id,)).fetchall()
        result = {key: row[key] for key in row.keys() if row[key] is not None}
        result['size'] = int(result['size']) if str(result.get('size', '')).isdigit() else 0
        result['haspwd'] = str(result.get('haspwd', '0')) in ('1', 'true', 'True')
        result['filelist'] = [{key: item[key] for key in item.keys() if item[key] is not None} for item in files]
        return result
