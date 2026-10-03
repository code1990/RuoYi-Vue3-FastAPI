import sqlite3
import tempfile
import unittest
from pathlib import Path

from module_future.dao.future_history_dao import FutureHistoryDao


class FutureHistoryDaoTest(unittest.TestCase):
    def test_reads_series_and_daily_bars(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'future.db'
            with sqlite3.connect(path) as connection:
                connection.execute('CREATE TABLE t_future_series(thscode TEXT,product_code TEXT,exchange_code TEXT,series_type TEXT,series_name TEXT)')
                connection.execute('CREATE TABLE t_future_daily_bar(thscode TEXT,trade_date TEXT,open_price REAL,high_price REAL,low_price REAL,close_price REAL,volume REAL,turnover REAL)')
                connection.execute("INSERT INTO t_future_series VALUES('AZL.DCE','A','DCE','main','豆一主连')")
                connection.execute("INSERT INTO t_future_daily_bar VALUES('AZL.DCE','20260102',1,2,0.5,1.5,10,15)")
            self.assertEqual('AZL.DCE', FutureHistoryDao.get_series(str(path))[0]['thscode'])
            self.assertEqual(1.5, FutureHistoryDao.get_daily(str(path), 'AZL.DCE')[0]['close_price'])
