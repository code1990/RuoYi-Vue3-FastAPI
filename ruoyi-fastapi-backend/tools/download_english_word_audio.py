"""Download UK/US pronunciation MP3 files for imported Koolearn words."""

import asyncio
import hashlib
import re
import sys
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from sqlalchemy import select

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config.database import AsyncSessionLocal
from config.env import UploadConfig
from module_english.entity.do.english_do import EnglishMediaAsset, EnglishWord, EnglishWordPronunciation


PRONUNCIATION_RE = re.compile(r'<span class="word-spell">(?P<label>英|美) \[(?P<phonetic>[^]]+)\]</span><span class="word-spell-audio" data-url="(?P<url>[^"]+)"')
ACCENTS = {'英': 'uk', '美': 'us'}


def fetch(url: str) -> bytes:
    request = Request(url, headers={'User-Agent': 'Mozilla/5.0 (EnglishGarden audio import)'})
    with urlopen(request, timeout=20) as response:
        return response.read()


def pronunciations(page_url: str, html: str) -> list[tuple[str, str, str]]:
    return [(ACCENTS[item['label']], item['phonetic'], urljoin(page_url, item['url'])) for item in PRONUNCIATION_RE.finditer(html)]


async def main() -> None:
    root = Path(UploadConfig.UPLOAD_PATH).resolve() / 'english/audio'
    root.mkdir(parents=True, exist_ok=True)
    saved = 0
    async with AsyncSessionLocal() as db:
        words = (await db.scalars(select(EnglishWord).where(EnglishWord.source_url.like('%koolearn.com%')))).all()
        for word in words:
            page = await asyncio.to_thread(fetch, word.source_url)
            for accent, phonetic, audio_url in pronunciations(word.source_url, page.decode('utf-8', 'replace')):
                content = await asyncio.to_thread(fetch, audio_url)
                if not content.startswith(b'ID3') and content[:2] != b'\xff\xfb':
                    continue
                storage_path = f'english/audio/{word.word_id}-{accent}.mp3'
                (root / f'{word.word_id}-{accent}.mp3').write_bytes(content)
                media = await db.scalar(select(EnglishMediaAsset).where(EnglishMediaAsset.storage_path == storage_path))
                if not media:
                    media = EnglishMediaAsset(media_type='audio', storage_path=storage_path)
                    db.add(media)
                    await db.flush()
                media.source_url, media.sha256, media.file_size, media.status = audio_url, hashlib.sha256(content).hexdigest(), len(content), 'ready'
                relation = await db.scalar(select(EnglishWordPronunciation).where(EnglishWordPronunciation.word_id == word.word_id, EnglishWordPronunciation.accent == accent))
                if not relation:
                    relation = EnglishWordPronunciation(word_id=word.word_id, accent=accent)
                    db.add(relation)
                relation.phonetic, relation.media_id = phonetic, media.media_id
                saved += 1
        await db.commit()
    print(f'downloaded {saved} pronunciations')


if __name__ == '__main__':
    asyncio.run(main())
