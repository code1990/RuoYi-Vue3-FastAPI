from datetime import datetime

from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Integer, JSON, Numeric, String, Text, UniqueConstraint

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
    star = Column(Integer, nullable=False, default=0, server_default='0')
    symbol_adaptation = Column(String(500))
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
    visual_enabled = Column(Boolean, nullable=False, default=False, server_default='0')
    visual_summary = Column(String(200))
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


class ResearchBacktest(Base):
    __tablename__ = 'research_backtest'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    combination_id = Column(BigInteger, ForeignKey('func_combination_manage.id'), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    symbol = Column(String(50), nullable=False)
    timeframe = Column(String(20), nullable=False)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    initial_capital = Column(Numeric(18, 4), nullable=False, default=100000)
    status = Column(String(20), nullable=False, default='pending')
    total_return = Column(Numeric(18, 4), default=0)
    win_rate = Column(Numeric(8, 4), default=0)
    max_drawdown = Column(Numeric(18, 4), default=0)
    trade_count = Column(BigInteger, default=0)
    result_data = Column(JSON)
    created_by = Column(String(50))
    create_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class ResearchStrategy(Base):
    __tablename__ = 'research_strategy'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    combination_id = Column(BigInteger, ForeignKey('func_combination_manage.id'), nullable=False, index=True)
    strategy_name = Column(String(200), nullable=False)
    description = Column(String(500))
    status = Column(String(20), nullable=False, default='enabled')
    created_by = Column(String(50))
    create_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class ResearchSimAccount(Base):
    __tablename__ = 'research_sim_account'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    account_name = Column(String(100), nullable=False, unique=True)
    initial_balance = Column(Numeric(18, 4), nullable=False, default=100000)
    available_balance = Column(Numeric(18, 4), nullable=False, default=100000)
    total_pnl = Column(Numeric(18, 4), nullable=False, default=0)
    status = Column(String(20), nullable=False, default='active')
    created_by = Column(String(50))
    create_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class ResearchReview(Base):
    __tablename__ = 'research_review'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    source_type = Column(String(20), nullable=False)
    source_id = Column(BigInteger, nullable=False)
    rating = Column(String(20), nullable=False)
    reason = Column(Text)
    lesson = Column(Text)
    tags = Column(String(200))
    created_by = Column(String(50))
    create_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)
