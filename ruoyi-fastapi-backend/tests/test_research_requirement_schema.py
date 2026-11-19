from module_project.entity.do.project_do import ResearchFeature, ResearchRequirement
from module_project.controller.project_controller import _function_ids_exist
from unittest.mock import AsyncMock
import asyncio


def test_research_requirement_schema_links_features_to_requirements():
    assert ResearchRequirement.__tablename__ == 'research_requirement'
    assert ResearchRequirement.__table_args__[0].name == 'uk_research_requirement_code'
    assert ResearchRequirement.core_concepts.type.python_type is str
    assert ResearchRequirement.core_viewpoints.type.python_type is str
    assert ResearchFeature.__tablename__ == 'research_feature'
    assert ResearchFeature.requirement_id.index is True
    assert ResearchFeature.function_ids.type.__class__.__name__ == 'JSON'
    assert ResearchFeature.__table_args__[0].name == 'uk_research_feature_code'


def test_function_id_check_rejects_missing_function():
    result = type('Result', (), {'scalar_one': lambda self: 1})()
    db = type('Db', (), {'execute': AsyncMock(return_value=result)})()
    assert asyncio.run(_function_ids_exist(db, [3, 5])) is False
