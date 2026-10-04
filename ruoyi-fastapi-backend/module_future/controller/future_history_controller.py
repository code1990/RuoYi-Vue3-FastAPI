from typing import Annotated

from fastapi import HTTPException, Query, Response, status

from common.router import APIRouterPro
from module_future.service.future_history_service import FutureHistoryService
from utils.response_util import ResponseUtil


future_history_controller = APIRouterPro(prefix='/future/history', order_num=39, tags=['期货-历史日线'])

@future_history_controller.get('/catalog/{kind}', summary='查询期货目录数据')
async def get_future_catalog(kind: str) -> Response:
    if kind not in {'varieties', 'plates', 'roles'}: raise HTTPException(status_code=404, detail='Catalog type not found')
    return ResponseUtil.success(data=await FutureHistoryService.get_catalog(kind))
@future_history_controller.get('/research/{kind}', summary='查询期货仓单或持仓')
async def get_future_research(kind: str) -> Response:
    if kind not in {'warehouse','positions'}: raise HTTPException(status_code=404, detail='Research type not found')
    return ResponseUtil.success(data=await FutureHistoryService.get_research_rows(kind))


@future_history_controller.get('/basis', summary='查询期货主连基差')
async def get_future_history_basis(thscode: Annotated[str | None, Query(min_length=3, max_length=40)] = None) -> Response:
    try:
        return ResponseUtil.success(data=await FutureHistoryService.get_basis(thscode.upper() if thscode else None))
    except FileNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Future basis data source unavailable') from error


@future_history_controller.get('/contracts', summary='查询期货合约目录')
async def get_future_history_contracts(
    page_num: Annotated[int, Query(alias='pageNum', ge=1)] = 1,
    page_size: Annotated[int, Query(alias='pageSize', ge=1, le=200)] = 50,
    keyword: Annotated[str | None, Query(max_length=50)] = None,
) -> Response:
    try:
        return ResponseUtil.success(data=await FutureHistoryService.get_contracts(page_num, page_size, keyword))
    except FileNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Future history data source unavailable') from error


@future_history_controller.get('/series', summary='查询已入库期货历史序列')
async def get_future_history_series() -> Response:
    try:
        return ResponseUtil.success(data=await FutureHistoryService.get_series())
    except FileNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Future history data source unavailable') from error


@future_history_controller.get('/daily', summary='查询期货历史日线')
async def get_future_history_daily(thscode: Annotated[str, Query(min_length=3, max_length=40)]) -> Response:
    try:
        return ResponseUtil.success(data=await FutureHistoryService.get_daily(thscode.upper()))
    except FileNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Future history data source unavailable') from error
