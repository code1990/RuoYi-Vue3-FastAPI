import asyncio
import json
import sqlite3

from config.env import AppConfig
from module_stock.controller.stock_main_fund_controller import get_stock_main_fund_performance_list


def test_main_fund_performance_list_paginates_sqlite_result_table(tmp_path, monkeypatch):
    database_path = tmp_path / 'stock_stat.db'
    with sqlite3.connect(database_path) as connection:
        connection.execute('''CREATE TABLE t_stock_55d_fund_performance (stock_code TEXT NOT NULL, signal_date TEXT NOT NULL, strategy TEXT NOT NULL, signal_type TEXT NOT NULL, stock_name TEXT NOT NULL, industry_name TEXT NOT NULL, entry_price REAL NOT NULL, signal_score REAL, strength_10d REAL, strength_55d REAL, flow_5d REAL, flow_10d REAL, flow_20d REAL, flow_55d REAL, consecutive_inflow_days INTEGER, close_return_pct REAL, t1_max_return_pct REAL, t2_max_return_pct REAL, t3_max_return_pct REAL, t4_max_return_pct REAL, t5_max_return_pct REAL, PRIMARY KEY (stock_code, signal_date, strategy, signal_type))''')
        connection.execute("""INSERT INTO t_stock_55d_fund_performance VALUES ('600001','20260806','55日主连','inflow','示例甲','电子',10,88,1,2,3,4,5,6,7,1,2,3,4,5,6), ('600002','20260806','55日主连','inflow','示例乙','银行',8,99,1,2,3,4,5,6,3,1,2,3,4,5,6), ('600003','20260805','55日主连','inflow','示例丙','医药',9,50,1,2,3,4,5,6,2,1,2,3,4,5,6)""")
    monkeypatch.setattr(AppConfig, 'stock_stat_db_path', str(database_path))

    response = asyncio.run(get_stock_main_fund_performance_list(start_date='20260806', end_date='20260806', page_num=1, page_size=1))
    payload = json.loads(response.body)

    assert payload['data']['total'] == 2
    assert payload['data']['hasNext'] is True
    assert payload['data']['rows'][0]['stockCode'] == '600002'
    assert payload['data']['rows'][0]['t5MaxReturnPct'] == 6.0

    response = asyncio.run(get_stock_main_fund_performance_list(stock_code='600001', page_num=1, page_size=20))
    payload = json.loads(response.body)
    assert payload['data']['total'] == 1
    assert payload['data']['rows'][0]['stockCode'] == '600001'
