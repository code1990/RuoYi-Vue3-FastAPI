from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class ProjectModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)
    id: int | None = None
    project_name: str | None = Field(default=None, min_length=1, max_length=200)
    repo_url: str | None = None
    description: str | None = None
    language: str | None = None
    research_direction: str | None = None
    star: int | None = None
    symbol_adaptation: str | None = None
    version: str | None = None
    created_by: str | None = None
    create_time: datetime | None = None
    update_time: datetime | None = None


class ProjectPageQuery(ProjectModel):
    page_num: int = 1
    page_size: int = 10


class FuncModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)
    id: int | None = None
    project_id: int | None = None
    func_name: str | None = None
    func_desc: str | None = None
    logic: str | None = None
    visual_enabled: bool = False
    visual_summary: str | None = None
    language: str | None = None
    func_type: str | None = None
    func_code: str | None = None
    params_template: dict | None = None
    func_tags: str | None = None
    file_path: str | None = None
    class_name: str | None = None
    created_by: str | None = None
    create_time: datetime | None = None
    update_time: datetime | None = None


class FuncPageQuery(FuncModel):
    page_num: int = 1
    page_size: int = 10


class CombinationModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)
    id: int | None = None
    project_id: int | None = None
    combination_name: str | None = None
    research_direction: str | None = None
    description: str | None = None
    function_ids: list[int] | None = None
    create_time: datetime | None = None
    update_time: datetime | None = None


class CombinationPageQuery(CombinationModel):
    page_num: int = 1
    page_size: int = 10


class BacktestModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)
    id: int | None = None
    combination_id: int | None = None
    name: str | None = None
    symbol: str | None = None
    timeframe: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    initial_capital: float | None = None
    status: str | None = None
    total_return: float | None = None
    win_rate: float | None = None
    max_drawdown: float | None = None
    trade_count: int | None = None
    result_data: dict | None = None
    created_by: str | None = None
    create_time: datetime | None = None
    update_time: datetime | None = None


class BacktestPageQuery(BacktestModel):
    page_num: int = 1
    page_size: int = 10


class StrategyModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)
    id: int | None = None
    combination_id: int | None = None
    strategy_name: str | None = None
    description: str | None = None
    status: str | None = None
    created_by: str | None = None
    create_time: datetime | None = None
    update_time: datetime | None = None


class StrategyPageQuery(StrategyModel):
    page_num: int = 1
    page_size: int = 10


class SimAccountModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)
    id: int | None = None
    account_name: str | None = None
    initial_balance: float | None = None
    available_balance: float | None = None
    total_pnl: float | None = None
    status: str | None = None
    created_by: str | None = None
    create_time: datetime | None = None
    update_time: datetime | None = None


class SimAccountPageQuery(SimAccountModel):
    page_num: int = 1
    page_size: int = 10


class ReviewModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)
    id: int | None = None
    source_type: str | None = None
    source_id: int | None = None
    rating: str | None = None
    reason: str | None = None
    lesson: str | None = None
    tags: str | None = None
    created_by: str | None = None
    create_time: datetime | None = None
    update_time: datetime | None = None


class ReviewPageQuery(ReviewModel):
    page_num: int = 1
    page_size: int = 10
