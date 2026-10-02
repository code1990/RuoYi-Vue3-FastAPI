import sqlite3
import tempfile
import unittest
from pathlib import Path

from module_future.dao.future_option_dao import FutureOptionDao


class FutureOptionDaoTest(unittest.TestCase):
    def test_lists_only_io_contracts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'option.db'
            with sqlite3.connect(path) as connection:
                connection.execute('CREATE TABLE t_option_contract (thscode TEXT, ticker TEXT, name TEXT, variety_code TEXT, list_date TEXT, last_trade_date TEXT)')
                connection.executemany('INSERT INTO t_option_contract VALUES (?, ?, ?, ?, ?, ?)', [
                    ('IO2601-C-4000.CFE', 'IO2601-C-4000', '沪深300', 'IO', '2026-01-01', '2026-01-16'),
                    ('10011425.SH', '510050', '50ETF', '510050O', '2026-01-01', '2026-01-16'),
                ])
            rows, total = FutureOptionDao.get_io_contracts(str(path), 1, 100)
            self.assertEqual((1, 'IO2601-C-4000.CFE'), (total, rows[0]['thscode']))
