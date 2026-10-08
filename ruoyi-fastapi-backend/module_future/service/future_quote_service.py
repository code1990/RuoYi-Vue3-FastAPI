import asyncio

from config.env import AppConfig
from module_future.dao.future_quote_dao import FutureQuoteDao
from module_future.entity.vo.future_quote_vo import FutureQuotePageModel


class FutureQuoteService:
    @classmethod
    async def get_page_services(cls, scope: str, keyword: str | None, page_num: int, page_size: int) -> FutureQuotePageModel:
        rows, total = await asyncio.to_thread(FutureQuoteDao.get_page, AppConfig.future_stat_db_path, scope, keyword, page_num, page_size, True)
        return FutureQuotePageModel(rows=rows, total=total, page_num=page_num, page_size=page_size, has_next=page_num * page_size < total)
