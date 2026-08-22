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
    def get_order_by(sort_by: str | None, sort_order: str | None, fields: dict[str, str], default: str) -> str:
        field = fields.get(sort_by or '')
        if field is None or sort_order not in ('ascending', 'descending'):
            return default
        return f"{field} {'ASC' if sort_order == 'ascending' else 'DESC'}"

    @staticmethod
    def get_limit_up_slots(stock_name: str, morning_change_pct, noon_change_pct, close_change_pct) -> list[str]:
        threshold = 4.5 if 'ST' in stock_name.upper() else 9.5
        return [
            slot
            for slot, change_pct in (
                ('morning', morning_change_pct),
                ('noon', noon_change_pct),
                ('close', close_change_pct),
            )
            if change_pct is not None and float(change_pct) >= threshold
        ]

    @staticmethod
    def get_signal_performance_page(
        database_path: str, start_date: str | None, end_date: str | None, page_num: int, page_size: int,
        sort_by: str | None, sort_order: str | None,
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
        order_by = StockDdeDao.get_order_by(sort_by, sort_order, {
            'tradeDate': 'trade_date', 'entryPrice': 'entry_price', 'signalChangePct': 'signal_change_pct',
            'largeNetAmount': 'large_net_amount', 'marketCap': 'market_cap', 'mainNetRatio': 'main_net_ratio',
            'closeReturnPct': 'close_return_pct', **{f't{day}MaxReturnPct': f't{day}_max_return_pct' for day in range(1, 6)},
        }, "trade_date DESC, CASE signal_slot WHEN 'close' THEN 3 WHEN 'noon' THEN 2 WHEN 'morning' THEN 1 ELSE 0 END DESC, main_net_ratio DESC, signal_rank_no ASC")
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
                    large_net_amount, market_cap, main_net_ratio,
                    close_return_pct, t1_max_return_pct, t2_max_return_pct,
                    t3_max_return_pct, t4_max_return_pct, t5_max_return_pct
                FROM t_stock_dde_signal_performance
                WHERE {where_sql}
                ORDER BY {order_by}
                LIMIT :limit OFFSET :offset
                ''',
                params,
            ).fetchall()
        return [dict(row) for row in rows], total

    @staticmethod
    def get_combo_page(
        database_path: str, start_date: str | None, end_date: str | None, page_num: int, page_size: int,
        sort_by: str | None, sort_order: str | None,
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
        order_by = StockDdeDao.get_order_by(sort_by, sort_order, {
            'signalDate': 'signal_date', 'previousSignalDate': 'previous_signal_date', 'comboRank': 'combo_rank',
            'todayBestRank': 'today_best_rank', 'previousSignalCount': 'previous_signal_count', 'todaySignalCount': 'today_signal_count',
            'entryPrice': 'entry_price', 'currentPrice': 'current_price', 'todayMainNetRatio': 'today_main_net_ratio',
            'previousMainNetRatio': 'previous_main_net_ratio', 'closeReturnPct': 'close_return_pct',
            **{f't{day}MaxReturnPct': f't{day}_max_return_pct' for day in range(1, 6)},
        }, 'signal_date DESC, combo_rank ASC')
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
                    ORDER BY {order_by} LIMIT :limit OFFSET :offset''', params
            ).fetchall()
        return [dict(row) for row in rows], total

    @staticmethod
    def get_top30_performance_page(
        database_path: str, signal_slot: str | None, start_date: str | None, end_date: str | None, page_num: int, page_size: int,
        sort_by: str | None, sort_order: str | None,
    ) -> tuple[list[dict], int]:
        path = Path(database_path)
        if not path.is_file():
            raise FileNotFoundError(f'Stock statistics database does not exist: {path}')
        clauses, params = ['1 = 1'], {'limit': page_size, 'offset': (page_num - 1) * page_size}
        if signal_slot:
            clauses.append('signal_slot = :signal_slot')
            params['signal_slot'] = signal_slot
        if start_date:
            clauses.append('trade_date >= :start_date')
            params['start_date'] = start_date
        if end_date:
            clauses.append('trade_date <= :end_date')
            params['end_date'] = end_date
        where_sql = ' AND '.join(clauses)
        order_by = StockDdeDao.get_order_by(sort_by, sort_order, {
            'tradeDate': 'trade_date', 'signalRankNo': 'signal_rank_no', 'rawRankNo': 'raw_rank_no',
            'entryPrice': 'entry_price', 'mainNetAmount': 'main_net_amount', 'mainNetRatio': 'main_net_ratio',
            'marketCap': 'market_cap', 'signalChangePct': 'signal_change_pct', 'closeReturnPct': 'close_return_pct',
            **{f't{day}MaxReturnPct': f't{day}_max_return_pct' for day in range(1, 6)},
        }, "trade_date DESC, CASE signal_slot WHEN 'post_close' THEN 4 WHEN 'close' THEN 3 WHEN 'noon' THEN 2 WHEN 'morning' THEN 1 ELSE 0 END DESC, raw_rank_no ASC")
        uri = f'file:{path.resolve().as_posix()}?mode=ro'
        with sqlite3.connect(uri, uri=True) as connection:
            connection.row_factory = sqlite3.Row
            total = connection.execute(f'SELECT COUNT(*) FROM t_stock_dde_30_signal_performance WHERE {where_sql}', params).fetchone()[0]
            rows = connection.execute(
                f'''SELECT stock_code, trade_date, stock_name, signal_slot, signal_rank_no, raw_rank_no, entry_price,
                           signal_change_pct, main_net_amount, market_cap, main_net_ratio, close_return_pct,
                           t1_max_return_pct, t2_max_return_pct, t3_max_return_pct, t4_max_return_pct, t5_max_return_pct
                    FROM t_stock_dde_30_signal_performance WHERE {where_sql}
                    ORDER BY {order_by} LIMIT :limit OFFSET :offset''', params
            ).fetchall()
        return [dict(row) for row in rows], total

    @staticmethod
    def get_signal_statistics(database_path: str, start_date: str | None, end_date: str | None, target_return_pct: float) -> list[dict]:
        path = Path(database_path)
        if not path.is_file():
            raise FileNotFoundError(f'Stock statistics database does not exist: {path}')
        clauses, params = ['performance.max_return_t5_pct IS NOT NULL'], {'target_return_pct': target_return_pct}
        if start_date:
            clauses.append('performance.trade_date >= :start_date')
            params['start_date'] = start_date
        if end_date:
            clauses.append('performance.trade_date <= :end_date')
            params['end_date'] = end_date
        where_sql = ' AND '.join(clauses)
        uri = f'file:{path.resolve().as_posix()}?mode=ro'
        with sqlite3.connect(uri, uri=True) as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(f'''SELECT performance.trade_date, performance.signal_slot,
                CASE WHEN performance.main_net_ratio < 0.05 THEN '0-5%' WHEN performance.main_net_ratio < 0.15 THEN '5-15%' ELSE '15%+' END AS strength_band,
                SUM(CASE WHEN performance.max_return_t5_pct >= :target_return_pct THEN 1 ELSE 0 END) AS success_count,
                SUM(CASE WHEN performance.max_return_t5_pct < :target_return_pct THEN 1 ELSE 0 END) AS failure_count,
                COUNT(*) AS sample_count, 0 AS limit_up_excluded_count
                FROM t_stock_dde_signal_performance AS performance
                WHERE {where_sql}
                GROUP BY performance.trade_date, performance.signal_slot, strength_band
                ORDER BY performance.trade_date, CASE performance.signal_slot WHEN 'morning' THEN 1 WHEN 'noon' THEN 2 WHEN 'close' THEN 3 ELSE 4 END, strength_band''', params).fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def get_hot_rank_page(
        database_path: str, page_num: int, page_size: int, large_cap: bool | None, high_price: bool | None,
        sort_by: str | None, sort_order: str | None,
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
            order_by = StockDdeDao.get_order_by(sort_by, sort_order, {
                'rankNo': 'rank_no', 'appearanceCount': 'appearance_count', 'signalDayCount': 'signal_day_count',
                'recent5Count': 'recent_5_count', 'latestSignalDate': 'latest_signal_date', 'bestRank': 'best_rank',
                'averageRank': 'average_rank', 'limitUpCount': 'limit_up_count', 'tradableSignalCount': 'tradable_signal_count',
                'tradableSampleDayCount': 'tradable_sample_day_count', 'completedTradableSampleDayCount': 'completed_tradable_sample_day_count',
                'targetHitCount': 'target_hit_count', 'targetHitRate': 'target_hit_rate', 'latestTailPrice': 'latest_tail_price',
                'latestTailMarketCap': 'latest_tail_market_cap',
            }, 'rank_no ASC')
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
                    ORDER BY {order_by} LIMIT :limit OFFSET :offset''',
                params,
            ).fetchall()
        return [dict(row) for row in rows], total, stat_range['stat_start_date'], stat_range['stat_end_date']

    @classmethod
    def get_observation_page(
        cls, database_path: str, dimension: str, start_date: str | None, end_date: str | None, page_num: int, page_size: int,
        sort_by: str | None, sort_order: str | None,
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
        order_by = cls.get_order_by(sort_by, sort_order, {
            'tradeDate': 'observation.trade_date', 'signalCount': 'observation.signal_count', 'bestRank': 'observation.best_rank',
            'entryPrice': 'observation.entry_price', 'marketCap': 'observation.market_cap', 'changePct': 'observation.change_pct',
        }, 'observation.trade_date DESC, observation.best_rank ASC, observation.stock_code ASC')
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
            has_fund_flow = connection.execute(
                "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 't_stock_dde_fund_flow'"
            ).fetchone()
            slot_columns = (
                "morning.change_pct AS morning_change_pct, noon.change_pct AS noon_change_pct, close.change_pct AS close_change_pct"
                if has_fund_flow
                else 'NULL AS morning_change_pct, NULL AS noon_change_pct, NULL AS close_change_pct'
            )
            slot_joins = (
                f'''LEFT JOIN t_stock_dde_fund_flow AS morning ON morning.stock_code = observation.stock_code AND morning.trade_date = observation.trade_date AND morning.snapshot_slot = 'morning'
                    LEFT JOIN t_stock_dde_fund_flow AS noon ON noon.stock_code = observation.stock_code AND noon.trade_date = observation.trade_date AND noon.snapshot_slot = 'noon'
                    LEFT JOIN t_stock_dde_fund_flow AS close ON close.stock_code = observation.stock_code AND close.trade_date = observation.trade_date AND close.snapshot_slot = 'close' '''
                if has_fund_flow
                else ''
            )
            rows = connection.execute(
                f'''SELECT observation.trade_date, observation.stock_code, observation.stock_name, observation.morning_count, observation.noon_count, observation.close_count,
                           observation.signal_count, observation.best_rank, observation.combo_type, observation.entry_price, observation.market_cap, observation.change_pct,
                           observation.is_limit_up, observation.is_tradable, observation.is_completed, observation.target_hit, {slot_columns}
                    FROM {table_name} AS observation {slot_joins} WHERE {where_sql.replace('trade_date', 'observation.trade_date')}
                    ORDER BY {order_by} LIMIT :limit OFFSET :offset''',
                params,
            ).fetchall()
        result_rows = []
        for row in rows:
            result = dict(row)
            result['limit_up_slots'] = cls.get_limit_up_slots(
                str(row['stock_name'] or ''), row['morning_change_pct'], row['noon_change_pct'], row['close_change_pct']
            )
            result_rows.append(result)
        return result_rows, int(summary['total']), dict(summary)
