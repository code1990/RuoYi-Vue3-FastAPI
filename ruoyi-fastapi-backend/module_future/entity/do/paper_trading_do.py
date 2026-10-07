from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, Float, Integer, String, UniqueConstraint

from config.database import Base


class FuturePaperAccount(Base):
    __tablename__ = 'future_paper_account'

    user_id = Column(BigInteger, primary_key=True, nullable=False)
    cash = Column(Float, nullable=False, default=1000000.0)
    initial_cash = Column(Float, nullable=False, default=1000000.0)
    update_time = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)


class FuturePaperPosition(Base):
    __tablename__ = 'future_paper_position'
    __table_args__ = (UniqueConstraint('user_id', 'contract_code', 'side', name='uk_future_paper_position'),)

    position_id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    contract_code = Column(String(40), nullable=False)
    contract_name = Column(String(100), nullable=False, default='')
    side = Column(String(4), nullable=False)
    quantity = Column(Integer, nullable=False)
    average_price = Column(Float, nullable=False)
    multiplier = Column(Float, nullable=False)
    margin = Column(Float, nullable=False)
    create_time = Column(DateTime, nullable=False, default=datetime.now)
    update_time = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)


class FuturePaperOrder(Base):
    __tablename__ = 'future_paper_order'

    order_id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    contract_code = Column(String(40), nullable=False)
    contract_name = Column(String(100), nullable=False, default='')
    side = Column(String(4), nullable=False)
    action = Column(String(8), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    fee = Column(Float, nullable=False, default=0.0)
    realized_pnl = Column(Float, nullable=True)
    create_time = Column(DateTime, nullable=False, default=datetime.now)
