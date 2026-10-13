import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo

from config.env import AppConfig
from module_future.dao.future_quote_dao import FutureQuoteDao
from module_future.entity.vo.future_quote_vo import FutureQuotePageModel
from module_future.service.training_service import TrainingService


class FutureQuoteService:
    @classmethod
    async def get_page_services(cls, scope: str, keyword: str | None, page_num: int, page_size: int) -> FutureQuotePageModel:
        rows, total = await asyncio.to_thread(FutureQuoteDao.get_page, AppConfig.future_stat_db_path, scope, keyword, page_num, page_size, True)
        now = datetime.now(ZoneInfo('Asia/Shanghai'))
        for row in rows:
            row['night_session_open'] = row['market_code'] in FutureQuoteDao.MARKETS['domestic'] and TrainingService.is_night_session(row['contract_code'], now)
        return FutureQuotePageModel(rows=rows, total=total, page_num=page_num, page_size=page_size, has_next=page_num * page_size < total)
