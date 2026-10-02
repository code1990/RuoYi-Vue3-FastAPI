import asyncio
from typing import Annotated

import requests
from fastapi import HTTPException, Query, Response, status

from common.router import APIRouterPro
from common.vo import DataResponseModel
from module_future.entity.vo.future_option_vo import FutureOptionChainModel, FutureOptionContractSummaryPageModel, FutureOptionVarietyPageModel
from module_future.service.future_option_price_service import FutureOptionPriceService
from module_future.service.future_option_service import FutureOptionService
from utils.response_util import ResponseUtil


future_option_controller = APIRouterPro(prefix='/future/option', order_num=38, tags=['期权-大盘期权池'])


@future_option_controller.get('/varieties', summary='查询期权品种目录', response_model=DataResponseModel[FutureOptionVarietyPageModel])
async def get_option_varieties(
    page_num: Annotated[int, Query(alias='pageNum', ge=1)] = 1,
    page_size: Annotated[int, Query(alias='pageSize', ge=1, le=100)] = 100,
) -> Response:
    return ResponseUtil.success(data=await FutureOptionService.get_varieties(page_num, page_size))


@future_option_controller.get('/contracts', summary='查询全部期权合约汇总', response_model=DataResponseModel[FutureOptionContractSummaryPageModel])
async def get_option_contract_summaries(
    page_num: Annotated[int, Query(alias='pageNum', ge=1)] = 1,
    page_size: Annotated[int, Query(alias='pageSize', ge=1, le=100)] = 100,
    variety_code: Annotated[str | None, Query(alias='varietyCode', max_length=40)] = None,
    exchange_code: Annotated[str | None, Query(alias='exchangeCode', max_length=40)] = None,
) -> Response:
    try:
        result = await FutureOptionService.get_contract_summaries(page_num, page_size, variety_code, exchange_code)
    except FileNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Option data source unavailable') from error
    return ResponseUtil.success(data=result)


@future_option_controller.get('/chain', summary='查询期货标的对应期权链', response_model=DataResponseModel[list[FutureOptionChainModel]])
async def get_option_chain(underlying_code: Annotated[str, Query(alias='underlyingCode', min_length=2, max_length=40)]) -> Response:
    return ResponseUtil.success(data=await FutureOptionService.get_underlying_chain(underlying_code.upper()))


@future_option_controller.get('/chain/daily-research', summary='更新期货标的对应期权链日线')
async def refresh_option_chain_daily(underlying_code: Annotated[str, Query(alias='underlyingCode', min_length=2, max_length=40)]) -> Response:
    try:
        await asyncio.to_thread(FutureOptionPriceService.refresh_underlying_daily_research, underlying_code.upper())
    except (RuntimeError, requests.RequestException) as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Option chain daily data source unavailable') from error
    return ResponseUtil.success()


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
