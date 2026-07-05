from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class StockXgNightDimensionModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    source_type: int = Field(description='夜盘来源：60=60min，240=240min，300=60+240交集')
    label: str = Field(description='维度展示名称')


class StockXgNightCardModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    exists: bool = Field(description='当前维度是否存在统计数据')
    source_type: int = Field(description='夜盘来源')
    label: str = Field(description='维度展示名称')
    trade_date: int | None = Field(default=None, description='出票日期，yyyyMMdd')
    signal_name: str | None = Field(default=None, description='选股器名称')
    total_count: int | None = Field(default=None, description='出票总数')
    ok_count: int | None = Field(default=None, description='3日达标数量')
    ok_rate: Decimal | None = Field(default=None, description='3日达标比例，百分比')
    super_count: int | None = Field(default=None, description='3日超额数量')
    super_rate: Decimal | None = Field(default=None, description='3日超额比例，百分比')
    target_percent: Decimal | None = Field(default=None, description='达标收益阈值')
    super_percent: Decimal | None = Field(default=None, description='超额收益阈值')
    window_days: int | None = Field(default=None, description='统计窗口交易日数')
    updated_at: datetime | None = Field(default=None, description='更新时间')
    empty_reason: str | None = Field(default=None, description='空态原因')


class StockXgNightSuperCardRowModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    signal_name: str = Field(description='选股器名称')
    rank_score: Decimal = Field(description='排序分数，取当前选股器最大超额比例')
    cards: dict[str, StockXgNightCardModel] = Field(description='固定包含240、60、300三个维度卡片')


class StockXgNightSuperCardsModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    trade_date: int | None = Field(default=None, description='当前展示出票日期')
    limit: int = Field(description='返回选股器数量')
    dimensions: list[StockXgNightDimensionModel] = Field(description='固定展示维度')
    rows: list[StockXgNightSuperCardRowModel] = Field(description='选股器卡片行')
