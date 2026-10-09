from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, Float, Integer, String, Text, UniqueConstraint

from config.database import Base


class EnglishBook(Base):
    __tablename__ = 'english_book'
    book_id = Column(BigInteger, primary_key=True, autoincrement=True)
    title = Column(String(100), nullable=False)
    description = Column(String(500), nullable=False, default='')
    cover_url = Column(String(500), nullable=False, default='')
    source_url = Column(String(500), nullable=False, default='')
    status = Column(String(16), nullable=False, default='draft')
    sort_no = Column(Integer, nullable=False, default=0)
    create_time = Column(DateTime, nullable=False, default=datetime.now)
    update_time = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)


class EnglishUnit(Base):
    __tablename__ = 'english_unit'
    unit_id = Column(BigInteger, primary_key=True, autoincrement=True)
    book_id = Column(BigInteger, nullable=False, index=True)
    title = Column(String(100), nullable=False)
    sort_no = Column(Integer, nullable=False, default=0)


class EnglishScene(Base):
    __tablename__ = 'english_scene'
    scene_id = Column(BigInteger, primary_key=True, autoincrement=True)
    title = Column(String(100), nullable=False)
    description = Column(String(500), nullable=False, default='')
    cover_url = Column(String(500), nullable=False, default='')
    animation_media_id = Column(BigInteger, nullable=True)
    status = Column(String(16), nullable=False, default='draft')
    sort_no = Column(Integer, nullable=False, default=0)
    create_time = Column(DateTime, nullable=False, default=datetime.now)
    update_time = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)


class EnglishWord(Base):
    __tablename__ = 'english_word'
    word_id = Column(BigInteger, primary_key=True, autoincrement=True)
    word = Column(String(100), nullable=False, unique=True)
    phonetic_uk = Column(String(200), nullable=False, default='')
    phonetic_us = Column(String(200), nullable=False, default='')
    meaning_zh = Column(Text, nullable=False, default='')
    part_of_speech = Column(String(100), nullable=False, default='')
    example_en = Column(Text, nullable=False, default='')
    example_zh = Column(Text, nullable=False, default='')
    source_url = Column(String(500), nullable=False, default='')


class EnglishBookWord(Base):
    __tablename__ = 'english_book_word'
    __table_args__ = (UniqueConstraint('book_id', 'unit_id', 'word_id', name='uk_english_book_word'),)
    relation_id = Column(BigInteger, primary_key=True, autoincrement=True)
    book_id = Column(BigInteger, nullable=False, index=True)
    unit_id = Column(BigInteger, nullable=False, index=True)
    word_id = Column(BigInteger, nullable=False, index=True)
    sort_no = Column(Integer, nullable=False, default=0)


class EnglishSceneWord(Base):
    __tablename__ = 'english_scene_word'
    __table_args__ = (UniqueConstraint('scene_id', 'word_id', name='uk_english_scene_word'),)
    relation_id = Column(BigInteger, primary_key=True, autoincrement=True)
    scene_id = Column(BigInteger, nullable=False, index=True)
    word_id = Column(BigInteger, nullable=False, index=True)
    sort_no = Column(Integer, nullable=False, default=0)


class EnglishMediaAsset(Base):
    __tablename__ = 'english_media_asset'
    media_id = Column(BigInteger, primary_key=True, autoincrement=True)
    media_type = Column(String(16), nullable=False)  # audio / animation
    storage_path = Column(String(500), nullable=False, unique=True)
    source_url = Column(String(500), nullable=False, default='')
    sha256 = Column(String(64), nullable=False, default='')
    file_size = Column(BigInteger, nullable=False, default=0)
    duration = Column(Float, nullable=True)
    status = Column(String(16), nullable=False, default='ready')
    create_time = Column(DateTime, nullable=False, default=datetime.now)


class EnglishWordPronunciation(Base):
    __tablename__ = 'english_word_pronunciation'
    __table_args__ = (UniqueConstraint('word_id', 'accent', name='uk_english_word_pronunciation'),)
    pronunciation_id = Column(BigInteger, primary_key=True, autoincrement=True)
    word_id = Column(BigInteger, nullable=False, index=True)
    accent = Column(String(4), nullable=False)  # uk / us
    phonetic = Column(String(200), nullable=False, default='')
    media_id = Column(BigInteger, nullable=False)


class EnglishWordAnimation(Base):
    __tablename__ = 'english_word_animation'
    animation_id = Column(BigInteger, primary_key=True, autoincrement=True)
    word_id = Column(BigInteger, nullable=False, unique=True)
    animation_type = Column(String(32), nullable=False, default='template')
    animation_config = Column(Text, nullable=False, default='{}')
    media_id = Column(BigInteger, nullable=True)
    status = Column(String(16), nullable=False, default='draft')
