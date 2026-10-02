import asyncio
import json
import sqlite3
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from config.env import AppConfig
from module_future.entity.vo.future_relation_vo import FutureRelationModel


class FutureRelationService:
    @classmethod
    async def get_list_services(cls, db: AsyncSession) -> list[FutureRelationModel]:
        result = await db.execute(
            text('''SELECT link_id, group_name, relation_type, source_scope, market_code, product_code, contract_prefix,
                           related_scope, related_market_code, related_product_code, related_contract_prefix, review_status, remark
                    FROM t_future_product_link ORDER BY sort_order, link_id''')
        )
        rows = [FutureRelationModel.model_validate(row) for row in result.mappings().all()]
        return await asyncio.to_thread(cls._with_quotes, rows)

    @staticmethod
    def _with_quotes(rows: list[FutureRelationModel]) -> list[FutureRelationModel]:
        path = Path(AppConfig.future_stat_db_path)
        if not path.is_file():
            return rows
        wanted = {(row.market_code, row.product_code, row.contract_prefix) for row in rows}
        wanted |= {(row.related_market_code, row.related_product_code, row.related_contract_prefix) for row in rows}
        selected = {}
        with sqlite3.connect(f'file:{path.resolve().as_posix()}?mode=ro', uri=True) as connection:
            for market, product, code, payload in connection.execute('SELECT market_code, product_code, contract_code, payload_json FROM t_future_quote'):
                for key in wanted:
                    if (market, product) == key[:2] and code.startswith(key[2]):
                        data = json.loads(payload)
                        priority = 2 if '主力' in str(data.get('prod_name', '')) or '888' in code or '001' in code else 1
                        if key not in selected or priority > selected[key][0]:
                            selected[key] = (priority, str(data.get('prod_name') or ''), data.get('px_change_rate'))
        for row in rows:
            source = selected.get((row.market_code, row.product_code, row.contract_prefix), (0, '', None))
            related = selected.get((row.related_market_code, row.related_product_code, row.related_contract_prefix), (0, '', None))
            row.source_contract, row.source_change_rate = source[1:]
            row.related_contract, row.related_change_rate = related[1:]
        return rows
