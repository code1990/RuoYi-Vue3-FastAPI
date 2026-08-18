import sqlite3
from pathlib import Path


class StockDdeDao:
    """Read-only access to the stock statistics SQLite database."""

    @staticmethod
    def get_signal_performance_page(
        database_path: str, start_date: str | None, end_date: str | None, page_num: int, page_size: int
    ) -> tuple[list[dict], int]:
        path = Path(database_path)
        if not path.is_file():
            raise FileNotFoundError(f'Stock statistics database does not exist: {path}')

        where_clauses = ['1 = 1']
        params: dict[str, str | int] = {}
        if start_date:
            where_clauses.append('trade_date >= :start_date')
            params['start_date'] = start_date
        if end_date:
            where_clauses.append('trade_date <= :end_date')
            params['end_date'] = end_date

        where_sql = ' AND '.join(where_clauses)
        params['limit'] = page_size
        params['offset'] = (page_num - 1) * page_size
        database_uri = f'file:{path.resolve().as_posix()}?mode=ro'
        with sqlite3.connect(database_uri, uri=True) as connection:
            connection.row_factory = sqlite3.Row
            total = connection.execute(
                f'SELECT COUNT(*) FROM t_stock_dde_signal_performance WHERE {where_sql}', params
            ).fetchone()[0]
            rows = connection.execute(
                f'''
                SELECT
                    stock_code, trade_date, stock_name, signal_slot, entry_price, signal_change_pct,
                    large_net_amount, market_cap, main_net_ratio, industry_name,
                    close_return_pct, t1_max_return_pct, t2_max_return_pct,
                    t3_max_return_pct, t4_max_return_pct, t5_max_return_pct
                FROM t_stock_dde_signal_performance
                WHERE {where_sql}
                ORDER BY
                    trade_date DESC,
                    CASE signal_slot
                        WHEN 'close' THEN 3
                        WHEN 'noon' THEN 2
                        WHEN 'morning' THEN 1
                        ELSE 0
                    END DESC,
                    main_net_ratio DESC,
                    signal_rank_no ASC
                LIMIT :limit OFFSET :offset
                ''',
                params,
            ).fetchall()
        return [dict(row) for row in rows], total

    @staticmethod
    def get_combo_page(
        database_path: str, start_date: str | None, end_date: str | None, page_num: int, page_size: int
    ) -> tuple[list[dict], int]:
        path = Path(database_path)
        if not path.is_file():
            raise FileNotFoundError(f'Stock statistics database does not exist: {path}')
        clauses = ['1 = 1']
        params: dict[str, str | int] = {'limit': page_size, 'offset': (page_num - 1) * page_size}
        if start_date:
            clauses.append('signal_date >= :start_date')
            params['start_date'] = start_date
        if end_date:
            clauses.append('signal_date <= :end_date')
            params['end_date'] = end_date
        where_sql = ' AND '.join(clauses)
        uri = f'file:{path.resolve().as_posix()}?mode=ro'
        with sqlite3.connect(uri, uri=True) as connection:
            connection.row_factory = sqlite3.Row
            total = connection.execute(f'SELECT COUNT(*) FROM t_stock_dde_combo_signal WHERE {where_sql}', params).fetchone()[0]
            rows = connection.execute(
                f'''SELECT signal_date, previous_signal_date, stock_code, stock_name, previous_signal_count,
                           today_signal_count, today_morning_count, today_noon_count, today_close_count,
                           today_best_rank, today_main_net_ratio, previous_main_net_ratio, entry_price, current_price, combo_rank,
                           close_return_pct, t1_max_return_pct, t2_max_return_pct, t3_max_return_pct,
                           t4_max_return_pct, t5_max_return_pct
                    FROM t_stock_dde_combo_signal WHERE {where_sql}
                    ORDER BY signal_date DESC, combo_rank ASC LIMIT :limit OFFSET :offset''', params
            ).fetchall()
        return [dict(row) for row in rows], total

    @staticmethod
    def get_top30_performance_page(
        database_path: str, start_date: str | None, end_date: str | None, page_num: int, page_size: int
    ) -> tuple[list[dict], int]:
        path = Path(database_path)
        if not path.is_file():
            raise FileNotFoundError(f'Stock statistics database does not exist: {path}')
        clauses, params = ['1 = 1'], {'limit': page_size, 'offset': (page_num - 1) * page_size}
        if start_date:
            clauses.append('trade_date >= :start_date')
            params['start_date'] = start_date
        if end_date:
            clauses.append('trade_date <= :end_date')
            params['end_date'] = end_date
        where_sql = ' AND '.join(clauses)
        uri = f'file:{path.resolve().as_posix()}?mode=ro'
        with sqlite3.connect(uri, uri=True) as connection:
            connection.row_factory = sqlite3.Row
            total = connection.execute(f'SELECT COUNT(*) FROM t_stock_dde_30_signal_performance WHERE {where_sql}', params).fetchone()[0]
            rows = connection.execute(
                f'''SELECT stock_code, trade_date, stock_name, signal_slot, signal_rank_no, raw_rank_no, entry_price,
                           signal_change_pct, main_net_amount, market_cap, main_net_ratio, industry_name, close_return_pct,
                           t1_max_return_pct, t2_max_return_pct, t3_max_return_pct, t4_max_return_pct, t5_max_return_pct
                    FROM t_stock_dde_30_signal_performance WHERE {where_sql}
                    ORDER BY trade_date DESC, signal_rank_no ASC LIMIT :limit OFFSET :offset''', params
            ).fetchall()
        return [dict(row) for row in rows], total
