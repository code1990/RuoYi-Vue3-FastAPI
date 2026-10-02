import asyncio

from config.env import AppConfig
from module_future.dao.future_option_dao import FutureOptionDao
from module_future.entity.vo.future_option_vo import FutureOptionContractPageModel


class FutureOptionService:
    @classmethod
    async def get_io_contracts(cls, page_num: int, page_size: int) -> FutureOptionContractPageModel:
        rows, total = await asyncio.to_thread(FutureOptionDao.get_io_contracts, AppConfig.future_stat_db_path, page_num, page_size)
        return FutureOptionContractPageModel(rows=rows, total=total, page_num=page_num, page_size=page_size, has_next=page_num * page_size < total)
