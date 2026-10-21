import sqlite3
from pathlib import Path


class StockCompanyCompareDao:
    @staticmethod
    def get_profile(database_path: str, stock_code: str) -> dict:
        path = Path(database_path)
        if not path.is_file():
            raise FileNotFoundError(f'Stock statistics database does not exist: {path}')
        profile = {'stock_code': stock_code, 'stock_name': '', 'industry': '', 'concept': ''}
        with sqlite3.connect(f'file:{path.resolve().as_posix()}?mode=ro', uri=True) as connection:
            connection.row_factory = sqlite3.Row
            has_table = lambda name: connection.execute("SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?", (name,)).fetchone()
            if has_table('t_stock_pool'):
                row = connection.execute('''SELECT stock_name, full_industry AS industry, full_concept AS concept
                    FROM t_stock_pool WHERE substr(stock_code, 1, 6) = ? LIMIT 1''', (stock_code,)).fetchone()
                if row:
                    profile.update({key: value or '' for key, value in dict(row).items()})
            if has_table('t_stock_quote'):
                row = connection.execute('''SELECT CAST(last_px AS REAL) AS last_price, replace(market_date, '-', '') AS market_date
                    FROM t_stock_quote WHERE substr(stock_code, 1, 6) = ? AND CAST(last_px AS REAL) > 0
                    ORDER BY market_date DESC LIMIT 1''', (stock_code,)).fetchone()
                if row:
                    profile.update(dict(row))
            if has_table('t_stock_daily_240'):
                rows = connection.execute('''SELECT CAST(close AS REAL) AS close FROM t_stock_daily_240
                    WHERE substr(stock_code, 1, 6) = ? AND CAST(close AS REAL) > 0 ORDER BY trade_date DESC LIMIT 1''', (stock_code,)).fetchall()
                if rows:
                    profile['previous_close'] = rows[0]['close']
                    if profile.get('last_price'):
                        profile['change_pct'] = (profile['last_price'] / profile['previous_close'] - 1) * 100
            if has_table('t_stock_org_holder_tab'):
                row = connection.execute('''WITH latest AS (
                        SELECT MAX(report_date) AS report_date FROM t_stock_org_holder_tab WHERE substr(stock_code, 1, 6) = ?
                    ) SELECT latest.report_date,
                        MAX(CASE WHEN tab.tab_name = '全部' THEN CAST(tab.holder_rate AS REAL) END) AS main_holding_rate,
                        MAX(CASE WHEN tab.tab_name = '基金' THEN CAST(tab.holder_rate AS REAL) END) AS fund_holding_rate
                    FROM latest LEFT JOIN t_stock_org_holder_tab AS tab ON tab.report_date = latest.report_date
                        AND substr(tab.stock_code, 1, 6) = ?''', (stock_code, stock_code)).fetchone()
                if row and row['report_date']:
                    profile.update(dict(row))
        return profile

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
