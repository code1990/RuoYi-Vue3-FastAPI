import sqlite3
from pathlib import Path


class StockMarginDao:
    @staticmethod
    def get_combo_statistics(database_path: str, window_days: int, target_return_pct: float) -> list[dict]:
        path = Path(database_path)
        if not path.is_file():
            raise FileNotFoundError(f'Stock statistics database does not exist: {path}')
        max_return = 'MAX(t1_max_return_pct, t2_max_return_pct, t3_max_return_pct, t4_max_return_pct, t5_max_return_pct)'
        with sqlite3.connect(f'file:{path.resolve().as_posix()}?mode=ro', uri=True) as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                f'''SELECT signal_date,
                           CASE WHEN total_score < 0.3 THEN '0-0.3'
                                WHEN total_score < 0.6 THEN '0.3-0.6' ELSE '0.6+' END AS score_band,
                           SUM(CASE WHEN {max_return} >= :target_return_pct THEN 1 ELSE 0 END) AS success_count,
                           SUM(CASE WHEN {max_return} < :target_return_pct THEN 1 ELSE 0 END) AS failure_count,
                           COUNT(*) AS sample_count
                    FROM t_stock_margin_combo_signal
                    WHERE window_days = :window_days AND t5_max_return_pct IS NOT NULL
                    GROUP BY signal_date, score_band
                    ORDER BY signal_date, CASE score_band WHEN '0-0.3' THEN 1 WHEN '0.3-0.6' THEN 2 ELSE 3 END''',
                {'window_days': window_days, 'target_return_pct': target_return_pct},
            ).fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def get_long_statistics(database_path: str, start_date: str | None, end_date: str | None, target_return_pct: float) -> list[dict]:
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
                           CASE WHEN participation_ratio < 0.1 THEN '10%以下'
                                WHEN participation_ratio < 0.2 THEN '10-20%' ELSE '20%+' END AS participation_band,
                           SUM(CASE WHEN {max_return} >= :target_return_pct THEN 1 ELSE 0 END) AS success_count,
                           SUM(CASE WHEN {max_return} < :target_return_pct THEN 1 ELSE 0 END) AS failure_count,
                           COUNT(*) AS sample_count
                    FROM t_stock_margin_long_performance WHERE {' AND '.join(clauses)}
                    GROUP BY signal_date, participation_band
                    ORDER BY signal_date, CASE participation_band WHEN '10%以下' THEN 1 WHEN '10-20%' THEN 2 ELSE 3 END''', params,
            ).fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def get_combo_page(
        database_path: str, window_days: int, start_date: str | None, end_date: str | None, page_num: int, page_size: int
    ) -> tuple[list[dict], int]:
        path = Path(database_path)
        if not path.is_file():
            raise FileNotFoundError(f'Stock statistics database does not exist: {path}')
        clauses = ['window_days = :window_days']
        params: dict[str, str | int] = {'window_days': window_days, 'limit': page_size, 'offset': (page_num - 1) * page_size}
        if start_date:
            clauses.append('signal_date >= :start_date')
            params['start_date'] = int(start_date)
        if end_date:
            clauses.append('signal_date <= :end_date')
            params['end_date'] = int(end_date)
        where_sql = ' AND '.join(clauses)
        uri = f'file:{path.resolve().as_posix()}?mode=ro'
        with sqlite3.connect(uri, uri=True) as connection:
            connection.row_factory = sqlite3.Row
            total = connection.execute(f'SELECT COUNT(*) FROM t_stock_margin_combo_signal WHERE {where_sql}', params).fetchone()[0]
            rows = connection.execute(
                f'''SELECT signal_date, window_days, stock_code, stock_name, latest_rank, avg_rank,
                           total_score, avg_score, avg_participation_ratio, avg_balance_change_ratio,
                           entry_trade_date, entry_price, entry_open_return_pct, close_return_pct,
                           t1_max_return_pct, t2_max_return_pct, t3_max_return_pct, t4_max_return_pct,
                           t5_max_return_pct, performance_updated_at
                    FROM t_stock_margin_combo_signal
                    WHERE {where_sql}
                    ORDER BY signal_date DESC, total_score DESC, stock_code ASC
                    LIMIT :limit OFFSET :offset''', params
            ).fetchall()
        return [dict(row) for row in rows], total

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
            columns = {row[1] for row in connection.execute('PRAGMA table_info(t_stock_margin_long_performance)')}
            entry_change_sql = 'entry_change_pct' if 'entry_change_pct' in columns else 'NULL AS entry_change_pct'
            total = connection.execute(
                f'SELECT COUNT(*) FROM t_stock_margin_long_performance WHERE {where_sql}', params
            ).fetchone()[0]
            rows = connection.execute(
                f'''
                SELECT stock_code, margin_trade_date, signal_date, stock_name, rank_no, score,
                       participation_ratio, balance_change_ratio, entry_price, {entry_change_sql}, industry_name,
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
