import asyncio

from config.env import AppConfig
from module_stock.dao.stock_dde_dao import StockDdeDao
from module_stock.entity.vo.stock_dde_vo import StockDdeSignalPerformancePageModel


class StockDdeService:
    @classmethod
    async def get_signal_performance_page_services(
        cls, start_date: str | None, end_date: str | None, page_num: int, page_size: int
    ) -> StockDdeSignalPerformancePageModel:
        rows, total = await asyncio.to_thread(
            StockDdeDao.get_signal_performance_page,
            AppConfig.stock_stat_db_path,
            start_date,
            end_date,
            page_num,
            page_size,
        )
        return StockDdeSignalPerformancePageModel(
            rows=rows,
            total=total,
            page_num=page_num,
            page_size=page_size,
            has_next=page_num * page_size < total,
        )
