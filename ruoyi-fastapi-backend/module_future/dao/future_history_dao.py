import sqlite3
from pathlib import Path


class FutureHistoryDao:
    @staticmethod
    def _connect(database_path: str) -> sqlite3.Connection:
        path = Path(database_path)
        if not path.is_file():
            raise FileNotFoundError(f'Future statistics database does not exist: {path}')
        return sqlite3.connect(f'file:{path.resolve().as_posix()}?mode=ro', uri=True)

    @classmethod
    def get_series(cls, database_path: str) -> list[dict]:
        with cls._connect(database_path) as connection:
            try:
                rows = connection.execute(
                    "SELECT s.thscode,s.product_code,s.exchange_code,s.series_type,s.series_name,MIN(b.trade_date),MAX(b.trade_date),COUNT(b.trade_date) "
                    "FROM t_future_series s LEFT JOIN t_future_daily_bar b ON b.thscode=s.thscode "
                    "GROUP BY s.thscode,s.product_code,s.exchange_code,s.series_type,s.series_name "
                    "HAVING COUNT(b.trade_date)>0 ORDER BY s.product_code,s.exchange_code,s.series_type"
                ).fetchall()
            except sqlite3.OperationalError:
                return []
        return [dict(zip(('thscode', 'product_code', 'exchange_code', 'series_type', 'series_name', 'first_trade_date', 'last_trade_date', 'samples'), row)) for row in rows]

    @classmethod
    def get_daily(cls, database_path: str, thscode: str) -> list[dict]:
        with cls._connect(database_path) as connection:
            try:
                rows = connection.execute(
                    "SELECT trade_date,open_price,high_price,low_price,close_price,volume,turnover "
                    "FROM t_future_daily_bar WHERE thscode=? ORDER BY trade_date DESC", (thscode,)
                ).fetchall()
            except sqlite3.OperationalError:
                return []
        return [dict(zip(('trade_date', 'open_price', 'high_price', 'low_price', 'close_price', 'volume', 'turnover'), row)) for row in rows]
