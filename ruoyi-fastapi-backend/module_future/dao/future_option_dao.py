import sqlite3
from pathlib import Path


class FutureOptionDao:
    MARKET_POOL = {
        'IO': 'CFFEX', 'HO': 'CFFEX', '510300O': 'SSE', '159919O': 'SZSE', '510050O': 'SSE',
        '510500O': 'SSE', '159901O': 'SZSE', '159922O': 'SZSE',
    }

    @classmethod
    def _pool_where(cls) -> tuple[str, list[str]]:
        return ' OR '.join('(variety_code=? AND exchange_code=?)' for _ in cls.MARKET_POOL), [item for pair in cls.MARKET_POOL.items() for item in pair]

    @staticmethod
    def _connect(database_path: str) -> sqlite3.Connection:
        path = Path(database_path)
        if not path.is_file():
            raise FileNotFoundError(f'Future statistics database does not exist: {path}')
        return sqlite3.connect(f'file:{path.resolve().as_posix()}?mode=ro', uri=True)

    @classmethod
    def get_market_contracts(cls, database_path: str, page_num: int, page_size: int) -> tuple[list[dict], int]:
        where, params = cls._pool_where()
        with cls._connect(database_path) as connection:
            total = connection.execute(f'SELECT COUNT(*) FROM t_option_contract WHERE {where}', params).fetchone()[0]
            rows = connection.execute(
                f'SELECT thscode, ticker, name, variety_code, exchange_code, list_date, last_trade_date FROM t_option_contract WHERE {where} '
                'ORDER BY variety_code, last_trade_date, thscode LIMIT ? OFFSET ?', [*params, page_size, (page_num - 1) * page_size],
            ).fetchall()
        return [dict(zip(('thscode', 'ticker', 'name', 'variety_code', 'exchange_code', 'list_date', 'last_trade_date'), row)) for row in rows], total

    @classmethod
    def get_market_varieties(cls, database_path: str) -> list[dict]:
        where, params = cls._pool_where()
        with cls._connect(database_path) as connection:
            rows = connection.execute(
                f'SELECT variety_code, name, exchange_code, exchange_name, settlement_type, contract_multiplier FROM t_option_base WHERE {where} ORDER BY variety_code', params
            ).fetchall()
        return [dict(zip(('variety_code', 'name', 'exchange_code', 'exchange_name', 'settlement_type', 'contract_multiplier'), row)) for row in rows]

    @classmethod
    def is_market_contract(cls, database_path: str, thscode: str) -> bool:
        where, params = cls._pool_where()
        with cls._connect(database_path) as connection:
            return bool(connection.execute(f'SELECT 1 FROM t_option_contract WHERE thscode=? AND ({where})', [thscode, *params]).fetchone())
