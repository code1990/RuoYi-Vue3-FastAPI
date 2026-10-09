from tools.build_english_word_animations import render


def test_word_animation_escapes_word_and_keeps_scene_label() -> None:
    html = render('fish & chips', '鱼类')
    assert 'fish &amp; chips' in html
    assert '鱼类' in html and '@keyframes' in html
