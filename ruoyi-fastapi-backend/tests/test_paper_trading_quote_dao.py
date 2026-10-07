import json
import sqlite3
from pathlib import Path

from module_future.dao.future_quote_dao import FutureQuoteDao


def test_get_contract_uses_server_quote(tmp_path: Path) -> None:
    database = tmp_path / 'future.db'
    with sqlite3.connect(database) as connection:
        connection.executescript('''
            CREATE TABLE t_future_quote (contract_code TEXT, last_px REAL, payload_json TEXT, market_code TEXT, product_code TEXT);
            CREATE TABLE t_future_product (market_code TEXT, product_code TEXT, product_name TEXT);
        ''')
        connection.execute('INSERT INTO t_future_product VALUES (?, ?, ?)', ('XSGE', 'RB', '螺纹钢'))
        connection.execute('INSERT INTO t_future_quote VALUES (?, ?, ?, ?, ?)', ('RB2601', 3210, json.dumps({'prod_name': '螺纹钢主力', 'contract_unit': 10}), 'XSGE', 'RB'))

    assert FutureQuoteDao.get_contract(str(database), 'RB2601') == {
        'contract_code': 'RB2601', 'market_code': 'XSGE', 'contract_name': '螺纹钢主力', 'price': 3210.0, 'multiplier': 10.0,
    }
