import sqlite3
from pathlib import Path


class StockFundVisualDao:
    @staticmethod
    def get_history(database_path: str, stock_code: str) -> tuple[list[dict], list[dict], list[dict]]:
        path = Path(database_path)
        if not path.is_file():
            raise FileNotFoundError(f'Stock statistics database does not exist: {path}')
        with sqlite3.connect(f'file:{path.resolve().as_posix()}?mode=ro', uri=True) as connection:
            connection.row_factory = sqlite3.Row
            exists = lambda table: connection.execute("SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?", (table,)).fetchone()
            main_fund = connection.execute(
                '''SELECT flow_date AS trade_date, CAST(main_net_amount AS REAL) / 100000000 AS value
                   FROM t_stock_55d_main_fund_flow WHERE stock_code = ? ORDER BY flow_date''', (stock_code,)
            ).fetchall() if exists('t_stock_55d_main_fund_flow') else []
            margin = connection.execute(
                '''SELECT trade_date, CAST(margin_buy_amount AS REAL) / 100000000 AS value
                   FROM t_stock_margin_trading WHERE stock_code = ? ORDER BY trade_date''', (stock_code,)
            ).fetchall() if exists('t_stock_margin_trading') else []
            dde_rows = connection.execute(
                '''SELECT trade_date, snapshot_slot,
                          (CAST(COALESCE(super_large_net_amount, 0) AS REAL) + CAST(COALESCE(large_net_amount, 0) AS REAL))
                          / NULLIF(CAST(market_cap AS REAL), 0) * 100 AS value
                   FROM t_stock_dde_fund_flow WHERE stock_code = ?''', (stock_code,)
            ).fetchall() if exists('t_stock_dde_fund_flow') else []
        priorities = {'post_close': 4, 'close': 3, 'noon': 2, 'morning': 1}
        dde_by_date = {}
        for row in dde_rows:
            if priorities.get(row['snapshot_slot'], 0) >= priorities.get(dde_by_date.get(row['trade_date'], {}).get('snapshot_slot'), 0):
                dde_by_date[row['trade_date']] = dict(row)
        return [dict(row) for row in main_fund], [dict(row) for row in margin], [
            {'trade_date': trade_date, 'value': row['value']} for trade_date, row in sorted(dde_by_date.items())
        ]
