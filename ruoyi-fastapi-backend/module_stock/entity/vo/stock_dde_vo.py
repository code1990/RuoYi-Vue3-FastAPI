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
    combo_rank: int


class StockDdeComboSignalPageModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    rows: list[StockDdeComboSignalModel]
    total: int
    page_num: int
    page_size: int
    has_next: bool
