import sqlite3
from pathlib import Path


class StockMarginDao:
    @staticmethod
    def get_long_performance_page(
        database_path: str, start_date: str | None, end_date: str | None, page_num: int, page_size: int
    ) -> tuple[list[dict], int]:
        path = Path(database_path)
        if not path.is_file():
            raise FileNotFoundError(f'Stock statistics database does not exist: {path}')

        where_clauses = ['1 = 1']
        params: dict[str, str | int] = {}
        if start_date:
            where_clauses.append('signal_date >= :start_date')
            params['start_date'] = start_date
        if end_date:
            where_clauses.append('signal_date <= :end_date')
            params['end_date'] = end_date
        where_sql = ' AND '.join(where_clauses)
        params.update(limit=page_size, offset=(page_num - 1) * page_size)
        database_uri = f'file:{path.resolve().as_posix()}?mode=ro'
        with sqlite3.connect(database_uri, uri=True) as connection:
            connection.row_factory = sqlite3.Row
            total = connection.execute(
                f'SELECT COUNT(*) FROM t_stock_margin_long_performance WHERE {where_sql}', params
            ).fetchone()[0]
            rows = connection.execute(
                f'''
                SELECT stock_code, margin_trade_date, signal_date, stock_name, rank_no, score,
                       participation_ratio, balance_change_ratio, entry_price, industry_name,
                       close_return_pct, t1_max_return_pct, t2_max_return_pct, t3_max_return_pct,
                       t4_max_return_pct, t5_max_return_pct
                FROM t_stock_margin_long_performance
                WHERE {where_sql}
                ORDER BY signal_date DESC, score DESC, rank_no ASC
                LIMIT :limit OFFSET :offset
                ''',
                params,
            ).fetchall()
        return [dict(row) for row in rows], total
