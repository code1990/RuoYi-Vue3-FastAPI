from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class StockCompanyCompareQuoteModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    stock_code: str
    trade_date: int
    close: float
    high: float


class StockCompanyCompareCompanyModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    stock_code: str
    stock_name: str
    industry: str
    concept: str
    market_cap: float
    report_date: str | None = None
    main_holding_rate: float | None = None
    fund_holding_rate: float | None = None


class StockCompanyCompareHistoryModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    companies: list[StockCompanyCompareCompanyModel]
    quotes: list[StockCompanyCompareQuoteModel]
