import asyncio

from config.env import AppConfig
from module_stock.dao.stock_company_compare_dao import StockCompanyCompareDao
from module_stock.entity.vo.stock_company_compare_vo import StockCompanyCompareHistoryModel


class StockCompanyCompareService:
    @classmethod
    async def get_history_services(cls, stock_codes: list[str]) -> StockCompanyCompareHistoryModel:
        companies, quotes = await asyncio.to_thread(StockCompanyCompareDao.get_history, AppConfig.stock_stat_db_path, stock_codes)
        return StockCompanyCompareHistoryModel(companies=companies, quotes=quotes)
