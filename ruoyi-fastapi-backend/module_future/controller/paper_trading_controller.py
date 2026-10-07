from typing import Annotated

from fastapi import HTTPException, Path, Query, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from common.aspect.db_seesion import DBSessionDependency
from common.aspect.pre_auth import CurrentUserDependency, PreAuthDependency
from common.router import APIRouterPro
from common.vo import DataResponseModel, ResponseBaseModel
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_future.entity.do.paper_trading_do import FuturePaperOrder
from module_future.entity.vo.paper_trading_vo import PaperAccountModel, PaperOrderModel, PaperTradeOpenModel
from module_future.service.paper_trading_service import PaperTradingService
from utils.response_util import ResponseUtil


paper_trading_controller = APIRouterPro(prefix='/future/paper-trading', order_num=38, tags=['期货-模拟交易'], dependencies=[PreAuthDependency()])


@paper_trading_controller.get('/status', response_model=DataResponseModel[dict])
async def get_trading_status(contract_code: str = Query(alias='contractCode', min_length=1, max_length=40)) -> Response:
    return ResponseUtil.success(data=await PaperTradingService.status(contract_code))


@paper_trading_controller.get('/floating-calendar', response_model=DataResponseModel[list[dict]])
async def get_floating_calendar(db: Annotated[AsyncSession, DBSessionDependency()], current_user: Annotated[CurrentUserModel, CurrentUserDependency()], month: str = Query(pattern=r'^\d{4}-\d{2}$')) -> Response:
    try:
        return ResponseUtil.success(data=await PaperTradingService.floating_calendar(db, current_user.user.user_id, month))
    except ValueError as error:
        raise HTTPException(status_code=400, detail='Invalid month') from error


@paper_trading_controller.get('/account', response_model=DataResponseModel[PaperAccountModel])
async def get_account(db: Annotated[AsyncSession, DBSessionDependency()], current_user: Annotated[CurrentUserModel, CurrentUserDependency()]) -> Response:
    return ResponseUtil.success(data=await PaperTradingService.account(db, current_user.user.user_id))


@paper_trading_controller.post('/open', response_model=ResponseBaseModel)
async def open_position(data: PaperTradeOpenModel, db: Annotated[AsyncSession, DBSessionDependency()], current_user: Annotated[CurrentUserModel, CurrentUserDependency()]) -> Response:
    await PaperTradingService.open(db, current_user.user.user_id, data)
    return ResponseUtil.success(msg='模拟开仓成功')


@paper_trading_controller.post('/positions/{position_id}/close', response_model=ResponseBaseModel)
async def close_position(position_id: Annotated[int, Path(ge=1)], db: Annotated[AsyncSession, DBSessionDependency()], current_user: Annotated[CurrentUserModel, CurrentUserDependency()]) -> Response:
    await PaperTradingService.close(db, current_user.user.user_id, position_id)
    return ResponseUtil.success(msg='模拟平仓成功')


@paper_trading_controller.get('/orders', response_model=DataResponseModel[list[PaperOrderModel]])
async def get_orders(db: Annotated[AsyncSession, DBSessionDependency()], current_user: Annotated[CurrentUserModel, CurrentUserDependency()]) -> Response:
    rows = (await db.scalars(select(FuturePaperOrder).where(FuturePaperOrder.user_id == current_user.user.user_id).order_by(FuturePaperOrder.order_id.desc()).limit(100))).all()
    return ResponseUtil.success(data=rows)
