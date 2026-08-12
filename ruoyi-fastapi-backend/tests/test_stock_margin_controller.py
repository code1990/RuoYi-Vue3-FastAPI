import asyncio
import json
import sqlite3

from config.env import AppConfig
from module_stock.controller.stock_margin_controller import get_stock_margin_long_performance_list


def test_margin_long_performance_list_paginates_sqlite_result_table(tmp_path, monkeypatch):
    database_path = tmp_path / 'stock_stat.db'
    with sqlite3.connect(database_path) as connection:
        connection.execute('''CREATE TABLE t_stock_margin_long_performance (stock_code TEXT NOT NULL, margin_trade_date TEXT NOT NULL, signal_date TEXT NOT NULL, stock_name TEXT NOT NULL, rank_no INTEGER NOT NULL, score REAL NOT NULL, participation_ratio REAL NOT NULL, balance_change_ratio REAL NOT NULL, entry_price REAL NOT NULL, industry_name TEXT NOT NULL, close_return_pct REAL, t1_max_return_pct REAL, t2_max_return_pct REAL, t3_max_return_pct REAL, t4_max_return_pct REAL, t5_max_return_pct REAL, PRIMARY KEY (margin_trade_date, rank_no))''')
        connection.execute("""INSERT INTO t_stock_margin_long_performance VALUES ('600001','20260805','20260806','示例甲',2,80,0.1,0.2,10,'电子',1,2,3,4,5,6), ('600002','20260805','20260806','示例乙',1,95,0.2,0.3,8,'银行',1,2,3,4,5,6), ('600003','20260804','20260805','示例丙',1,50,0.1,0.1,9,'医药',1,2,3,4,5,6)""")
    monkeypatch.setattr(AppConfig, 'stock_stat_db_path', str(database_path))

    response = asyncio.run(get_stock_margin_long_performance_list(start_date='20260806', end_date='20260806', page_num=1, page_size=1))
    payload = json.loads(response.body)

    assert payload['data']['total'] == 2
    assert payload['data']['hasNext'] is True
    assert payload['data']['rows'][0]['stockCode'] == '600002'
    assert payload['data']['rows'][0]['t5MaxReturnPct'] == 6.0
