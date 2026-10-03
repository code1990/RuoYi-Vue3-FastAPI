import asyncio

from config.env import AppConfig
from module_future.dao.future_history_dao import FutureHistoryDao


class FutureHistoryService:
    @classmethod
    async def get_basis(cls, thscode: str | None) -> list[dict]:
        return await asyncio.to_thread(FutureHistoryDao.get_basis, AppConfig.future_stat_db_path, thscode)

    @classmethod
    async def get_contracts(cls, page_num: int, page_size: int, keyword: str | None) -> dict:
        rows, total = await asyncio.to_thread(FutureHistoryDao.get_contracts, AppConfig.future_stat_db_path, page_num, page_size, keyword)
        return {'rows': rows, 'total': total, 'page_num': page_num, 'page_size': page_size}

    @classmethod
    async def get_series(cls) -> list[dict]:
        return await asyncio.to_thread(FutureHistoryDao.get_series, AppConfig.future_stat_db_path)

    @classmethod
    async def get_daily(cls, thscode: str) -> list[dict]:
        return await asyncio.to_thread(FutureHistoryDao.get_daily, AppConfig.future_stat_db_path, thscode)
