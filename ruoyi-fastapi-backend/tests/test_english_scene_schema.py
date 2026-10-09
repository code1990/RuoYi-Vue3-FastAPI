from module_english.entity.do.english_do import EnglishScene, EnglishSceneWord


def test_scene_models_keep_word_unique_per_scene() -> None:
    assert EnglishScene.__tablename__ == 'english_scene'
    assert 'source_url' in EnglishScene.__table__.columns
    assert EnglishSceneWord.__tablename__ == 'english_scene_word'
    assert {column.name for column in EnglishSceneWord.__table_args__[0].columns} == {'scene_id', 'word_id'}
