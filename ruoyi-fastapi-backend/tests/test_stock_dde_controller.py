import json
import sqlite3
import asyncio

import pytest

from config.env import AppConfig
from module_stock.controller.stock_dde_controller import get_stock_dde_combo_list, get_stock_dde_signal_performance_list, get_stock_dde_top30_performance_list


@pytest.fixture
def stock_database(tmp_path):
    database_path = tmp_path / 'stock_stat.db'
    with sqlite3.connect(database_path) as connection:
        connection.execute('''CREATE TABLE t_stock_dde_signal_performance (stock_code TEXT NOT NULL, trade_date TEXT NOT NULL, stock_name TEXT NOT NULL, signal_slot TEXT NOT NULL, signal_rank_no INTEGER, entry_price REAL NOT NULL, signal_change_pct REAL, large_net_amount REAL, market_cap REAL, main_net_ratio REAL, industry_name TEXT NOT NULL, close_return_pct REAL, t1_max_return_pct REAL, t2_max_return_pct REAL, t3_max_return_pct REAL, t4_max_return_pct REAL, t5_max_return_pct REAL, PRIMARY KEY (stock_code, trade_date))''')
        connection.execute("""INSERT INTO t_stock_dde_signal_performance VALUES ('000001','20260806','平安银行','noon',2,10,1.2,100000000,2000000000,0.05,'银行',2,3,4,5,6,7), ('603459','20260806','红板科技','morning',1,105.58,9.5,1310000000,6800000000,0.1941,'电子',1,2,3,4,5,6), ('600000','20260805','浦发银行','close',1,8,-0.2,20000000,1000000000,0.01,'银行',NULL,NULL,NULL,NULL,NULL,NULL)""")
        connection.execute('''CREATE TABLE t_stock_dde_combo_signal (signal_date TEXT, previous_signal_date TEXT, stock_code TEXT, stock_name TEXT, previous_signal_count INTEGER, today_signal_count INTEGER, today_morning_count INTEGER, today_noon_count INTEGER, today_close_count INTEGER, today_best_rank INTEGER, today_main_net_ratio REAL, previous_main_net_ratio REAL, entry_price REAL, current_price REAL, combo_rank INTEGER, close_return_pct REAL, t1_max_return_pct REAL, t2_max_return_pct REAL, t3_max_return_pct REAL, t4_max_return_pct REAL, t5_max_return_pct REAL)''')
        connection.execute("INSERT INTO t_stock_dde_combo_signal VALUES ('20260807','20260806','000001','平安银行',1,2,1,1,0,3,.02,.01,10.5,11,1,1,2,3,4,5,6)")
        connection.execute('''CREATE TABLE t_stock_dde_30_signal_performance (stock_code TEXT, trade_date TEXT, stock_name TEXT, signal_slot TEXT, signal_rank_no INTEGER, raw_rank_no INTEGER, entry_price REAL, signal_change_pct REAL, main_net_amount REAL, market_cap REAL, main_net_ratio REAL, industry_name TEXT, close_return_pct REAL, t1_max_return_pct REAL, t2_max_return_pct REAL, t3_max_return_pct REAL, t4_max_return_pct REAL, t5_max_return_pct REAL)''')
        connection.execute("INSERT INTO t_stock_dde_30_signal_performance VALUES ('000001','20260806','平安银行','morning',1,3,10,1,20000000,2000000000,.01,'银行',.2,3,4,5,6,7)")
    return database_path


def test_dde_performance_list_reads_sqlite_result_table(stock_database, monkeypatch):
    monkeypatch.setattr(AppConfig, 'stock_stat_db_path', str(stock_database))
    response = asyncio.run(
        get_stock_dde_signal_performance_list(start_date='20260806', end_date='20260806', page_num=1, page_size=20)
    )
    payload = json.loads(response.body)
    assert payload['data']['total'] == 2
    assert [row['stockCode'] for row in payload['data']['rows']] == ['000001', '603459']
    assert payload['data']['rows'][0]['tradeDate'] == '20260806'
    assert payload['data']['rows'][0]['signalSlot'] == 'noon'
    assert payload['data']['rows'][0]['t5MaxReturnPct'] == 7.0


def test_dde_combo_list_reads_yesterday_today_candidates(stock_database, monkeypatch):
    monkeypatch.setattr(AppConfig, 'stock_stat_db_path', str(stock_database))
    payload = json.loads(asyncio.run(get_stock_dde_combo_list(page_num=1, page_size=20)).body)
    assert payload['data']['total'] == 1
    assert payload['data']['rows'][0]['previousSignalDate'] == '20260806'
    assert payload['data']['rows'][0]['todaySignalCount'] == 2
    assert payload['data']['rows'][0]['currentPrice'] == 11.0
    assert payload['data']['rows'][0]['t5MaxReturnPct'] == 6.0


def test_dde_top30_list_reads_observation_performance(stock_database, monkeypatch):
    monkeypatch.setattr(AppConfig, 'stock_stat_db_path', str(stock_database))
    payload = json.loads(asyncio.run(get_stock_dde_top30_performance_list(page_num=1, page_size=20)).body)
    assert payload['data']['total'] == 1
    assert payload['data']['rows'][0]['rawRankNo'] == 3
    assert payload['data']['rows'][0]['t5MaxReturnPct'] == 7.0
