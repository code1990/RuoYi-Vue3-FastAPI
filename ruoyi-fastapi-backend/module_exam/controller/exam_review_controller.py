from typing import Annotated
from fastapi import Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from common.aspect.db_seesion import DBSessionDependency
from common.aspect.pre_auth import CurrentUserDependency, PreAuthDependency
from common.router import APIRouterPro
from common.vo import DataResponseModel
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_exam.entity.vo.exam_review_vo import ExamCardRateModel
from module_exam.service.exam_review_service import ExamReviewService
from utils.response_util import ResponseUtil

exam_review_controller = APIRouterPro(prefix='/exam/review', order_num=43, tags=['考试-复习'], dependencies=[PreAuthDependency()])

@exam_review_controller.get('/overview', response_model=DataResponseModel[dict])
async def overview(db: Annotated[AsyncSession, DBSessionDependency()], current_user: Annotated[CurrentUserModel, CurrentUserDependency()], year: Annotated[int | None, Query(ge=2020, le=2100)] = None) -> Response:
    return ResponseUtil.success(data=await ExamReviewService.overview(db, current_user.user.user_id, year))

@exam_review_controller.get('/next', response_model=DataResponseModel[dict | None])
async def next_card(db: Annotated[AsyncSession, DBSessionDependency()], current_user: Annotated[CurrentUserModel, CurrentUserDependency()]) -> Response:
    return ResponseUtil.success(data=await ExamReviewService.next_card(db, current_user.user.user_id))

@exam_review_controller.post('/{card_id}/rate', response_model=DataResponseModel[dict])
async def rate(card_id: int, data: ExamCardRateModel, db: Annotated[AsyncSession, DBSessionDependency()], current_user: Annotated[CurrentUserModel, CurrentUserDependency()]) -> Response:
    return ResponseUtil.success(data=await ExamReviewService.rate(db, current_user.user.user_id, card_id, data.rating))
