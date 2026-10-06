from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class FutureQuoteModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    contract_code: str
    contract_name: str = ''
    market_code: str = ''
    market_date: str
    last_px: float | None = None
    px_change_rate: float | None = None
    min5_chgpct: float | None = None
    px_change: float | None = None
    open_px: float | None = None
    high_px: float | None = None
    low_px: float | None = None
    prev_settlement: float | None = None
    market_name: str = ''
    product_name: str = ''


class FutureQuotePageModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    rows: list[FutureQuoteModel]
    total: int
    page_num: int
    page_size: int
    has_next: bool
