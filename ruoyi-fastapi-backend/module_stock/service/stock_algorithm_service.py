import asyncio

from config.env import AppConfig
from module_stock.dao.stock_algorithm_dao import StockAlgorithmDao
from module_stock.entity.vo.stock_algorithm_vo import StockAlgorithmExperimentModel


class StockAlgorithmService:
    @classmethod
    async def get_latest_experiment_services(cls, source_type: str) -> StockAlgorithmExperimentModel | None:
        result = await asyncio.to_thread(StockAlgorithmDao.get_latest_experiment, AppConfig.stock_stat_db_path, source_type)
        return StockAlgorithmExperimentModel.model_validate(result) if result else None
