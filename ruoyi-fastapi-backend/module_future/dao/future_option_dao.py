import sqlite3
from pathlib import Path


class FutureOptionDao:
    @staticmethod
    def get_io_contracts(database_path: str, page_num: int, page_size: int) -> tuple[list[dict], int]:
        path = Path(database_path)
        if not path.is_file():
            raise FileNotFoundError(f'Future statistics database does not exist: {path}')
        with sqlite3.connect(f'file:{path.resolve().as_posix()}?mode=ro', uri=True) as connection:
            total = connection.execute("SELECT COUNT(*) FROM t_option_contract WHERE variety_code='IO'").fetchone()[0]
            rows = connection.execute(
                "SELECT thscode, ticker, name, list_date, last_trade_date FROM t_option_contract WHERE variety_code='IO' "
                "ORDER BY last_trade_date, thscode LIMIT ? OFFSET ?", (page_size, (page_num - 1) * page_size),
            ).fetchall()
        return [dict(zip(('thscode', 'ticker', 'name', 'list_date', 'last_trade_date'), row)) for row in rows], total
