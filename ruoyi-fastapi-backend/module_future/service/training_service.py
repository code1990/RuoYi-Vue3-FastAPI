from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config.env import AppConfig
from exceptions.exception import ServiceWarning
from module_future.dao.future_quote_dao import FutureQuoteDao
from module_future.entity.do.paper_trading_do import FutureTrainingDecision
from module_future.entity.vo.training_vo import TrainingDecisionCreateModel


class TrainingService:
    TZ = ZoneInfo('Asia/Shanghai')

    @classmethod
    async def _quote(cls, code: str) -> dict:
        quote = FutureQuoteDao.get_contract(AppConfig.future_stat_db_path, code)
        if not quote or quote['market_code'] not in FutureQuoteDao.MARKETS['domestic']:
            raise ServiceWarning(message='仅支持国内有效期货合约训练')
        return quote

    @classmethod
    async def settle(cls, db: AsyncSession, user_id: int) -> None:
        today = datetime.now(cls.TZ).date()
        rows = (await db.scalars(select(FutureTrainingDecision).where(FutureTrainingDecision.user_id == user_id, FutureTrainingDecision.status == 'pending'))).all()
        for item in rows:
            quote = await cls._quote(item.contract_code)
            if item.trade_date >= today or str(quote.get('market_date', '')).replace('-', '') != today.strftime('%Y%m%d'):
                continue
            item.settle_date, item.settle_price, item.status = today, quote['price'], 'settled'
            item.pnl_rate = 0.0 if item.decision == '放弃' else (quote['price'] - item.entry_price) / item.entry_price * 100 * (1 if item.decision == '多' else -1)

    @classmethod
    async def list_today(cls, db: AsyncSession, user_id: int) -> list[dict]:
        await cls.settle(db, user_id)
        today = datetime.now(cls.TZ).date()
        decisions = (await db.scalars(select(FutureTrainingDecision).where(FutureTrainingDecision.user_id == user_id, FutureTrainingDecision.trade_date == today))).all()
        done = {item.contract_code: item for item in decisions}
        rows, _ = FutureQuoteDao.get_page(AppConfig.future_stat_db_path, 'domestic', None, 1, 100)
        await db.commit()
        return [{**item, 'submitted': item['contract_code'] in done} for item in rows]

    @classmethod
    async def submit(cls, db: AsyncSession, user_id: int, data: TrainingDecisionCreateModel) -> FutureTrainingDecision:
        now = datetime.now(cls.TZ)
        if now.time().hour < 14 or (now.time().hour == 14 and now.time().minute < 55):
            raise ServiceWarning(message='训练决策请在14:55后的尾盘提交')
        quote = await cls._quote(data.contract_code)
        if str(quote.get('market_date', '')).replace('-', '') != now.strftime('%Y%m%d'):
            raise ServiceWarning(message='今日没有可用于训练的收盘行情')
        current = await db.scalar(select(FutureTrainingDecision).where(FutureTrainingDecision.user_id == user_id, FutureTrainingDecision.trade_date == now.date(), FutureTrainingDecision.contract_code == quote['contract_code']))
        if current:
            raise ServiceWarning(message='该合约今日已完成训练决策')
        item = FutureTrainingDecision(user_id=user_id, trade_date=now.date(), contract_code=quote['contract_code'], contract_name=quote['contract_name'], decision=data.decision, entry_price=quote['price'])
        db.add(item)
        await db.commit()
        await db.refresh(item)
        return item

    @classmethod
    async def history(cls, db: AsyncSession, user_id: int) -> list[FutureTrainingDecision]:
        await cls.settle(db, user_id)
        rows = (await db.scalars(select(FutureTrainingDecision).where(FutureTrainingDecision.user_id == user_id).order_by(FutureTrainingDecision.decision_id.desc()).limit(60))).all()
        await db.commit()
        return rows
