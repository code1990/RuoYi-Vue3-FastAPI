from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class StockMarginLongPerformanceModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    stock_code: str = Field(description='股票代码')
    margin_trade_date: str = Field(description='两融数据日')
    signal_date: str = Field(description='信号交易日')
    stock_name: str = Field(description='股票名称')
    rank_no: int = Field(description='做多排名')
    score: float = Field(description='评分')
    participation_ratio: float = Field(description='融资买入成交参与度')
    balance_change_ratio: float = Field(description='融资余额变化强度')
    entry_price: float = Field(description='买入价')
    industry_name: str = Field(description='行业')
    close_return_pct: float | None = Field(default=None, description='尾盘涨幅')
    t1_max_return_pct: float | None = Field(default=None, description='T+1最高涨幅')
    t2_max_return_pct: float | None = Field(default=None, description='T+2最高涨幅')
    t3_max_return_pct: float | None = Field(default=None, description='T+3最高涨幅')
    t4_max_return_pct: float | None = Field(default=None, description='T+4最高涨幅')
    t5_max_return_pct: float | None = Field(default=None, description='T+5最高涨幅')


class StockMarginLongPerformancePageModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    rows: list[StockMarginLongPerformanceModel]
    total: int
    page_num: int
    page_size: int
    has_next: bool
