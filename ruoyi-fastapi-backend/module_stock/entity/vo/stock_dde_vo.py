from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class StockDdeSignalPerformanceModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    stock_code: str = Field(description='股票代码')
    trade_date: str = Field(description='信号交易日，YYYYMMDD')
    stock_name: str = Field(description='股票名称')
    signal_slot: str = Field(description='最早信号时段')
    entry_price: float = Field(description='买入价')
    signal_change_pct: float | None = Field(default=None, description='信号时涨跌幅')
    large_net_amount: float | None = Field(default=None, description='大单净额')
    market_cap: float | None = Field(default=None, description='市值')
    main_net_ratio: float | None = Field(default=None, description='主力净流入强度')
    industry_name: str = Field(description='行业')
    close_return_pct: float | None = Field(default=None, description='尾盘涨幅')
    t1_max_return_pct: float | None = Field(default=None, description='T+1涨幅')
    t2_max_return_pct: float | None = Field(default=None, description='T+2涨幅')
    t3_max_return_pct: float | None = Field(default=None, description='T+3涨幅')
    t4_max_return_pct: float | None = Field(default=None, description='T+4涨幅')
    t5_max_return_pct: float | None = Field(default=None, description='T+5涨幅')


class StockDdeSignalPerformancePageModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    rows: list[StockDdeSignalPerformanceModel]
    total: int
    page_num: int
    page_size: int
    has_next: bool


class StockDdeTop30PerformanceModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    stock_code: str
    trade_date: str
    stock_name: str
    signal_slot: str
    signal_rank_no: int
    raw_rank_no: int
    entry_price: float
    signal_change_pct: float | None = None
    main_net_amount: float | None = None
    market_cap: float | None = None
    main_net_ratio: float | None = None
    industry_name: str
    close_return_pct: float | None = None
    t1_max_return_pct: float | None = None
    t2_max_return_pct: float | None = None
    t3_max_return_pct: float | None = None
    t4_max_return_pct: float | None = None
    t5_max_return_pct: float | None = None


class StockDdeTop30PerformancePageModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    rows: list[StockDdeTop30PerformanceModel]
    total: int
    page_num: int
    page_size: int
    has_next: bool


class StockDdeComboSignalModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    signal_date: str
    previous_signal_date: str
    stock_code: str
    stock_name: str
    previous_signal_count: int
    today_signal_count: int
    today_morning_count: int
    today_noon_count: int
    today_close_count: int
    today_best_rank: int
    today_main_net_ratio: float
    previous_main_net_ratio: float
    entry_price: float | None = None
    current_price: float | None = None
    combo_rank: int
    close_return_pct: float | None = None
    t1_max_return_pct: float | None = None
    t2_max_return_pct: float | None = None
    t3_max_return_pct: float | None = None
    t4_max_return_pct: float | None = None
    t5_max_return_pct: float | None = None


class StockDdeComboSignalPageModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    rows: list[StockDdeComboSignalModel]
    total: int
    page_num: int
    page_size: int
    has_next: bool


class StockDdeHotRankModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    rank_no: int
    stock_code: str
    stock_name: str
    appearance_count: int
    signal_day_count: int
    morning_count: int
    noon_count: int
    close_count: int
    recent_5_count: int
    latest_signal_date: str
    latest_signal_slot: str
    best_rank: int
    average_rank: float
    limit_up_count: int
    tradable_signal_count: int
    tradable_sample_day_count: int
    completed_tradable_sample_day_count: int
    target_hit_count: int
    target_hit_rate: float | None = None
    latest_tail_price: float | None = None
    latest_tail_market_cap: float | None = None
    is_large_cap: bool
    is_high_price: bool
    is_latest_signal_limit_up: bool


class StockDdeHotRankPageModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    rows: list[StockDdeHotRankModel]
    total: int
    page_num: int
    page_size: int
    has_next: bool
    stat_start_date: str | None = None
    stat_end_date: str | None = None


class StockDdeObservationModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    trade_date: str
    stock_code: str
    stock_name: str
    morning_count: int
    noon_count: int
    close_count: int
    signal_count: int
    best_rank: int
    combo_type: str
    entry_price: float
    market_cap: float
    change_pct: float | None = None
    limit_up_slots: list[str] = []
    is_limit_up: bool
    is_tradable: bool
    is_completed: bool
    target_hit: bool | None = None


class StockDdeObservationPageModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    rows: list[StockDdeObservationModel]
    total: int
    page_num: int
    page_size: int
    has_next: bool
    tradable_count: int
    completed_count: int
    target_hit_count: int
    target_hit_rate: float | None = None
