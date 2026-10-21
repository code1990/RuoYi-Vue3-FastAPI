from time import time
from typing import Any

import requests


class StockKlineService:
    PERIODS = {'1m': 1, '5m': 2, '15m': 3, '30m': 4, '60m': 5, '1d': 6, '1w': 7, '1mo': 8, '1y': 9}

    @staticmethod
    def market_code(stock_code: str) -> str:
        if stock_code.startswith('6'):
            return f'{stock_code}.SS'
        if stock_code.startswith(('4', '8')):
            return f'{stock_code}.BJ'
        return f'{stock_code}.SZ'

    @classmethod
    def _trend_rows(cls, market_code: str, endpoint: str) -> list[dict[str, Any]]:
        response = requests.get(
            f'https://quotedata.cnfin.com/quote/v1/{endpoint}',
            params={'localDate': int(time() * 1000), 'prod_code': market_code, 'fields': 'last_px,business_amount,business_balance,avg_px,index_rise_trend,index_fall_trend'},
            headers={'User-Agent': 'Mozilla/5.0', 'Origin': 'https://www.cnfin.com', 'Referer': 'https://www.cnfin.com/'}, timeout=(5, 20),
        )
        response.raise_for_status()
        trend = (response.json().get('data') or {}).get('trend') or {}
        indexes = {name: index for index, name in enumerate(trend.get('fields') or [])}
        rows, result = trend.get(market_code) or [], []
        if any(field not in indexes for field in ('min_time', 'last_px')):
            return result
        previous_date = previous_volume = previous_turnover = None
        for row in rows:
            if not isinstance(row, list):
                continue
            date, price = str(row[indexes['min_time']])[:8], row[indexes['last_px']]
            volume = row[indexes['business_amount']] if 'business_amount' in indexes else 0
            turnover = row[indexes['business_balance']] if 'business_balance' in indexes else 0
            if date != previous_date:
                previous_date, previous_volume, previous_turnover = date, 0, 0
            result.append({'time': row[indexes['min_time']], 'open': price, 'high': price, 'low': price, 'close': price, 'volume': max(volume - previous_volume, 0), 'turnover': max(turnover - previous_turnover, 0)})
            previous_volume, previous_turnover = volume, turnover
        return result

    @classmethod
    def _kline_rows(cls, market_code: str, period: str, count: int) -> list[dict[str, Any]]:
        response = requests.get(
            'https://quotedata.cnfin.com/quote/v1/kline',
            params={'localDate': int(time() * 1000), 'prod_code': market_code, 'candle_period': cls.PERIODS[period], 'get_type': 'offset', 'candle_mode': 1, 'fields': 'min_time,open_px,high_px,low_px,close_px,business_amount,business_balance', 'data_count': count},
            headers={'User-Agent': 'Mozilla/5.0', 'Origin': 'https://www.cnfin.com', 'Referer': 'https://www.cnfin.com/'}, timeout=(5, 20),
        )
        response.raise_for_status()
        candle = (response.json().get('data') or {}).get('candle') or {}
        indexes = {name: index for index, name in enumerate(candle.get('fields') or [])}
        required = ('min_time', 'open_px', 'high_px', 'low_px', 'close_px')
        if any(field not in indexes for field in required):
            return []
        return [
            {'time': row[indexes['min_time']], 'open': row[indexes['open_px']], 'high': row[indexes['high_px']], 'low': row[indexes['low_px']], 'close': row[indexes['close_px']], 'volume': row[indexes['business_amount']] if 'business_amount' in indexes else None, 'turnover': row[indexes['business_balance']] if 'business_balance' in indexes else None}
            for row in candle.get(market_code) or [] if isinstance(row, list)
        ]

    @classmethod
    def get(cls, stock_code: str, period: str, count: int) -> dict[str, Any]:
        market_code = cls.market_code(stock_code)
        rows = cls._trend_rows(market_code, 'real_trend' if period == 'minute' else 'trend5day') if period in ('minute', '5d') else cls._kline_rows(market_code, period, count)
        if period == '5d':
            dates = sorted({str(row['time'])[:8] for row in rows})[-5:]
            rows = [row for row in rows if str(row['time'])[:8] in dates]
        return {'stockCode': stock_code, 'period': period, 'rows': rows}
