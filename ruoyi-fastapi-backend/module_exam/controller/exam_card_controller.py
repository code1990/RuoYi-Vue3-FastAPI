from typing import Annotated

from fastapi import Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from common.aspect.db_seesion import DBSessionDependency
from common.aspect.interface_auth import UserInterfaceAuthDependency
from common.aspect.pre_auth import PreAuthDependency
from common.router import APIRouterPro
from common.vo import DataResponseModel
from module_exam.entity.vo.exam_review_vo import ExamCardAiSummaryVersionCreateModel
from module_exam.service.exam_card_service import ExamCardService
from utils.response_util import ResponseUtil


exam_card_controller = APIRouterPro(prefix='/exam', order_num=42, tags=['考试'], dependencies=[PreAuthDependency()])


@exam_card_controller.get('/categories', response_model=DataResponseModel[list[dict]], summary='查询知识卡片分类')
async def get_categories(db: Annotated[AsyncSession, DBSessionDependency()]) -> Response:
    return ResponseUtil.success(data=await ExamCardService.categories(db))


@exam_card_controller.get('/cards', response_model=DataResponseModel[list[dict]], summary='查询已发布知识卡片')
async def get_cards(
    db: Annotated[AsyncSession, DBSessionDependency()],
    category_id: Annotated[int | None, Query(alias='categoryId', ge=1)] = None,
) -> Response:
    return ResponseUtil.success(data=await ExamCardService.cards(db, category_id))


@exam_card_controller.get('/cards/{card_id}/ai-summary-versions', response_model=DataResponseModel[dict], summary='查询题目AI总结方案')
async def get_ai_summary_versions(
    card_id: int,
    db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    return ResponseUtil.success(data=await ExamCardService.ai_summary_versions(db, card_id))


@exam_card_controller.post(
    '/cards/{card_id}/ai-summary-versions',
    response_model=DataResponseModel[dict],
    summary='新增题目AI总结方案',
    dependencies=[UserInterfaceAuthDependency('exam:card:edit')],
)
async def add_ai_summary_version(
    card_id: int,
    data: ExamCardAiSummaryVersionCreateModel,
    db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    return ResponseUtil.success(data=await ExamCardService.add_ai_summary_version(db, card_id, data.title, data.ai_summary))


@exam_card_controller.post(
    '/cards/{card_id}/ai-summary-versions/{summary_version_id}/activate',
    response_model=DataResponseModel[dict],
    summary='启用题目AI总结方案',
    dependencies=[UserInterfaceAuthDependency('exam:card:edit')],
)
async def activate_ai_summary_version(
    card_id: int,
    summary_version_id: int,
    db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    return ResponseUtil.success(data=await ExamCardService.activate_ai_summary_version(db, card_id, summary_version_id))
