import asyncio

from config.env import AppConfig
from module_future.dao.future_quote_dao import FutureQuoteDao
from module_future.entity.vo.future_profit_effect_vo import FutureProfitEffectModel


class FutureProfitEffectService:
    @classmethod
    async def get_list_services(cls) -> list[FutureProfitEffectModel]:
        rows = await asyncio.to_thread(FutureQuoteDao.get_profit_effect, AppConfig.future_stat_db_path)
        return [FutureProfitEffectModel.model_validate(row) for row in rows]
