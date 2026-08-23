from typing import Annotated

from fastapi import HTTPException, Query, Response, status

from common.router import APIRouterPro
from common.vo import DataResponseModel
from module_stock.entity.vo.stock_algorithm_vo import StockAlgorithmExperimentModel, StockAlgorithmExperimentSummaryModel
from module_stock.service.stock_algorithm_service import StockAlgorithmService
from utils.response_util import ResponseUtil

stock_algorithm_controller = APIRouterPro(prefix='/stock/algorithm', order_num=37, tags=['股票-算法实验'])


@stock_algorithm_controller.get('/dde/list', summary='查询DDE二分实验列表', response_model=DataResponseModel[list[StockAlgorithmExperimentSummaryModel]])
async def get_stock_algorithm_dde_list(
    experiment_status: Annotated[str | None, Query(alias='status', pattern=r'^(observing|rejected)$')] = None,
) -> Response:
    try:
        result = await StockAlgorithmService.get_experiment_list_services('dde', experiment_status)
    except FileNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Stock data source unavailable') from error
    return ResponseUtil.success(data=result)


@stock_algorithm_controller.get('/dde/{experiment_key}', summary='查询DDE二分实验详情', response_model=DataResponseModel[StockAlgorithmExperimentModel | None])
async def get_stock_algorithm_dde_experiment(experiment_key: str) -> Response:
    try:
        result = await StockAlgorithmService.get_experiment_services('dde', experiment_key)
    except FileNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Stock data source unavailable') from error
    return ResponseUtil.success(data=result)
