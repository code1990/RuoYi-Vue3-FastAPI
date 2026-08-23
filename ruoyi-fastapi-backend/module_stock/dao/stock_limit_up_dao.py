import sqlite3
from pathlib import Path


class StockLimitUpDao:
    @staticmethod
    def get_theme_top15(database_path: str, start_date: str | None, end_date: str | None) -> tuple[list[str], list[dict]]:
        path = Path(database_path)
        if not path.is_file():
            raise FileNotFoundError(f'Stock statistics database does not exist: {path}')
        with sqlite3.connect(f'file:{path.resolve().as_posix()}?mode=ro', uri=True) as connection:
            connection.row_factory = sqlite3.Row
            if not connection.execute("SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 't_stock_limit_up_theme'").fetchone():
                return [], []
            clauses = ["theme_key NOT LIKE 'T %'", "TRIM(SUBSTR(theme_key, 3)) <> 'None'", 'trade_date >= ?']
            params = [start_date or '2026-01-01']
            if end_date:
                clauses.append('trade_date <= ?')
                params.append(end_date)
            where_sql = ' AND '.join(clauses)
            themes = connection.execute(
                f'''SELECT theme_key, SUBSTR(theme_key, 1, 1) AS theme_type, TRIM(SUBSTR(theme_key, 3)) AS theme_name,
                           SUM(stock_count) AS total_count
                    FROM t_stock_limit_up_theme WHERE {where_sql}
                    GROUP BY theme_key ORDER BY total_count DESC, theme_key ASC LIMIT 15''',
                params,
            ).fetchall()
            if not themes:
                return [], []
            dates = [row[0] for row in connection.execute(
                f'SELECT DISTINCT trade_date FROM t_stock_limit_up_theme WHERE {where_sql} ORDER BY trade_date', params
            ).fetchall()]
            theme_keys = [row['theme_key'] for row in themes]
            placeholders = ', '.join('?' for _ in theme_keys)
            counts = connection.execute(
                f'''SELECT trade_date, theme_key, stock_count FROM t_stock_limit_up_theme
                    WHERE {where_sql} AND theme_key IN ({placeholders})''',
                [*params, *theme_keys],
            ).fetchall()
        values = {(row['trade_date'], row['theme_key']): row['stock_count'] for row in counts}
        return dates, [
            dict(rank_no=index, theme_type=row['theme_type'], theme_name=row['theme_name'], total_count=row['total_count'],
                 values=[values.get((trade_date, row['theme_key']), 0) for trade_date in dates])
            for index, row in enumerate(themes, 1)
        ]
