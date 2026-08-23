from typing import Annotated

from fastapi import HTTPException, Query, Response, status

from common.router import APIRouterPro
from common.vo import DataResponseModel
from module_stock.entity.vo.stock_fund_visual_vo import StockFundVisualHistoryModel
from module_stock.service.stock_fund_visual_service import StockFundVisualService
from utils.response_util import ResponseUtil

stock_fund_visual_controller = APIRouterPro(prefix='/stock/fund-visual', order_num=36, tags=['股票-资金可视化'])


@stock_fund_visual_controller.get('/history', summary='查询单股资金柱图历史', response_model=DataResponseModel[StockFundVisualHistoryModel])
async def get_stock_fund_visual_history(
    stock_code: Annotated[str, Query(alias='stockCode', pattern=r'^\d{6}$')],
) -> Response:
    try:
        result = await StockFundVisualService.get_history_services(stock_code)
    except FileNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Stock data source unavailable') from error
    return ResponseUtil.success(data=result)
