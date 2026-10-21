import asyncio
from typing import Annotated, Literal

import requests
from fastapi import HTTPException, Query, Response, status

from common.router import APIRouterPro
from module_stock.service.stock_kline_service import StockKlineService
from utils.response_util import ResponseUtil


stock_kline_controller = APIRouterPro(prefix='/stock/kline', order_num=32, tags=['股票-K线'])


@stock_kline_controller.get('', summary='查询新华财经股票K线')
async def get_stock_kline(
    stock_code: Annotated[str, Query(alias='stockCode', pattern=r'^\d{6}$')],
    period: Literal['minute', '5d', '1m', '5m', '15m', '30m', '60m', '1d', '1w', '1mo', '1y'] = '1d',
    count: Annotated[int, Query(ge=20, le=500)] = 200,
) -> Response:
    try:
        data = await asyncio.to_thread(StockKlineService.get, stock_code, period, count)
    except requests.RequestException as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='新华财经K线服务不可用') from error
    return ResponseUtil.success(data=data)
