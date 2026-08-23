import asyncio

from config.env import AppConfig
from module_stock.dao.stock_dde_dao import StockDdeDao
from module_stock.entity.vo.stock_dde_vo import (
    StockDdeComboSignalPageModel,
    StockDdeComboStatisticsModel,
    StockDdeHotRankPageModel,
    StockDdeObservationPageModel,
    StockDdeObservationStatisticsModel,
    StockDdeSignalPerformancePageModel,
    StockDdeTop30PerformancePageModel,
)


class StockDdeService:
    @classmethod
    async def get_combo_page_services(cls, start_date, end_date, page_num, page_size, sort_by, sort_order) -> StockDdeComboSignalPageModel:
        rows, total = await asyncio.to_thread(StockDdeDao.get_combo_page, AppConfig.stock_stat_db_path, start_date, end_date, page_num, page_size, sort_by, sort_order)
        return StockDdeComboSignalPageModel(rows=rows, total=total, page_num=page_num, page_size=page_size, has_next=page_num * page_size < total)

    @classmethod
    async def get_combo_statistics_services(
        cls, start_date: str | None, end_date: str | None, target_return_pct: float,
    ) -> list[StockDdeComboStatisticsModel]:
        rows = await asyncio.to_thread(StockDdeDao.get_combo_statistics, AppConfig.stock_stat_db_path, start_date, end_date, target_return_pct)
        return [StockDdeComboStatisticsModel.model_validate(row) for row in rows]

    @classmethod
    async def get_signal_performance_page_services(
        cls, start_date: str | None, end_date: str | None, page_num: int, page_size: int, sort_by: str | None, sort_order: str | None,
    ) -> StockDdeSignalPerformancePageModel:
        rows, total = await asyncio.to_thread(
            StockDdeDao.get_signal_performance_page,
            AppConfig.stock_stat_db_path,
            start_date,
            end_date,
            page_num,
            page_size,
            sort_by,
            sort_order,
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
        cls, signal_slot: str | None, start_date: str | None, end_date: str | None, page_num: int, page_size: int, sort_by: str | None, sort_order: str | None,
    ) -> StockDdeTop30PerformancePageModel:
        rows, total = await asyncio.to_thread(
            StockDdeDao.get_top30_performance_page, AppConfig.stock_stat_db_path, signal_slot, start_date, end_date, page_num, page_size, sort_by, sort_order
        )
        return StockDdeTop30PerformancePageModel(
            rows=rows, total=total, page_num=page_num, page_size=page_size, has_next=page_num * page_size < total
        )

    @classmethod
    async def get_signal_statistics_services(cls, start_date: str | None, end_date: str | None, target_return_pct: float) -> list[dict]:
        return await asyncio.to_thread(StockDdeDao.get_signal_statistics, AppConfig.stock_stat_db_path, start_date, end_date, target_return_pct)

    @classmethod
    async def get_hot_rank_page_services(
        cls, page_num: int, page_size: int, large_cap: bool | None, high_price: bool | None, sort_by: str | None, sort_order: str | None,
    ) -> StockDdeHotRankPageModel:
        rows, total, stat_start_date, stat_end_date = await asyncio.to_thread(
            StockDdeDao.get_hot_rank_page, AppConfig.stock_stat_db_path, page_num, page_size, large_cap, high_price, sort_by, sort_order
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
        cls, dimension: str, start_date: str | None, end_date: str | None, page_num: int, page_size: int, sort_by: str | None, sort_order: str | None,
    ) -> StockDdeObservationPageModel:
        rows, total, summary = await asyncio.to_thread(
            StockDdeDao.get_observation_page,
            AppConfig.stock_stat_db_path,
            dimension,
            start_date,
            end_date,
            page_num,
            page_size,
            sort_by,
            sort_order,
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

    @classmethod
    async def get_observation_statistics_services(
        cls, start_date: str | None, end_date: str | None,
    ) -> list[StockDdeObservationStatisticsModel]:
        rows = await asyncio.to_thread(StockDdeDao.get_observation_statistics, AppConfig.stock_stat_db_path, start_date, end_date)
        return [StockDdeObservationStatisticsModel.model_validate(row) for row in rows]
