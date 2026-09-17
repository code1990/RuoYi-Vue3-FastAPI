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
    j_trend: str = 'flat'
    rsv_cross_k: int
    rsv_cross_d: int
    golden_cross: int


class StockKdjHistoryModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    candles: list[StockKdjCandleModel]
    indicators: list[StockKdjIndicatorModel]


class StockKdjSignalBacktestModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    stock_code: str
    stock_name: str = ''
    industry_name: str = ''
    concept: str = ''
    signal_date: int
    year: int
    signal_code: str
    active_signals: str = ''
    signal_count: int
    is_candidate: bool
    entry_date: int | None = None
    entry_price: float | None = None
    t1_max_return_pct: float | None = None
    t2_max_return_pct: float | None = None
    t3_max_return_pct: float | None = None
    t4_max_return_pct: float | None = None
    t5_max_return_pct: float | None = None
    t1_close_return_pct: float | None = None
    t2_close_return_pct: float | None = None
    t3_close_return_pct: float | None = None
    t4_close_return_pct: float | None = None
    t5_close_return_pct: float | None = None
    max_return_pct: float | None = None
    exit_return_pct: float | None = None
    target_return_pct: float = 1.8
    target_hit: bool | None = None
    hit_day: int | None = None
    holding_days: int | None = None
    is_completed: bool
    kdj9_rsv: float | None = None
    kdj9_k: float | None = None
    kdj9_d: float | None = None
    kdj9_j: float | None = None
    kdj9_j_trend: str = 'flat'
    kdj90_rsv: float | None = None
    kdj90_k: float | None = None
    kdj90_d: float | None = None
    kdj90_j: float | None = None
    kdj90_j_trend: str = 'flat'


class StockKdjSignalBacktestPageModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    rows: list[StockKdjSignalBacktestModel]
    total: int
    page_num: int
    page_size: int
    has_next: bool
    candidate_count: int
    completed_count: int
    hit_count: int
    hit_rate: float | None = None
    candidates: list[dict] = []
