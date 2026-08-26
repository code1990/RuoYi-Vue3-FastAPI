import asyncio

from config.env import AppConfig
from module_stock.dao.stock_algorithm_dao import StockAlgorithmDao
from module_stock.entity.vo.stock_algorithm_vo import StockAlgorithmExperimentModel, StockAlgorithmExperimentSummaryModel, StockAlgorithmRuleCandidateModel


class StockAlgorithmService:
    @classmethod
    async def get_experiment_services(cls, source_type: str, experiment_key: str) -> StockAlgorithmExperimentModel | None:
        rows = await asyncio.to_thread(StockAlgorithmDao.get_experiments, AppConfig.stock_stat_db_path, source_type, experiment_key)
        return StockAlgorithmExperimentModel.model_validate(rows[0]) if rows else None

    @classmethod
    async def get_experiment_list_services(cls, source_type: str, status: str | None) -> list[StockAlgorithmExperimentSummaryModel]:
        rows = await asyncio.to_thread(StockAlgorithmDao.get_experiments, AppConfig.stock_stat_db_path, source_type, None, status)
        return [StockAlgorithmExperimentSummaryModel.model_validate(row) for row in rows]


    @classmethod
    async def get_rule_candidates_services(cls, experiment_key: str | None, status: str | None) -> list[StockAlgorithmRuleCandidateModel]:
        rows = await asyncio.to_thread(StockAlgorithmDao.get_rule_candidates, AppConfig.stock_stat_db_path, experiment_key, status)
        return [StockAlgorithmRuleCandidateModel.model_validate(row) for row in rows]
