import asyncio
import json
import sqlite3

from config.env import AppConfig
from module_stock.controller.stock_company_compare_controller import get_stock_company_compare


def test_company_compare_returns_requested_price_history(tmp_path, monkeypatch):
    database_path = tmp_path / 'stock_stat.db'
    with sqlite3.connect(database_path) as connection:
        connection.execute('CREATE TABLE t_stock_daily_240 (stock_code TEXT, trade_date INTEGER, close REAL, high REAL)')
        connection.execute('CREATE TABLE t_stock_pool (stock_code TEXT, stock_name TEXT, full_industry TEXT, full_concept TEXT, capital REAL)')
        connection.execute('CREATE TABLE t_stock_org_holder_tab (stock_code TEXT, report_period TEXT, report_date TEXT, tab_id TEXT, tab_name TEXT, holder_rate TEXT)')
        connection.executemany('INSERT INTO t_stock_pool VALUES (?, ?, ?, ?, ?)', [
            ('000001.SZ', '甲', '银行', '金融', 100), ('000002.SZ', '乙', '地产', '国企改革', 200),
        ])
        connection.executemany('INSERT INTO t_stock_org_holder_tab VALUES (?, ?, ?, ?, ?, ?)', [
            ('000001.SZ', '2026中报', '2026-06-30', 'all', '全部', '12.5'),
            ('000001.SZ', '2026中报', '2026-06-30', 'fund', '基金', '2.5'),
            ('000002.SZ', '2026一季报', '2026-03-31', 'all', '全部', '20'),
        ])
        connection.executemany('INSERT INTO t_stock_daily_240 VALUES (?, ?, ?, ?)', [
            ('000001.SZ', 20260901, 10, 11), ('000001.SZ', 20260902, 11, 12),
            ('000002.SZ', 20260901, 20, 21), ('000002.SZ', 20260902, 18, 19),
        ])
    monkeypatch.setattr(AppConfig, 'stock_stat_db_path', str(database_path))

    payload = json.loads(asyncio.run(get_stock_company_compare(stock_codes='000001,000002')).body)

    assert payload['data']['quotes'] == [
        {'stockCode': '000001', 'tradeDate': 20260901, 'close': 10.0, 'high': 11.0},
        {'stockCode': '000001', 'tradeDate': 20260902, 'close': 11.0, 'high': 12.0},
        {'stockCode': '000002', 'tradeDate': 20260901, 'close': 20.0, 'high': 21.0},
        {'stockCode': '000002', 'tradeDate': 20260902, 'close': 18.0, 'high': 19.0},
    ]
    assert [row['stockCode'] for row in payload['data']['companies']] == ['000002', '000001']
    assert payload['data']['companies'][1]['fundHoldingRate'] == 2.5
