import sqlite3
from pathlib import Path


class StockDdeDao:
    """Read-only access to the stock statistics SQLite database."""

    OBSERVATION_TABLES = {
        'high_price': 't_stock_dde_high_price_observation',
        'large_cap': 't_stock_dde_large_cap_observation',
        'intraday_combo': 't_stock_dde_intraday_combo_observation',
    }

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

    @staticmethod
    def get_hot_rank_page(
        database_path: str, page_num: int, page_size: int, large_cap: bool | None, high_price: bool | None
    ) -> tuple[list[dict], int, str | None, str | None]:
        path = Path(database_path)
        if not path.is_file():
            raise FileNotFoundError(f'Stock statistics database does not exist: {path}')
        uri = f'file:{path.resolve().as_posix()}?mode=ro'
        with sqlite3.connect(uri, uri=True) as connection:
            connection.row_factory = sqlite3.Row
            exists = connection.execute(
                "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 't_stock_dde_hot_rank'"
            ).fetchone()
            if not exists:
                return [], 0, None, None
            stat_range = connection.execute(
                "SELECT stat_start_date, stat_end_date FROM t_stock_dde_hot_rank "
                "ORDER BY stat_end_date DESC, stat_start_date DESC LIMIT 1"
            ).fetchone()
            if not stat_range:
                return [], 0, None, None
            clauses = ['stat_start_date = :stat_start_date', 'stat_end_date = :stat_end_date']
            params: dict[str, str | int] = {
                'stat_start_date': stat_range['stat_start_date'],
                'stat_end_date': stat_range['stat_end_date'],
                'limit': page_size,
                'offset': (page_num - 1) * page_size,
            }
            if large_cap:
                clauses.append('is_large_cap = 1')
            if high_price:
                clauses.append('is_high_price = 1')
            where_sql = ' AND '.join(clauses)
            total = connection.execute(f'SELECT COUNT(*) FROM t_stock_dde_hot_rank WHERE {where_sql}', params).fetchone()[0]
            rows = connection.execute(
                f'''SELECT rank_no, stock_code, stock_name, appearance_count, signal_day_count,
                           morning_count, noon_count, close_count, recent_5_count, latest_signal_date,
                           latest_signal_slot, best_rank, average_rank, limit_up_count,
                           tradable_signal_count, tradable_sample_day_count,
                           completed_tradable_sample_day_count, target_hit_count, target_hit_rate,
                           latest_tail_price, latest_tail_market_cap, is_large_cap, is_high_price,
                           is_latest_signal_limit_up
                    FROM t_stock_dde_hot_rank WHERE {where_sql}
                    ORDER BY rank_no ASC LIMIT :limit OFFSET :offset''',
                params,
            ).fetchall()
        return [dict(row) for row in rows], total, stat_range['stat_start_date'], stat_range['stat_end_date']

    @classmethod
    def get_observation_page(
        cls, database_path: str, dimension: str, start_date: str | None, end_date: str | None, page_num: int, page_size: int
    ) -> tuple[list[dict], int, dict[str, int]]:
        table_name = cls.OBSERVATION_TABLES.get(dimension)
        if table_name is None:
            raise ValueError(f'Unsupported DDE observation dimension: {dimension}')
        path = Path(database_path)
        if not path.is_file():
            raise FileNotFoundError(f'Stock statistics database does not exist: {path}')
        clauses = ['1 = 1']
        params: dict[str, str | int] = {'limit': page_size, 'offset': (page_num - 1) * page_size}
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
            exists = connection.execute(
                "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?", (table_name,)
            ).fetchone()
            if not exists:
                return [], 0, {'tradable_count': 0, 'completed_count': 0, 'target_hit_count': 0}
            summary = connection.execute(
                f'''SELECT COUNT(*) AS total, COALESCE(SUM(is_tradable), 0) AS tradable_count,
                           COALESCE(SUM(is_completed), 0) AS completed_count,
                           COALESCE(SUM(target_hit), 0) AS target_hit_count
                    FROM {table_name} WHERE {where_sql}''',
                params,
            ).fetchone()
            rows = connection.execute(
                f'''SELECT trade_date, stock_code, stock_name, morning_count, noon_count, close_count,
                           signal_count, best_rank, combo_type, entry_price, market_cap, change_pct,
                           is_limit_up, is_tradable, is_completed, target_hit
                    FROM {table_name} WHERE {where_sql}
                    ORDER BY trade_date DESC, best_rank ASC, stock_code ASC LIMIT :limit OFFSET :offset''',
                params,
            ).fetchall()
        return [dict(row) for row in rows], int(summary['total']), dict(summary)
