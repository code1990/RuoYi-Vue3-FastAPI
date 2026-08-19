import asyncio

from config.env import AppConfig
from module_stock.dao.stock_dde_dao import StockDdeDao
from module_stock.entity.vo.stock_dde_vo import (
    StockDdeComboSignalPageModel,
    StockDdeHotRankPageModel,
    StockDdeObservationPageModel,
    StockDdeSignalPerformancePageModel,
    StockDdeTop30PerformancePageModel,
)


class StockDdeService:
    @classmethod
    async def get_combo_page_services(cls, start_date, end_date, page_num, page_size) -> StockDdeComboSignalPageModel:
        rows, total = await asyncio.to_thread(StockDdeDao.get_combo_page, AppConfig.stock_stat_db_path, start_date, end_date, page_num, page_size)
        return StockDdeComboSignalPageModel(rows=rows, total=total, page_num=page_num, page_size=page_size, has_next=page_num * page_size < total)

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

    @classmethod
    async def get_top30_performance_page_services(
        cls, start_date: str | None, end_date: str | None, page_num: int, page_size: int
    ) -> StockDdeTop30PerformancePageModel:
        rows, total = await asyncio.to_thread(
            StockDdeDao.get_top30_performance_page, AppConfig.stock_stat_db_path, start_date, end_date, page_num, page_size
        )
        return StockDdeTop30PerformancePageModel(
            rows=rows, total=total, page_num=page_num, page_size=page_size, has_next=page_num * page_size < total
        )

    @classmethod
    async def get_hot_rank_page_services(
        cls, page_num: int, page_size: int, large_cap: bool | None, high_price: bool | None
    ) -> StockDdeHotRankPageModel:
        rows, total, stat_start_date, stat_end_date = await asyncio.to_thread(
            StockDdeDao.get_hot_rank_page, AppConfig.stock_stat_db_path, page_num, page_size, large_cap, high_price
        )
        return StockDdeHotRankPageModel(
            rows=rows,
            total=total,
            page_num=page_num,
            page_size=page_size,
            has_next=page_num * page_size < total,
            stat_start_date=stat_start_date,
            stat_end_date=stat_end_date,
        )

    @classmethod
    async def get_observation_page_services(
        cls, dimension: str, start_date: str | None, end_date: str | None, page_num: int, page_size: int
    ) -> StockDdeObservationPageModel:
        rows, total, summary = await asyncio.to_thread(
            StockDdeDao.get_observation_page,
            AppConfig.stock_stat_db_path,
            dimension,
            start_date,
            end_date,
            page_num,
            page_size,
        )
        completed_count = summary['completed_count']
        target_hit_count = summary['target_hit_count']
        return StockDdeObservationPageModel(
            rows=rows,
            total=total,
            page_num=page_num,
            page_size=page_size,
            has_next=page_num * page_size < total,
            tradable_count=summary['tradable_count'],
            completed_count=completed_count,
            target_hit_count=target_hit_count,
            target_hit_rate=target_hit_count / completed_count if completed_count else None,
        )
