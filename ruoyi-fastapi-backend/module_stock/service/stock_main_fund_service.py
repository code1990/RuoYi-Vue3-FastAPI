import asyncio

from config.env import AppConfig
from module_stock.dao.stock_main_fund_dao import StockMainFundDao
from module_stock.entity.vo.stock_main_fund_vo import StockMainFundPerformancePageModel, StockMainFundStatisticsModel


class StockMainFundService:
    @classmethod
    async def get_performance_page_services(
        cls, stock_code: str | None, start_date: str | None, end_date: str | None, page_num: int, page_size: int
    ) -> StockMainFundPerformancePageModel:
        rows, total = await asyncio.to_thread(
            StockMainFundDao.get_performance_page,
            AppConfig.stock_stat_db_path,
            stock_code,
            start_date,
            end_date,
            page_num,
            page_size,
        )
        return StockMainFundPerformancePageModel(
            rows=rows,
            total=total,
            page_num=page_num,
            page_size=page_size,
            has_next=page_num * page_size < total,
        )

    @classmethod
    async def get_statistics_services(cls, start_date: str | None, end_date: str | None, target_return_pct: float) -> list[StockMainFundStatisticsModel]:
        rows = await asyncio.to_thread(StockMainFundDao.get_statistics, AppConfig.stock_stat_db_path, start_date, end_date, target_return_pct)
        return [StockMainFundStatisticsModel.model_validate(row) for row in rows]
