from typing import Annotated

from fastapi import HTTPException, Query, Response, status

from common.router import APIRouterPro
from common.vo import DataResponseModel
from module_stock.entity.vo.stock_limit_up_vo import StockLimitUpThemeListModel
from module_stock.service.stock_limit_up_service import StockLimitUpService
from utils.response_util import ResponseUtil

stock_limit_up_controller = APIRouterPro(prefix='/stock/limit-up', order_num=35, tags=['股票-涨停题材'])


@stock_limit_up_controller.get('/theme/top15', summary='查询交易日涨停题材前15', response_model=DataResponseModel[StockLimitUpThemeListModel])
async def get_stock_limit_up_theme_top15(
    trade_date: Annotated[str | None, Query(alias='tradeDate', pattern=r'^\d{4}-\d{2}-\d{2}$')] = None,
) -> Response:
    try:
        result = await StockLimitUpService.get_theme_top15_services(trade_date)
    except FileNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Stock data source unavailable') from error
    return ResponseUtil.success(data=result)
