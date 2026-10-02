import sqlite3
import json
import re
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
    def get_contract_summaries(cls, database_path: str, page_num: int, page_size: int, variety_code: str | None = None, exchange_code: str | None = None) -> tuple[list[dict], int]:
        where, params = ('WHERE variety_code=? AND exchange_code=?', [variety_code, exchange_code]) if variety_code and exchange_code else ('', [])
        with cls._connect(database_path) as connection:
            total = connection.execute(f'SELECT COUNT(*) FROM (SELECT 1 FROM t_option_contract {where} GROUP BY exchange_code, variety_code)', params).fetchone()[0]
            rows = connection.execute(
                f"SELECT exchange_code || '/' || variety_code AS code, MAX(name), GROUP_CONCAT(thscode, '、'), GROUP_CONCAT(DISTINCT name) "
                f'FROM t_option_contract {where} GROUP BY exchange_code, variety_code ORDER BY exchange_code, variety_code LIMIT ? OFFSET ?',
                [*params, page_size, (page_num - 1) * page_size],
            ).fetchall()
        return [dict(zip(('code', 'name', 'contract_code_summary', 'name_summary'), row)) for row in rows], total

    @classmethod
    def get_varieties(cls, database_path: str, page_num: int, page_size: int) -> tuple[list[dict], int]:
        with cls._connect(database_path) as connection:
            total = connection.execute('SELECT COUNT(*) FROM t_option_base').fetchone()[0]
            rows = connection.execute(
                'SELECT variety_code, name, exchange_code, exchange_name, settlement_type, contract_multiplier FROM t_option_base '
                'ORDER BY exchange_code, variety_code LIMIT ? OFFSET ?', (page_size, (page_num - 1) * page_size),
            ).fetchall()
        return [dict(zip(('variety_code', 'name', 'exchange_code', 'exchange_name', 'settlement_type', 'contract_multiplier'), row)) for row in rows], total

    @classmethod
    def get_underlying_chain(cls, database_path: str, underlying_code: str) -> list[dict]:
        with cls._connect(database_path) as connection:
            contracts = connection.execute('SELECT thscode, name FROM t_option_contract WHERE thscode LIKE ? ORDER BY thscode', (f'{underlying_code}-%',)).fetchall()
            has_quotes = bool(connection.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='t_option_quote'").fetchone())
            result = []
            for thscode, name in contracts:
                parts = thscode.rsplit('.', 1)[0].split('-')
                latest = connection.execute('SELECT close_price FROM t_option_quote WHERE thscode=? ORDER BY trade_date DESC LIMIT 2', (thscode,)).fetchall() if has_quotes else []
                change = (latest[0][0] / latest[1][0] - 1) * 100 if len(latest) == 2 and latest[0][0] and latest[1][0] else None
                result.append({'thscode': thscode, 'name': name, 'option_type': 'call' if parts[1].upper() == 'C' else 'put', 'strike_price': float(parts[2]), 'day_change_rate': change})
        return result

    @classmethod
    def get_underlyings(cls, database_path: str) -> list[dict]:
        with cls._connect(database_path) as connection:
            rows = connection.execute("SELECT substr(thscode, 1, instr(thscode, '-') - 1), MIN(name) FROM t_option_contract WHERE instr(thscode, '-') > 0 GROUP BY 1 ORDER BY 1").fetchall()
        return [{'underlying_code': code, 'name': re.sub(r'[购沽]\d+(?:\.\d+)?$', '', name or '')} for code, name in rows]

    @classmethod
    def get_underlying_future(cls, database_path: str, underlying_code: str) -> dict:
        with cls._connect(database_path) as connection:
            row = connection.execute("SELECT contract_code, last_px, px_change_rate, payload_json FROM t_future_quote WHERE contract_code LIKE ? LIMIT 1", (f'{underlying_code}.%',)).fetchone()
        if not row:
            return {'contract_code': underlying_code, 'contract_name': '', 'last_px': None, 'px_change_rate': None}
        contract_code, last_px, change_rate, payload = row
        return {'contract_code': contract_code, 'contract_name': json.loads(payload).get('prod_name', ''), 'last_px': last_px, 'px_change_rate': change_rate}

    @classmethod
    def is_market_contract(cls, database_path: str, thscode: str) -> bool:
        where, params = cls._pool_where()
        with cls._connect(database_path) as connection:
            return bool(connection.execute(f'SELECT 1 FROM t_option_contract WHERE thscode=? AND ({where})', [thscode, *params]).fetchone())

    @classmethod
    def is_option_contract(cls, database_path: str, thscode: str) -> bool:
        with cls._connect(database_path) as connection:
            return bool(connection.execute('SELECT 1 FROM t_option_contract WHERE thscode=?', (thscode,)).fetchone())
