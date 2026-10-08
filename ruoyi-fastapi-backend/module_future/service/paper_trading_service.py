import asyncio
import json
import re
from datetime import date, datetime, time
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions.exception import ServiceWarning
from module_future.dao.future_quote_dao import FutureQuoteDao
from module_future.dao.future_history_dao import FutureHistoryDao
from module_future.entity.do.paper_trading_do import FuturePaperAccount, FuturePaperDailyMark, FuturePaperOrder, FuturePaperPosition
from module_future.entity.vo.paper_trading_vo import PaperAccountModel, PaperPositionModel, PaperTradeOpenModel
from module_future.service.future_kline_service import FutureKlineService
from module_future.service.training_service import TrainingService
from config.env import AppConfig


class PaperTradingService:
    INITIAL_CASH = 1000000.0
    MARGIN_RATE = 1.0
    COMMISSION_RATE = 0.0001
    # 默认自助开户按交易所基准的 3 倍总费率模拟：交易所 1 份、期货公司佣金 2 份。
    BROKER_COMMISSION_MULTIPLIER = 2.0
    FEE_SPECS = {
        'RB': {'rate': 0.0001}, 'I': {'rate': 0.0005}, 'SA': {'rate': 0.0001}, 'AG': {'rate': 0.00005},
        'FG': {'fixed': 2.0}, 'M': {'fixed': 1.5}, 'C': {'fixed': 1.2}, 'SC': {'fixed': 20.0},
        'IF': {'rate': 0.000092, 'close_today_rate': 0.00092},
        'IC': {'rate': 0.000092, 'close_today_rate': 0.00092},
        'IM': {'rate': 0.000092, 'close_today_rate': 0.00092},
    }
    DOMESTIC_MARKETS = {'XSGE', 'XDCE', 'XZCE', 'XGFE', 'SHGE'}
    STATUS_CACHE_TTL = 60

    @classmethod
    async def _quote(cls, contract_code: str) -> dict:
        quote = await asyncio.to_thread(FutureQuoteDao.get_contract, AppConfig.future_stat_db_path, contract_code, True)
        if not quote:
            raise ServiceWarning(message='未找到可交易的期货行情')
        return quote

    @classmethod
    def trading_status(cls, quote: dict, now: datetime | None = None) -> dict:
        if quote['market_code'] not in cls.DOMESTIC_MARKETS:
            return {'tradable': False, 'reason': '国际期货仅供查看行情，不参与模拟交易'}
        now = now or datetime.now(ZoneInfo('Asia/Shanghai'))
        if now.weekday() >= 5:
            return {'tradable': False, 'reason': '周末休市，暂不支持模拟交易'}
        if cls.is_domestic_holiday(now.date()):
            return {'tradable': False, 'reason': '法定节假日休市，暂不支持模拟交易'}
        if str(quote.get('market_date', '')).replace('-', '') != now.strftime('%Y%m%d'):
            return {'tradable': False, 'reason': '非交易日，暂不支持模拟交易'}
        if not TrainingService.is_trading_time(quote['contract_code'], now):
            return {'tradable': False, 'reason': '非交易时段，暂不支持模拟交易'}
        return {'tradable': True, 'reason': ''}

    @classmethod
    async def status(cls, contract_code: str, redis=None) -> dict:
        cache_key = f'api_cache:paper_trading_status:{contract_code}'
        if redis:
            try:
                cached = await redis.get(cache_key)
                if cached:
                    return json.loads(cached)
            except Exception:
                pass
        status = cls.trading_status(await cls._quote(contract_code))
        if redis:
            try:
                await redis.set(cache_key, json.dumps(status, ensure_ascii=False), ex=cls.STATUS_CACHE_TTL)
            except Exception:
                pass
        return status

    @classmethod
    async def _ensure_tradable(cls, quote: dict) -> None:
        status = cls.trading_status(quote)
        if not status['tradable']:
            raise ServiceWarning(message=status['reason'])

    @classmethod
    async def _execution_quote(cls, contract_code: str) -> dict:
        """Use a fresh upstream quote for an order; page and SQLite prices never set fills."""
        quote = await cls._quote(contract_code)
        await cls._ensure_tradable(quote)
        try:
            quote = {**quote, 'price': await asyncio.to_thread(FutureKlineService.get_latest_price, quote['contract_code'])}
        except Exception as error:
            raise ServiceWarning(message='最新行情获取失败，未提交模拟交易') from error
        return quote

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

    @staticmethod
    def floating_pnl(mark_price: float, base_price: float, multiplier: float, quantity: int, side: str) -> float:
        return (mark_price - base_price) * multiplier * quantity * (1 if side == '多' else -1)

    @staticmethod
    def is_domestic_holiday(day: date) -> bool:
        # 国庆长假为国内期货统一休市；其它调休日优先以入库交易日历为准。
        return day.month == 10 and day.day <= 7

    @classmethod
    async def account(cls, db: AsyncSession, user_id: int) -> PaperAccountModel:
        account = await cls._account(db, user_id)
        positions = (await db.scalars(select(FuturePaperPosition).where(FuturePaperPosition.user_id == user_id))).all()
        result = []
        unrealized = 0.0
        now = datetime.now(ZoneInfo('Asia/Shanghai'))
        today = now.date()
        for position in positions:
            quote = await cls._quote(position.contract_code)
            pnl = cls.floating_pnl(quote['price'], position.average_price, position.multiplier, position.quantity, position.side)
            unrealized += pnl
            if now.time() >= time(15, 5) and str(quote.get('market_date', '')).replace('-', '') == today.strftime('%Y%m%d'):
                mark = await db.scalar(select(FuturePaperDailyMark).where(FuturePaperDailyMark.user_id == user_id, FuturePaperDailyMark.position_id == position.position_id, FuturePaperDailyMark.trade_date == today))
                previous = await db.scalar(select(FuturePaperDailyMark).where(FuturePaperDailyMark.user_id == user_id, FuturePaperDailyMark.position_id == position.position_id, FuturePaperDailyMark.trade_date < today).order_by(FuturePaperDailyMark.trade_date.desc()).limit(1))
                daily_pnl = cls.floating_pnl(quote['price'], previous.mark_price if previous else position.average_price, position.multiplier, position.quantity, position.side)
                if mark:
                    mark.mark_price, mark.floating_pnl = quote['price'], daily_pnl
                else:
                    db.add(FuturePaperDailyMark(user_id=user_id, position_id=position.position_id, contract_code=position.contract_code, trade_date=today, mark_price=quote['price'], floating_pnl=daily_pnl))
            result.append(PaperPositionModel(position_id=position.position_id, contract_code=position.contract_code, contract_name=position.contract_name, side=position.side, quantity=position.quantity, average_price=position.average_price, last_price=quote['price'], margin=position.margin, unrealized_pnl=pnl))
        cash = account.cash
        equity = cash + sum(item.margin for item in positions) + unrealized
        response = PaperAccountModel(cash=cash, equity=equity, unrealized_pnl=unrealized, positions=result)
        await db.commit()
        return response

    @classmethod
    async def floating_calendar(cls, db: AsyncSession, user_id: int, month: str) -> list[dict]:
        start = datetime.strptime(f'{month}-01', '%Y-%m-%d').date()
        end = date(start.year + (start.month == 12), start.month % 12 + 1, 1)
        marks = (await db.scalars(select(FuturePaperDailyMark).where(FuturePaperDailyMark.user_id == user_id, FuturePaperDailyMark.trade_date >= start, FuturePaperDailyMark.trade_date < end))).all()
        rows: dict[date, float] = {}
        for mark in marks:
            rows[mark.trade_date] = rows.get(mark.trade_date, 0) + mark.floating_pnl
        positions = (await db.scalars(select(FuturePaperPosition).where(FuturePaperPosition.user_id == user_id))).all()
        today = datetime.now(ZoneInfo('Asia/Shanghai')).date()
        sealed_today = any(mark.trade_date == today for mark in marks)
        if start <= today < end and not sealed_today:
            floating = 0.0
            for position in positions:
                quote = await cls._quote(position.contract_code)
                previous = await db.scalar(select(FuturePaperDailyMark).where(FuturePaperDailyMark.user_id == user_id, FuturePaperDailyMark.position_id == position.position_id, FuturePaperDailyMark.trade_date < today).order_by(FuturePaperDailyMark.trade_date.desc()).limit(1))
                base_price = previous.mark_price if previous else position.average_price
                floating += cls.floating_pnl(quote['price'], base_price, position.multiplier, position.quantity, position.side)
            if floating or positions:
                rows[today] = floating
        calendar_days = await asyncio.to_thread(FutureHistoryDao.get_trading_dates, AppConfig.future_stat_db_path, start.strftime('%Y%m%d'), end.strftime('%Y%m%d'))
        # 没有入库交易日历时不猜测节假日，工作日仍按可交易日展示，避免误标休市。
        has_calendar = bool(calendar_days)
        result = []
        current = start
        while current < end:
            if current.weekday() < 5 and current <= today:
                trading_day = not cls.is_domestic_holiday(current) and (not has_calendar or current.strftime('%Y%m%d') in calendar_days)
                result.append({'trade_date': current.isoformat(), 'floating_pnl': rows.get(current, 0.0) if trading_day else None, 'estimated': current == today and not sealed_today and trading_day, 'closed': not trading_day})
            current = date.fromordinal(current.toordinal() + 1)
        return result

    @classmethod
    async def profit_summary(cls, db: AsyncSession, user_id: int) -> list[dict]:
        """Net realized result by contract; open-position floating P&L is excluded."""
        orders = (await db.scalars(select(FuturePaperOrder).where(FuturePaperOrder.user_id == user_id))).all()
        rows: dict[str, dict] = {}
        for order in orders:
            item = rows.setdefault(order.contract_code, {'contract_code': order.contract_code, 'contract_name': order.contract_name, 'realized_pnl': 0.0, 'fee': 0.0, 'trade_count': 0})
            item['fee'] += order.fee or 0.0
            if order.action == '平仓':
                item['realized_pnl'] += order.realized_pnl or 0.0
                item['trade_count'] += 1
        result = []
        for item in rows.values():
            if item['trade_count']:
                item['net_pnl'] = item['realized_pnl'] - item['fee']
                result.append(item)
        return sorted(result, key=lambda item: item['net_pnl'], reverse=True)

    @classmethod
    async def open(cls, db: AsyncSession, user_id: int, data: PaperTradeOpenModel) -> None:
        quote = await cls._execution_quote(data.contract_code)
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
        quote = await cls._execution_quote(position.contract_code)
        account = await cls._account(db, user_id)
        pnl = (quote['price'] - position.average_price) * position.multiplier * position.quantity * (1 if position.side == '多' else -1)
        exchange_fee, broker_fee = cls.fee_breakdown(quote, position.quantity, position.create_time.date() == datetime.now().date())
        fee = exchange_fee + broker_fee
        account.cash += position.margin + pnl - fee
        db.add(FuturePaperOrder(user_id=user_id, contract_code=position.contract_code, contract_name=position.contract_name, side=position.side, action='平仓', quantity=position.quantity, price=quote['price'], fee=fee, exchange_fee=exchange_fee, broker_fee=broker_fee, realized_pnl=pnl))
        await db.delete(position)
        await db.commit()
