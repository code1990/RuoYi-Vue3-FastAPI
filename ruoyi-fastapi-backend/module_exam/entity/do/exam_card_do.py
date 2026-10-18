from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, Integer, String, Text, UniqueConstraint

from config.database import Base


class ExamCategory(Base):
    __tablename__ = 'exam_category'
    __table_args__ = (UniqueConstraint('parent_id', 'name', name='uk_exam_category_parent_name'),)

    category_id = Column(BigInteger, primary_key=True, autoincrement=True)
    parent_id = Column(BigInteger, nullable=False, default=0, index=True)
    name = Column(String(100), nullable=False)
    sort_no = Column(Integer, nullable=False, default=0)
    status = Column(String(16), nullable=False, default='published')
    create_time = Column(DateTime, nullable=False, default=datetime.now)
    update_time = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)


class ExamCard(Base):
    __tablename__ = 'exam_card'

    card_id = Column(BigInteger, primary_key=True, autoincrement=True)
    category_id = Column(BigInteger, nullable=False, index=True)
    question = Column(String(500), nullable=False)
    answer = Column(Text, nullable=False)
    key_points = Column(Text, nullable=False, default='')
    tags = Column(String(500), nullable=False, default='')
    card_type = Column(String(32), nullable=False, default='concept')
    difficulty = Column(Integer, nullable=False, default=3)
    status = Column(String(16), nullable=False, default='published')
    sort_no = Column(Integer, nullable=False, default=0)
    create_time = Column(DateTime, nullable=False, default=datetime.now)
    update_time = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
