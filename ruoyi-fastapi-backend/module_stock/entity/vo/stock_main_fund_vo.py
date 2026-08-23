from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class StockMainFundPerformanceModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    stock_code: str = Field(description='股票代码')
    signal_date: str = Field(description='信号日期，YYYYMMDD')
    strategy: str = Field(description='策略')
    signal_type: str = Field(description='信号类型')
    stock_name: str = Field(description='股票名称')
    industry_name: str = Field(description='行业')
    entry_price: float = Field(description='买入价')
    signal_score: float | None = Field(default=None, description='信号评分')
    strength_10d: float | None = Field(default=None, description='10日强度')
    strength_55d: float | None = Field(default=None, description='55日强度')
    flow_5d: float | None = Field(default=None, description='5日资金流')
    flow_10d: float | None = Field(default=None, description='10日资金流')
    flow_20d: float | None = Field(default=None, description='20日资金流')
    flow_55d: float | None = Field(default=None, description='55日资金流')
    consecutive_inflow_days: int | None = Field(default=None, description='连续流入天数')
    close_return_pct: float | None = Field(default=None, description='尾盘涨幅')
    t1_max_return_pct: float | None = Field(default=None, description='T+1最高涨幅')
    t2_max_return_pct: float | None = Field(default=None, description='T+2最高涨幅')
    t3_max_return_pct: float | None = Field(default=None, description='T+3最高涨幅')
    t4_max_return_pct: float | None = Field(default=None, description='T+4最高涨幅')
    t5_max_return_pct: float | None = Field(default=None, description='T+5最高涨幅')


class StockMainFundPerformancePageModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    rows: list[StockMainFundPerformanceModel]
    total: int
    page_num: int
    page_size: int
    has_next: bool


class StockMainFundStatisticsModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    signal_date: str
    inflow_band: str
    success_count: int
    failure_count: int
    sample_count: int
