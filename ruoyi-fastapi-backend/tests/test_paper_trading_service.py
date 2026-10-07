import pytest
from datetime import datetime

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
    quote = {'market_code': 'XSGE', 'market_date': '20261007'}
    assert PaperTradingService.trading_status(quote, datetime(2026, 10, 7, 9, 30))['tradable'] is True
    assert PaperTradingService.trading_status(quote, datetime(2026, 10, 7, 12, 0))['tradable'] is False
    assert PaperTradingService.trading_status(quote, datetime(2026, 10, 8, 9, 30))['reason'] == '今日休市，暂不支持模拟交易'


def test_position_model_accepts_service_field_names() -> None:
    position = PaperPositionModel(position_id=1, contract_code='BU888.XSGE', contract_name='沥青主力', side='空', quantity=3, average_price=5013, last_price=5013, margin=150390, unrealized_pnl=0)
    assert position.model_dump(by_alias=True)['positionId'] == 1
