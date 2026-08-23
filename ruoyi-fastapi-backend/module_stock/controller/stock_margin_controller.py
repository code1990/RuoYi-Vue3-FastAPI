from typing import Annotated

from fastapi import HTTPException, Query, Response, status

from common.router import APIRouterPro
from common.vo import DataResponseModel
from module_stock.entity.vo.stock_margin_vo import StockMarginComboPageModel, StockMarginLongPerformancePageModel, StockMarginLongStatisticsModel
from module_stock.service.stock_margin_service import StockMarginService
from utils.response_util import ResponseUtil

stock_margin_controller = APIRouterPro(prefix='/stock/margin', order_num=33, tags=['股票-融资融券'])


@stock_margin_controller.get(
    '/long-performance/list',
    summary='查询融资融券做多收益列表',
    response_model=DataResponseModel[StockMarginLongPerformancePageModel],
)
async def get_stock_margin_long_performance_list(
    start_date: Annotated[str | None, Query(alias='startDate', pattern=r'^\d{8}$')] = None,
    end_date: Annotated[str | None, Query(alias='endDate', pattern=r'^\d{8}$')] = None,
    page_num: Annotated[int, Query(alias='pageNum', ge=1)] = 1,
    page_size: Annotated[int, Query(alias='pageSize', ge=1, le=200)] = 20,
) -> Response:
    try:
        result = await StockMarginService.get_long_performance_page_services(start_date, end_date, page_num, page_size)
    except FileNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Stock data source unavailable') from error
    return ResponseUtil.success(data=result)


@stock_margin_controller.get('/long-performance/statistics', summary='查询融资融券列表统计', response_model=DataResponseModel[list[StockMarginLongStatisticsModel]])
async def get_stock_margin_long_statistics(
    start_date: Annotated[str | None, Query(alias='startDate', pattern=r'^\d{8}$')] = None,
    end_date: Annotated[str | None, Query(alias='endDate', pattern=r'^\d{8}$')] = None,
    target_return_pct: Annotated[float, Query(alias='targetReturnPct', ge=0, le=100)] = 1.8,
) -> Response:
    try:
        result = await StockMarginService.get_long_statistics_services(start_date, end_date, target_return_pct)
    except FileNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Stock data source unavailable') from error
    return ResponseUtil.success(data=result)


@stock_margin_controller.get(
    '/combo/list',
    summary='查询多日综合融资排名',
    response_model=DataResponseModel[StockMarginComboPageModel],
)
async def get_stock_margin_combo_list(
    window_days: Annotated[int, Query(alias='windowDays', ge=2, le=5)],
    start_date: Annotated[str | None, Query(alias='startDate', pattern=r'^\d{8}$')] = None,
    end_date: Annotated[str | None, Query(alias='endDate', pattern=r'^\d{8}$')] = None,
    page_num: Annotated[int, Query(alias='pageNum', ge=1)] = 1,
    page_size: Annotated[int, Query(alias='pageSize', ge=1, le=200)] = 20,
) -> Response:
    if window_days not in (2, 3, 5):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='windowDays must be 2, 3, or 5')
    try:
        result = await StockMarginService.get_combo_page_services(window_days, start_date, end_date, page_num, page_size)
    except FileNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Stock data source unavailable') from error
    return ResponseUtil.success(data=result)
