from typing import Annotated

from fastapi import HTTPException, Query, Response, status

from common.router import APIRouterPro
from common.vo import DataResponseModel
from module_stock.entity.vo.stock_dde_vo import (
    StockDdeComboSignalPageModel,
    StockDdeComboStatisticsModel,
    StockDdeHotRankPageModel,
    StockDdeObservationPageModel,
    StockDdeObservationStatisticsModel,
    StockDdeSignalPerformancePageModel,
    StockDdeTop30PerformancePageModel,
    StockDdeTop30ListStatisticsModel,
    StockDdeTop30StatisticsModel,
)
from module_stock.service.stock_dde_service import StockDdeService
from utils.response_util import ResponseUtil

stock_dde_controller = APIRouterPro(prefix='/stock/dde', order_num=31, tags=['股票-DDE资金'])


@stock_dde_controller.get('/combo/list', summary='查询昨日今日DDE捡漏候选', response_model=DataResponseModel[StockDdeComboSignalPageModel])
async def get_stock_dde_combo_list(
    start_date: Annotated[str | None, Query(alias='startDate', pattern=r'^\d{8}$')] = None,
    end_date: Annotated[str | None, Query(alias='endDate', pattern=r'^\d{8}$')] = None,
    page_num: Annotated[int, Query(alias='pageNum', ge=1)] = 1,
    page_size: Annotated[int, Query(alias='pageSize', ge=1, le=200)] = 20,
    sort_by: Annotated[str | None, Query(alias='sortBy')] = None,
    sort_order: Annotated[str | None, Query(alias='sortOrder', pattern=r'^(ascending|descending)$')] = None,
) -> Response:
    try:
        result = await StockDdeService.get_combo_page_services(start_date, end_date, page_num, page_size, sort_by, sort_order)
    except FileNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Stock data source unavailable') from error
    return ResponseUtil.success(data=result)


@stock_dde_controller.get('/combo/statistics', summary='查询2日DDE列表统计', response_model=DataResponseModel[list[StockDdeComboStatisticsModel]])
async def get_stock_dde_combo_statistics(
    start_date: Annotated[str | None, Query(alias='startDate', pattern=r'^\d{8}$')] = None,
    end_date: Annotated[str | None, Query(alias='endDate', pattern=r'^\d{8}$')] = None,
    target_return_pct: Annotated[float, Query(alias='targetReturnPct', ge=0, le=100)] = 1.8,
) -> Response:
    try:
        result = await StockDdeService.get_combo_statistics_services(start_date, end_date, target_return_pct)
    except FileNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Stock data source unavailable') from error
    return ResponseUtil.success(data=result)


@stock_dde_controller.get(
    '/performance/list',
    summary='查询DDE信号收益列表',
    response_model=DataResponseModel[StockDdeSignalPerformancePageModel],
)
async def get_stock_dde_signal_performance_list(
    start_date: Annotated[str | None, Query(alias='startDate', pattern=r'^\d{8}$')] = None,
    end_date: Annotated[str | None, Query(alias='endDate', pattern=r'^\d{8}$')] = None,
    page_num: Annotated[int, Query(alias='pageNum', ge=1)] = 1,
    page_size: Annotated[int, Query(alias='pageSize', ge=1, le=200)] = 20,
    sort_by: Annotated[str | None, Query(alias='sortBy')] = None,
    sort_order: Annotated[str | None, Query(alias='sortOrder', pattern=r'^(ascending|descending)$')] = None,
) -> Response:
    try:
        result = await StockDdeService.get_signal_performance_page_services(
            start_date, end_date, page_num, page_size, sort_by, sort_order
        )
    except FileNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Stock data source unavailable') from error
    return ResponseUtil.success(data=result)


@stock_dde_controller.get('/top30/performance/list', summary='查询DDE原始Top30收益列表（涨停不计）', response_model=DataResponseModel[StockDdeTop30PerformancePageModel])
async def get_stock_dde_top30_performance_list(
    signal_slot: Annotated[str | None, Query(alias='signalSlot', pattern=r'^(morning|noon|close|post_close)$')] = None,
    start_date: Annotated[str | None, Query(alias='startDate', pattern=r'^\d{8}$')] = None,
    end_date: Annotated[str | None, Query(alias='endDate', pattern=r'^\d{8}$')] = None,
    page_num: Annotated[int, Query(alias='pageNum', ge=1)] = 1,
    page_size: Annotated[int, Query(alias='pageSize', ge=1, le=200)] = 20,
    sort_by: Annotated[str | None, Query(alias='sortBy')] = None,
    sort_order: Annotated[str | None, Query(alias='sortOrder', pattern=r'^(ascending|descending)$')] = None,
) -> Response:
    try:
        result = await StockDdeService.get_top30_performance_page_services(signal_slot, start_date, end_date, page_num, page_size, sort_by, sort_order)
    except FileNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Stock data source unavailable') from error
    return ResponseUtil.success(data=result)


@stock_dde_controller.get('/top30/statistics', summary='查询DDE资金30列表统计', response_model=DataResponseModel[list[StockDdeTop30ListStatisticsModel]])
async def get_stock_dde_top30_statistics(
    start_date: Annotated[str | None, Query(alias='startDate', pattern=r'^\d{8}$')] = None,
    end_date: Annotated[str | None, Query(alias='endDate', pattern=r'^\d{8}$')] = None,
    target_return_pct: Annotated[float, Query(alias='targetReturnPct', ge=0, le=100)] = 1.8,
) -> Response:
    try:
        result = await StockDdeService.get_top30_list_statistics_services(start_date, end_date, target_return_pct)
    except FileNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Stock data source unavailable') from error
    return ResponseUtil.success(data=result)


@stock_dde_controller.get('/statistics', summary='查询DDE收益列表统计', response_model=DataResponseModel[list[StockDdeTop30StatisticsModel]])
async def get_stock_dde_statistics(
    start_date: Annotated[str | None, Query(alias='startDate', pattern=r'^\d{8}$')] = None,
    end_date: Annotated[str | None, Query(alias='endDate', pattern=r'^\d{8}$')] = None,
    target_return_pct: Annotated[float, Query(alias='targetReturnPct', ge=0, le=100)] = 1.8,
) -> Response:
    try:
        result = await StockDdeService.get_signal_statistics_services(start_date, end_date, target_return_pct)
    except FileNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Stock data source unavailable') from error
    return ResponseUtil.success(data=result)


@stock_dde_controller.get('/hot-rank/list', summary='查询DDE热度榜', response_model=DataResponseModel[StockDdeHotRankPageModel])
async def get_stock_dde_hot_rank_list(
    large_cap: Annotated[bool | None, Query(alias='largeCap')] = None,
    high_price: Annotated[bool | None, Query(alias='highPrice')] = None,
    page_num: Annotated[int, Query(alias='pageNum', ge=1)] = 1,
    page_size: Annotated[int, Query(alias='pageSize', ge=1, le=200)] = 20,
    sort_by: Annotated[str | None, Query(alias='sortBy')] = None,
    sort_order: Annotated[str | None, Query(alias='sortOrder', pattern=r'^(ascending|descending)$')] = None,
) -> Response:
    try:
        result = await StockDdeService.get_hot_rank_page_services(page_num, page_size, large_cap, high_price, sort_by, sort_order)
    except FileNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Stock data source unavailable') from error
    return ResponseUtil.success(data=result)


@stock_dde_controller.get('/observation/list', summary='查询DDE观察列表', response_model=DataResponseModel[StockDdeObservationPageModel])
async def get_stock_dde_observation_list(
    dimension: Annotated[str, Query(pattern=r'^(high_price|large_cap|high_strength|intraday_combo)$')] = 'high_price',
    start_date: Annotated[str | None, Query(alias='startDate', pattern=r'^\d{8}$')] = None,
    end_date: Annotated[str | None, Query(alias='endDate', pattern=r'^\d{8}$')] = None,
    page_num: Annotated[int, Query(alias='pageNum', ge=1)] = 1,
    page_size: Annotated[int, Query(alias='pageSize', ge=1, le=200)] = 20,
    sort_by: Annotated[str | None, Query(alias='sortBy')] = None,
    sort_order: Annotated[str | None, Query(alias='sortOrder', pattern=r'^(ascending|descending)$')] = None,
) -> Response:
    try:
        result = await StockDdeService.get_observation_page_services(dimension, start_date, end_date, page_num, page_size, sort_by, sort_order)
    except FileNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Stock data source unavailable') from error
    return ResponseUtil.success(data=result)


@stock_dde_controller.get('/observation/statistics', summary='查询DDE专项回测统计', response_model=DataResponseModel[list[StockDdeObservationStatisticsModel]])
async def get_stock_dde_observation_statistics(
    start_date: Annotated[str | None, Query(alias='startDate', pattern=r'^\d{8}$')] = None,
    end_date: Annotated[str | None, Query(alias='endDate', pattern=r'^\d{8}$')] = None,
) -> Response:
    try:
        result = await StockDdeService.get_observation_statistics_services(start_date, end_date)
    except FileNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Stock data source unavailable') from error
    return ResponseUtil.success(data=result)
