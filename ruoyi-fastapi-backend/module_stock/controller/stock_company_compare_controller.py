from typing import Annotated

from fastapi import HTTPException, Query, Response, status

from common.router import APIRouterPro
from common.vo import DataResponseModel
from module_stock.entity.vo.stock_company_compare_vo import StockCompanyCompareHistoryModel, StockCompanyProfileModel
from module_stock.service.stock_company_compare_service import StockCompanyCompareService
from utils.response_util import ResponseUtil

stock_company_compare_controller = APIRouterPro(prefix='/stock/company-compare', order_num=38, tags=['股票-可比公司'])


@stock_company_compare_controller.get('/profile', summary='查询股票行情与资料摘要', response_model=DataResponseModel[StockCompanyProfileModel])
async def get_stock_company_profile(stock_code: Annotated[str, Query(alias='stockCode', pattern=r'^\d{6}$')]) -> Response:
    try:
        result = await StockCompanyCompareService.get_profile_services(stock_code)
    except FileNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Stock data source unavailable') from error
    return ResponseUtil.success(data=result)


@stock_company_compare_controller.get('/history', summary='查询可比公司行情', response_model=DataResponseModel[StockCompanyCompareHistoryModel])
async def get_stock_company_compare(
    stock_codes: Annotated[str, Query(alias='stockCodes')],
) -> Response:
    codes = list(dict.fromkeys(code.strip() for code in stock_codes.split(',')))
    if not 2 <= len(codes) <= 10 or any(len(code) != 6 or not code.isdigit() for code in codes):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='stockCodes must contain 2 to 10 six-digit codes')
    try:
        result = await StockCompanyCompareService.get_history_services(codes)
    except FileNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Stock data source unavailable') from error
    return ResponseUtil.success(data=result)
