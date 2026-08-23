import asyncio

from config.env import AppConfig
from module_stock.dao.stock_limit_up_dao import StockLimitUpDao
from module_stock.entity.vo.stock_limit_up_vo import StockLimitUpThemeListModel


class StockLimitUpService:
    @classmethod
    async def get_theme_top15_services(cls, trade_date: str | None) -> StockLimitUpThemeListModel:
        resolved_date, rows = await asyncio.to_thread(StockLimitUpDao.get_theme_top15, AppConfig.stock_stat_db_path, trade_date)
        return StockLimitUpThemeListModel(trade_date=resolved_date, rows=rows)
