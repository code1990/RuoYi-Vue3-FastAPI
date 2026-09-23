import asyncio
import json
import sqlite3

from config.env import AppConfig
from module_stock.controller.stock_signal_analysis_controller import get_stock_signal_analysis_page


def test_signal_analysis_reads_three_tables_and_pool_metadata(tmp_path, monkeypatch):
    database_path = tmp_path / 'stock_stat.db'
    with sqlite3.connect(database_path) as connection:
        connection.execute('CREATE TABLE t_stock_pool (stock_code TEXT, stock_name TEXT, industry_1 TEXT, full_concept TEXT)')
        connection.execute("INSERT INTO t_stock_pool VALUES ('000001', '示例股', '银行', '中特估')")
        connection.execute('CREATE TABLE t_stock_stat_info (signal_name TEXT, stock_code TEXT, stat_year INTEGER, sample_count INTEGER, win_count_1 INTEGER, win_count_2 INTEGER, win_rate_1 REAL, win_rate_2 REAL)')
        connection.execute("INSERT INTO t_stock_stat_info VALUES ('双K', '000001', 2026, 12, 10, 9, .8333, .75)")
    monkeypatch.setattr(AppConfig, 'stock_stat_db_path', str(database_path))

    response = asyncio.run(get_stock_signal_analysis_page(table='raw', signal_name='双K', page_num=1, page_size=20))
    payload = json.loads(response.body)

    assert payload['data']['total'] == 1
    assert payload['data']['rows'][0]['stockName'] == '示例股'
    assert payload['data']['rows'][0]['industryName'] == '银行'
    assert payload['data']['rows'][0]['concept'] == '中特估'
