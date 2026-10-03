import sqlite3
from pathlib import Path


class FutureHistoryDao:
    @classmethod
    def get_catalog(cls, database_path: str, kind: str) -> list[dict]:
        queries = {
            'varieties': ('SELECT variety_code,name,exchange_code,exchange_name,has_night_session,margin_rate,main_contract_thscode FROM t_future_variety ORDER BY exchange_code,variety_code', ('variety_code','name','exchange_code','exchange_name','has_night_session','margin_rate','main_contract_thscode')),
            'plates': ('SELECT variety_code,variety_name,plate_level,plate_name FROM t_future_variety_plate ORDER BY plate_name,plate_level,variety_code', ('variety_code','variety_name','plate_level','plate_name')),
            'roles': ('SELECT role_type,thscode,ticker,contract_name,variety_code,variety_name,exchange_code FROM t_future_contract_role_current ORDER BY role_type,thscode', ('role_type','thscode','ticker','contract_name','variety_code','variety_name','exchange_code')),
        }
        sql, fields = queries[kind]
        with cls._connect(database_path) as connection:
            try: rows = connection.execute(sql).fetchall()
            except sqlite3.OperationalError: return []
        return [dict(zip(fields, row)) for row in rows]
    @staticmethod
    def _connect(database_path: str) -> sqlite3.Connection:
        path = Path(database_path)
        if not path.is_file():
            raise FileNotFoundError(f'Future statistics database does not exist: {path}')
        return sqlite3.connect(f'file:{path.resolve().as_posix()}?mode=ro', uri=True)

    @classmethod
    def get_basis(cls, database_path: str, thscode: str | None = None) -> list[dict]:
        with cls._connect(database_path) as connection:
            try:
                if thscode:
                    rows = connection.execute(
                        "SELECT thscode,trade_date,contract_name,variety_name,spot_price,close_price,close_basis,close_basis_rate,settle_basis,settle_basis_rate "
                        "FROM t_future_basis_daily WHERE thscode=? ORDER BY trade_date DESC", (thscode,)
                    ).fetchall()
                else:
                    rows = connection.execute(
                        "SELECT b.thscode,b.trade_date,b.contract_name,b.variety_name,b.spot_price,b.close_price,b.close_basis,b.close_basis_rate,b.settle_basis,b.settle_basis_rate "
                        "FROM t_future_basis_daily b JOIN (SELECT thscode,MAX(trade_date) trade_date FROM t_future_basis_daily GROUP BY thscode) latest "
                        "ON latest.thscode=b.thscode AND latest.trade_date=b.trade_date ORDER BY b.thscode"
                    ).fetchall()
            except sqlite3.OperationalError:
                return []
        fields = ('thscode', 'trade_date', 'contract_name', 'variety_name', 'spot_price', 'close_price', 'close_basis', 'close_basis_rate', 'settle_basis', 'settle_basis_rate')
        return [dict(zip(fields, row)) for row in rows]

    @classmethod
    def get_contracts(cls, database_path: str, page_num: int, page_size: int, keyword: str | None) -> tuple[list[dict], int]:
        with cls._connect(database_path) as connection:
            where, params = '', []
            if keyword:
                where, params = 'WHERE thscode LIKE ? OR contract_name LIKE ? OR product_code LIKE ?', [f'%{keyword}%', f'%{keyword}%', f'%{keyword}%']
            try:
                total = connection.execute(f'SELECT COUNT(*) FROM t_future_contract {where}', params).fetchone()[0]
                rows = connection.execute(
                    f"SELECT thscode,ticker,contract_name,exchange_code,product_code,list_date,last_trade_date FROM t_future_contract {where} "
                    "ORDER BY product_code,exchange_code,thscode LIMIT ? OFFSET ?", [*params, page_size, (page_num - 1) * page_size]
                ).fetchall()
            except sqlite3.OperationalError:
                return [], 0
        return [dict(zip(('thscode', 'ticker', 'contract_name', 'exchange_code', 'product_code', 'list_date', 'last_trade_date'), row)) for row in rows], total

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
