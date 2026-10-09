"""Build scene-themed SVG word animations without replacing existing content."""

import asyncio
import hashlib
import json
import sys
from html import escape
from pathlib import Path

from sqlalchemy import select

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config.database import AsyncSessionLocal
from config.env import UploadConfig
from module_english.entity.do.english_do import EnglishMediaAsset, EnglishScene, EnglishSceneWord, EnglishWord, EnglishWordAnimation


THEMES = {
    '哺乳动物': ('#bde7a6', '🐾'), '禽类': ('#bfe7ff', '🪶'), '爬行动物': ('#f6d29a', '🐢'),
    '鱼类': ('#9ee5f5', '🐟'), '昆虫': ('#f9dea0', '🐝'), '甲壳动物': ('#a8dfeb', '🦀'),
    '蠕虫': ('#d8b38b', '🌱'), '花': ('#ffd7a8', '🌸'), '树': ('#b9dfaa', '🌳'),
    '动物': ('#f6cd82', '🦁'), '植物': ('#b9e7b5', '🍃'),
}


def render(word: str, scene: str) -> str:
    color, icon = THEMES[scene]
    return f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>
*{{box-sizing:border-box}}body{{margin:0;overflow:hidden;background:{color};font-family:system-ui,sans-serif}}svg{{width:100vw;height:100vh;min-height:260px}}.bubble{{animation:float 1.7s ease-in-out infinite alternate}}.spark{{animation:spin 3s linear infinite;transform-origin:center}}.word{{font-size:54px;font-weight:900;fill:#24435c}}.scene{{font-size:22px;font-weight:800;fill:#477168}}@keyframes float{{to{{translate:0 -20px}}}}@keyframes spin{{to{{rotate:360deg}}}}
</style><svg viewBox="0 0 640 420" role="img" aria-label="{escape(word)} English word"><rect width="640" height="420" rx="34" fill="{color}"/><g class="spark"><circle cx="85" cy="92" r="13" fill="#fff"/><circle cx="548" cy="105" r="9" fill="#fff"/><circle cx="520" cy="320" r="12" fill="#fff"/></g><g class="bubble"><circle cx="320" cy="190" r="104" fill="#fff" opacity=".88"/><text x="320" y="145" text-anchor="middle" font-size="70">{icon}</text><text x="320" y="230" text-anchor="middle" class="word">{escape(word)}</text></g><rect x="185" y="330" width="270" height="46" rx="23" fill="#fff" opacity=".72"/><text x="320" y="360" text-anchor="middle" class="scene">{escape(scene)} · Let's learn!</text></svg>'''


async def main() -> None:
    root = Path(UploadConfig.UPLOAD_PATH).resolve() / 'english/words'
    root.mkdir(parents=True, exist_ok=True)
    async with AsyncSessionLocal() as db:
        rows = (await db.execute(select(EnglishWord, EnglishScene).join(EnglishSceneWord, EnglishSceneWord.word_id == EnglishWord.word_id).join(EnglishScene, EnglishScene.scene_id == EnglishSceneWord.scene_id).where(EnglishWord.source_url.like('https://koolearn.com/%')).order_by(EnglishWord.word_id, EnglishScene.sort_no))).all()
        primary_scene, built = {}, 0
        for word, scene in rows:
            primary_scene.setdefault(word.word_id, scene)
        for word_id, scene in primary_scene.items():
            word = await db.get(EnglishWord, word_id)
            animation = await db.scalar(select(EnglishWordAnimation).where(EnglishWordAnimation.word_id == word_id))
            if animation and animation.animation_type != 'svg':
                continue
            content = render(word.word, scene.title).encode()
            storage_path = f'english/words/word-{word.word_id}.html'
            (root / f'word-{word.word_id}.html').write_bytes(content)
            media = await db.scalar(select(EnglishMediaAsset).where(EnglishMediaAsset.storage_path == storage_path))
            if not media:
                media = EnglishMediaAsset(media_type='animation', storage_path=storage_path)
                db.add(media)
                await db.flush()
            media.sha256, media.file_size, media.status = hashlib.sha256(content).hexdigest(), len(content), 'ready'
            if not animation:
                animation = EnglishWordAnimation(word_id=word_id)
                db.add(animation)
            animation.animation_type, animation.animation_config, animation.media_id, animation.status = 'svg', json.dumps({'scene': scene.title}, ensure_ascii=False), media.media_id, 'published'
            built += 1
        await db.commit()
        print(f'built {built} word animations; preserved {len(primary_scene) - built} existing animations')


if __name__ == '__main__':
    asyncio.run(main())
