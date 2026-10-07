from typing import Annotated

from fastapi import Response
from sqlalchemy.ext.asyncio import AsyncSession

from common.aspect.db_seesion import DBSessionDependency
from common.aspect.pre_auth import CurrentUserDependency, PreAuthDependency
from common.router import APIRouterPro
from common.vo import DataResponseModel, ResponseBaseModel
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_future.entity.vo.training_vo import TrainingDecisionCreateModel, TrainingDecisionModel
from module_future.service.training_service import TrainingService
from utils.response_util import ResponseUtil

training_controller = APIRouterPro(prefix='/future/training', order_num=40, tags=['期货-盘感训练'], dependencies=[PreAuthDependency()])


@training_controller.get('/list', response_model=DataResponseModel[list[dict]])
async def list_training(db: Annotated[AsyncSession, DBSessionDependency()], current_user: Annotated[CurrentUserModel, CurrentUserDependency()]) -> Response:
    return ResponseUtil.success(data=await TrainingService.list_today(db, current_user.user.user_id))


@training_controller.post('/decision', response_model=DataResponseModel[TrainingDecisionModel])
async def create_training_decision(data: TrainingDecisionCreateModel, db: Annotated[AsyncSession, DBSessionDependency()], current_user: Annotated[CurrentUserModel, CurrentUserDependency()]) -> Response:
    return ResponseUtil.success(msg='训练决策已记录', data=await TrainingService.submit(db, current_user.user.user_id, data))


@training_controller.get('/history', response_model=DataResponseModel[list[TrainingDecisionModel]])
async def get_training_history(db: Annotated[AsyncSession, DBSessionDependency()], current_user: Annotated[CurrentUserModel, CurrentUserDependency()]) -> Response:
    return ResponseUtil.success(data=await TrainingService.history(db, current_user.user.user_id))
