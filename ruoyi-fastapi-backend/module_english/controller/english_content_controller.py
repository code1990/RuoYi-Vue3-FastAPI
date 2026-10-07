from typing import Annotated

from fastapi import HTTPException, Query, Response
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from common.aspect.db_seesion import DBSessionDependency
from common.router import APIRouterPro
from common.vo import DataResponseModel
from module_english.service.english_content_service import EnglishContentService
from module_english.entity.do.english_do import EnglishMediaAsset
from config.env import UploadConfig
from pathlib import Path
from utils.response_util import ResponseUtil


english_content_controller = APIRouterPro(prefix='/english', order_num=41, tags=['英语学习'])


@english_content_controller.get('/books', response_model=DataResponseModel[list[dict]])
async def get_books(db: Annotated[AsyncSession, DBSessionDependency()]) -> Response:
    return ResponseUtil.success(data=await EnglishContentService.books(db))


@english_content_controller.get('/units', response_model=DataResponseModel[list[dict]])
async def get_units(book_id: Annotated[int, Query(alias='bookId', ge=1)], db: Annotated[AsyncSession, DBSessionDependency()]) -> Response:
    return ResponseUtil.success(data=await EnglishContentService.units(db, book_id))


@english_content_controller.get('/words', response_model=DataResponseModel[list[dict]])
async def get_words(unit_id: Annotated[int, Query(alias='unitId', ge=1)], db: Annotated[AsyncSession, DBSessionDependency()]) -> Response:
    return ResponseUtil.success(data=await EnglishContentService.words(db, unit_id))


@english_content_controller.get('/media/{media_id}')
async def get_media(media_id: int, db: Annotated[AsyncSession, DBSessionDependency()]):
    media = await db.get(EnglishMediaAsset, media_id)
    path = Path(UploadConfig.UPLOAD_PATH).resolve() / (media.storage_path if media else '')
    if not media or media.status != 'ready' or not path.is_file():
        raise HTTPException(status_code=404, detail='英语媒体不存在')
    return FileResponse(path, media_type='audio/mpeg' if media.media_type == 'audio' else 'text/html')
