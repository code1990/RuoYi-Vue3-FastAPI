from typing import Annotated

from fastapi import HTTPException, Query, Response, status

from common.router import APIRouterPro
from common.vo import DataResponseModel
from module_stock.entity.vo.stock_dde_vo import StockDdeComboSignalPageModel, StockDdeSignalPerformancePageModel, StockDdeTop30PerformancePageModel
from module_stock.service.stock_dde_service import StockDdeService
from utils.response_util import ResponseUtil

stock_dde_controller = APIRouterPro(prefix='/stock/dde', order_num=31, tags=['股票-DDE资金'])


@stock_dde_controller.get('/combo/list', summary='查询昨日今日DDE捡漏候选', response_model=DataResponseModel[StockDdeComboSignalPageModel])
async def get_stock_dde_combo_list(
    start_date: Annotated[str | None, Query(alias='startDate', pattern=r'^\d{8}$')] = None,
    end_date: Annotated[str | None, Query(alias='endDate', pattern=r'^\d{8}$')] = None,
    page_num: Annotated[int, Query(alias='pageNum', ge=1)] = 1,
    page_size: Annotated[int, Query(alias='pageSize', ge=1, le=200)] = 20,
) -> Response:
    try:
        result = await StockDdeService.get_combo_page_services(start_date, end_date, page_num, page_size)
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
) -> Response:
    try:
        result = await StockDdeService.get_signal_performance_page_services(
            start_date, end_date, page_num, page_size
        )
    except FileNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Stock data source unavailable') from error
    return ResponseUtil.success(data=result)


@stock_dde_controller.get('/top30/performance/list', summary='查询DDE可交易Top30收益列表', response_model=DataResponseModel[StockDdeTop30PerformancePageModel])
async def get_stock_dde_top30_performance_list(
    start_date: Annotated[str | None, Query(alias='startDate', pattern=r'^\d{8}$')] = None,
    end_date: Annotated[str | None, Query(alias='endDate', pattern=r'^\d{8}$')] = None,
    page_num: Annotated[int, Query(alias='pageNum', ge=1)] = 1,
    page_size: Annotated[int, Query(alias='pageSize', ge=1, le=200)] = 20,
) -> Response:
    try:
        result = await StockDdeService.get_top30_performance_page_services(start_date, end_date, page_num, page_size)
    except FileNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Stock data source unavailable') from error
    return ResponseUtil.success(data=result)
