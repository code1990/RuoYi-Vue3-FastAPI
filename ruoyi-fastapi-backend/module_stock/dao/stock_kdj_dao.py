import json
import os
import sqlite3
from pathlib import Path


class StockKdjDao:
    @staticmethod
    def get_history(database_path: str, stock_code: str, limit: int, year: int | None = None) -> tuple[list[dict], list[dict]]:
        path = Path(database_path)
        if not path.is_file():
            raise FileNotFoundError(f'Stock statistics database does not exist: {path}')
        database_uri = f'file:{path.resolve().as_posix()}?mode=ro'
        with sqlite3.connect(database_uri, uri=True) as connection:
            connection.row_factory = sqlite3.Row
            if not connection.execute(
                "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 't_stock_daily_240'"
            ).fetchone():
                return [], []
            raw_code = str(stock_code).split('.', 1)[0].zfill(6)
            params = {'stock_code': stock_code, 'stock_raw': raw_code, 'limit': limit}
            date_clause = ''
            if year is not None:
                params.update(year_start=year * 10000 + 101, year_end=year * 10000 + 1231)
                date_clause = ' AND trade_date BETWEEN :year_start AND :year_end'
            candles = connection.execute(
                f'''
                WITH dates AS (
                    SELECT trade_date
                    FROM t_stock_daily_240
                    WHERE (stock_code = :stock_code OR substr(stock_code, 1, 6) = :stock_raw){date_clause}
                    ORDER BY trade_date DESC
                    LIMIT :limit
                )
                SELECT daily.trade_date, daily.open, daily.high, daily.low, daily.close,
                       daily.vol, daily.amount, daily.vol_rate, daily.percent, daily.changes, daily.pre_close
                FROM t_stock_daily_240 AS daily
                JOIN dates ON dates.trade_date = daily.trade_date
                WHERE (daily.stock_code = :stock_code OR substr(daily.stock_code, 1, 6) = :stock_raw)
                ORDER BY daily.trade_date
                ''',
                params,
            ).fetchall()
            indicators = []
            if connection.execute(
                "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 't_stock_kdj_daily'"
            ).fetchone():
                kdj_columns = {row[1] for row in connection.execute('PRAGMA table_info(t_stock_kdj_daily)')}
                trend_column = 'kdj.j_trend' if 'j_trend' in kdj_columns else "'flat'"
                indicators = connection.execute(
                    f'''
                    WITH dates AS (
                        SELECT trade_date
                        FROM t_stock_daily_240
                        WHERE (stock_code = :stock_code OR substr(stock_code, 1, 6) = :stock_raw){date_clause}
                        ORDER BY trade_date DESC
                        LIMIT :limit
                    )
                    SELECT kdj.trade_date, kdj.period, kdj.rsv, kdj.k, kdj.d, kdj.j, {trend_column} AS j_trend,
                           kdj.rsv_cross_k, kdj.rsv_cross_d, kdj.golden_cross
                    FROM t_stock_kdj_daily AS kdj
                    JOIN dates ON dates.trade_date = kdj.trade_date
                    WHERE (kdj.stock_code = :stock_code OR substr(kdj.stock_code, 1, 6) = :stock_raw) AND kdj.period IN (9, 90)
                    ORDER BY kdj.trade_date, kdj.period
                    ''',
                    params,
                ).fetchall()
        return [dict(row) for row in candles], [dict(row) for row in indicators]

    @staticmethod
    def get_backtest_page(
        database_path: str,
        stock_code: str | None,
        year: int | None,
        signal_status: str,
        page_num: int,
        page_size: int,
        sort_by: str | None = None,
        sort_order: str | None = None,
    ) -> tuple[list[dict], int, dict[str, object]]:
        path = Path(database_path)
        if not path.is_file():
            raise FileNotFoundError(f'Stock statistics database does not exist: {path}')
        artifact_root = Path(os.getenv('KDJ_AUDIT_DIR', '/root/data/disk/kdj_audit')) / 'latest'
        artifact = artifact_root / 'signals.jsonl'
        candidates = []
        candidate_file = artifact_root / 'candidates.json'
        if candidate_file.is_file():
            try:
                candidates = json.loads(candidate_file.read_text(encoding='utf-8'))
            except (OSError, ValueError):
                candidates = []
        if not artifact.is_file():
            return [], 0, {'candidate_count': 0, 'completed_count': 0, 'hit_count': 0, 'hit_rate': None, 'candidates': candidates}
        rows = []
        for line in artifact.read_text(encoding='utf-8').splitlines():
            if line.strip():
                try:
                    rows.append(json.loads(line))
                except ValueError:
                    continue
        raw_code = str(stock_code).split('.', 1)[0].zfill(6) if stock_code else None
        if raw_code:
            rows = [row for row in rows if str(row.get('stock_code', '')).split('.', 1)[0].zfill(6) == raw_code]
        if year is not None:
            rows = [row for row in rows if int(row.get('year', 0)) == year]
        if signal_status == 'candidate':
            rows = [row for row in rows if row.get('is_candidate')]
        elif signal_status == 'hit':
            rows = [row for row in rows if row.get('is_completed') and row.get('target_hit') == 1]
        elif signal_status == 'fail':
            rows = [row for row in rows if row.get('is_completed') and row.get('target_hit') == 0]
        elif signal_status == 'pending':
            rows = [row for row in rows if not row.get('is_completed')]

        with sqlite3.connect(f'file:{path.resolve().as_posix()}?mode=ro', uri=True) as connection:
            pool_columns = {row[1] for row in connection.execute('PRAGMA table_info(t_stock_pool)')} if connection.execute(
                "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 't_stock_pool'"
            ).fetchone() else set()
            if {'stock_code', 'stock_name', 'full_industry', 'full_concept'} <= pool_columns:
                names = {
                    str(row[0]).split('.', 1)[0].zfill(6): (row[1] or '', row[2] or '', row[3] or '')
                    for row in connection.execute('SELECT stock_code, stock_name, full_industry, full_concept FROM t_stock_pool')
                }
            else:
                names = {}
        for row in rows:
            name, industry, concept = names.get(str(row.get('stock_code', '')).split('.', 1)[0].zfill(6), ('', '', ''))
            row.update(stock_name=name, industry_name=industry, concept=concept)
        sortable = {
            'signalDate': 'signal_date', 'signalCount': 'signal_count', 'maxReturnPct': 'max_return_pct',
            'targetHit': 'target_hit', **{f't{day}MaxReturnPct': f't{day}_max_return_pct' for day in range(1, 6)},
            **{f't{day}CloseReturnPct': f't{day}_close_return_pct' for day in range(1, 6)},
        }
        field = sortable.get(sort_by or '', 'signal_date')
        rows.sort(key=lambda row: (row.get(field) is None, row.get(field), row.get('stock_code', '')), reverse=sort_order != 'ascending')
        total = len(rows)
        offset = (page_num - 1) * page_size
        page_rows = rows[offset:offset + page_size]
        completed_count = sum(bool(row.get('is_completed')) for row in rows)
        hit_count = sum(row.get('target_hit') == 1 for row in rows if row.get('is_completed'))
        return page_rows, total, {
            'candidate_count': sum(bool(row.get('is_candidate')) for row in rows),
            'completed_count': completed_count, 'hit_count': hit_count,
            'hit_rate': hit_count / completed_count if completed_count else None,
            'candidates': candidates,
        }
