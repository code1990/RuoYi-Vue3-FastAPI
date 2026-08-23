import sqlite3
from pathlib import Path


class StockLimitUpDao:
    @staticmethod
    def get_theme_top15(database_path: str, trade_date: str | None) -> tuple[str | None, list[dict]]:
        path = Path(database_path)
        if not path.is_file():
            raise FileNotFoundError(f'Stock statistics database does not exist: {path}')
        with sqlite3.connect(f'file:{path.resolve().as_posix()}?mode=ro', uri=True) as connection:
            connection.row_factory = sqlite3.Row
            if not connection.execute("SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 't_stock_limit_up_theme'").fetchone():
                return None, []
            resolved_date = trade_date or connection.execute('SELECT MAX(trade_date) FROM t_stock_limit_up_theme').fetchone()[0]
            if not resolved_date:
                return None, []
            rows = connection.execute(
                '''SELECT SUBSTR(theme_key, 1, 1) AS theme_type, TRIM(SUBSTR(theme_key, 3)) AS theme_name,
                          stock_count AS limit_up_count, amount
                   FROM t_stock_limit_up_theme
                   WHERE trade_date = ? AND theme_key NOT LIKE 'T %' AND TRIM(SUBSTR(theme_key, 3)) <> 'None'
                   ORDER BY stock_count DESC, amount DESC, theme_key ASC LIMIT 15''',
                (resolved_date,),
            ).fetchall()
        return resolved_date, [dict(rank_no=index, **dict(row)) for index, row in enumerate(rows, 1)]
