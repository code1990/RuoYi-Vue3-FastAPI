from module_project.entity.do.project_do import ResearchFeature, ResearchRequirement


def test_research_requirement_schema_links_features_to_requirements():
    assert ResearchRequirement.__tablename__ == 'research_requirement'
    assert ResearchRequirement.__table_args__[0].name == 'uk_research_requirement_code'
    assert ResearchRequirement.core_concepts.type.python_type is str
    assert ResearchRequirement.core_viewpoints.type.python_type is str
    assert ResearchFeature.__tablename__ == 'research_feature'
    assert ResearchFeature.requirement_id.index is True
    assert ResearchFeature.__table_args__[0].name == 'uk_research_feature_code'
