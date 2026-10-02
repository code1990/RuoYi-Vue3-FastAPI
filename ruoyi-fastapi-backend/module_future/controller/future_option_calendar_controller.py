import asyncio
from typing import Annotated

import requests
from fastapi import HTTPException, Query, Response, status

from common.router import APIRouterPro
from module_future.service.future_option_calendar_service import FutureOptionCalendarService
from utils.response_util import ResponseUtil


future_option_calendar_controller = APIRouterPro(prefix='/future/option/calendar', order_num=38, tags=['期权-交易时间轴'])


@future_option_calendar_controller.get('/session-timeline', summary='查询期权合约交易时间轴')
async def get_option_session_timeline(thscode: Annotated[str, Query(min_length=3, max_length=80)]) -> Response:
    try:
        data = await asyncio.to_thread(FutureOptionCalendarService.get_timeline, thscode)
    except RuntimeError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error)) from error
    except requests.RequestException as error:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail='Option calendar data source unavailable') from error
    return ResponseUtil.success(data=data)
