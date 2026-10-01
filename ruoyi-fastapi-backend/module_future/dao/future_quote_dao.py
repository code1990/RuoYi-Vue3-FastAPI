import json
import sqlite3
from pathlib import Path


class FutureQuoteDao:
    MARKETS = {
        'domestic': ('XSGE', 'XDCE', 'XZCE', 'XGFE', 'SHGE'),
        'overseas': ('CBOT', 'CME', 'NYMEX', 'COMEX'),
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
                f'''SELECT q.contract_code, q.market_date, q.last_px, q.px_change_rate, q.px_change, q.open_px,
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
