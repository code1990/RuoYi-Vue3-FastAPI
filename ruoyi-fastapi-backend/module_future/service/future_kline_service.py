from typing import Any

import requests


class FutureKlineService:
    PERIODS = {'1m': 1, '5m': 2, '15m': 3, '30m': 4, '60m': 5, '1d': 6, '1w': 7, '1mo': 8, '1y': 9, 'minute': 10, '5d': 11}

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
        rows = cls._get_rows(contract_code, cls.PERIODS[period], count)
        # 新华财经的 period=10 只提供当日分时，闭市日会返回空数组；回退到五日
        # 数据中的最后一个交易日，仍然展示新华财经的真实分时数据。
        if period == 'minute' and not rows:
            history = cls._get_rows(contract_code, cls.PERIODS['5d'], count)
            if history:
                last_date = max(str(item['time'])[:8] for item in history)
                rows = [item for item in history if str(item['time'])[:8] == last_date]
        return {'contractCode': contract_code, 'period': period, 'rows': rows}
