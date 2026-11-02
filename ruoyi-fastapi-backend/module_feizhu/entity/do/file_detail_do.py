from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text, UniqueConstraint

from config.database import Base


class FileKeyword(Base):
    __tablename__ = 't_file_keyword'

    id = Column(String(32), primary_key=True)
    keyword = Column(String(255), nullable=False, unique=True)
    sort_no = Column(Integer, nullable=False, default=0)
    create_by = Column(String(64), nullable=False, default='')
    create_time = Column(DateTime, default=datetime.now)
    update_by = Column(String(64), nullable=False, default='')
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    remark = Column(String(500), nullable=False, default='')


class FileKeywordTopic(Base):
    __tablename__ = 't_file_keyword_topic'
    __table_args__ = (UniqueConstraint('keyword_id', 'topic', name='uk_file_keyword_topic'),)

    id = Column(String(32), primary_key=True)
    keyword_id = Column(String(32), nullable=False, index=True)
    topic = Column(String(255), nullable=False, index=True)
    sort_no = Column(Integer, nullable=False, default=0)
    create_by = Column(String(64), nullable=False, default='')
    create_time = Column(DateTime, default=datetime.now)
    update_by = Column(String(64), nullable=False, default='')
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class FileDetail(Base):
    __tablename__ = 't_file_detail'

    id = Column(String(32), primary_key=True)
    topic = Column(String(255), nullable=False, index=True)
    eu = Column(String(255), nullable=False)
    filename = Column(String(255))
    size = Column(String(255))
    ctime = Column(DateTime)
    utime = Column(DateTime)
    ext = Column(String(32), nullable=False, default='2', index=True)
    category = Column(Integer, index=True)
    owner = Column('user', String(32))
    type = Column(String(32), index=True)
    file_list = Column(Text)
    url = Column(String(255))
    pwd = Column(String(255))
    haspwd = Column(String(255), index=True)
    valid = Column(String(255), index=True)
    create_by = Column(String(64), nullable=False, default='')
    create_time = Column(DateTime)
    update_by = Column(String(64), nullable=False, default='')
    update_time = Column(DateTime)
    remark = Column(String(500), nullable=False, default='')
