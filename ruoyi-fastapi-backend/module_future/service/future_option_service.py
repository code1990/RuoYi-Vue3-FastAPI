import asyncio

from config.env import AppConfig
from module_future.dao.future_option_dao import FutureOptionDao
from module_future.entity.vo.future_option_vo import FutureOptionChainModel, FutureOptionChainResponseModel, FutureOptionContractSummaryPageModel, FutureOptionUnderlyingModel, FutureOptionVarietyModel, FutureOptionVarietyPageModel


class FutureOptionService:
    @classmethod
    async def get_contract_summaries(cls, page_num: int, page_size: int, variety_code: str | None, exchange_code: str | None) -> FutureOptionContractSummaryPageModel:
        rows, total = await asyncio.to_thread(FutureOptionDao.get_contract_summaries, AppConfig.future_stat_db_path, page_num, page_size, variety_code, exchange_code)
        return FutureOptionContractSummaryPageModel(rows=rows, total=total, page_num=page_num, page_size=page_size, has_next=page_num * page_size < total)

    @classmethod
    async def get_varieties(cls, page_num: int, page_size: int) -> FutureOptionVarietyPageModel:
        rows, total = await asyncio.to_thread(FutureOptionDao.get_varieties, AppConfig.future_stat_db_path, page_num, page_size)
        return FutureOptionVarietyPageModel(rows=rows, total=total, page_num=page_num, page_size=page_size, has_next=page_num * page_size < total)

    @classmethod
    async def get_underlying_chain(cls, underlying_code: str) -> FutureOptionChainResponseModel:
        rows, future = await asyncio.gather(
            asyncio.to_thread(FutureOptionDao.get_underlying_chain, AppConfig.future_stat_db_path, underlying_code),
            asyncio.to_thread(FutureOptionDao.get_underlying_future, AppConfig.future_stat_db_path, underlying_code),
        )
        return FutureOptionChainResponseModel(future=future, rows=rows)

    @classmethod
    async def get_underlyings(cls) -> list[FutureOptionUnderlyingModel]:
        rows = await asyncio.to_thread(FutureOptionDao.get_underlyings, AppConfig.future_stat_db_path)
        return [FutureOptionUnderlyingModel.model_validate(row) for row in rows]
