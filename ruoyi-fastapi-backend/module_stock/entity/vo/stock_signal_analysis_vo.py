from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class StockSignalAnalysisRowModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    signal_name: str
    stock_code: str
    stock_name: str = ''
    industry_name: str = ''
    concept: str = ''
    stat_year: int | None = None
    sample_count: int | None = None
    win_count_1: int | None = None
    win_count_2: int | None = None
    win_rate_1: float | None = None
    win_rate_2: float | None = None
    sample_count_1: int | None = None
    sample_count_2: int | None = None


class StockSignalAnalysisPageModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    rows: list[StockSignalAnalysisRowModel]
    total: int
    page_num: int
    page_size: int
    has_next: bool
    table_name: str
    signal_names: list[str]
