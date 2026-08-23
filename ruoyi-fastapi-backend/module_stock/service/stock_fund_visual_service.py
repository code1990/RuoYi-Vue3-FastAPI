import asyncio

from config.env import AppConfig
from module_stock.dao.stock_fund_visual_dao import StockFundVisualDao
from module_stock.entity.vo.stock_fund_visual_vo import StockFundVisualHistoryModel


class StockFundVisualService:
    @classmethod
    async def get_history_services(cls, stock_code: str) -> StockFundVisualHistoryModel:
        main_fund, margin, dde = await asyncio.to_thread(StockFundVisualDao.get_history, AppConfig.stock_stat_db_path, stock_code)
        return StockFundVisualHistoryModel(main_fund=main_fund, margin=margin, dde=dde)
