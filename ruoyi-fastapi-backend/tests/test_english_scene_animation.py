from tools.build_english_scene_animations import SCENES, render


def test_every_imported_scene_has_an_svg_animation() -> None:
    assert len(SCENES) == 11
    for title, (subtitle, words, color, kind) in SCENES.items():
        html = render(title, subtitle, words, color, kind)
        assert '<svg' in html and words in html and '@keyframes' in html
