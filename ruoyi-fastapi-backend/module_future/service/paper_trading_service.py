import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions.exception import ServiceWarning
from module_future.dao.future_quote_dao import FutureQuoteDao
from module_future.entity.do.paper_trading_do import FuturePaperAccount, FuturePaperOrder, FuturePaperPosition
from module_future.entity.vo.paper_trading_vo import PaperAccountModel, PaperPositionModel, PaperTradeOpenModel
from config.env import AppConfig


class PaperTradingService:
    INITIAL_CASH = 2000000.0
    MARGIN_RATE = 1.0
    DOMESTIC_MARKETS = {'XSGE', 'XDCE', 'XZCE', 'XGFE', 'SHGE'}

    @classmethod
    async def _quote(cls, contract_code: str) -> dict:
        quote = await asyncio.to_thread(FutureQuoteDao.get_contract, AppConfig.future_stat_db_path, contract_code)
        if not quote:
            raise ServiceWarning(message='未找到可交易的期货行情')
        return quote

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
        if quote['market_code'] not in cls.DOMESTIC_MARKETS:
            raise ServiceWarning(message='国际期货仅供查看行情，暂不支持模拟交易')
        account = await cls._account(db, user_id)
        margin = quote['price'] * quote['multiplier'] * data.quantity * cls.MARGIN_RATE
        if margin > account.cash:
            raise ServiceWarning(message='可用模拟资金不足')
        position = await db.scalar(select(FuturePaperPosition).where(FuturePaperPosition.user_id == user_id, FuturePaperPosition.contract_code == quote['contract_code'], FuturePaperPosition.side == data.side).with_for_update())
        if position:
            total = position.quantity + data.quantity
            position.average_price = (position.average_price * position.quantity + quote['price'] * data.quantity) / total
            position.quantity = total
            position.margin += margin
        else:
            db.add(FuturePaperPosition(user_id=user_id, contract_code=quote['contract_code'], contract_name=quote['contract_name'], side=data.side, quantity=data.quantity, average_price=quote['price'], multiplier=quote['multiplier'], margin=margin))
        account.cash -= margin
        db.add(FuturePaperOrder(user_id=user_id, contract_code=quote['contract_code'], contract_name=quote['contract_name'], side=data.side, action='开仓', quantity=data.quantity, price=quote['price']))
        await db.commit()

    @classmethod
    async def close(cls, db: AsyncSession, user_id: int, position_id: int) -> None:
        position = await db.scalar(select(FuturePaperPosition).where(FuturePaperPosition.position_id == position_id, FuturePaperPosition.user_id == user_id).with_for_update())
        if position is None:
            raise ServiceWarning(message='持仓不存在')
        quote = await cls._quote(position.contract_code)
        if quote['market_code'] not in cls.DOMESTIC_MARKETS:
            raise ServiceWarning(message='国际期货仅供查看行情，暂不支持模拟交易')
        account = await cls._account(db, user_id)
        pnl = (quote['price'] - position.average_price) * position.multiplier * position.quantity * (1 if position.side == '多' else -1)
        account.cash += position.margin + pnl
        db.add(FuturePaperOrder(user_id=user_id, contract_code=position.contract_code, contract_name=position.contract_name, side=position.side, action='平仓', quantity=position.quantity, price=quote['price'], realized_pnl=pnl))
        await db.delete(position)
        await db.commit()
