from typing import Annotated

from fastapi import Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from common.aspect.db_seesion import DBSessionDependency
from common.router import APIRouterPro
from common.vo import DataResponseModel
from module_stock.entity.vo.stock_xg_night_vo import StockXgNightSuperCardsModel
from module_stock.service.stock_xg_night_service import StockXgNightService
from utils.log_util import logger
from utils.response_util import ResponseUtil


stock_xg_night_controller = APIRouterPro(prefix='/stock/xg/night-super', order_num=30, tags=['股票-夜盘选股'])


@stock_xg_night_controller.get(
    '/cards',
    summary='获取夜盘选股三日超额统计卡片接口',
    description='用于获取夜盘选股器在240min、60min、60+240交集三个维度的三日达标和超额统计卡片',
    response_model=DataResponseModel[StockXgNightSuperCardsModel],
)
async def get_stock_xg_night_super_cards(
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    trade_date: Annotated[int | None, Query(alias='tradeDate', description='出票日期，格式yyyyMMdd')] = None,
    limit: Annotated[int, Query(ge=1, le=50, description='返回选股器数量，默认3，展开可传10')] = 3,
) -> Response:
    card_result = await StockXgNightService.get_night_super_cards_services(query_db, trade_date, limit)
    logger.info('获取夜盘选股三日超额统计卡片成功')

    return ResponseUtil.success(data=card_result)
