import asyncio
import json
import sqlite3

from config.env import AppConfig
from module_stock.controller.stock_kdj_controller import get_stock_kdj_backtest, get_stock_kdj_history


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
    assert payload['data']['indicators'][0]['goldenCross'] == 1
    assert payload['data']['indicators'][-1]['goldenCross'] == 1


def test_kdj_history_filters_requested_year(tmp_path, monkeypatch):
    database_path = tmp_path / 'stock_stat.db'
    with sqlite3.connect(database_path) as connection:
        connection.execute('CREATE TABLE t_stock_daily_240 (stock_code TEXT, trade_date INTEGER, open REAL, high REAL, low REAL, close REAL, vol REAL, amount REAL, vol_rate REAL, percent REAL, changes REAL, pre_close REAL)')
        connection.execute('CREATE TABLE t_stock_kdj_daily (stock_code TEXT, trade_date INTEGER, period INTEGER, rsv REAL, k REAL, d REAL, j REAL, rsv_cross_k INTEGER, rsv_cross_d INTEGER, golden_cross INTEGER)')
        connection.executemany('INSERT INTO t_stock_daily_240 VALUES (?,?,?,?,?,?,?,?,?,?,?,?)', [
            ('000001.SZ', 20251231, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
            ('000001.SZ', 20260102, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
        ])
        connection.executemany('INSERT INTO t_stock_kdj_daily VALUES (?,?,?,?,?,?,?,?,?,?)', [
            ('000001.SZ', day, period, 1, 2, 3, 4, 0, 0, 0)
            for day in (20251231, 20260102) for period in (9, 90)
        ])
    monkeypatch.setattr(AppConfig, 'stock_stat_db_path', str(database_path))

    payload = json.loads(asyncio.run(get_stock_kdj_history(stock_code='000001', limit=30, year=2026)).body)
    assert [row['tradeDate'] for row in payload['data']['candles']] == [20260102]


def test_kdj_backtest_lists_rows_and_filters_status(tmp_path, monkeypatch):
    database_path = tmp_path / 'stock_stat.db'
    with sqlite3.connect(database_path) as connection:
        connection.execute('CREATE TABLE t_stock_pool (stock_code TEXT, stock_name TEXT, full_industry TEXT, full_concept TEXT)')
        connection.execute("INSERT INTO t_stock_pool VALUES ('000001.SZ', '示例股', '银行', '中特估')")
    artifact = tmp_path / 'kdj_audit' / 'latest'
    artifact.mkdir(parents=True)
    rows = [
        {'stock_code': '000001', 'signal_date': 20260102, 'year': 2026, 'signal_code': '110000', 'active_signals': '9rsv_cross_k|9rsv_cross_d', 'signal_count': 2, 'is_candidate': 1, 't1_max_return_pct': 2, 'target_hit': 1, 'is_completed': 1},
        {'stock_code': '000002', 'signal_date': 20260103, 'year': 2026, 'signal_code': '100000', 'signal_count': 1, 'is_candidate': 0, 'target_hit': 0, 'is_completed': 0},
    ]
    (artifact / 'signals.jsonl').write_text('\n'.join(json.dumps(row) for row in rows), encoding='utf-8')
    monkeypatch.setattr(AppConfig, 'stock_stat_db_path', str(database_path))
    monkeypatch.setenv('KDJ_AUDIT_DIR', str(artifact.parent))

    payload = json.loads(asyncio.run(get_stock_kdj_backtest(year=2026, signal_status='candidate', page_num=1, page_size=20)).body)
    assert payload['data']['total'] == 1
    assert payload['data']['rows'][0]['stockName'] == '示例股'
    assert payload['data']['rows'][0]['t1MaxReturnPct'] == 2.0
    assert payload['data']['hitRate'] == 1.0
