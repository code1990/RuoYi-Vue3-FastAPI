import json
import sqlite3
from pathlib import Path


class FutureQuoteDao:
    MARKETS = {
        'domestic': ('XSGE', 'XDCE', 'XZCE', 'XGFE', 'SHGE'),
        'overseas': ('CBOT', 'CME', 'NYMEX', 'COMEX'),
    }
    PROFIT_SPECS = {
        'RM': (10, 0.10, 3.0), 'CS': (10, 0.10, 3.0), 'RB': (10, 0.10, 2.0), 'MA': (10, 0.10, 2.0),
        'SR': (10, 0.10, 6.0), 'C': (10, 0.10, 2.4), 'M': (10, 0.10, 3.0), 'V': (5, 0.10, 2.0),
    }

    @staticmethod
    def number(value: object) -> float:
        try:
            return float(value or 0)
        except (TypeError, ValueError):
            return 0

    @classmethod
    def get_page(cls, database_path: str, scope: str, keyword: str | None, page_num: int, page_size: int) -> tuple[list[dict], int]:
        path = Path(database_path)
        if not path.is_file():
            raise FileNotFoundError(f'Future statistics database does not exist: {path}')
        marks = ','.join('?' for _ in cls.MARKETS[scope])
        where = [f'q.market_code IN ({marks})']
        params: list[object] = [*cls.MARKETS[scope]]
        condition = ' AND '.join(where)
        with sqlite3.connect(f'file:{path.resolve().as_posix()}?mode=ro', uri=True) as connection:
            connection.row_factory = sqlite3.Row
            result = connection.execute(
                f'''SELECT q.contract_code, q.product_code, q.market_date, q.last_px, q.px_change_rate, q.px_change, q.open_px,
                           q.high_px, q.low_px, q.prev_settlement, q.payload_json, p.market_name, p.product_name
                    FROM t_future_quote q LEFT JOIN t_future_product p ON p.market_code=q.market_code AND p.product_code=q.product_code
                    WHERE {condition}''',
                params,
            ).fetchall()
        selected = {}
        for row in result:
            item = dict(row)
            if cls.number(item['open_px']) == 0:
                continue
            payload = json.loads(item.pop('payload_json'))
            item['contract_name'] = payload.get('prod_name') or payload.get('prod_name_ext') or item['product_name'] or ''
            item['min5_chgpct'] = payload.get('min5_chgpct')
            name = item['contract_name']
            priority = 2 if '主力' in name or '888' in item['contract_code'] else 1 if '主连' in name or '连续' in name else 0
            turnover = cls.number(payload.get('current_amount') or payload.get('amount') or payload.get('business_amount'))
            key = (item['market_name'], item['product_name'])
            if key not in selected or (priority, turnover) > selected[key][:2]:
                selected[key] = (priority, turnover, item)
        rows = [entry[2] for entry in selected.values()]
        if keyword:
            text = keyword.lower()
            rows = [row for row in rows if text in row['contract_code'].lower() or text in row['contract_name'].lower() or text in row['product_name'].lower()]
        rows.sort(key=lambda row: (-cls.number(row['px_change_rate']), row['contract_code']))
        total = len(rows)
        return rows[(page_num - 1) * page_size:page_num * page_size], total

    @classmethod
    def get_profit_effect(cls, database_path: str) -> list[dict]:
        path = Path(database_path)
        if not path.is_file():
            raise FileNotFoundError(f'Future statistics database does not exist: {path}')
        marks = ','.join('?' for _ in cls.MARKETS['domestic'])
        with sqlite3.connect(f'file:{path.resolve().as_posix()}?mode=ro', uri=True) as connection:
            raw_quotes = connection.execute(
                f'SELECT contract_code, market_date, last_px, open_px, payload_json FROM t_future_quote WHERE market_code IN ({marks})',
                cls.MARKETS['domestic'],
            ).fetchall()
        quotes = {}
        for contract_code, market_date, last_px, open_px, payload_json in raw_quotes:
            contract_prefix = ''.join(char for char in str(contract_code).split('.', 1)[0] if char.isalpha())
            if contract_prefix not in cls.PROFIT_SPECS:
                continue
            payload = json.loads(payload_json)
            name = str(payload.get('prod_name') or payload.get('prod_name_ext') or '')
            priority = 2 if '主力' in name or '888' in str(contract_code) else 1 if '主连' in name or '连续' in name else 0
            turnover = cls.number(payload.get('current_amount') or payload.get('amount') or payload.get('business_amount'))
            if contract_prefix not in quotes or (priority, turnover) > quotes[contract_prefix][0]:
                quotes[contract_prefix] = ((priority, turnover), {'contract_code': contract_code, 'contract_name': name, 'market_date': market_date, 'open_px': open_px, 'last_px': last_px})
        rows = []
        for contract_prefix, (_, quote) in quotes.items():
            spec = cls.PROFIT_SPECS.get(contract_prefix)
            open_px, last_px = cls.number(quote['open_px']), cls.number(quote['last_px'])
            if not spec or open_px <= 0 or last_px <= 0:
                continue
            multiplier, margin_rate, fee = spec
            spread = abs(last_px - open_px)
            margin = open_px * multiplier * margin_rate
            capital = margin + fee
            net_profit = spread * multiplier - fee
            price_change_rate = (last_px - open_px) / open_px * 100
            rows.append({
                'contract_code': quote['contract_code'], 'contract_name': quote['contract_name'], 'market_date': quote['market_date'],
                'open_px': open_px, 'last_px': last_px, 'direction': '做多' if last_px >= open_px else '做空',
                'price_spread': spread, 'net_profit': net_profit, 'margin': margin, 'fee': fee, 'capital': capital,
                'profit_rate': net_profit / capital * 100, 'stock_same_move_profit': capital * price_change_rate / 100,
                'stock_required_change_rate': net_profit / capital * 100,
            })
        return sorted(rows, key=lambda row: row['net_profit'], reverse=True)
