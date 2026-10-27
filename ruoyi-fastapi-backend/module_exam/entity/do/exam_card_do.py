from datetime import datetime

from sqlalchemy import BigInteger, Boolean, Column, DateTime, Integer, String, Text, UniqueConstraint

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


class ExamCardReview(Base):
    __tablename__ = 'exam_card_review'
    __table_args__ = (UniqueConstraint('user_id', 'card_id', name='uk_exam_card_review_user_card'),)
    review_id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    card_id = Column(BigInteger, nullable=False, index=True)
    state = Column(String(16), nullable=False, default='learning')
    required_repetitions = Column(Integer, nullable=False, default=4)
    completed_repetitions = Column(Integer, nullable=False, default=0)
    review_round = Column(Integer, nullable=False, default=0)
    learning_batch = Column(Integer, nullable=False, default=0)
    interval_days = Column(Integer, nullable=False, default=1)
    next_review_time = Column(DateTime, nullable=True)
    last_review_time = Column(DateTime, nullable=True)
    create_time = Column(DateTime, nullable=False, default=datetime.now)
    update_time = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)


class ExamCardReviewLog(Base):
    __tablename__ = 'exam_card_review_log'
    log_id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    card_id = Column(BigInteger, nullable=False, index=True)
    rating = Column(String(8), nullable=False)
    reviewed_time = Column(DateTime, nullable=False, default=datetime.now, index=True)


class ExamCard(Base):
    __tablename__ = 'exam_card'

    card_id = Column(BigInteger, primary_key=True, autoincrement=True)
    category_id = Column(BigInteger, nullable=False, index=True)
    question = Column(String(500), nullable=False)
    answer = Column(Text, nullable=False)
    ai_summary = Column(Text, nullable=False, default='')
    key_points = Column(Text, nullable=False, default='')
    tags = Column(String(500), nullable=False, default='')
    card_type = Column(String(32), nullable=False, default='concept')
    difficulty = Column(Integer, nullable=False, default=3)
    status = Column(String(16), nullable=False, default='published')
    review_enabled = Column(Boolean, nullable=False, default=False)
    sort_no = Column(Integer, nullable=False, default=0)
    create_time = Column(DateTime, nullable=False, default=datetime.now)
    update_time = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
