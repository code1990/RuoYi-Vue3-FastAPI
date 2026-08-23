import json
import sqlite3
from pathlib import Path


class StockAlgorithmDao:
    @staticmethod
    def get_experiments(database_path: str, source_type: str, experiment_key: str | None = None, status: str | None = None) -> list[dict]:
        path = Path(database_path)
        if not path.is_file():
            raise FileNotFoundError(f'Stock statistics database does not exist: {path}')
        with sqlite3.connect(f'file:{path.resolve().as_posix()}?mode=ro', uri=True) as connection:
            connection.row_factory = sqlite3.Row
            exists = connection.execute("SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 't_stock_algorithm_experiment'").fetchone()
            if not exists:
                return []
            clauses = ['source_type = ?']
            params = [source_type]
            if experiment_key:
                clauses.append('experiment_key = ?')
                params.append(experiment_key)
            if status:
                clauses.append('status = ?')
                params.append(status)
            rows = connection.execute(
                '''SELECT experiment_key, data_start_date, data_end_date, target_rule, feature_rules, tree_json,
                          train_metrics, validation_metrics, status, conclusion
                   FROM t_stock_algorithm_experiment WHERE ''' + ' AND '.join(clauses), params
            ).fetchall()
        results = []
        for row in rows:
            result = dict(row)
            result['tree'] = json.loads(result.pop('tree_json'))
            for name in ('feature_rules', 'train_metrics', 'validation_metrics'):
                result[name] = json.loads(result[name])
            results.append(result)
        return sorted(results, key=lambda row: (
            row['status'] != 'observing',
            -(row['validation_metrics']['root']['hit_rate'] or 0),
            -row['validation_metrics']['root']['sample_count'],
            row['experiment_key'],
        ))
