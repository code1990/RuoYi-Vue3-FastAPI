from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class PaperTradeOpenModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    contract_code: str = Field(min_length=1, max_length=40)
    side: Literal['多', '空']
    quantity: int = Field(ge=1, le=100)


class PaperPositionModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)
    position_id: int
    contract_code: str
    contract_name: str
    side: str
    quantity: int
    average_price: float
    last_price: float
    margin: float
    unrealized_pnl: float


class PaperOrderModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)
    order_id: int
    contract_code: str
    contract_name: str
    side: str
    action: str
    quantity: int
    price: float
    realized_pnl: float | None
    create_time: datetime


class PaperAccountModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    cash: float
    equity: float
    unrealized_pnl: float
    positions: list[PaperPositionModel]
