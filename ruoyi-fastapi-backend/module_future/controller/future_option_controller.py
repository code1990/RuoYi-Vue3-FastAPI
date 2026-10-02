import asyncio
from typing import Annotated

import requests
from fastapi import HTTPException, Query, Response, status

from common.router import APIRouterPro
from common.vo import DataResponseModel
from module_future.entity.vo.future_option_vo import FutureOptionContractPageModel
from module_future.service.future_option_price_service import FutureOptionPriceService
from module_future.service.future_option_service import FutureOptionService
from utils.response_util import ResponseUtil


future_option_controller = APIRouterPro(prefix='/future/option', order_num=38, tags=['期权-沪深300'])


@future_option_controller.get('/contracts/io', summary='查询沪深300股指期权合约目录', response_model=DataResponseModel[FutureOptionContractPageModel])
async def get_io_option_contracts(
    page_num: Annotated[int, Query(alias='pageNum', ge=1)] = 1,
    page_size: Annotated[int, Query(alias='pageSize', ge=1, le=1000)] = 100,
) -> Response:
    try:
        result = await FutureOptionService.get_io_contracts(page_num, page_size)
    except FileNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Option data source unavailable') from error
    return ResponseUtil.success(data=result)


@future_option_controller.get('/prices/intraday', summary='查询沪深300期权当前分时')
async def get_io_option_intraday(thscode: Annotated[str, Query(min_length=3, max_length=80)]) -> Response:
    try:
        data = await asyncio.to_thread(FutureOptionPriceService.get_intraday, thscode)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error)) from error
    except (RuntimeError, requests.RequestException) as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Option price data source unavailable') from error
    return ResponseUtil.success(data=data)


@future_option_controller.get('/prices/daily-research', summary='查询并缓存沪深300期权日线研究数据')
async def get_io_option_daily_research(thscode: Annotated[str, Query(min_length=3, max_length=80)]) -> Response:
    try:
        data = await asyncio.to_thread(FutureOptionPriceService.get_daily_research, thscode)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error)) from error
    except (RuntimeError, requests.RequestException) as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Option price data source unavailable') from error
    return ResponseUtil.success(data=data)
