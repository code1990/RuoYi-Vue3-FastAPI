from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class StockFundVisualBarModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    trade_date: str
    value: float | None = None


class StockFundVisualHistoryModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    main_fund: list[StockFundVisualBarModel]
    margin: list[StockFundVisualBarModel]
    dde: list[StockFundVisualBarModel]
