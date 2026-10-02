from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from module_future.entity.vo.future_relation_vo import FutureRelationModel


class FutureRelationService:
    @classmethod
    async def get_list_services(cls, db: AsyncSession) -> list[FutureRelationModel]:
        result = await db.execute(
            text('''SELECT group_name, relation_type, source_scope, market_code, contract_prefix,
                           related_scope, related_market_code, related_contract_prefix, review_status, remark
                    FROM t_future_product_link ORDER BY sort_order, link_id''')
        )
        return [FutureRelationModel.model_validate(row) for row in result.mappings().all()]
