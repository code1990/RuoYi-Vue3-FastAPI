from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class TrainingDecisionCreateModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    contract_code: str = Field(min_length=1, max_length=40)
    decision: Literal['多', '空', '放弃']
    reason: str = Field(min_length=2, max_length=500)


class TrainingDecisionModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    decision_id: int
    trade_date: date
    contract_code: str
    contract_name: str
    decision: str
    reason: str
    entry_price: float
    settle_date: date | None
    settle_price: float | None
    pnl_rate: float | None
    status: str
    create_time: datetime
