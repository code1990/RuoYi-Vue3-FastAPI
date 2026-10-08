import json
import re
import sqlite3
from pathlib import Path

import requests


class FutureQuoteDao:
    STOCK_DAILY_LIMIT_RATE = 10.0
    DEFAULT_MARGIN_RATE = 0.10
    DEFAULT_FEE = 2.0
    MARKETS = {
        'domestic': ('XSGE', 'XDCE', 'XZCE', 'XGFE', 'SHGE'),
        'overseas': ('CBOT', 'CME', 'NYMEX', 'COMEX'),
    }
    PROFIT_SPECS = {
        'RM': (10, 0.10, 3.0), 'CS': (10, 0.10, 3.0), 'RB': (10, 0.10, 2.0), 'MA': (10, 0.10, 2.0),
        'SR': (10, 0.10, 6.0), 'C': (10, 0.10, 2.4), 'M': (10, 0.10, 3.0), 'V': (5, 0.10, 2.0),
    }
    REAL_FIELDS = 'last_px,open_px,high_px,low_px,prev_settlement,px_change,px_change_rate,prod_name,prod_name_ext,market_date,contract_unit,up_px,down_px,min5_chgpct,current_amount,business_amount'

    @staticmethod
    def number(value: object) -> float:
        try:
            return float(value or 0)
        except (TypeError, ValueError):
            return 0

    @classmethod
    def _live_rows(cls, contract_codes: list[str]) -> dict[str, dict]:
        """Return the latest snapshots; the database remains the fallback catalog."""
        if not contract_codes:
            return {}
        try:
            response = requests.get(
                'https://quotedata.cnfin.com/quote/v1/real',
                params={'en_prod_code': ','.join(contract_codes), 'fields': cls.REAL_FIELDS},
                headers={'User-Agent': 'Mozilla/5.0', 'Origin': 'https://www.cnfin.com', 'Referer': 'https://www.cnfin.com/'},
                timeout=(3, 8),
            )
            response.raise_for_status()
            snapshot = ((response.json().get('data') or {}).get('snapshot') or {})
            fields = snapshot.get('fields') or []
            return {code: dict(zip(fields, values)) for code, values in snapshot.items() if code != 'fields' and isinstance(values, list)}
        except requests.RequestException:
            return {}

    @classmethod
    def _refresh(cls, rows: list[dict], discard_missing: bool = False) -> list[dict]:
        snapshots = cls._live_rows([row['contract_code'] for row in rows])
        refreshed = []
        for row in rows:
            data = snapshots.get(row['contract_code'])
            if not data or cls.number(data.get('last_px')) <= 0:
                if not discard_missing:
                    refreshed.append(row)
                continue
            row.update({key: str(data[key]) if key == 'market_date' else data[key] for key in ('market_date', 'last_px', 'open_px', 'high_px', 'low_px', 'prev_settlement', 'px_change', 'px_change_rate', 'up_px', 'down_px', 'min5_chgpct') if key in data})
            row['contract_name'] = data.get('prod_name') or data.get('prod_name_ext') or row['contract_name']
            if 'price' in row:
                row['price'] = cls.number(data['last_px'])
                row['multiplier'] = cls.number(data.get('contract_unit')) or row['multiplier']
            else:
                row['contract_unit'] = cls.number(data.get('contract_unit')) or row['contract_unit']
            refreshed.append(row)
        return refreshed

    @staticmethod
    def _main_contract_code(contract_code: str, market_code: str) -> str:
        prefix = re.match(r'[A-Za-z]+', contract_code.split('.', 1)[0])
        return f'{prefix.group(0).upper()}888.{market_code}' if prefix else contract_code

    @classmethod
    def get_contract(cls, database_path: str, contract_code: str, live: bool = False) -> dict | None:
        path = Path(database_path)
        if not path.is_file():
            raise FileNotFoundError(f'Future statistics database does not exist: {path}')
        with sqlite3.connect(f'file:{path.resolve().as_posix()}?mode=ro', uri=True) as connection:
            row = connection.execute(
                '''SELECT q.contract_code, q.market_code, q.market_date, q.last_px, q.payload_json, p.product_name
                   FROM t_future_quote q LEFT JOIN t_future_product p ON p.market_code=q.market_code AND p.product_code=q.product_code
                   WHERE q.contract_code=? LIMIT 1''',
                (contract_code,),
            ).fetchone()
        if not row:
            if not live:
                return None
            snapshot = cls._live_rows([contract_code]).get(contract_code)
            if not snapshot or cls.number(snapshot.get('last_px')) <= 0:
                return None
            return {
                'contract_code': contract_code,
                'market_code': contract_code.rsplit('.', 1)[-1],
                'market_date': str(snapshot.get('market_date') or ''),
                'contract_name': snapshot.get('prod_name') or snapshot.get('prod_name_ext') or contract_code,
                'price': cls.number(snapshot['last_px']),
                'multiplier': cls.number(snapshot.get('contract_unit')) or 1,
            }
        if cls.number(row[3]) <= 0:
            return None
        payload = json.loads(row[4])
        result = {
            'contract_code': row[0],
            'market_code': row[1],
            'market_date': str(row[2] or ''),
            'contract_name': payload.get('prod_name') or payload.get('prod_name_ext') or row[5] or row[0],
            'price': cls.number(row[3]),
            'multiplier': cls.number(payload.get('contract_unit')) or 1,
        }
        return cls._refresh([result])[0] if live else result

    @classmethod
    def get_page(cls, database_path: str, scope: str, keyword: str | None, page_num: int, page_size: int, live: bool = False) -> tuple[list[dict], int]:
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
                f'''SELECT q.contract_code, q.product_code, q.market_code, q.market_date, q.last_px, q.px_change_rate, q.px_change, q.open_px,
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
            item['contract_unit'] = cls.number(payload.get('contract_unit')) or 1
            item['up_px'] = cls.number(payload.get('up_px')) or None
            item['down_px'] = cls.number(payload.get('down_px')) or None
            item['min5_chgpct'] = payload.get('min5_chgpct')
            name = item['contract_name']
            priority = 2 if '主力' in name or '888' in item['contract_code'] else 1 if '主连' in name or '连续' in name else 0
            turnover = cls.number(payload.get('current_amount') or payload.get('amount') or payload.get('business_amount'))
            key = (item['market_name'], item['product_name'])
            if key not in selected or (priority, turnover) > selected[key][:2]:
                selected[key] = (priority, turnover, item)
        rows = [entry[2] for entry in selected.values()]
        if live:
            # 本地库只提供品种目录；旧报价绝不进入当前列表。
            for row in rows:
                row['contract_code'] = cls._main_contract_code(row['contract_code'], row['market_code'])
            rows = cls._refresh(rows, discard_missing=True)
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
            payload = json.loads(payload_json)
            name = str(payload.get('prod_name') or payload.get('prod_name_ext') or '')
            priority = 2 if '主力' in name or '888' in str(contract_code) else 1 if '主连' in name or '连续' in name else 0
            if priority < 2 or cls.number(payload.get('contract_unit')) <= 0:
                continue
            turnover = cls.number(payload.get('current_amount') or payload.get('amount') or payload.get('business_amount'))
            if contract_prefix not in quotes or (priority, turnover) > quotes[contract_prefix][0]:
                quotes[contract_prefix] = ((priority, turnover), {'contract_code': contract_code, 'contract_name': name, 'market_date': market_date, 'open_px': open_px, 'last_px': last_px, 'contract_unit': payload.get('contract_unit')})
        rows = []
        for contract_prefix, (_, quote) in quotes.items():
            multiplier, margin_rate, fee = cls.PROFIT_SPECS.get(contract_prefix, (cls.number(quote['contract_unit']), cls.DEFAULT_MARGIN_RATE, cls.DEFAULT_FEE))
            open_px, last_px = cls.number(quote['open_px']), cls.number(quote['last_px'])
            if open_px <= 0 or last_px <= 0:
                continue
            spread = abs(last_px - open_px)
            margin = open_px * multiplier * margin_rate
            capital = margin + fee
            net_profit = spread * multiplier - fee
            price_change_rate = (last_px - open_px) / open_px * 100
            rows.append({
                'contract_code': quote['contract_code'], 'contract_name': quote['contract_name'], 'market_date': quote['market_date'],
                'open_px': open_px, 'last_px': last_px, 'direction': '做多' if last_px >= open_px else '做空',
                'price_spread': spread, 'net_profit': net_profit, 'margin': margin, 'fee': fee, 'capital': capital,
                'profit_rate': net_profit / capital * 100,
                'stock_same_move_profit': capital * max(-cls.STOCK_DAILY_LIMIT_RATE, min(cls.STOCK_DAILY_LIMIT_RATE, price_change_rate)) / 100,
                'stock_required_change_rate': net_profit / capital * 100,
            })
        return sorted(rows, key=lambda row: row['net_profit'], reverse=True)
