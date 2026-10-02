from fastapi import HTTPException, Response, status

from common.router import APIRouterPro
from common.vo import DataResponseModel
from module_future.entity.vo.future_profit_effect_vo import FutureProfitEffectModel
from module_future.service.future_profit_effect_service import FutureProfitEffectService
from utils.response_util import ResponseUtil


future_profit_effect_controller = APIRouterPro(prefix='/future/profit-effect', order_num=37, tags=['期货-开盘收益效应'])


@future_profit_effect_controller.get('/list', summary='查询期货开盘收益效应', response_model=DataResponseModel[list[FutureProfitEffectModel]])
async def get_future_profit_effect_list() -> Response:
    try:
        rows = await FutureProfitEffectService.get_list_services()
    except FileNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Future data source unavailable') from error
    return ResponseUtil.success(data=rows)
