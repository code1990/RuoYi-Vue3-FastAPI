import asyncio

from config.env import AppConfig
from module_stock.dao.stock_kdj_dao import StockKdjDao
from module_stock.entity.vo.stock_kdj_vo import StockKdjHistoryModel, StockKdjSignalBacktestPageModel


class StockKdjService:
    @classmethod
    async def get_history_services(cls, stock_code: str, limit: int, year: int | None = None) -> StockKdjHistoryModel:
        candles, indicators = await asyncio.to_thread(StockKdjDao.get_history, AppConfig.stock_stat_db_path, stock_code, limit, year)
        return StockKdjHistoryModel(candles=candles, indicators=indicators)

    @classmethod
    async def get_backtest_page_services(
        cls, stock_code: str | None, year: int | None, signal_status: str,
        page_num: int, page_size: int, sort_by: str | None, sort_order: str | None,
    ) -> StockKdjSignalBacktestPageModel:
        rows, total, summary = await asyncio.to_thread(
            StockKdjDao.get_backtest_page,
            AppConfig.stock_stat_db_path, stock_code, year, signal_status,
            page_num, page_size, sort_by, sort_order,
        )
        return StockKdjSignalBacktestPageModel(
            rows=rows, total=total, page_num=page_num, page_size=page_size,
            has_next=page_num * page_size < total, **summary,
        )
