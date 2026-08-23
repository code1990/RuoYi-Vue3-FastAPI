from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class StockKdjCandleModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    trade_date: int
    open: float | None = None
    high: float | None = None
    low: float | None = None
    close: float | None = None
    vol: float | None = None
    amount: float | None = None
    vol_rate: float | None = None
    percent: float | None = None
    changes: float | None = None
    pre_close: float | None = None


class StockKdjIndicatorModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    trade_date: int
    period: int
    rsv: float | None = None
    k: float | None = None
    d: float | None = None
    j: float | None = None
    rsv_cross_k: bool
    rsv_cross_d: bool
    golden_cross: bool


class StockKdjHistoryModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    candles: list[StockKdjCandleModel]
    indicators: list[StockKdjIndicatorModel]
