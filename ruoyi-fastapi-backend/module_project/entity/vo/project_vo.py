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
