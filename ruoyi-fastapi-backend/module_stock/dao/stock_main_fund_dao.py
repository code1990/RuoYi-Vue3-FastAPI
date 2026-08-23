import sqlite3
from pathlib import Path


class StockMainFundDao:
    @staticmethod
    def get_performance_page(
        database_path: str, stock_code: str | None, start_date: str | None, end_date: str | None, page_num: int, page_size: int
    ) -> tuple[list[dict], int]:
        path = Path(database_path)
        if not path.is_file():
            raise FileNotFoundError(f'Stock statistics database does not exist: {path}')

        where_clauses = ['1 = 1']
        params: dict[str, str | int] = {}
        if stock_code:
            where_clauses.append('stock_code = :stock_code')
            params['stock_code'] = stock_code
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
                f'SELECT COUNT(*) FROM t_stock_55d_fund_performance WHERE {where_sql}', params
            ).fetchone()[0]
            rows = connection.execute(
                f'''
                SELECT stock_code, signal_date, strategy, signal_type, stock_name, industry_name, entry_price,
                       signal_score, strength_10d, strength_55d, flow_5d, flow_10d, flow_20d, flow_55d,
                       consecutive_inflow_days, close_return_pct, t1_max_return_pct, t2_max_return_pct,
                       t3_max_return_pct, t4_max_return_pct, t5_max_return_pct
                FROM t_stock_55d_fund_performance
                WHERE {where_sql}
                ORDER BY signal_date DESC, signal_score DESC, stock_code ASC
                LIMIT :limit OFFSET :offset
                ''',
                params,
            ).fetchall()
        return [dict(row) for row in rows], total

    @staticmethod
    def get_statistics(database_path: str, start_date: str | None, end_date: str | None, target_return_pct: float) -> list[dict]:
        path = Path(database_path)
        if not path.is_file():
            raise FileNotFoundError(f'Stock statistics database does not exist: {path}')
        clauses = ['t5_max_return_pct IS NOT NULL']
        params: dict[str, str | float] = {'target_return_pct': target_return_pct}
        if start_date:
            clauses.append('signal_date >= :start_date')
            params['start_date'] = start_date
        if end_date:
            clauses.append('signal_date <= :end_date')
            params['end_date'] = end_date
        max_return = 'MAX(t1_max_return_pct, t2_max_return_pct, t3_max_return_pct, t4_max_return_pct, t5_max_return_pct)'
        with sqlite3.connect(f'file:{path.resolve().as_posix()}?mode=ro', uri=True) as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                f'''SELECT signal_date,
                           CASE WHEN consecutive_inflow_days <= 2 THEN '1-2天'
                                WHEN consecutive_inflow_days <= 5 THEN '3-5天' ELSE '6天+' END AS inflow_band,
                           SUM(CASE WHEN {max_return} >= :target_return_pct THEN 1 ELSE 0 END) AS success_count,
                           SUM(CASE WHEN {max_return} < :target_return_pct THEN 1 ELSE 0 END) AS failure_count,
                           COUNT(*) AS sample_count
                    FROM t_stock_55d_fund_performance WHERE {' AND '.join(clauses)}
                    GROUP BY signal_date, inflow_band
                    ORDER BY signal_date, CASE inflow_band WHEN '1-2天' THEN 1 WHEN '3-5天' THEN 2 ELSE 3 END''', params,
            ).fetchall()
        return [dict(row) for row in rows]
