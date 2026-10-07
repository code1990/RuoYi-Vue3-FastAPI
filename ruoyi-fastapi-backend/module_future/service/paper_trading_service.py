import asyncio
import re
from datetime import datetime, time
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions.exception import ServiceWarning
from module_future.dao.future_quote_dao import FutureQuoteDao
from module_future.entity.do.paper_trading_do import FuturePaperAccount, FuturePaperOrder, FuturePaperPosition
from module_future.entity.vo.paper_trading_vo import PaperAccountModel, PaperPositionModel, PaperTradeOpenModel
from config.env import AppConfig


class PaperTradingService:
    INITIAL_CASH = 1000000.0
    MARGIN_RATE = 1.0
    COMMISSION_RATE = 0.0001
    BROKER_COMMISSION_MULTIPLIER = 0.0
    FEE_SPECS = {
        'RB': {'rate': 0.0001}, 'I': {'rate': 0.0005}, 'SA': {'rate': 0.0001}, 'AG': {'rate': 0.00005},
        'FG': {'fixed': 2.0}, 'M': {'fixed': 1.5}, 'C': {'fixed': 1.2}, 'SC': {'fixed': 20.0},
        'IF': {'rate': 0.000092, 'close_today_rate': 0.00092},
        'IC': {'rate': 0.000092, 'close_today_rate': 0.00092},
        'IM': {'rate': 0.000092, 'close_today_rate': 0.00092},
    }
    DOMESTIC_MARKETS = {'XSGE', 'XDCE', 'XZCE', 'XGFE', 'SHGE'}

    @classmethod
    async def _quote(cls, contract_code: str) -> dict:
        quote = await asyncio.to_thread(FutureQuoteDao.get_contract, AppConfig.future_stat_db_path, contract_code)
        if not quote:
            raise ServiceWarning(message='未找到可交易的期货行情')
        return quote

    @classmethod
    def trading_status(cls, quote: dict, now: datetime | None = None) -> dict:
        if quote['market_code'] not in cls.DOMESTIC_MARKETS:
            return {'tradable': False, 'reason': '国际期货仅供查看行情，不参与模拟交易'}
        now = now or datetime.now(ZoneInfo('Asia/Shanghai'))
        if str(quote.get('market_date', '')).replace('-', '') != now.strftime('%Y%m%d'):
            return {'tradable': False, 'reason': '今日休市，暂不支持模拟交易'}
        if now.weekday() >= 5 or not (time(9, 0) <= now.time() <= time(10, 15) or time(10, 30) <= now.time() <= time(11, 30) or time(13, 30) <= now.time() <= time(15, 0)):
            return {'tradable': False, 'reason': '当前不在日盘交易时段'}
        return {'tradable': True, 'reason': ''}

    @classmethod
    async def status(cls, contract_code: str) -> dict:
        return cls.trading_status(await cls._quote(contract_code))

    @classmethod
    async def _ensure_tradable(cls, quote: dict) -> None:
        status = cls.trading_status(quote)
        if not status['tradable']:
            raise ServiceWarning(message=status['reason'])

    @classmethod
    def fee_breakdown(cls, quote: dict, quantity: int, close_today: bool = False) -> tuple[float, float]:
        prefix = re.match(r'[A-Za-z]+', str(quote['contract_code']).split('.', 1)[0])
        rule = cls.FEE_SPECS.get((prefix.group(0) if prefix else '').upper(), {'rate': cls.COMMISSION_RATE})
        if 'fixed' in rule:
            exchange_fee = rule['fixed'] * quantity
        else:
            rate = rule.get('close_today_rate') if close_today else None
            exchange_fee = quote['price'] * quote['multiplier'] * quantity * (rate if rate is not None else rule['rate'])
        return exchange_fee, exchange_fee * cls.BROKER_COMMISSION_MULTIPLIER

    @classmethod
    def fee(cls, quote: dict, quantity: int, close_today: bool = False) -> float:
        return sum(cls.fee_breakdown(quote, quantity, close_today))

    @classmethod
    async def _account(cls, db: AsyncSession, user_id: int) -> FuturePaperAccount:
        account = await db.scalar(select(FuturePaperAccount).where(FuturePaperAccount.user_id == user_id).with_for_update())
        if account is None:
            account = FuturePaperAccount(user_id=user_id, cash=cls.INITIAL_CASH, initial_cash=cls.INITIAL_CASH)
            db.add(account)
            await db.flush()
        return account

    @classmethod
    async def account(cls, db: AsyncSession, user_id: int) -> PaperAccountModel:
        account = await cls._account(db, user_id)
        positions = (await db.scalars(select(FuturePaperPosition).where(FuturePaperPosition.user_id == user_id))).all()
        result = []
        unrealized = 0.0
        for position in positions:
            quote = await cls._quote(position.contract_code)
            pnl = (quote['price'] - position.average_price) * position.multiplier * position.quantity * (1 if position.side == '多' else -1)
            unrealized += pnl
            result.append(PaperPositionModel(position_id=position.position_id, contract_code=position.contract_code, contract_name=position.contract_name, side=position.side, quantity=position.quantity, average_price=position.average_price, last_price=quote['price'], margin=position.margin, unrealized_pnl=pnl))
        cash = account.cash
        equity = cash + sum(item.margin for item in positions) + unrealized
        response = PaperAccountModel(cash=cash, equity=equity, unrealized_pnl=unrealized, positions=result)
        await db.commit()
        return response

    @classmethod
    async def open(cls, db: AsyncSession, user_id: int, data: PaperTradeOpenModel) -> None:
        quote = await cls._quote(data.contract_code)
        await cls._ensure_tradable(quote)
        account = await cls._account(db, user_id)
        margin = quote['price'] * quote['multiplier'] * data.quantity * cls.MARGIN_RATE
        exchange_fee, broker_fee = cls.fee_breakdown(quote, data.quantity)
        fee = exchange_fee + broker_fee
        if margin + fee > account.cash:
            raise ServiceWarning(message='可用模拟资金不足')
        position = await db.scalar(select(FuturePaperPosition).where(FuturePaperPosition.user_id == user_id, FuturePaperPosition.contract_code == quote['contract_code'], FuturePaperPosition.side == data.side).with_for_update())
        if position:
            total = position.quantity + data.quantity
            position.average_price = (position.average_price * position.quantity + quote['price'] * data.quantity) / total
            position.quantity = total
            position.margin += margin
        else:
            db.add(FuturePaperPosition(user_id=user_id, contract_code=quote['contract_code'], contract_name=quote['contract_name'], side=data.side, quantity=data.quantity, average_price=quote['price'], multiplier=quote['multiplier'], margin=margin))
        account.cash -= margin + fee
        db.add(FuturePaperOrder(user_id=user_id, contract_code=quote['contract_code'], contract_name=quote['contract_name'], side=data.side, action='开仓', quantity=data.quantity, price=quote['price'], fee=fee, exchange_fee=exchange_fee, broker_fee=broker_fee))
        await db.commit()

    @classmethod
    async def close(cls, db: AsyncSession, user_id: int, position_id: int) -> None:
        position = await db.scalar(select(FuturePaperPosition).where(FuturePaperPosition.position_id == position_id, FuturePaperPosition.user_id == user_id).with_for_update())
        if position is None:
            raise ServiceWarning(message='持仓不存在')
        quote = await cls._quote(position.contract_code)
        await cls._ensure_tradable(quote)
        account = await cls._account(db, user_id)
        pnl = (quote['price'] - position.average_price) * position.multiplier * position.quantity * (1 if position.side == '多' else -1)
        exchange_fee, broker_fee = cls.fee_breakdown(quote, position.quantity, position.create_time.date() == datetime.now().date())
        fee = exchange_fee + broker_fee
        account.cash += position.margin + pnl - fee
        db.add(FuturePaperOrder(user_id=user_id, contract_code=position.contract_code, contract_name=position.contract_name, side=position.side, action='平仓', quantity=position.quantity, price=quote['price'], fee=fee, exchange_fee=exchange_fee, broker_fee=broker_fee, realized_pnl=pnl))
        await db.delete(position)
        await db.commit()
