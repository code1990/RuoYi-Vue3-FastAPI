import sqlite3
import tempfile
import unittest
from pathlib import Path

from module_future.dao.future_quote_dao import FutureQuoteDao


class FutureQuoteDaoTest(unittest.TestCase):
    def test_filters_scope_and_reads_quote_fields(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'future.db'
            with sqlite3.connect(path) as connection:
                connection.executescript('CREATE TABLE t_future_quote (contract_code TEXT, market_code TEXT, product_code TEXT, market_date TEXT, last_px TEXT, px_change TEXT, px_change_rate TEXT, open_px TEXT, high_px TEXT, low_px TEXT, prev_settlement TEXT, payload_json TEXT); CREATE TABLE t_future_product (market_code TEXT, product_code TEXT, market_name TEXT, product_name TEXT);')
                connection.execute("INSERT INTO t_future_quote VALUES ('RU888.XSGE','XSGE','FC.RU','20261001','20000','100','1.2','19900','20100','19800','19900','{\"prod_name\":\"橡胶主力\",\"min5_chgpct\":0.2}')")
                connection.execute("INSERT INTO t_future_quote VALUES ('RU2610.XSGE','XSGE','FC.RU','20261001','20100','200','2','20000','20200','19900','19900','{\"prod_name\":\"橡胶2610\",\"current_amount\":999}')")
                connection.execute("INSERT INTO t_future_quote VALUES ('CU888.XSGE','XSGE','FC.CU','20261001','1','1','1','0','1','1','1','{}')")
                connection.execute("INSERT INTO t_future_quote VALUES ('NG001.NYMEX','NYMEX','FC.NG','20261001','3','-0.1','-2','3.1','3.2','2.9','3.1','{}')")
                connection.execute("INSERT INTO t_future_product VALUES ('XSGE','FC.RU','上海期货交易所','橡胶')")
            rows, total = FutureQuoteDao.get_page(str(path), 'domestic', None, 1, 50)
            self.assertEqual((total, rows[0]['contract_code'], rows[0]['contract_name'], rows[0]['min5_chgpct']), (1, 'RU888.XSGE', '橡胶主力', 0.2))

    def test_calculates_opening_profit_effect_and_stock_comparison(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'future.db'
            with sqlite3.connect(path) as connection:
                connection.executescript('CREATE TABLE t_future_quote (contract_code TEXT, market_code TEXT, product_code TEXT, market_date TEXT, last_px TEXT, px_change TEXT, px_change_rate TEXT, open_px TEXT, high_px TEXT, low_px TEXT, prev_settlement TEXT, payload_json TEXT); CREATE TABLE t_future_product (market_code TEXT, product_code TEXT, market_name TEXT, product_name TEXT);')
                connection.execute("INSERT INTO t_future_quote VALUES ('C888.XDCE','XDCE','FC.CORN','20261002','2277','-23','-1','2300','2325','2275','2300','{\"prod_name\":\"玉米主力\"}')")
                connection.execute("INSERT INTO t_future_product VALUES ('XDCE','FC.CORN','大连商品交易所','玉米')")
            row = FutureQuoteDao.get_profit_effect(str(path))[0]
            self.assertEqual(('做空', row['net_profit'], row['margin'], row['fee']), ('做空', 227.6, 2300.0, 2.4))
            self.assertAlmostEqual(row['stock_same_move_profit'], -23.024)


if __name__ == '__main__':
    unittest.main()
