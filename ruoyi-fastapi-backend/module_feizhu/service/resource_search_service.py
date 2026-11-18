import html
import os
import sqlite3
from datetime import datetime, timedelta
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
    async def search(cls, kw: str, page: int, line: int, res_type: str | None = None, file_type: str | None = None, size: str | None = None, time: str | None = None) -> dict:
        if not RESOURCE_DB_PATH.exists() or not kw:
            return {'resources': [], 'total': 0}
        with sqlite3.connect(RESOURCE_DB_PATH) as connection:
            connection.row_factory = sqlite3.Row
            where, params = ["instr(',' || topic || ',', ',' || ? || ',') > 0"], [kw]
            if res_type:
                where.append('type=?')
                params.append(res_type)
            if file_type == 'folder':
                where.append('isdir=1')
            elif file_type == 'mp4':
                where.append("ext IN ('mp4','mkv','avi','mov')")
            elif file_type == 'music':
                where.append("ext IN ('mp3','wav','flac','aac')")
            elif file_type == 'image':
                where.append("ext IN ('jpg','jpeg','png','gif','webp')")
            elif file_type == 'document':
                where.append("ext IN ('pdf','doc','docx','xls','xlsx','ppt','pptx','txt','md','mobi','epub')")
            elif file_type == 'software':
                where.append("ext IN ('exe','dmg','apk','msi')")
            elif file_type == 'archive':
                where.append("ext IN ('zip','rar','7z','tar','gz')")
            elif file_type == 'torrent':
                where.append("ext='torrent'")
            ranges = {'tiny': (None, 20 * 1024**2), 'small': (20 * 1024**2, 200 * 1024**2), 'middle': (200 * 1024**2, 2 * 1024**3), 'large': (2 * 1024**3, None)}
            if size in ranges:
                lower, upper = ranges[size]
                if lower is not None:
                    where.append('CAST(size AS INTEGER)>=?')
                    params.append(lower)
                if upper is not None:
                    where.append('CAST(size AS INTEGER)<?')
                    params.append(upper)
            days = {'week': 7, 'month': 31, 'half-year': 183, 'year': 366}
            if time in days:
                where.append('COALESCE(updatetime,utime)>=?')
                params.append((datetime.now() - timedelta(days=days[time])).strftime('%Y-%m-%d %H:%M:%S'))
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
