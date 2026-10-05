import asyncio
from typing import Annotated
from fastapi import Query,Response
from common.router import APIRouterPro
from module_future.service.future_intraday_service import FutureIntradayService
from utils.response_util import ResponseUtil
future_intraday_controller=APIRouterPro(prefix='/future/intraday',order_num=40,tags=['期货-分时'])
@future_intraday_controller.get('',summary='查询期货当日分时')
async def get_intraday(thscode:Annotated[str,Query(min_length=3,max_length=40)])->Response:return ResponseUtil.success(data=await asyncio.to_thread(FutureIntradayService.get,thscode.upper()))
