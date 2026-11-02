from datetime import datetime

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class FileKeywordOptionModel(BaseModel):
    id: str
    name: str


class FileDetailOptionsModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    keywords: list[FileKeywordOptionModel]
    topics: list[str]
    exts: list[str]
    categories: list[int]
    types: list[str]
    valids: list[str]
    haspwds: list[str]


class FileDetailModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: str
    topic: str
    filename: str | None = None
    size: str | None = None
    ext: str | None = None
    category: int | None = None
    type: str | None = None
    url: str | None = None
    pwd: str | None = None
    haspwd: str | None = None
    valid: str | None = None
    ctime: datetime | None = None
    utime: datetime | None = None


class FileDetailPageModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    rows: list[FileDetailModel]
    total: int
    page_num: int
    page_size: int
