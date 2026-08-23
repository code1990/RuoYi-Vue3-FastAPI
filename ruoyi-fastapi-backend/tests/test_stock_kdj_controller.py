import asyncio
import json
import sqlite3

from config.env import AppConfig
from module_stock.controller.stock_kdj_controller import get_stock_kdj_history


def test_kdj_history_returns_candles_and_both_periods(tmp_path, monkeypatch):
    database_path = tmp_path / 'stock_stat.db'
    with sqlite3.connect(database_path) as connection:
        connection.execute('''CREATE TABLE t_stock_daily_240 (
            stock_code TEXT, trade_date INTEGER, open REAL, high REAL, low REAL, close REAL,
            vol REAL, amount REAL, vol_rate REAL, percent REAL, changes REAL, pre_close REAL
        )''')
        connection.execute('''CREATE TABLE t_stock_kdj_daily (
            stock_code TEXT, trade_date INTEGER, period INTEGER, rsv REAL, k REAL, d REAL, j REAL,
            rsv_cross_k INTEGER, rsv_cross_d INTEGER, golden_cross INTEGER
        )''')
        connection.executemany(
            'INSERT INTO t_stock_daily_240 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            [
                ('000001', 20260801, 10, 11, 9, 10.5, 1000, 10500, 1.2, 5, 0.5, 10),
                ('000001', 20260802, 10.5, 12, 10, 11.5, 2000, 23000, 1.5, 9.52, 1, 10.5),
                ('000001', 20260803, 11.5, 13, 11, 12, 3000, 36000, 1.8, 4.35, 0.5, 11.5),
            ],
        )
        connection.executemany(
            'INSERT INTO t_stock_kdj_daily VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            [
                ('000001', 20260801, period, 50, 40, 35, 50, 0, 0, 0)
                for period in (9, 90)
            ]
            + [
                ('000001', 20260802, period, 60, 50, 40, 70, 1, 0, period == 9)
                for period in (9, 90)
            ]
            + [
                ('000001', 20260803, period, 70, 60, 50, 80, 0, 1, period == 90)
                for period in (9, 90)
            ],
        )
    monkeypatch.setattr(AppConfig, 'stock_stat_db_path', str(database_path))

    response = asyncio.run(get_stock_kdj_history(stock_code='000001', limit=2))
    payload = json.loads(response.body)

    assert [row['tradeDate'] for row in payload['data']['candles']] == [20260802, 20260803]
    assert payload['data']['candles'][0]['amount'] == 23000
    assert len(payload['data']['indicators']) == 4
    assert payload['data']['indicators'][0]['goldenCross'] is True
    assert payload['data']['indicators'][-1]['goldenCross'] is True
