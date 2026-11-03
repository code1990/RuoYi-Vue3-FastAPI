from typing import Annotated

from fastapi import Query, Response
from common.aspect.pre_auth import PreAuthDependency
from common.router import APIRouterPro
from common.vo import DataResponseModel
from module_feizhu.entity.vo.file_detail_vo import FileDetailOptionsModel, FileDetailPageModel
from module_feizhu.service.file_detail_service import FileDetailService
from utils.response_util import ResponseUtil

file_detail_controller = APIRouterPro(prefix='/feizhu/file-details', order_num=44, tags=['飞猪盘'], dependencies=[PreAuthDependency()])


@file_detail_controller.get('/options', response_model=DataResponseModel[FileDetailOptionsModel], summary='查询文件明细筛选项')
async def get_file_detail_options(
    keyword_ids: Annotated[str | None, Query(alias='keywordIds', max_length=2048)] = None,
) -> Response:
    return ResponseUtil.success(data=await FileDetailService.options(keyword_ids))


@file_detail_controller.get('', response_model=DataResponseModel[FileDetailPageModel], summary='查询文件明细')
async def get_file_details(
    page_num: Annotated[int, Query(alias='pageNum', ge=1)] = 1,
    page_size: Annotated[int, Query(alias='pageSize', ge=1, le=100)] = 20,
    keyword_ids: Annotated[str | None, Query(alias='keywordIds', max_length=2048)] = None,
    topics: Annotated[str | None, Query(max_length=4096)] = None,
    exts: Annotated[str | None, Query(max_length=1024)] = None,
    category: Annotated[int | None, Query()] = None,
    resource_type: Annotated[str | None, Query(alias='resourceType', max_length=32)] = None,
    valid: Annotated[str | None, Query(max_length=255)] = None,
    haspwd: Annotated[str | None, Query(max_length=255)] = None,
    keyword: Annotated[str | None, Query(max_length=255)] = None,
) -> Response:
    return ResponseUtil.success(data=await FileDetailService.page(page_num, page_size, keyword_ids, topics, exts, category, resource_type, valid, haspwd, keyword))
