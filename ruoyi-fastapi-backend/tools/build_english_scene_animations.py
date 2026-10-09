"""Build and register self-contained SVG animations for imported English scenes."""

import asyncio
import hashlib
import sys
from pathlib import Path

from sqlalchemy import select

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config.database import AsyncSessionLocal
from config.env import UploadConfig
from module_english.entity.do.english_do import EnglishMediaAsset, EnglishScene


SCENES = {
    '哺乳动物': ('草原动物园', 'zebra · yak · walrus', '#bde7a6', 'land'),
    '禽类': ('天空鸟乐园', 'parrot · owl · swan', '#bfe7ff', 'sky'),
    '爬行动物': ('沙漠探险', 'snake · turtle · lizard', '#f6d29a', 'desert'),
    '鱼类': ('海洋馆', 'shark · salmon · carp', '#9ee5f5', 'water'),
    '昆虫': ('昆虫花园', 'bee · butterfly · ant', '#f9dea0', 'garden'),
    '甲壳动物': ('海边小屋', 'crab · lobster · oyster', '#a8dfeb', 'water'),
    '蠕虫': ('泥土朋友', 'earthworm · tapeworm', '#d8b38b', 'soil'),
    '花': ('花朵花园', 'rose · tulip · sunflower', '#ffd7a8', 'garden'),
    '树': ('森林散步', 'oak · pine · sycamore', '#b9dfaa', 'forest'),
    '动物': ('动物世界', 'lion · tiger · zebra', '#f6cd82', 'land'),
    '植物': ('植物王国', 'leaf · cactus · fern', '#b9e7b5', 'forest'),
}


def art(kind: str) -> str:
    if kind == 'water':
        return '<path class="wave" d="M0 330q80-55 160 0t160 0t160 0t160 0v150H0z"/><g class="fish f1"><ellipse rx="58" ry="30"/><path d="M55 0l42-35v70z"/><circle cx="-25" cy="-7" r="5"/></g><g class="fish f2"><ellipse rx="40" ry="22"/><path d="M38 0l30-25v50z"/><circle cx="-16" cy="-5" r="4"/></g>'
    if kind == 'sky':
        return '<path class="cloud" d="M80 125q25-45 55 0q42-34 67 10H80zM470 90q22-38 48 0q35-28 57 8H470z"/><path class="bird b1" d="M0 0q25-35 50 0q25-35 50 0"/><path class="bird b2" d="M0 0q22-31 44 0q22-31 44 0"/>'
    if kind == 'desert':
        return '<path class="dune" d="M0 355q120-115 260 0q130-95 380 0v125H0z"/><path class="snake" d="M175 375q45-80 92 0t92 0q45-80 92 0"/><g class="turtle"><ellipse rx="55" ry="36"/><circle cx="57" cy="0" r="17"/><path d="M-30-25l60 50M-30 25l60-50"/></g>'
    if kind == 'garden':
        return '<path class="ground" d="M0 390q100-35 200 0t220 0t220 0v90H0z"/><g class="flower"><path d="M0 80V0"/><circle cy="-18" r="25"/><circle cx="25" r="25"/><circle cx="-25" r="25"/><circle cy="25" r="25"/><circle cy="0" r="13"/></g><g class="bug"><ellipse rx="30" ry="21"/><circle cx="-28" cy="-5" r="13"/><path d="M13-16l18-22M13 16l18 22"/></g>'
    if kind == 'soil':
        return '<path class="ground" d="M0 300q110-38 230 0t220 0t190 0v180H0z"/><path class="worm" d="M175 355q45-80 90 0t90 0t90 0"/><g class="leaf"><path d="M0 0q52-65 95 0q-52 65-95 0"/></g>'
    if kind == 'forest':
        return '<path class="ground" d="M0 385q120-36 245 0t200 0t195 0v95H0z"/><g class="tree t1"><rect x="-12" y="60" width="24" height="90"/><circle cy="30" r="65"/><circle cx="42" cy="65" r="48"/></g><g class="tree t2"><rect x="-10" y="58" width="20" height="82"/><path d="M0-60l65 120H-65z"/></g>'
    return '<path class="ground" d="M0 385q120-36 245 0t200 0t195 0v95H0z"/><g class="animal a1"><ellipse rx="65" ry="42"/><circle cx="58" cy="-35" r="29"/><path d="M35-62l-13-28M65-63l15-27"/><path d="M-35 32v48M25 32v48"/></g><g class="animal a2"><ellipse rx="50" ry="32"/><circle cx="45" cy="-25" r="23"/><path d="M-24 25v43M18 25v43"/></g>'


def render(title: str, subtitle: str, words: str, color: str, kind: str) -> str:
    return f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>
*{{box-sizing:border-box}}body{{margin:0;overflow:hidden;background:{color};font-family:system-ui,sans-serif}}svg{{width:100vw;height:100vh;min-height:280px}}text{{font-weight:800;fill:#25415a}}.label{{font-size:30px;fill:#fff}}.words{{font-size:18px;fill:#25415a}}.ground,.dune{{fill:#79bd76}}.wave{{fill:#4bbad2}}.cloud{{fill:#fff;opacity:.78}}.fish{{fill:#ff9471;stroke:#25415a;stroke-width:5}}.f1{{transform:translate(180px,280px);animation:swim 5s ease-in-out infinite alternate}}.f2{{transform:translate(470px,215px) scale(.8);fill:#ffe070;animation:swim 4s ease-in-out infinite alternate-reverse}}.bird{{fill:none;stroke:#344a72;stroke-width:8;stroke-linecap:round}}.b1{{transform:translate(150px,220px);animation:fly 3s ease-in-out infinite alternate}}.b2{{transform:translate(410px,155px);animation:fly 3.7s ease-in-out infinite alternate-reverse}}.animal,.turtle{{fill:#f6b65c;stroke:#5b4636;stroke-width:6}}.a1{{transform:translate(215px,330px);animation:bob 1s ease-in-out infinite alternate}}.a2{{transform:translate(465px,365px);fill:#f7e59c;animation:bob 1.3s ease-in-out infinite alternate-reverse}}.turtle{{transform:translate(420px,340px);animation:walk 3s ease-in-out infinite alternate}}.snake,.worm{{fill:none;stroke:#a66a43;stroke-width:22;stroke-linecap:round;animation:wriggle 1.5s ease-in-out infinite alternate}}.flower{{transform:translate(185px,320px);fill:#ff7594;stroke:#477c45;stroke-width:7;animation:bob 1.4s ease-in-out infinite alternate}}.bug{{transform:translate(460px,220px);fill:#ffcf4e;stroke:#5b4636;stroke-width:5;animation:fly 2.4s ease-in-out infinite alternate}}.tree{{fill:#519d5c;stroke:#477c45;stroke-width:6}}.t1{{transform:translate(180px,240px);animation:sway 2s ease-in-out infinite alternate}}.t2{{transform:translate(450px,255px);animation:sway 2.4s ease-in-out infinite alternate-reverse}}.leaf{{transform:translate(430px,250px);fill:#5cae64;animation:sway 1.6s ease-in-out infinite alternate}}@keyframes swim{{to{{transform:translate(360px,250px)}}}}@keyframes fly{{to{{translate:30px -35px}}}}@keyframes bob{{to{{translate:0 -15px}}}}@keyframes walk{{to{{translate:70px 0}}}}@keyframes wriggle{{to{{translate:20px -10px;rotate:4deg}}}}@keyframes sway{{to{{rotate:4deg}}}}
</style><svg viewBox="0 0 640 480" role="img" aria-label="{title} English scene"><rect width="640" height="480" fill="{color}" rx="28"/>{art(kind)}<rect x="45" y="35" width="550" height="78" rx="34" fill="#ffffff" opacity=".9"/><text x="320" y="70" text-anchor="middle" font-size="34">{title}</text><text x="320" y="98" text-anchor="middle" class="words">{words}</text><rect x="185" y="420" width="270" height="45" rx="22" fill="#25415a" opacity=".88"/><text x="320" y="450" text-anchor="middle" class="label">{subtitle}</text></svg>'''


async def main() -> None:
    root = Path(UploadConfig.UPLOAD_PATH).resolve() / 'english/scenes'
    root.mkdir(parents=True, exist_ok=True)
    async with AsyncSessionLocal() as db:
        scenes = (await db.scalars(select(EnglishScene).where(EnglishScene.title.in_(SCENES)))).all()
        for scene in scenes:
            subtitle, words, color, kind = SCENES[scene.title]
            content = render(scene.title, subtitle, words, color, kind).encode()
            storage_path = f'english/scenes/scene-{scene.scene_id}.html'
            path = root / f'scene-{scene.scene_id}.html'
            path.write_bytes(content)
            media = await db.scalar(select(EnglishMediaAsset).where(EnglishMediaAsset.storage_path == storage_path))
            if not media:
                media = EnglishMediaAsset(media_type='animation', storage_path=storage_path)
                db.add(media)
                await db.flush()
            media.sha256, media.file_size, media.status = hashlib.sha256(content).hexdigest(), len(content), 'ready'
            scene.animation_media_id = media.media_id
        await db.commit()
        print(f'built {len(scenes)} SVG scene animations')


if __name__ == '__main__':
    asyncio.run(main())
