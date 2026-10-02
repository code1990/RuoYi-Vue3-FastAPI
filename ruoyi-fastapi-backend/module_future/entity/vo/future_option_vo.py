from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class FutureOptionContractSummaryModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    code: str
    name: str | None = None
    contract_code_summary: str | None = None
    name_summary: str | None = None


class FutureOptionContractSummaryPageModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    rows: list[FutureOptionContractSummaryModel]
    total: int
    page_num: int
    page_size: int
    has_next: bool


class FutureOptionVarietyModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    variety_code: str
    name: str | None = None
    exchange_code: str | None = None
    exchange_name: str | None = None
    settlement_type: str | None = None
    contract_multiplier: float | None = None


class FutureOptionVarietyPageModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    rows: list[FutureOptionVarietyModel]
    total: int
    page_num: int
    page_size: int
    has_next: bool


class FutureOptionChainModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    thscode: str
    name: str | None = None
    option_type: str
    strike_price: float
    day_change_rate: float | None = None


class FutureOptionUnderlyingModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    underlying_code: str
    name: str | None = None


class FutureOptionUnderlyingFutureModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    contract_code: str
    contract_name: str = ''
    last_px: float | None = None
    px_change_rate: float | None = None


class FutureOptionChainResponseModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    future: FutureOptionUnderlyingFutureModel
    rows: list[FutureOptionChainModel]


class FutureOptionLinkageSummaryModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    contract_code: str
    contract_name: str = ''
    last_px: float | None = None
    px_change_rate: float | None = None
    put: dict | None = None
    call: dict | None = None
