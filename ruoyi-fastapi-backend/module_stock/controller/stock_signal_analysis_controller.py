from typing import Annotated

from fastapi import HTTPException, Query, Response, status

from common.router import APIRouterPro
from common.vo import DataResponseModel
from module_stock.entity.vo.stock_signal_analysis_vo import StockSignalAnalysisPageModel
from module_stock.service.stock_signal_analysis_service import StockSignalAnalysisService
from utils.response_util import ResponseUtil


stock_signal_analysis_controller = APIRouterPro(prefix='/stock/signal-analysis', order_num=35, tags=['股票-信号分析'])


@stock_signal_analysis_controller.get('/page', summary='查询信号三表分析', response_model=DataResponseModel[StockSignalAnalysisPageModel])
async def get_stock_signal_analysis_page(
    table: Annotated[str, Query(pattern=r'^(raw|filtered|total)$')] = 'raw',
    signal_name: Annotated[str | None, Query(alias='signalName', max_length=100)] = None,
    stock_code: Annotated[str | None, Query(alias='stockCode', pattern=r'^\d{6}$')] = None,
    year: Annotated[int | None, Query(ge=2000, le=2100)] = None,
    page_num: Annotated[int, Query(alias='pageNum', ge=1)] = 1,
    page_size: Annotated[int, Query(alias='pageSize', ge=1, le=200)] = 20,
) -> Response:
    try:
        result = await StockSignalAnalysisService.get_page_services(table, signal_name, stock_code, year, page_num, page_size)
    except FileNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Stock data source unavailable') from error
    return ResponseUtil.success(data=result)
