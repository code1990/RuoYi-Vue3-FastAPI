import asyncio
from typing import Annotated, Literal

import requests
from fastapi import HTTPException, Query, Response, status

from common.router import APIRouterPro
from module_future.service.future_kline_service import FutureKlineService
from utils.response_util import ResponseUtil


future_kline_controller = APIRouterPro(prefix='/future/kline', order_num=41, tags=['期货-K线'])


@future_kline_controller.get('', summary='查询新华财经期货K线')
async def get_future_kline(
    contract_code: Annotated[str, Query(alias='contractCode', min_length=3, max_length=60)],
    period: Literal['minute', '5d', '1m', '5m', '15m', '30m', '60m', '1d', '1w', '1mo', '1y'] = '1d',
    count: Annotated[int, Query(ge=20, le=500)] = 200,
) -> Response:
    try:
        data = await asyncio.to_thread(FutureKlineService.get, contract_code.upper(), period, count)
    except requests.RequestException as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='新华财经K线服务不可用') from error
    return ResponseUtil.success(data=data)
