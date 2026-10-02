from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class FutureProfitEffectModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    contract_code: str
    contract_name: str
    market_date: str
    open_px: float
    last_px: float
    direction: str
    price_spread: float
    net_profit: float
    margin: float
    fee: float
    capital: float
    profit_rate: float
    stock_same_move_profit: float
    stock_required_change_rate: float
