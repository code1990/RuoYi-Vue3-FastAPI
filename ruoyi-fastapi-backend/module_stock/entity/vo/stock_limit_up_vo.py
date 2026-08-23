from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class StockLimitUpThemeModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    rank_no: int
    theme_type: str
    theme_name: str
    total_count: int
    values: list[int]


class StockLimitUpThemeListModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    trade_dates: list[str]
    rows: list[StockLimitUpThemeModel]
