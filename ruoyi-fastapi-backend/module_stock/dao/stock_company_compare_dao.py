import sqlite3
from pathlib import Path


class StockCompanyCompareDao:
    @staticmethod
    def get_history(database_path: str, stock_codes: list[str]) -> tuple[list[dict], list[dict]]:
        path = Path(database_path)
        if not path.is_file():
            raise FileNotFoundError(f'Stock statistics database does not exist: {path}')
        with sqlite3.connect(f'file:{path.resolve().as_posix()}?mode=ro', uri=True) as connection:
            connection.row_factory = sqlite3.Row
            if not connection.execute("SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 't_stock_daily_240'").fetchone():
                return [], []
            placeholders = ', '.join('?' for _ in stock_codes)
            companies = connection.execute(
                f'''SELECT substr(stock_code, 1, 6) AS stock_code, stock_name, full_industry AS industry, full_concept AS concept, capital AS market_cap
                    FROM t_stock_pool WHERE substr(stock_code, 1, 6) IN ({placeholders})
                    ORDER BY capital DESC, stock_code''', stock_codes,
            ).fetchall()
            holdings = {}
            if connection.execute("SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 't_stock_org_holder_tab'").fetchone():
                rows = connection.execute(
                    f'''WITH latest AS (
                           SELECT stock_code, MAX(report_date) AS report_date
                           FROM t_stock_org_holder_tab
                           WHERE substr(stock_code, 1, 6) IN ({placeholders})
                           GROUP BY stock_code
                       )
                       SELECT substr(tab.stock_code, 1, 6) AS stock_code, tab.report_date,
                              MAX(CASE WHEN tab.tab_name = '全部' THEN CAST(tab.holder_rate AS REAL) END) AS main_holding_rate,
                              MAX(CASE WHEN tab.tab_name = '基金' THEN CAST(tab.holder_rate AS REAL) END) AS fund_holding_rate
                       FROM t_stock_org_holder_tab AS tab
                       JOIN latest ON latest.stock_code = tab.stock_code AND latest.report_date = tab.report_date
                       GROUP BY tab.stock_code, tab.report_date''', stock_codes,
                ).fetchall()
                holdings = {row['stock_code']: dict(row) for row in rows}
            quotes = connection.execute(
                f'''SELECT substr(stock_code, 1, 6) AS stock_code, trade_date, close, high
                    FROM t_stock_daily_240
                    WHERE substr(stock_code, 1, 6) IN ({placeholders}) AND trade_date >= 20260101 AND close > 0
                    ORDER BY stock_code, trade_date''', stock_codes,
            ).fetchall()
        return [{**dict(row), **holdings.get(row['stock_code'], {})} for row in companies], [dict(row) for row in quotes]
