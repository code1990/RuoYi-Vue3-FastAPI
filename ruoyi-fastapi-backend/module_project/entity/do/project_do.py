from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, JSON, String, Text, UniqueConstraint

from config.database import Base


class ProjectManage(Base):
    __tablename__ = 'project_manage'
    __table_args__ = (UniqueConstraint('project_name', name='uk_project_manage_name'),)

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    project_name = Column(String(200), nullable=False)
    repo_url = Column(String(500))
    description = Column(String(500))
    language = Column(String(20))
    research_direction = Column(String(50))
    version = Column(String(100))
    created_by = Column(String(50))
    create_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class FuncManage(Base):
    __tablename__ = 'func_manage'
    __table_args__ = (UniqueConstraint('project_id', 'func_name', name='uk_func_manage_project_name'),)

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    project_id = Column(BigInteger, ForeignKey('project_manage.id'), nullable=False, index=True)
    func_name = Column(String(100), nullable=False)
    func_desc = Column(String(500))
    logic = Column(Text)
    language = Column(String(20), nullable=False)
    func_type = Column(String(20), nullable=False)
    func_code = Column(Text, nullable=False)
    params_template = Column(JSON)
    func_tags = Column(String(200))
    file_path = Column(String(500))
    class_name = Column(String(100))
    created_by = Column(String(50))
    create_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class FuncCombinationManage(Base):
    __tablename__ = 'func_combination_manage'
    __table_args__ = (UniqueConstraint('project_id', 'combination_name', name='uk_func_combination_project_name'),)

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    project_id = Column(BigInteger, ForeignKey('project_manage.id'), nullable=False, index=True)
    combination_name = Column(String(200), nullable=False)
    research_direction = Column(String(50))
    description = Column(String(500))
    function_ids = Column(JSON)
    create_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)
