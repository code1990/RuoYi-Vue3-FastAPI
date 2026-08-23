from fastapi import HTTPException, Response, status

from common.router import APIRouterPro
from common.vo import DataResponseModel
from module_stock.entity.vo.stock_algorithm_vo import StockAlgorithmExperimentModel
from module_stock.service.stock_algorithm_service import StockAlgorithmService
from utils.response_util import ResponseUtil

stock_algorithm_controller = APIRouterPro(prefix='/stock/algorithm', order_num=37, tags=['股票-算法实验'])


@stock_algorithm_controller.get('/dde/latest', summary='查询最新DDE二分实验', response_model=DataResponseModel[StockAlgorithmExperimentModel | None])
async def get_stock_algorithm_dde_latest() -> Response:
    try:
        result = await StockAlgorithmService.get_latest_experiment_services('dde')
    except FileNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Stock data source unavailable') from error
    return ResponseUtil.success(data=result)
