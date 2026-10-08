import re
from datetime import datetime, time
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
    NIGHT_TO_2300 = {'RB', 'HC', 'RU', 'BR', 'BU', 'FU', 'SP', 'M', 'Y', 'P', 'I', 'JM', 'J', 'C', 'CS', 'L', 'PP', 'V', 'EG', 'EB', 'PG', 'BZ', 'MA', 'TA', 'SA', 'FG', 'CF', 'SR', 'RM', 'OI', 'ZC', 'PX', 'PL', 'PR'}
    NIGHT_TO_0100 = {'CU', 'AL', 'ZN', 'PB', 'NI', 'SN', 'SS', 'AO', 'AD', 'BC'}
    NIGHT_TO_0230 = {'AU', 'AG', 'SC'}

    @classmethod
    def is_trading_time(cls, contract_code: str, now: datetime) -> bool:
        """Domestic session schedule; holidays are rejected by the live quote date check."""
        if now.weekday() >= 5:
            return False
        current = now.time()
        if time(8, 55) <= current < time(10, 15) or time(10, 30) <= current < time(11, 30) or time(13, 30) <= current < time(15):
            return True
        product = re.match(r'[A-Z]+', contract_code.upper())
        code = product.group() if product else ''
        if code in cls.NIGHT_TO_2300:
            return time(21) <= current < time(23)
        if code in cls.NIGHT_TO_0100:
            return current >= time(21) or current < time(1)
        if code in cls.NIGHT_TO_0230:
            return current >= time(21) or current < time(2, 30)
        return False

    @classmethod
    async def _quote(cls, code: str) -> dict:
        quote = FutureQuoteDao.get_contract(AppConfig.future_stat_db_path, code, True)
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
        now = datetime.now(cls.TZ)
        today = now.date()
        decisions = (await db.scalars(select(FutureTrainingDecision).where(FutureTrainingDecision.user_id == user_id, FutureTrainingDecision.trade_date == today))).all()
        done = {item.contract_code: item for item in decisions}
        rows, _ = FutureQuoteDao.get_page(AppConfig.future_stat_db_path, 'domestic', None, 1, 100, True)
        await db.commit()
        return [item for item in rows if item['contract_code'] not in done and str(item.get('market_date', '')).replace('-', '') == now.strftime('%Y%m%d') and cls.is_trading_time(item['contract_code'], now)]

    @classmethod
    async def submit(cls, db: AsyncSession, user_id: int, data: TrainingDecisionCreateModel) -> FutureTrainingDecision:
        now = datetime.now(cls.TZ)
        if now.time().hour < 14 or (now.time().hour == 14 and now.time().minute < 55):
            raise ServiceWarning(message='训练决策请在14:55后的尾盘提交')
        quote = await cls._quote(data.contract_code)
        if str(quote.get('market_date', '')).replace('-', '') != now.strftime('%Y%m%d'):
            raise ServiceWarning(message='今日没有可用于训练的收盘行情')
        if not cls.is_trading_time(quote['contract_code'], now):
            raise ServiceWarning(message='当前不是该合约交易时段')
        current = await db.scalar(select(FutureTrainingDecision).where(FutureTrainingDecision.user_id == user_id, FutureTrainingDecision.trade_date == now.date(), FutureTrainingDecision.contract_code == quote['contract_code']))
        if current:
            raise ServiceWarning(message='该合约今日已完成训练决策')
        item = FutureTrainingDecision(user_id=user_id, trade_date=now.date(), contract_code=quote['contract_code'], contract_name=quote['contract_name'], decision=data.decision, reason=data.reason.strip(), entry_price=quote['price'])
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
