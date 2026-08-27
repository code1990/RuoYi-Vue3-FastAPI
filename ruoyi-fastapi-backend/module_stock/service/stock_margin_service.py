import asyncio

from config.env import AppConfig
from module_stock.dao.stock_margin_dao import StockMarginDao
from module_stock.entity.vo.stock_margin_vo import StockMarginComboPageModel, StockMarginComboStatisticsModel, StockMarginLongPerformancePageModel, StockMarginLongStatisticsModel, StockMarginLongModelPage


class StockMarginService:
    @classmethod
    async def get_long_model_services(cls, page_num: int, page_size: int, start_date: str | None, end_date: str | None) -> StockMarginLongModelPage:
        rows, total = await asyncio.to_thread(StockMarginDao.get_long_model, AppConfig.stock_stat_db_path, page_num, page_size, start_date, end_date)
        return StockMarginLongModelPage(rows=rows, total=total, page_num=page_num, page_size=page_size, has_next=page_num * page_size < total)
    @classmethod
    async def get_combo_statistics_services(cls, window_days: int, target_return_pct: float) -> list[StockMarginComboStatisticsModel]:
        rows = await asyncio.to_thread(StockMarginDao.get_combo_statistics, AppConfig.stock_stat_db_path, window_days, target_return_pct)
        return [StockMarginComboStatisticsModel.model_validate(row) for row in rows]

    @classmethod
    async def get_long_statistics_services(cls, start_date: str | None, end_date: str | None, target_return_pct: float) -> list[StockMarginLongStatisticsModel]:
        rows = await asyncio.to_thread(StockMarginDao.get_long_statistics, AppConfig.stock_stat_db_path, start_date, end_date, target_return_pct)
        return [StockMarginLongStatisticsModel.model_validate(row) for row in rows]

    @classmethod
    async def get_combo_page_services(cls, window_days, start_date, end_date, page_num, page_size) -> StockMarginComboPageModel:
        rows, total = await asyncio.to_thread(StockMarginDao.get_combo_page, AppConfig.stock_stat_db_path, window_days, start_date, end_date, page_num, page_size)
        return StockMarginComboPageModel(rows=rows, total=total, page_num=page_num, page_size=page_size, has_next=page_num * page_size < total)

    @classmethod
    async def get_long_performance_page_services(
        cls, stock_code: str | None, start_date: str | None, end_date: str | None, page_num: int, page_size: int
    ) -> StockMarginLongPerformancePageModel:
        rows, total = await asyncio.to_thread(
            StockMarginDao.get_long_performance_page,
            AppConfig.stock_stat_db_path,
            stock_code,
            start_date,
            end_date,
            page_num,
            page_size,
        )
        return StockMarginLongPerformancePageModel(
            rows=rows,
            total=total,
            page_num=page_num,
            page_size=page_size,
            has_next=page_num * page_size < total,
        )
