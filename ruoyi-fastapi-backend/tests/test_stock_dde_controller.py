import asyncio
import json
import sqlite3

import pytest

from config.env import AppConfig
from module_stock.dao.stock_dde_dao import StockDdeDao
from module_stock.controller.stock_dde_controller import (
    get_stock_dde_combo_list,
    get_stock_dde_combo_statistics,
    get_stock_dde_hot_rank_list,
    get_stock_dde_observation_list,
    get_stock_dde_observation_statistics,
    get_stock_dde_intraday_combo_statistics,
    get_stock_dde_signal_performance_list,
    get_stock_dde_top30_performance_list,
    get_stock_dde_top30_statistics,
)


@pytest.fixture
def stock_database(tmp_path):
    database_path = tmp_path / 'stock_stat.db'
    with sqlite3.connect(database_path) as connection:
        connection.execute('''CREATE TABLE t_stock_dde_signal_performance (stock_code TEXT NOT NULL, trade_date TEXT NOT NULL, stock_name TEXT NOT NULL, signal_slot TEXT NOT NULL, signal_rank_no INTEGER, entry_price REAL NOT NULL, signal_change_pct REAL, large_net_amount REAL, market_cap REAL, main_net_ratio REAL, industry_name TEXT NOT NULL, close_return_pct REAL, t1_max_return_pct REAL, t2_max_return_pct REAL, t3_max_return_pct REAL, t4_max_return_pct REAL, t5_max_return_pct REAL, PRIMARY KEY (stock_code, trade_date))''')
        connection.execute("""INSERT INTO t_stock_dde_signal_performance VALUES ('000001','20260806','平安银行','noon',2,10,1.2,100000000,2000000000,0.05,'银行',2,3,4,5,6,7), ('603459','20260806','红板科技','morning',1,105.58,9.5,1310000000,6800000000,0.1941,'电子',1,2,3,4,5,6), ('600000','20260805','浦发银行','close',1,8,-0.2,20000000,1000000000,0.01,'银行',NULL,NULL,NULL,NULL,NULL,NULL)""")
        connection.execute('''CREATE TABLE t_stock_dde_combo_signal (signal_date TEXT, previous_signal_date TEXT, stock_code TEXT, stock_name TEXT, previous_signal_count INTEGER, today_signal_count INTEGER, today_morning_count INTEGER, today_noon_count INTEGER, today_close_count INTEGER, today_best_rank INTEGER, today_main_net_ratio REAL, previous_main_net_ratio REAL, entry_price REAL, current_price REAL, combo_rank INTEGER, close_return_pct REAL, t1_max_return_pct REAL, t2_max_return_pct REAL, t3_max_return_pct REAL, t4_max_return_pct REAL, t5_max_return_pct REAL)''')
        connection.execute("INSERT INTO t_stock_dde_combo_signal VALUES ('20260807','20260806','000001','平安银行',1,2,1,1,0,3,.02,.01,10.5,11,1,1,2,3,4,5,6)")
        connection.execute('''CREATE TABLE t_stock_dde_30_signal_performance (stock_code TEXT, trade_date TEXT, stock_name TEXT, signal_slot TEXT, signal_rank_no INTEGER, raw_rank_no INTEGER, entry_price REAL, signal_change_pct REAL, main_net_amount REAL, market_cap REAL, main_net_ratio REAL, industry_name TEXT, close_return_pct REAL, t1_max_return_pct REAL, t2_max_return_pct REAL, t3_max_return_pct REAL, t4_max_return_pct REAL, t5_max_return_pct REAL)''')
        connection.executemany("INSERT INTO t_stock_dde_30_signal_performance VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", [
            ('000001','20260806','平安银行','morning',1,3,10,1,20000000,2000000000,.01,'银行',.2,3,4,5,6,7),
            ('000002','20260806','万科A','close',1,2,8,1,10000000,1500000000,.02,'地产',.3,3,4,5,6,7),
        ])
        connection.execute('''CREATE TABLE t_stock_dde_hot_rank (
            stat_start_date TEXT, stat_end_date TEXT, rank_no INTEGER, stock_code TEXT, stock_name TEXT,
            appearance_count INTEGER, signal_day_count INTEGER, morning_count INTEGER, noon_count INTEGER,
            close_count INTEGER, recent_5_count INTEGER, latest_signal_date TEXT, latest_signal_slot TEXT,
            best_rank INTEGER, average_rank REAL, limit_up_count INTEGER, tradable_signal_count INTEGER,
            tradable_sample_day_count INTEGER, completed_tradable_sample_day_count INTEGER,
            target_hit_count INTEGER, target_hit_rate REAL, latest_tail_price REAL,
            latest_tail_market_cap REAL, is_large_cap INTEGER, is_high_price INTEGER,
            is_latest_signal_limit_up INTEGER
        )''')
        connection.executemany(
            "INSERT INTO t_stock_dde_hot_rank VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                ('20260801', '20260818', 1, '000001', '平安银行', 12, 8, 3, 5, 4, 6, '20260818', 'close', 1, 2.5, 1, 11, 7, 5, 3, .6, 11.2, 220000000000, 1, 0, 0),
                ('20260801', '20260818', 2, '000002', '高价股', 8, 5, 2, 3, 3, 4, '20260817', 'noon', 2, 4.0, 0, 8, 5, 4, 2, .5, 88, 20000000000, 0, 1, 0),
            ],
        )
        connection.execute('''CREATE TABLE t_stock_dde_high_price_observation (
            trade_date TEXT, stock_code TEXT, stock_name TEXT, morning_count INTEGER, noon_count INTEGER,
            close_count INTEGER, signal_count INTEGER, best_rank INTEGER, combo_type TEXT, entry_price REAL,
            market_cap REAL, change_pct REAL, is_limit_up INTEGER, is_tradable INTEGER,
            is_completed INTEGER, target_hit INTEGER, close_return_pct REAL, t1_max_return_pct REAL,
            t2_max_return_pct REAL, t3_max_return_pct REAL, t4_max_return_pct REAL, t5_max_return_pct REAL,
            max_return_t5_pct REAL
        )''')
        connection.executemany(
            "INSERT INTO t_stock_dde_high_price_observation VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                ('20260806', '000001', '平安银行', 1, 1, 0, 2, 1, '', 88, 220000000000, 1.2, 0, 1, 1, 1, 1.2, 2, 2, 2, 2, 2, 2),
                ('20260805', '000002', '涨停高价', 0, 0, 1, 1, 2, '', 90, 10000000000, 9.5, 1, 1, 0, None, None, None, None, None, None, None, None),
            ],
        )
        connection.execute('CREATE TABLE t_stock_dde_high_strength_observation AS SELECT * FROM t_stock_dde_high_price_observation WHERE 0')
        connection.execute("INSERT INTO t_stock_dde_high_strength_observation SELECT * FROM t_stock_dde_high_price_observation WHERE stock_code = '000001'")
        connection.execute('CREATE TABLE t_stock_dde_large_cap_observation AS SELECT * FROM t_stock_dde_high_price_observation WHERE 0')
        connection.execute("INSERT INTO t_stock_dde_large_cap_observation SELECT * FROM t_stock_dde_high_price_observation WHERE stock_code = '000001'")
        connection.execute('CREATE TABLE t_stock_dde_intraday_combo_observation AS SELECT * FROM t_stock_dde_high_price_observation WHERE 0')
        connection.execute("INSERT INTO t_stock_dde_intraday_combo_observation SELECT * FROM t_stock_dde_high_price_observation WHERE stock_code = '000001'")
        connection.execute("UPDATE t_stock_dde_intraday_combo_observation SET combo_type = 'morning_noon'")
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


def test_dde_performance_list_includes_newly_captured_signal_without_returns(stock_database, monkeypatch):
    with sqlite3.connect(stock_database) as connection:
        connection.execute('''CREATE TABLE t_stock_dde_signal (
            stock_code TEXT, trade_date TEXT, snapshot_slot TEXT, signal_side TEXT, rank_no INTEGER, stock_name TEXT,
            entry_price REAL, market_cap REAL, turnover_amount REAL, main_net_amount REAL, total_net_amount REAL, main_net_ratio REAL
        )''')
        connection.execute('''CREATE TABLE t_stock_dde_fund_flow (
            stock_code TEXT, trade_date TEXT, snapshot_slot TEXT, change_pct REAL, large_net_amount REAL
        )''')
        connection.execute("INSERT INTO t_stock_dde_signal VALUES ('000001', '20260826', 'close', 'inflow', 1, '平安银行', 12.34, 2000000000, 0, 100000000, 0, .05)")
        connection.execute("INSERT INTO t_stock_dde_fund_flow VALUES ('000001', '20260826', 'close', 1.2, 80000000)")
    monkeypatch.setattr(AppConfig, 'stock_stat_db_path', str(stock_database))
    payload = json.loads(asyncio.run(get_stock_dde_signal_performance_list(start_date='20260826', end_date='20260826', page_num=1, page_size=20)).body)
    assert payload['data']['total'] == 1
    assert payload['data']['rows'][0]['entryPrice'] == 12.34
    assert payload['data']['rows'][0]['t1MaxReturnPct'] is None


def test_dde_combo_list_reads_yesterday_today_candidates(stock_database, monkeypatch):
    monkeypatch.setattr(AppConfig, 'stock_stat_db_path', str(stock_database))
    payload = json.loads(asyncio.run(get_stock_dde_combo_list(page_num=1, page_size=20)).body)
    assert payload['data']['total'] == 1
    assert payload['data']['rows'][0]['previousSignalDate'] == '20260806'
    assert payload['data']['rows'][0]['todaySignalCount'] == 2
    assert payload['data']['rows'][0]['currentPrice'] == 11.0
    assert payload['data']['rows'][0]['t5MaxReturnPct'] == 6.0


def test_dde_combo_statistics_uses_only_complete_list_samples(stock_database, monkeypatch):
    monkeypatch.setattr(AppConfig, 'stock_stat_db_path', str(stock_database))
    payload = json.loads(asyncio.run(get_stock_dde_combo_statistics()).body)
    assert payload['data'] == [{'signalDate': '20260807', 'comboBand': '3次', 'successCount': 1, 'failureCount': 0, 'sampleCount': 1}]


def test_dde_top30_list_reads_observation_performance(stock_database, monkeypatch):
    monkeypatch.setattr(AppConfig, 'stock_stat_db_path', str(stock_database))
    payload = json.loads(asyncio.run(get_stock_dde_top30_performance_list(page_num=1, page_size=20)).body)
    assert payload['data']['total'] == 2
    assert [row['signalSlot'] for row in payload['data']['rows']] == ['close', 'morning']
    assert [row['rawRankNo'] for row in payload['data']['rows']] == [2, 3]
    assert payload['data']['rows'][0]['t5MaxReturnPct'] == 7.0


def test_dde_top30_list_filters_requested_slot(stock_database, monkeypatch):
    monkeypatch.setattr(AppConfig, 'stock_stat_db_path', str(stock_database))
    payload = json.loads(asyncio.run(get_stock_dde_top30_performance_list(signal_slot='morning', page_num=1, page_size=20)).body)
    assert payload['data']['total'] == 1
    assert payload['data']['rows'][0]['rawRankNo'] == 3


def test_dde_top30_statistics_groups_complete_list_by_slot(stock_database, monkeypatch):
    monkeypatch.setattr(AppConfig, 'stock_stat_db_path', str(stock_database))
    payload = json.loads(asyncio.run(get_stock_dde_top30_statistics()).body)
    assert payload['data'] == [
        {'tradeDate': '20260806', 'signalSlot': 'morning', 'successCount': 1, 'failureCount': 0, 'sampleCount': 1},
        {'tradeDate': '20260806', 'signalSlot': 'close', 'successCount': 1, 'failureCount': 0, 'sampleCount': 1},
    ]


def test_dde_hot_rank_list_returns_latest_range_and_filters(stock_database, monkeypatch):
    monkeypatch.setattr(AppConfig, 'stock_stat_db_path', str(stock_database))
    payload = json.loads(asyncio.run(get_stock_dde_hot_rank_list(page_num=1, page_size=20, sort_by='targetHitRate', sort_order='descending')).body)
    assert payload['data']['statStartDate'] == '20260801'
    assert payload['data']['statEndDate'] == '20260818'
    assert payload['data']['total'] == 2
    assert payload['data']['rows'][0]['appearanceCount'] == 12
    assert payload['data']['rows'][0]['targetHitRate'] == 0.6
    assert payload['data']['rows'][0]['isLargeCap'] is True


def test_dde_observation_list_returns_summary_and_rows(stock_database, monkeypatch):
    monkeypatch.setattr(AppConfig, 'stock_stat_db_path', str(stock_database))
    payload = json.loads(asyncio.run(get_stock_dde_observation_list(dimension='high_price', page_num=1, page_size=20)).body)
    assert payload['data']['total'] == 2
    assert payload['data']['tradableCount'] == 2
    assert payload['data']['completedCount'] == 1
    assert payload['data']['targetHitRate'] == 1.0
    assert payload['data']['rows'][0]['entryPrice'] == 88.0
    assert payload['data']['rows'][0]['maxReturnT5Pct'] == 2.0


def test_dde_high_strength_observation_list(stock_database, monkeypatch):
    monkeypatch.setattr(AppConfig, 'stock_stat_db_path', str(stock_database))
    payload = json.loads(asyncio.run(get_stock_dde_observation_list(dimension='high_strength', page_num=1, page_size=20)).body)
    assert payload['data']['total'] == 1
    assert payload['data']['rows'][0]['stockCode'] == '000001'


def test_dde_observation_statistics_includes_limit_up_assumptions(stock_database, monkeypatch):
    monkeypatch.setattr(AppConfig, 'stock_stat_db_path', str(stock_database))
    payload = json.loads(asyncio.run(get_stock_dde_observation_statistics()).body)
    high_price = next(item for item in payload['data'] if item['dimension'] == 'high_price')
    assert high_price['sampleCount'] == 2
    assert high_price['limitUpCount'] == 1
    assert high_price['averageMaxReturnT5Pct'] == 2.0


def test_dde_intraday_combo_statistics_groups_complete_list_by_combo(stock_database, monkeypatch):
    monkeypatch.setattr(AppConfig, 'stock_stat_db_path', str(stock_database))
    payload = json.loads(asyncio.run(get_stock_dde_intraday_combo_statistics()).body)
    assert payload['data'] == [
        {'tradeDate': '20260806', 'comboType': 'morning_noon', 'successCount': 1, 'failureCount': 0, 'sampleCount': 1}
    ]


def test_dde_observation_limit_up_slots():
    assert StockDdeDao.get_limit_up_slots('测试股', 9.6, 8, 9.5) == ['morning', 'close']
