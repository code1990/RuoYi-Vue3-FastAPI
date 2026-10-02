import os
import sqlite3
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import requests
from dotenv import load_dotenv

from config.env import AppConfig
from module_future.dao.future_option_dao import FutureOptionDao


class FutureOptionPriceService:
    BASE_URL = 'https://fuyao.aicubes.cn/api/options/prices'

    @classmethod
    def _request(cls, endpoint: str, thscode: str) -> dict:
        if not FutureOptionDao.is_option_contract(AppConfig.future_stat_db_path, thscode):
            raise ValueError('Unknown option contract')
        load_dotenv(Path(AppConfig.future_stat_db_path).parent / '.env')
        key = os.getenv('HITHINK_FINANCE_API_KEY') or os.getenv('FUYAO_API_KEY')
        if not key:
            raise RuntimeError('FUYAO_API_KEY is required for option prices')
        response = requests.get(f'{cls.BASE_URL}/{endpoint}', params={'thscode': thscode}, headers={'X-api-key': key}, timeout=(5, 30))
        response.raise_for_status()
        payload = response.json()
        if int(payload.get('code', -1)) != 0:
            raise RuntimeError(f"option prices API failed: {payload.get('message')}")
        return payload.get('data') or {}

    @classmethod
    def get_intraday(cls, thscode: str) -> dict:
        return cls._request('intraday', thscode)

    @classmethod
    def get_daily_research(cls, thscode: str, database_path: str | None = None) -> dict:
        data = cls._request('daily', thscode)
        with sqlite3.connect(database_path or AppConfig.future_stat_db_path) as connection:
            connection.execute(
                '''CREATE TABLE IF NOT EXISTS t_option_quote (thscode TEXT NOT NULL, trade_date TEXT NOT NULL,
                open_price REAL, high_price REAL, low_price REAL, close_price REAL, volume REAL, turnover REAL,
                source_timestamp INTEGER, day_change_rate REAL, synced_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY(thscode, trade_date))'''
            )
            try:
                connection.execute('ALTER TABLE t_option_quote ADD COLUMN day_change_rate REAL')
            except sqlite3.OperationalError:
                pass
            items = sorted((item for item in data.get('item') or [] if item.get('timestamp') is not None), key=lambda item: item['timestamp'])
            if not items:
                return data
            item, previous = items[-1], items[-2] if len(items) > 1 else None
            close, previous_close = item.get('close_price'), previous and previous.get('close_price')
            change_rate = (float(close) / float(previous_close) - 1) * 100 if close and previous_close else None
            trade_date = datetime.fromtimestamp(int(item['timestamp']) / 1000, ZoneInfo('Asia/Shanghai')).strftime('%Y%m%d')
            connection.execute('DELETE FROM t_option_quote WHERE thscode=? AND trade_date<>?', (thscode, trade_date))
            connection.execute(
                '''INSERT INTO t_option_quote (thscode, trade_date, open_price, high_price, low_price, close_price, volume, turnover, source_timestamp, day_change_rate)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) ON CONFLICT(thscode, trade_date) DO UPDATE SET open_price=excluded.open_price,
                high_price=excluded.high_price, low_price=excluded.low_price, close_price=excluded.close_price, volume=excluded.volume,
                turnover=excluded.turnover, source_timestamp=excluded.source_timestamp, day_change_rate=excluded.day_change_rate, synced_at=CURRENT_TIMESTAMP''',
                (thscode, trade_date, item.get('open_price'), item.get('high_price'), item.get('low_price'), close, item.get('volume'), item.get('turnover'), data.get('timestamp'), change_rate),
            )
        return data

    @classmethod
    def refresh_underlying_daily_research(cls, underlying_code: str) -> None:
        with FutureOptionDao._connect(AppConfig.future_stat_db_path) as connection:
            contracts = [row[0] for row in connection.execute('SELECT thscode FROM t_option_contract WHERE thscode LIKE ?', (f'{underlying_code}-%',))]
        for thscode in contracts:
            cls.get_daily_research(thscode)
