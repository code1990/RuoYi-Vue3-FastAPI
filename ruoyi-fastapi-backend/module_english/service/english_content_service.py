from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from module_english.entity.do.english_do import EnglishBook, EnglishBookWord, EnglishMediaAsset, EnglishScene, EnglishSceneWord, EnglishUnit, EnglishWord, EnglishWordAnimation, EnglishWordPronunciation


class EnglishContentService:
    @classmethod
    async def books(cls, db: AsyncSession) -> list[dict]:
        rows = (await db.scalars(select(EnglishBook).where(EnglishBook.status == 'published').order_by(EnglishBook.sort_no, EnglishBook.book_id))).all()
        return [{'book_id': row.book_id, 'title': row.title, 'description': row.description, 'cover_url': row.cover_url} for row in rows]

    @classmethod
    async def units(cls, db: AsyncSession, book_id: int) -> list[dict]:
        rows = (await db.scalars(select(EnglishUnit).where(EnglishUnit.book_id == book_id).order_by(EnglishUnit.sort_no, EnglishUnit.unit_id))).all()
        return [{'unit_id': row.unit_id, 'title': row.title} for row in rows]

    @classmethod
    async def scenes(cls, db: AsyncSession) -> list[dict]:
        rows = (await db.scalars(select(EnglishScene).where(EnglishScene.status == 'published').order_by(EnglishScene.sort_no, EnglishScene.scene_id))).all()
        result = []
        for row in rows:
            media = await db.get(EnglishMediaAsset, row.animation_media_id) if row.animation_media_id else None
            result.append({'scene_id': row.scene_id, 'title': row.title, 'description': row.description, 'cover_url': row.cover_url, 'animation': {'type': 'html', 'url': f'/english/media/{media.media_id}'} if media and media.status == 'ready' else None})
        return result

    @classmethod
    async def _word_data(cls, db: AsyncSession, words: list[EnglishWord]) -> list[dict]:
        result = []
        for word in words:
            pronunciations = (await db.scalars(select(EnglishWordPronunciation).where(EnglishWordPronunciation.word_id == word.word_id))).all()
            audio = {}
            for pronunciation in pronunciations:
                media = await db.get(EnglishMediaAsset, pronunciation.media_id)
                if media and media.status == 'ready':
                    audio[pronunciation.accent] = f'/english/media/{media.media_id}'
            animation = await db.scalar(select(EnglishWordAnimation).where(EnglishWordAnimation.word_id == word.word_id, EnglishWordAnimation.status == 'published'))
            animation_data = None
            if animation and animation.media_id:
                animation_data = {'type': animation.animation_type, 'url': f'/english/media/{animation.media_id}'}
            result.append({'word_id': word.word_id, 'word': word.word, 'phonetic_uk': word.phonetic_uk, 'phonetic_us': word.phonetic_us, 'meaning_zh': word.meaning_zh, 'part_of_speech': word.part_of_speech, 'example_en': word.example_en, 'example_zh': word.example_zh, 'audio': audio, 'animation': animation_data})
        return result

    @classmethod
    async def words(cls, db: AsyncSession, unit_id: int) -> list[dict]:
        rows = (await db.execute(select(EnglishBookWord, EnglishWord).join(EnglishWord, EnglishWord.word_id == EnglishBookWord.word_id).where(EnglishBookWord.unit_id == unit_id).order_by(EnglishBookWord.sort_no, EnglishBookWord.relation_id))).all()
        return await cls._word_data(db, [word for _, word in rows])

    @classmethod
    async def scene_words(cls, db: AsyncSession, scene_id: int) -> list[dict]:
        rows = (await db.execute(select(EnglishSceneWord, EnglishWord).join(EnglishWord, EnglishWord.word_id == EnglishSceneWord.word_id).join(EnglishScene, EnglishScene.scene_id == EnglishSceneWord.scene_id).where(EnglishSceneWord.scene_id == scene_id, EnglishScene.status == 'published').order_by(EnglishSceneWord.sort_no, EnglishSceneWord.relation_id))).all()
        return await cls._word_data(db, [word for _, word in rows])
