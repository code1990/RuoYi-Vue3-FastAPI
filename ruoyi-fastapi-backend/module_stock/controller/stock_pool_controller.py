import os
import sqlite3
from pathlib import Path

import requests
from fastapi import HTTPException, Query, Response, status

from common.router import APIRouterPro
from config.env import AppConfig
from utils.response_util import ResponseUtil

stock_pool_controller = APIRouterPro(prefix='/stock/pools', order_num=34, tags=['股票-股票池'])


def formulas() -> list[dict]:
    with sqlite3.connect(AppConfig.stock_stat_db_path) as conn:
        return [dict(id=row[0], name=row[1]) for row in conn.execute("SELECT id,name FROM t_stock_formula WHERE name<>'' ORDER BY id")]


@stock_pool_controller.get('/formulas')
async def get_pool_formulas() -> Response:
    return ResponseUtil.success(data=formulas())


@stock_pool_controller.get('/results')
async def get_pool_results(formula_id: int = Query(alias='formulaId', ge=1), trade_date: int | None = Query(default=None, alias='tradeDate'), limit: int = Query(default=100, ge=1, le=500)) -> Response:
    with sqlite3.connect(AppConfig.stock_stat_db_path) as conn:
        formula = conn.execute("SELECT code FROM t_stock_formula WHERE id=? AND name<>''", (formula_id,)).fetchone()
    if not formula:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='formula not found')
    payload = {'formulaCode': formula[0], 'limit': limit}
    if trade_date:
        payload['tradeDate'] = trade_date
    base_url = os.getenv('STOCK_ADMIN_BASE_URL', 'http://127.0.0.1:8888').rstrip('/')
    try:
        response = requests.post(f'{base_url}/api/selection/day/run', json=payload, timeout=(3, 30))
        response.raise_for_status()
        body = response.json()
    except requests.RequestException as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='stock-admin unavailable') from error
    return ResponseUtil.success(data=body.get('data', body))
