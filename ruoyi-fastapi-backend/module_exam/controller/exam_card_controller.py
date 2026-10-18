from typing import Annotated

from fastapi import Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from common.aspect.db_seesion import DBSessionDependency
from common.aspect.pre_auth import PreAuthDependency
from common.router import APIRouterPro
from common.vo import DataResponseModel
from module_exam.service.exam_card_service import ExamCardService
from utils.response_util import ResponseUtil


exam_card_controller = APIRouterPro(prefix='/exam', order_num=42, tags=['考试-知识卡片'], dependencies=[PreAuthDependency()])


@exam_card_controller.get('/categories', response_model=DataResponseModel[list[dict]], summary='查询知识卡片分类')
async def get_categories(db: Annotated[AsyncSession, DBSessionDependency()]) -> Response:
    return ResponseUtil.success(data=await ExamCardService.categories(db))


@exam_card_controller.get('/cards', response_model=DataResponseModel[list[dict]], summary='查询已发布知识卡片')
async def get_cards(
    db: Annotated[AsyncSession, DBSessionDependency()],
    category_id: Annotated[int | None, Query(alias='categoryId', ge=1)] = None,
) -> Response:
    return ResponseUtil.success(data=await ExamCardService.cards(db, category_id))
