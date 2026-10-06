from typing import Any
from time import time

import requests


class FutureKlineService:
    PERIODS = {'1m': 1, '5m': 2, '15m': 3, '30m': 4, '60m': 5, '1d': 6, '1w': 7, '1mo': 8, '1y': 9, 'minute': 10, '5d': 11}

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
        for row in rows:
            if not isinstance(row, list):
                continue
            price = row[fields['last_px']]
            result.append({
                'time': row[fields['min_time']], 'open': price, 'high': price, 'low': price, 'close': price,
                'volume': row[fields['business_amount']] if 'business_amount' in fields else None,
                'turnover': row[fields['business_balance']] if 'business_balance' in fields else None,
            })
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
        else:
            rows = cls._get_rows(contract_code, cls.PERIODS[period], count)
        if period == '5d':
            dates = sorted({str(item['time'])[:8] for item in rows})[-5:]
            rows = [item for item in rows if str(item['time'])[:8] in dates]
        return {'contractCode': contract_code, 'period': period, 'rows': rows}
