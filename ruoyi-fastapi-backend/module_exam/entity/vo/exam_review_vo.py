from typing import Literal
from pydantic import BaseModel


class ExamCardRateModel(BaseModel):
    rating: Literal['again', 'hard', 'good', 'easy']
