from typing import Annotated

from fastapi import HTTPException, Query

from common.aspect.pre_auth import PreAuthDependency
from common.router import APIRouterPro
from module_feizhu.service.resource_search_service import ResourceSearchService


resource_search_controller = APIRouterPro(prefix='/feizhu/resources', order_num=45, tags=['飞猪盘资源'], dependencies=[PreAuthDependency()])


@resource_search_controller.get('/topics', summary='查询资源主题下拉项')
async def topics() -> list[str]:
    return await ResourceSearchService.topics()


@resource_search_controller.get('/search', summary='本地复刻资源搜索')
async def search(
    kw: Annotated[str, Query(min_length=1, max_length=255)],
    page: Annotated[int, Query(ge=1)] = 1,
    line: Annotated[int, Query(ge=1, le=100)] = 15,
    res_type: Annotated[str | None, Query(alias='resType', max_length=32)] = None,
) -> dict:
    return await ResourceSearchService.search(kw, page, line, res_type)


@resource_search_controller.get('/detail', summary='本地复刻资源详情')
async def detail(id: Annotated[str, Query(min_length=1, max_length=64)]) -> dict:
    result = await ResourceSearchService.detail(id)
    if result is None:
        raise HTTPException(status_code=404, detail='资源不存在')
    return result
