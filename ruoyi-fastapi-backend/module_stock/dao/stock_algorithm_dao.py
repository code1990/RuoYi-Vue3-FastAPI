import json
import sqlite3
from pathlib import Path


class StockAlgorithmDao:
    @staticmethod
    def get_latest_experiment(database_path: str, source_type: str) -> dict | None:
        path = Path(database_path)
        if not path.is_file():
            raise FileNotFoundError(f'Stock statistics database does not exist: {path}')
        with sqlite3.connect(f'file:{path.resolve().as_posix()}?mode=ro', uri=True) as connection:
            connection.row_factory = sqlite3.Row
            exists = connection.execute("SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 't_stock_algorithm_experiment'").fetchone()
            if not exists:
                return None
            row = connection.execute(
                '''SELECT experiment_key, data_start_date, data_end_date, target_rule, feature_rules, tree_json,
                          train_metrics, validation_metrics, status, conclusion
                   FROM t_stock_algorithm_experiment WHERE source_type = ? ORDER BY experiment_key DESC LIMIT 1''',
                (source_type,),
            ).fetchone()
        if not row:
            return None
        result = dict(row)
        result['tree'] = json.loads(result.pop('tree_json'))
        for name in ('feature_rules', 'train_metrics', 'validation_metrics'):
            result[name] = json.loads(result[name])
        return result
