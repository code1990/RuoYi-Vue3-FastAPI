import pytest
from datetime import datetime
from types import SimpleNamespace

from exceptions.exception import ServiceWarning
from module_future.entity.vo.paper_trading_vo import PaperPositionModel, PaperTradeOpenModel
from module_future.service.paper_trading_service import PaperTradingService


@pytest.mark.asyncio
async def test_open_rejects_overseas_contract(monkeypatch) -> None:
    async def overseas_quote(_: str) -> dict:
        return {
            'contract_code': 'QO0I00.XCEC',
            'market_code': 'XCEC',
            'contract_name': 'COMEX迷你黄金主力合约',
            'price': 4204.25,
            'multiplier': 1,
        }

    monkeypatch.setattr(PaperTradingService, '_quote', overseas_quote)

    with pytest.raises(ServiceWarning) as exc_info:
        await PaperTradingService.open(None, 1, PaperTradeOpenModel(contract_code='QO0I00.XCEC', side='多', quantity=1))
    assert exc_info.value.message == '国际期货仅供查看行情，不参与模拟交易'


def test_trading_status_requires_today_and_day_session() -> None:
    quote = {'market_code': 'XSGE', 'market_date': '20260930'}
    assert PaperTradingService.trading_status(quote, datetime(2026, 9, 30, 9, 30))['tradable'] is True
    assert PaperTradingService.trading_status(quote, datetime(2026, 9, 30, 12, 0))['tradable'] is False
    assert PaperTradingService.trading_status(quote, datetime(2026, 10, 1, 9, 30))['reason'] == '法定节假日休市，暂不支持模拟交易'
    assert PaperTradingService.trading_status(quote, datetime(2026, 10, 3, 9, 30))['reason'] == '周末休市，暂不支持模拟交易'
    assert PaperTradingService.trading_status(quote, datetime(2026, 10, 8, 9, 30))['reason'] == '非交易日，暂不支持模拟交易'


def test_position_model_accepts_service_field_names() -> None:
    position = PaperPositionModel(position_id=1, contract_code='BU888.XSGE', contract_name='沥青主力', side='空', quantity=3, average_price=5013, last_price=5013, margin=150390, unrealized_pnl=0)
    assert position.model_dump(by_alias=True)['positionId'] == 1


def test_fee_is_one_bps_of_notional() -> None:
    quote = {'contract_code': 'BU888.XSGE', 'price': 5013, 'multiplier': 10}
    assert PaperTradingService.fee_breakdown(quote, 3) == pytest.approx((15.039, 30.078))
    assert PaperTradingService.fee(quote, 3) == pytest.approx(45.117)


def test_fee_supports_fixed_and_close_today_rates() -> None:
    assert PaperTradingService.fee({'contract_code': 'FG888.XZCE', 'price': 1000, 'multiplier': 20}, 3) == 18
    assert PaperTradingService.fee({'contract_code': 'IF888.XCFE', 'price': 4000, 'multiplier': 300}, 1, True) == pytest.approx(3312)


def test_floating_pnl_uses_previous_mark_price() -> None:
    assert PaperTradingService.floating_pnl(5050, 5013, 10, 3, '多') == 1110
    assert PaperTradingService.floating_pnl(5050, 5013, 10, 3, '空') == -1110


@pytest.mark.asyncio
async def test_close_rejects_when_market_is_closed(monkeypatch) -> None:
    async def closed_quote(_: str) -> dict:
        return {'market_code': 'XSGE', 'market_date': '20260930'}

    class Database:
        async def scalar(self, _):
            return SimpleNamespace(contract_code='BU888.XSGE')

    monkeypatch.setattr(PaperTradingService, '_quote', closed_quote)
    with pytest.raises(ServiceWarning) as exc_info:
        await PaperTradingService.close(Database(), 1, 1)
    assert exc_info.value.message.endswith('暂不支持模拟交易')


@pytest.mark.asyncio
async def test_profit_summary_groups_closed_contract_result() -> None:
    class Database:
        async def scalars(self, _):
            return SimpleNamespace(all=lambda: [
                SimpleNamespace(contract_code='RB888.XSGE', contract_name='螺纹钢主力', action='开仓', fee=3, realized_pnl=None),
                SimpleNamespace(contract_code='RB888.XSGE', contract_name='螺纹钢主力', action='平仓', fee=4, realized_pnl=100),
                SimpleNamespace(contract_code='BU888.XSGE', contract_name='沥青主力', action='开仓', fee=2, realized_pnl=None),
            ])

    assert await PaperTradingService.profit_summary(Database(), 1) == [{
        'contract_code': 'RB888.XSGE', 'contract_name': '螺纹钢主力',
        'realized_pnl': 100.0, 'fee': 7.0, 'trade_count': 1, 'net_pnl': 93.0,
    }]
