import asyncio

from config.env import AppConfig
from module_stock.dao.stock_signal_analysis_dao import StockSignalAnalysisDao
from module_stock.entity.vo.stock_signal_analysis_vo import StockSignalAnalysisPageModel


class StockSignalAnalysisService:
    @classmethod
    async def get_page_services(cls, table_key: str, signal_name: str | None, stock_code: str | None,
                                year: int | None, page_num: int, page_size: int) -> StockSignalAnalysisPageModel:
        rows, total, signal_names = await asyncio.to_thread(
            StockSignalAnalysisDao.get_page, AppConfig.stock_stat_db_path, table_key, signal_name,
            stock_code, year, page_num, page_size,
        )
        return StockSignalAnalysisPageModel(rows=rows, total=total, page_num=page_num, page_size=page_size,
                                            has_next=page_num * page_size < total,
                                            table_name=StockSignalAnalysisDao.TABLES[table_key], signal_names=signal_names)
