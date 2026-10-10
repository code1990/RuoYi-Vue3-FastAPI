from tools.download_english_word_audio import pronunciations


def test_pronunciations_extracts_uk_and_us_audio():
    html = '<span class="word-spell">英 [wɔːl]</span><span class="word-spell-audio" data-url="//cdn.example/uk.mp3"></span><span class="word-spell">美 [wɑl]</span><span class="word-spell-audio" data-url="/us.mp3"></span>'
    assert pronunciations('https://example.com/word', html) == [('uk', 'wɔːl', 'https://cdn.example/uk.mp3'), ('us', 'wɑl', 'https://example.com/us.mp3')]
