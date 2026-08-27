import sqlite3
from pathlib import Path


class StockKdjDao:
    @staticmethod
    def get_history(database_path: str, stock_code: str, limit: int) -> tuple[list[dict], list[dict]]:
        path = Path(database_path)
        if not path.is_file():
            raise FileNotFoundError(f'Stock statistics database does not exist: {path}')
        database_uri = f'file:{path.resolve().as_posix()}?mode=ro'
        with sqlite3.connect(database_uri, uri=True) as connection:
            connection.row_factory = sqlite3.Row
            if not connection.execute(
                "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 't_stock_daily_240'"
            ).fetchone():
                return [], []
            params = {'stock_code': stock_code, 'limit': limit}
            candles = connection.execute(
                '''
                WITH dates AS (
                    SELECT trade_date
                    FROM t_stock_daily_240
                    WHERE stock_code = :stock_code
                    ORDER BY trade_date DESC
                    LIMIT :limit
                )
                SELECT daily.trade_date, daily.open, daily.high, daily.low, daily.close,
                       daily.vol, daily.amount, daily.vol_rate, daily.percent, daily.changes, daily.pre_close
                FROM t_stock_daily_240 AS daily
                JOIN dates ON dates.trade_date = daily.trade_date
                WHERE daily.stock_code = :stock_code
                ORDER BY daily.trade_date
                ''',
                params,
            ).fetchall()
            indicators = []
            if connection.execute(
                "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 't_stock_kdj_daily'"
            ).fetchone():
                indicators = connection.execute(
                    '''
                    WITH dates AS (
                        SELECT trade_date
                        FROM t_stock_daily_240
                        WHERE stock_code = :stock_code
                        ORDER BY trade_date DESC
                        LIMIT :limit
                    )
                    SELECT kdj.trade_date, kdj.period, kdj.rsv, kdj.k, kdj.d, kdj.j,
                           kdj.rsv_cross_k, kdj.rsv_cross_d, kdj.golden_cross
                    FROM t_stock_kdj_daily AS kdj
                    JOIN dates ON dates.trade_date = kdj.trade_date
                    WHERE kdj.stock_code = :stock_code AND kdj.period IN (9, 90)
                    ORDER BY kdj.trade_date, kdj.period
                    ''',
                    params,
                ).fetchall()
        return [dict(row) for row in candles], [dict(row) for row in indicators]
