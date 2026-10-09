"""Import the public Koolearn animal and plant word categories into English scenes."""

import asyncio
import re
import sys
import time
from html import unescape
from pathlib import Path
from urllib.request import Request, urlopen

from sqlalchemy import select

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config.database import AsyncSessionLocal
from module_english.entity.do.english_do import EnglishScene, EnglishSceneWord, EnglishWord


BASE_URL = 'https://koolearn.com'
CATEGORY_URL = f'{BASE_URL}/dict/fenlei_7_0_1.html'
SCENE_RE = re.compile(r'<div class="word-title">([^<]+)<a class="word-more" href="(/dict/tag_\d+_1\.html)">更多</a></div>\s*<div class="word-box">(.*?)</div>', re.S)
WORD_RE = re.compile(r'<a class="word" href="(/dict/wd_\d+\.html)">([^<]+)</a>')


def download(url: str) -> str:
    request = Request(url, headers={'User-Agent': 'Mozilla/5.0 (EnglishGarden content import)'})
    with urlopen(request, timeout=20) as response:
        return response.read().decode('utf-8', 'replace')


def scenes() -> list[tuple[str, str, list[tuple[str, str]]]]:
    catalog = download(CATEGORY_URL)
    result = []
    for title, path, _ in SCENE_RE.findall(catalog):
        time.sleep(0.2)
        words = [(unescape(word).strip(), f'{BASE_URL}{word_path}') for word_path, word in WORD_RE.findall(download(f'{BASE_URL}{path}'))]
        result.append((unescape(title).strip(), f'{BASE_URL}{path}', words))
    return result


async def save(rows: list[tuple[str, str, list[tuple[str, str]]]]) -> None:
    async with AsyncSessionLocal() as db:
        for scene_sort, (title, source_url, words) in enumerate(rows):
            scene = await db.scalar(select(EnglishScene).where(EnglishScene.title == title))
            if not scene:
                scene = EnglishScene(title=title, description=f'{title}英语词汇', source_url=source_url, status='published', sort_no=scene_sort)
                db.add(scene)
                await db.flush()
            for word_sort, (text, word_source_url) in enumerate(dict.fromkeys(words)):
                word = await db.scalar(select(EnglishWord).where(EnglishWord.word == text))
                if not word:
                    word = EnglishWord(word=text, meaning_zh='', source_url=word_source_url)
                    db.add(word)
                    await db.flush()
                relation = await db.scalar(select(EnglishSceneWord).where(EnglishSceneWord.scene_id == scene.scene_id, EnglishSceneWord.word_id == word.word_id))
                if not relation:
                    db.add(EnglishSceneWord(scene_id=scene.scene_id, word_id=word.word_id, sort_no=word_sort))
        await db.commit()


async def main() -> None:
    rows = await asyncio.to_thread(scenes)
    await save(rows)
    print(f'imported {len(rows)} scenes and {sum(len(words) for _, _, words in rows)} scene-word links')


if __name__ == '__main__':
    asyncio.run(main())
