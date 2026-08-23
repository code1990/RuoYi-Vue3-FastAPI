import asyncio

from config.env import AppConfig
from module_stock.dao.stock_kdj_dao import StockKdjDao
from module_stock.entity.vo.stock_kdj_vo import StockKdjHistoryModel


class StockKdjService:
    @classmethod
    async def get_history_services(cls, stock_code: str, limit: int) -> StockKdjHistoryModel:
        candles, indicators = await asyncio.to_thread(StockKdjDao.get_history, AppConfig.stock_stat_db_path, stock_code, limit)
        return StockKdjHistoryModel(candles=candles, indicators=indicators)
