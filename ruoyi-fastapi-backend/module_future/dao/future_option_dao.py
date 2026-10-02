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

    @staticmethod
    def parse_option_code(thscode: str) -> tuple[str, str, float] | None:
        code = thscode.rsplit('.', 1)[0]
        parts = code.split('-')
        if len(parts) >= 3 and parts[-2] in ('C', 'P'):
            try:
                return parts[0], 'call' if parts[-2] == 'C' else 'put', float(parts[-1])
            except ValueError:
                return None
        match = re.fullmatch(r'([A-Z]+\d+)([CP])(\d+(?:\.\d+)?)', code)
        return (match.group(1), 'call' if match.group(2) == 'C' else 'put', float(match.group(3))) if match else None

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
            contracts = [(code, name, parsed) for code, name in connection.execute('SELECT thscode, name FROM t_option_contract ORDER BY thscode') if (parsed := cls.parse_option_code(code)) and parsed[0] == underlying_code]
            has_quotes = bool(connection.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='t_option_quote'").fetchone())
            has_change_rate = has_quotes and 'day_change_rate' in {row[1] for row in connection.execute('PRAGMA table_info(t_option_quote)')}
            result = []
            for thscode, name, parsed in contracts:
                latest = connection.execute('SELECT day_change_rate FROM t_option_quote WHERE thscode=? ORDER BY trade_date DESC LIMIT 1', (thscode,)).fetchone() if has_change_rate else []
                change = latest[0] if latest else None
                result.append({'thscode': thscode, 'name': name, 'option_type': parsed[1], 'strike_price': parsed[2], 'day_change_rate': change})
        return result

    @classmethod
    def get_underlyings(cls, database_path: str) -> list[dict]:
        with cls._connect(database_path) as connection:
            rows = connection.execute('SELECT thscode, name FROM t_option_contract').fetchall()
        grouped = {}
        for thscode, name in rows:
            if parsed := cls.parse_option_code(thscode):
                grouped.setdefault(parsed[0], name)
        return [{'underlying_code': code, 'name': re.sub(r'[购沽]\d+(?:\.\d+)?$', '', name or '')} for code, name in sorted(grouped.items())]

    @classmethod
    def get_underlying_future(cls, database_path: str, underlying_code: str) -> dict:
        with cls._connect(database_path) as connection:
            row = connection.execute("SELECT contract_code, last_px, px_change_rate, payload_json FROM t_future_quote WHERE contract_code LIKE ? LIMIT 1", (f'{underlying_code}.%',)).fetchone()
        if not row:
            return {'contract_code': underlying_code, 'contract_name': '', 'last_px': None, 'px_change_rate': None}
        contract_code, last_px, change_rate, payload = row
        return {'contract_code': contract_code, 'contract_name': json.loads(payload).get('prod_name', ''), 'last_px': last_px, 'px_change_rate': change_rate}

    @classmethod
    def get_linkage_summary(cls, database_path: str) -> list[dict]:
        with cls._connect(database_path) as connection:
            quotes = {row[0].split('.', 1)[0]: row for row in connection.execute('SELECT contract_code, market_date, last_px, px_change_rate, payload_json FROM t_future_quote')}
            option_rates = {row[0]: (row[1], row[2]) for row in connection.execute('SELECT thscode, trade_date, day_change_rate FROM t_option_quote')}
            contracts = connection.execute('SELECT thscode FROM t_option_contract').fetchall()
        grouped = {}
        for (thscode,) in contracts:
            parsed = cls.parse_option_code(thscode)
            cached = option_rates.get(thscode)
            if not parsed or not cached or cached[1] is None:
                continue
            underlying, option_type, _ = parsed
            future = quotes.get(underlying)
            future_rate, option_rate = float(future[3] or 0) if future else 0, float(cached[1] or 0)
            if not future or future[1] != cached[0] or not future_rate or not option_rate:
                continue
            entry = grouped.setdefault(underlying, {'future': future, 'call': [0, 0], 'put': [0, 0]})
            bucket = entry[option_type]
            bucket[1] += 1
            aligned = future_rate * option_rate > 0 if option_type == 'call' else future_rate * option_rate < 0
            bucket[0] += int(aligned)
        rows = []
        for underlying, entry in grouped.items():
            contract_code, _, last_px, rate, payload = entry['future']
            def result(values): return None if values[1] < 3 else {'aligned': values[0], 'total': values[1], 'rate': values[0] / values[1] * 100}
            rows.append({'contract_code': contract_code, 'contract_name': json.loads(payload).get('prod_name', ''), 'last_px': last_px, 'px_change_rate': rate, 'put': result(entry['put']), 'call': result(entry['call'])})
        return sorted(rows, key=lambda row: row['contract_code'])

    @classmethod
    def is_market_contract(cls, database_path: str, thscode: str) -> bool:
        where, params = cls._pool_where()
        with cls._connect(database_path) as connection:
            return bool(connection.execute(f'SELECT 1 FROM t_option_contract WHERE thscode=? AND ({where})', [thscode, *params]).fetchone())

    @classmethod
    def is_option_contract(cls, database_path: str, thscode: str) -> bool:
        with cls._connect(database_path) as connection:
            return bool(connection.execute('SELECT 1 FROM t_option_contract WHERE thscode=?', (thscode,)).fetchone())
