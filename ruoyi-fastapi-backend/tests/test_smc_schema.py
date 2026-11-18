from module_project.entity.do.project_do import SmcFeature, SmcRequirement


def test_smc_schema_links_features_to_requirements():
    assert SmcRequirement.__tablename__ == 'smc_requirement'
    assert SmcRequirement.__table_args__[0].name == 'uk_smc_requirement_code'
    assert SmcFeature.__tablename__ == 'smc_feature'
    assert SmcFeature.requirement_id.index is True
    assert SmcFeature.__table_args__[0].name == 'uk_smc_feature_code'
