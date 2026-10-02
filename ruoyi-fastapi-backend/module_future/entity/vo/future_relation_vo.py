from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class FutureRelationModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    group_name: str
    relation_type: str
    source_scope: str
    market_code: str
    contract_prefix: str
    related_scope: str
    related_market_code: str
    related_contract_prefix: str
    review_status: str
    remark: str
