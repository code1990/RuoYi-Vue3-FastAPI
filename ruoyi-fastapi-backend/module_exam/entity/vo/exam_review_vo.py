from typing import Literal
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class ExamCardRateModel(BaseModel):
    rating: Literal['again', 'hard', 'good', 'easy']


class ExamCardAiSummaryVersionCreateModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)

    title: str = Field(min_length=1, max_length=100)
    ai_summary: str = Field(min_length=1, max_length=300)
