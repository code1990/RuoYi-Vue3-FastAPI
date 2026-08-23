import asyncio

from config.env import AppConfig
from module_stock.dao.stock_limit_up_dao import StockLimitUpDao
from module_stock.entity.vo.stock_limit_up_vo import StockLimitUpThemeListModel


class StockLimitUpService:
    @classmethod
    async def get_theme_top15_services(cls, start_date: str | None, end_date: str | None) -> StockLimitUpThemeListModel:
        trade_dates, rows = await asyncio.to_thread(StockLimitUpDao.get_theme_top15, AppConfig.stock_stat_db_path, start_date, end_date)
        return StockLimitUpThemeListModel(trade_dates=trade_dates, rows=rows)
