import json
from decimal import Decimal

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from module_stock.controller.stock_xg_night_controller import get_stock_xg_night_super_cards
from module_stock.service.stock_xg_night_service import StockXgNightService


CREATE_TABLE_SQL = """
CREATE TABLE stock_xg_night_super_stat (
    trade_date INTEGER NOT NULL,
    source_type INTEGER NOT NULL,
    signal_name TEXT NOT NULL,
    total_count INTEGER,
    ok_count INTEGER,
    ok_rate NUMERIC,
    super_count INTEGER,
    super_rate NUMERIC,
    target_percent NUMERIC,
    super_percent NUMERIC,
    window_days INTEGER,
    updated_at TEXT
)
"""


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine('sqlite+aiosqlite:///:memory:')
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.execute(text(CREATE_TABLE_SQL))

    async with session_factory() as session:
        await session.execute(
            text(
                """
                INSERT INTO stock_xg_night_super_stat (
                    trade_date, source_type, signal_name, total_count, ok_count, ok_rate,
                    super_count, super_rate, target_percent, super_percent, window_days, updated_at
                ) VALUES
                    (20260708, 240, '单K', 10, 8, 80.0, 5, 50.0, 2.0, 4.0, 3, '2026-07-08T21:00:00'),
                    (20260708, 60, '单K', 8, 5, 62.5, 2, 25.0, 2.0, 4.0, 3, '2026-07-08T21:00:00'),
                    (20260708, 300, '双K', 5, 4, 80.0, 4, 80.0, 2.0, 4.0, 3, '2026-07-08T21:00:00'),
                    (20260707, 240, '平量', 6, 2, 33.3, 1, 16.7, 2.0, 4.0, 3, '2026-07-07T21:00:00')
                """
            )
        )
        await session.commit()
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_service_returns_empty_cards_when_no_trade_date():
    engine = create_async_engine('sqlite+aiosqlite:///:memory:')
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.execute(text(CREATE_TABLE_SQL))

    async with session_factory() as session:
        result = await StockXgNightService.get_night_super_cards_services(session, None, 3)

    await engine.dispose()

    assert result.trade_date is None
    assert result.limit == 3
    assert [item.source_type for item in result.dimensions] == [240, 60, 300]
    assert result.rows == []


@pytest.mark.asyncio
async def test_service_uses_latest_trade_date_and_fills_missing_dimension(db_session):
    result = await StockXgNightService.get_night_super_cards_services(db_session, None, 3)

    assert result.trade_date == 20260708
    assert [item.signal_name for item in result.rows] == ['双K', '单K']
    assert result.rows[0].rank_score == Decimal('80.0')
    assert result.rows[0].cards['300'].exists is True
    assert result.rows[0].cards['240'].exists is False
    assert result.rows[0].cards['240'].empty_reason == '当前选股器该维度暂无统计数据'


@pytest.mark.asyncio
async def test_controller_returns_specified_trade_date_cards(db_session):
    response = await get_stock_xg_night_super_cards(db_session, trade_date=20260708, limit=1)
    payload = json.loads(response.body)

    assert payload['data']['tradeDate'] == 20260708
    assert payload['data']['limit'] == 1
    assert payload['data']['rows'][0]['signalName'] == '双K'
    assert payload['data']['rows'][0]['cards']['300']['exists'] is True
    assert payload['data']['rows'][0]['cards']['240']['exists'] is False


@pytest.mark.asyncio
async def test_service_returns_empty_rows_when_requested_date_has_no_rows(db_session):
    result = await StockXgNightService.get_night_super_cards_services(db_session, 20260710, 3)

    assert result.trade_date == 20260710
    assert result.rows == []
