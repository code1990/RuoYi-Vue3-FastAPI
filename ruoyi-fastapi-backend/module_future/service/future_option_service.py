import asyncio

from config.env import AppConfig
from module_future.dao.future_option_dao import FutureOptionDao
from module_future.entity.vo.future_option_vo import FutureOptionContractSummaryPageModel, FutureOptionVarietyModel, FutureOptionVarietyPageModel


class FutureOptionService:
    @classmethod
    async def get_contract_summaries(cls, page_num: int, page_size: int, variety_code: str | None, exchange_code: str | None) -> FutureOptionContractSummaryPageModel:
        rows, total = await asyncio.to_thread(FutureOptionDao.get_contract_summaries, AppConfig.future_stat_db_path, page_num, page_size, variety_code, exchange_code)
        return FutureOptionContractSummaryPageModel(rows=rows, total=total, page_num=page_num, page_size=page_size, has_next=page_num * page_size < total)

    @classmethod
    async def get_varieties(cls, page_num: int, page_size: int) -> FutureOptionVarietyPageModel:
        rows, total = await asyncio.to_thread(FutureOptionDao.get_varieties, AppConfig.future_stat_db_path, page_num, page_size)
        return FutureOptionVarietyPageModel(rows=rows, total=total, page_num=page_num, page_size=page_size, has_next=page_num * page_size < total)
