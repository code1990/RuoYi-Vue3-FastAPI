import asyncio

from config.env import AppConfig
from module_future.dao.future_history_dao import FutureHistoryDao


class FutureHistoryService:
    @classmethod
    async def get_series(cls) -> list[dict]:
        return await asyncio.to_thread(FutureHistoryDao.get_series, AppConfig.future_stat_db_path)

    @classmethod
    async def get_daily(cls, thscode: str) -> list[dict]:
        return await asyncio.to_thread(FutureHistoryDao.get_daily, AppConfig.future_stat_db_path, thscode)
