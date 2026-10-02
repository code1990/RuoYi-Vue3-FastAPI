from typing import Annotated

from fastapi import Response
from sqlalchemy.ext.asyncio import AsyncSession

from common.aspect.db_seesion import DBSessionDependency
from common.router import APIRouterPro
from common.vo import DataResponseModel
from module_future.entity.vo.future_relation_vo import FutureRelationModel
from module_future.service.future_relation_service import FutureRelationService
from utils.response_util import ResponseUtil


future_relation_controller = APIRouterPro(prefix='/future/relation', order_num=36, tags=['期货-合约关联'])


@future_relation_controller.get('/list', summary='查询期货合约关联', response_model=DataResponseModel[list[FutureRelationModel]])
async def get_future_relation_list(query_db: Annotated[AsyncSession, DBSessionDependency()]) -> Response:
    return ResponseUtil.success(data=await FutureRelationService.get_list_services(query_db))
