from typing import Annotated

from fastapi import HTTPException, Query, Response, status

from common.router import APIRouterPro
from common.vo import DataResponseModel
from module_stock.entity.vo.stock_dde_vo import StockDdeSignalPerformancePageModel
from module_stock.service.stock_dde_service import StockDdeService
from utils.response_util import ResponseUtil

stock_dde_controller = APIRouterPro(prefix='/stock/dde', order_num=31, tags=['股票-DDE资金'])


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
