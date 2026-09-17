from typing import Annotated

from fastapi import HTTPException, Query, Response, status

from common.router import APIRouterPro
from common.vo import DataResponseModel
from module_stock.entity.vo.stock_kdj_vo import StockKdjHistoryModel, StockKdjSignalBacktestPageModel
from module_stock.service.stock_kdj_service import StockKdjService
from utils.response_util import ResponseUtil

stock_kdj_controller = APIRouterPro(prefix='/stock/kdj', order_num=34, tags=['股票-KDJ'])


@stock_kdj_controller.get('/history', summary='查询K线与KDJ历史', response_model=DataResponseModel[StockKdjHistoryModel])
async def get_stock_kdj_history(
    stock_code: Annotated[str, Query(alias='stockCode', pattern=r'^\d{6}$')],
    limit: Annotated[int, Query(ge=30, le=1000)] = 250,
    year: Annotated[int | None, Query(ge=2000, le=2100)] = None,
) -> Response:
    try:
        result = await StockKdjService.get_history_services(stock_code, limit, year)
    except FileNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Stock data source unavailable') from error
    return ResponseUtil.success(data=result)


@stock_kdj_controller.get('/backtest', summary='查询KDJ双周期回测信号明细', response_model=DataResponseModel[StockKdjSignalBacktestPageModel])
async def get_stock_kdj_backtest(
    stock_code: Annotated[str | None, Query(alias='stockCode', pattern=r'^\d{6}$')] = None,
    year: Annotated[int | None, Query(ge=2000, le=2100)] = None,
    signal_status: Annotated[str, Query(alias='signalStatus', pattern=r'^(all|candidate|hit|fail|pending)$')] = 'all',
    page_num: Annotated[int, Query(alias='pageNum', ge=1)] = 1,
    page_size: Annotated[int, Query(alias='pageSize', ge=1, le=200)] = 20,
    sort_by: Annotated[str | None, Query(alias='sortBy')] = None,
    sort_order: Annotated[str | None, Query(alias='sortOrder', pattern=r'^(ascending|descending)$')] = None,
) -> Response:
    try:
        result = await StockKdjService.get_backtest_page_services(
            stock_code, year, signal_status, page_num, page_size, sort_by, sort_order
        )
    except FileNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Stock data source unavailable') from error
    return ResponseUtil.success(data=result)
