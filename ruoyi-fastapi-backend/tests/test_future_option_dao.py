import sqlite3
import tempfile
import unittest
from pathlib import Path

from module_future.dao.future_option_dao import FutureOptionDao


class FutureOptionDaoTest(unittest.TestCase):
    def test_lists_all_varieties(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'option.db'
            with sqlite3.connect(path) as connection:
                connection.execute('CREATE TABLE t_option_base (variety_code TEXT, name TEXT, exchange_code TEXT, exchange_name TEXT, settlement_type TEXT, contract_multiplier REAL)')
                connection.executemany('INSERT INTO t_option_base VALUES (?, ?, ?, ?, ?, ?)', [('IO', '沪深300', 'CFFEX', '中金所', 'cash', 100), ('i', '铁矿石', 'DCE', '大商所', 'physical', 100)])
            rows, total = FutureOptionDao.get_varieties(str(path), 1, 100)
            self.assertEqual((2, 'i'), (total, rows[1]['variety_code']))

    def test_lists_contract_summaries(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'option.db'
            with sqlite3.connect(path) as connection:
                connection.execute('CREATE TABLE t_option_contract (thscode TEXT, ticker TEXT, name TEXT, variety_code TEXT, exchange_code TEXT, list_date TEXT, last_trade_date TEXT)')
                connection.executemany('INSERT INTO t_option_contract VALUES (?, ?, ?, ?, ?, ?, ?)', [
                    ('IO2601-C-4000.CFE', 'IO2601-C-4000', '沪深300', 'IO', 'CFFEX', '2026-01-01', '2026-01-16'),
                    ('10011425.SH', '510050', '50ETF', '510050O', 'SSE', '2026-01-01', '2026-01-16'),
                ])
            rows, total = FutureOptionDao.get_contract_summaries(str(path), 1, 100)
            self.assertEqual((2, 'SSE/510050O'), (total, rows[1]['code']))
