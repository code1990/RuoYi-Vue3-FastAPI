import json
import sqlite3
from pathlib import Path


class FutureQuoteDao:
    MARKETS = {
        'domestic': ('XSGE', 'XDCE', 'XZCE', 'XGFE', 'SHGE'),
        'overseas': ('CBOT', 'CME', 'NYMEX', 'COMEX'),
    }

    @classmethod
    def get_page(cls, database_path: str, scope: str, keyword: str | None, page_num: int, page_size: int) -> tuple[list[dict], int]:
        path = Path(database_path)
        if not path.is_file():
            raise FileNotFoundError(f'Future statistics database does not exist: {path}')
        marks = ','.join('?' for _ in cls.MARKETS[scope])
        where = [f'q.market_code IN ({marks})']
        params: list[object] = [*cls.MARKETS[scope]]
        if keyword:
            where.append("(q.contract_code LIKE ? OR q.payload_json LIKE ? OR p.product_name LIKE ?)")
            params.extend([f'%{keyword}%'] * 3)
        condition = ' AND '.join(where)
        with sqlite3.connect(f'file:{path.resolve().as_posix()}?mode=ro', uri=True) as connection:
            connection.row_factory = sqlite3.Row
            total = connection.execute(f'SELECT COUNT(*) FROM t_future_quote q LEFT JOIN t_future_product p ON p.market_code=q.market_code AND p.product_code=q.product_code WHERE {condition}', params).fetchone()[0]
            result = connection.execute(
                f'''SELECT q.contract_code, q.market_date, q.last_px, q.px_change_rate, q.px_change, q.open_px,
                           q.high_px, q.low_px, q.prev_settlement, q.payload_json, p.market_name, p.product_name
                    FROM t_future_quote q LEFT JOIN t_future_product p ON p.market_code=q.market_code AND p.product_code=q.product_code
                    WHERE {condition} ORDER BY CAST(q.px_change_rate AS REAL) DESC, q.contract_code
                    LIMIT ? OFFSET ?''',
                [*params, page_size, (page_num - 1) * page_size],
            ).fetchall()
        rows = []
        for row in result:
            item = dict(row)
            payload = json.loads(item.pop('payload_json'))
            item['contract_name'] = payload.get('prod_name') or payload.get('prod_name_ext') or item['product_name'] or ''
            item['min5_chgpct'] = payload.get('min5_chgpct')
            rows.append(item)
        return rows, total
