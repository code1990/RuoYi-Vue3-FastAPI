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
