import re
import sqlite3
from pathlib import Path
from typing import Any
from time import time

import requests

from config.env import AppConfig


class FutureKlineService:
    PERIODS = {'1m': 1, '5m': 2, '15m': 3, '30m': 4, '60m': 5, '1d': 6, '1w': 7, '1mo': 8, '1y': 9, 'minute': 10, '5d': 11}
    EXCHANGES = {'XSGE': 'SHF', 'XDCE': 'DCE', 'XZCE': 'CZC', 'XGFE': 'GFEX', 'SHGE': 'SHGE'}

    @classmethod
    def _get_local_daily_rows(cls, contract_code: str, count: int) -> list[dict[str, Any]]:
        match = re.match(r'([A-Z]+)\d+\.([A-Z]+)$', contract_code)
        path = Path(AppConfig.future_stat_db_path)
        if not match or not path.is_file() or match.group(2) not in cls.EXCHANGES:
            return []
        with sqlite3.connect(f'file:{path.resolve().as_posix()}?mode=ro', uri=True) as connection:
            rows = connection.execute(
                '''SELECT b.trade_date,b.open_price,b.high_price,b.low_price,b.close_price,b.volume,b.turnover
                   FROM t_future_daily_bar b JOIN t_future_series s ON s.thscode=b.thscode
                   WHERE s.product_code=? AND s.exchange_code=? AND s.series_type='main'
                   ORDER BY b.trade_date DESC LIMIT ?''',
                (match.group(1), cls.EXCHANGES[match.group(2)], count),
            ).fetchall()
        return [dict(zip(('time', 'open', 'high', 'low', 'close', 'volume', 'turnover'), row)) for row in reversed(rows)]

    @classmethod
    def _get_trend_rows(cls, contract_code: str, endpoint: str) -> list[dict[str, Any]]:
        response = requests.get(
            f'https://quotedata.cnfin.com/quote/v1/{endpoint}',
            params={
                'localDate': int(time() * 1000), 'prod_code': contract_code,
                'fields': 'last_px,business_amount,business_balance,avg_px,index_rise_trend,index_fall_trend',
            },
            headers={'User-Agent': 'Mozilla/5.0', 'Origin': 'https://www.cnfin.com', 'Referer': 'https://www.cnfin.com/'},
            timeout=(5, 20),
        )
        response.raise_for_status()
        trend = (response.json().get('data') or {}).get('trend') or {}
        fields = {name: index for index, name in enumerate(trend.get('fields') or [])}
        rows = trend.get(contract_code) or []
        required = ('min_time', 'last_px')
        if any(field not in fields for field in required):
            return []
        result = []
        previous_date = None
        previous_volume = previous_turnover = 0
        for row in rows:
            if not isinstance(row, list):
                continue
            price = row[fields['last_px']]
            date = str(row[fields['min_time']])[:8]
            volume = row[fields['business_amount']] if 'business_amount' in fields else 0
            turnover = row[fields['business_balance']] if 'business_balance' in fields else 0
            if date != previous_date:
                previous_volume = previous_turnover = 0
                previous_date = date
            result.append({
                'time': row[fields['min_time']], 'open': price, 'high': price, 'low': price, 'close': price,
                'volume': max(volume - previous_volume, 0), 'turnover': max(turnover - previous_turnover, 0),
            })
            previous_volume, previous_turnover = volume, turnover
        return result

    @classmethod
    def _get_rows(cls, contract_code: str, candle_period: int, count: int) -> list[dict[str, Any]]:
        response = requests.get(
            'https://quotedata.cnfin.com/quote/v1/kline',
            params={
                'prod_code': contract_code,
                'candle_period': candle_period,
                'get_type': 'offset',
                'fields': 'open_px,high_px,low_px,close_px,business_amount,business_balance',
                'data_count': count,
            },
            headers={'User-Agent': 'Mozilla/5.0', 'Origin': 'https://www.cnfin.com', 'Referer': 'https://www.cnfin.com/'},
            timeout=(5, 20),
        )
        response.raise_for_status()
        candle = (response.json().get('data') or {}).get('candle') or {}
        fields = candle.get('fields') or []
        rows = candle.get(contract_code) or []
        indexes = {name: index for index, name in enumerate(fields)}
        result = []
        for row in rows:
            if not isinstance(row, list) or any(indexes.get(field) is None for field in ('min_time', 'open_px', 'high_px', 'low_px', 'close_px')):
                continue
            result.append({
                'time': row[indexes['min_time']], 'open': row[indexes['open_px']], 'high': row[indexes['high_px']],
                'low': row[indexes['low_px']], 'close': row[indexes['close_px']],
                'volume': row[indexes['business_amount']] if 'business_amount' in indexes else None,
                'turnover': row[indexes['business_balance']] if 'business_balance' in indexes else None,
            })
        return result

    @classmethod
    def get(cls, contract_code: str, period: str, count: int) -> dict[str, Any]:
        if period in ('minute', '5d'):
            # trend 接口是新华财经页面自身使用的逐分钟分时源；kline 的 10/11 档为稀疏 K 线数据。
            rows = cls._get_trend_rows(contract_code, 'real_trend' if period == 'minute' else 'trend5day')
        elif period == '1d':
            rows = cls._get_local_daily_rows(contract_code, count)
            today_row = cls._get_rows(contract_code, cls.PERIODS[period], 1 if rows else count)
            if not rows:
                rows = today_row
            if today_row and (not rows or str(today_row[-1]['time'])[:8] > str(rows[-1]['time'])[:8]):
                rows = [*rows, today_row[-1]][-count:]
        else:
            rows = cls._get_rows(contract_code, cls.PERIODS[period], count)
        if period == '5d':
            dates = sorted({str(item['time'])[:8] for item in rows})[-5:]
            rows = [item for item in rows if str(item['time'])[:8] in dates]
        return {'contractCode': contract_code, 'period': period, 'rows': rows}

    @classmethod
    def get_latest_price(cls, contract_code: str) -> float:
        """Return the latest price reported by the upstream real-time trend feed."""
        rows = cls._get_trend_rows(contract_code, 'real_trend')
        for row in reversed(rows):
            try:
                price = float(row['close'])
            except (KeyError, TypeError, ValueError):
                continue
            if price > 0:
                return price
        raise ValueError('新华财经未返回最新成交价')
