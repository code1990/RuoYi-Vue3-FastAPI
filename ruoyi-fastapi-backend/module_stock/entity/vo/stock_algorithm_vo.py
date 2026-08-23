from typing import Any

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class StockAlgorithmExperimentModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    experiment_key: str
    data_start_date: str
    data_end_date: str
    target_rule: str
    feature_rules: dict[str, Any]
    tree: dict[str, Any]
    train_metrics: dict[str, Any]
    validation_metrics: dict[str, Any]
    status: str
    conclusion: str
