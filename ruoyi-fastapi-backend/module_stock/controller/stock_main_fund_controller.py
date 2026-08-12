from typing import Annotated

from fastapi import HTTPException, Query, Response, status

from common.router import APIRouterPro
from common.vo import DataResponseModel
from module_stock.entity.vo.stock_main_fund_vo import StockMainFundPerformancePageModel
from module_stock.service.stock_main_fund_service import StockMainFundService
from utils.response_util import ResponseUtil

stock_main_fund_controller = APIRouterPro(prefix='/stock/main-fund', order_num=32, tags=['股票-主连资金'])


@stock_main_fund_controller.get(
    '/performance/list',
    summary='查询主连资金收益列表',
    response_model=DataResponseModel[StockMainFundPerformancePageModel],
)
async def get_stock_main_fund_performance_list(
    start_date: Annotated[str | None, Query(alias='startDate', pattern=r'^\d{8}$')] = None,
    end_date: Annotated[str | None, Query(alias='endDate', pattern=r'^\d{8}$')] = None,
    page_num: Annotated[int, Query(alias='pageNum', ge=1)] = 1,
    page_size: Annotated[int, Query(alias='pageSize', ge=1, le=200)] = 20,
) -> Response:
    try:
        result = await StockMainFundService.get_performance_page_services(start_date, end_date, page_num, page_size)
    except FileNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Stock data source unavailable') from error
    return ResponseUtil.success(data=result)
