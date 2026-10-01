from typing import Annotated, Literal

from fastapi import HTTPException, Query, Response, status

from common.router import APIRouterPro
from common.vo import DataResponseModel
from module_future.entity.vo.future_quote_vo import FutureQuotePageModel
from module_future.service.future_quote_service import FutureQuoteService
from utils.response_util import ResponseUtil


future_quote_controller = APIRouterPro(prefix='/future/quote', order_num=36, tags=['期货-行情'])


@future_quote_controller.get('/list', summary='查询期货当前行情', response_model=DataResponseModel[FutureQuotePageModel])
async def get_future_quote_list(
    scope: Annotated[Literal['domestic', 'overseas'], Query()] = 'domestic',
    keyword: Annotated[str | None, Query(max_length=50)] = None,
    page_num: Annotated[int, Query(alias='pageNum', ge=1)] = 1,
    page_size: Annotated[int, Query(alias='pageSize', ge=1, le=200)] = 50,
) -> Response:
    try:
        result = await FutureQuoteService.get_page_services(scope, keyword, page_num, page_size)
    except FileNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Future data source unavailable') from error
    return ResponseUtil.success(data=result)
