import sqlite3
from pathlib import Path


class StockSignalAnalysisDao:
    TABLES = {'raw': 't_stock_stat_info', 'filtered': 't_stock_stat_info_2', 'total': 't_stock_stat_total'}

    @classmethod
    def get_page(cls, database_path: str, table_key: str, signal_name: str | None, stock_code: str | None,
                 year: int | None, page_num: int, page_size: int) -> tuple[list[dict], int, list[str]]:
        table_name = cls.TABLES[table_key]
        path = Path(database_path)
        if not path.is_file():
            raise FileNotFoundError(f'Stock statistics database does not exist: {path}')
        with sqlite3.connect(f'file:{path.resolve().as_posix()}?mode=ro', uri=True) as connection:
            connection.row_factory = sqlite3.Row
            if not connection.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table_name,)).fetchone():
                return [], 0, []
            params: dict[str, object] = {}
            where = []
            if signal_name:
                where.append('stat.signal_name = :signal_name'); params['signal_name'] = signal_name
            if stock_code:
                where.append('substr(stat.stock_code, 1, 6) = :stock_code'); params['stock_code'] = stock_code.split('.', 1)[0].zfill(6)
            if year is not None and table_key != 'total':
                where.append('stat.stat_year = :year'); params['year'] = year
            condition = f"WHERE {' AND '.join(where)}" if where else ''
            pool_exists = connection.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='t_stock_pool'").fetchone()
            columns = {row[1] for row in connection.execute('PRAGMA table_info(t_stock_pool)')} if pool_exists else set()
            pool_code = 'pool.stock_code' if 'stock_code' in columns else "''"
            pool_name = 'pool.stock_name' if 'stock_name' in columns else "''"
            if {'full_industry', 'industry_1'} <= columns:
                pool_industry = "COALESCE(pool.full_industry, pool.industry_1, '')"
            elif 'full_industry' in columns:
                pool_industry = 'pool.full_industry'
            elif 'industry_1' in columns:
                pool_industry = 'pool.industry_1'
            else:
                pool_industry = "''"
            pool_concept = 'pool.full_concept' if 'full_concept' in columns else "''"
            if table_key == 'total':
                fields = 'NULL AS stat_year, NULL AS sample_count, NULL AS win_count_1, NULL AS win_count_2, NULL AS win_rate_1, NULL AS win_rate_2, stat.sample_count_1, stat.sample_count_2'
                order = 'stat.win_rate_2 DESC, stat.sample_count_2 DESC, stat.stock_code'
            else:
                fields = 'stat.stat_year, stat.sample_count, stat.win_count_1, stat.win_count_2, stat.win_rate_1, stat.win_rate_2, NULL AS sample_count_1, NULL AS sample_count_2'
                order = 'stat.stat_year DESC, stat.win_rate_1 DESC, stat.stock_code'
            join = f'LEFT JOIN t_stock_pool AS pool ON substr({pool_code}, 1, 6) = substr(stat.stock_code, 1, 6)' if columns else ''
            base = f'FROM {table_name} AS stat {join} {condition}'
            total = connection.execute(f'SELECT COUNT(*) {base}', params).fetchone()[0]
            rows = connection.execute(f'''SELECT stat.signal_name, stat.stock_code, {pool_name} AS stock_name,
                {pool_industry} AS industry_name, {pool_concept} AS concept, {fields} {base}
                ORDER BY {order} LIMIT :limit OFFSET :offset''', {**params, 'limit': page_size, 'offset': (page_num - 1) * page_size}).fetchall()
            names = [row[0] for row in connection.execute(f'SELECT DISTINCT signal_name FROM {table_name} ORDER BY signal_name')]
            return [dict(row) for row in rows], int(total), names
