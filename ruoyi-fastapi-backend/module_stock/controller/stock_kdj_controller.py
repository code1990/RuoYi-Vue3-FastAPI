from typing import Annotated

from fastapi import HTTPException, Query, Response, status

from common.router import APIRouterPro
from common.vo import DataResponseModel
from module_stock.entity.vo.stock_kdj_vo import StockKdjHistoryModel
from module_stock.service.stock_kdj_service import StockKdjService
from utils.response_util import ResponseUtil

stock_kdj_controller = APIRouterPro(prefix='/stock/kdj', order_num=34, tags=['股票-KDJ'])


@stock_kdj_controller.get('/history', summary='查询K线与KDJ历史', response_model=DataResponseModel[StockKdjHistoryModel])
async def get_stock_kdj_history(
    stock_code: Annotated[str, Query(alias='stockCode', pattern=r'^\d{6}$')],
    limit: Annotated[int, Query(ge=30, le=1000)] = 250,
) -> Response:
    try:
        result = await StockKdjService.get_history_services(stock_code, limit)
    except FileNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Stock data source unavailable') from error
    return ResponseUtil.success(data=result)
