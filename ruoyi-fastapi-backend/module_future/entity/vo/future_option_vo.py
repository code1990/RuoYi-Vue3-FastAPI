from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class FutureOptionContractModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    thscode: str
    ticker: str | None = None
    name: str | None = None
    list_date: str | None = None
    last_trade_date: str | None = None


class FutureOptionContractPageModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    rows: list[FutureOptionContractModel]
    total: int
    page_num: int
    page_size: int
    has_next: bool
