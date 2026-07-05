from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from module_stock.dao.stock_xg_night_dao import StockXgNightDao
from module_stock.entity.vo.stock_xg_night_vo import (
    StockXgNightCardModel,
    StockXgNightDimensionModel,
    StockXgNightSuperCardRowModel,
    StockXgNightSuperCardsModel,
)


DIMENSIONS = (
    (240, '240min'),
    (60, '60min'),
    (300, '60+240交集'),
)


class StockXgNightService:
    """
    夜盘选股统计服务层
    """

    @classmethod
    async def get_night_super_cards_services(
        cls, query_db: AsyncSession, trade_date: int | None, limit: int
    ) -> StockXgNightSuperCardsModel:
        resolved_trade_date = trade_date
        if resolved_trade_date is None:
            resolved_trade_date = await StockXgNightDao.get_latest_trade_date(query_db)

        dimensions = [
            StockXgNightDimensionModel(source_type=source_type, label=label) for source_type, label in DIMENSIONS
        ]
        if resolved_trade_date is None:
            return StockXgNightSuperCardsModel(trade_date=None, limit=limit, dimensions=dimensions, rows=[])

        source_rows = await StockXgNightDao.get_super_stat_rows(query_db, resolved_trade_date)
        grouped: dict[str, dict[int, dict[str, Any]]] = defaultdict(dict)
        for row in source_rows:
            signal_name = str(row['signal_name'] or '').strip()
            if not signal_name:
                continue
            grouped[signal_name][int(row['source_type'])] = row

        card_rows = [
            cls._build_card_row(signal_name, source_map, resolved_trade_date)
            for signal_name, source_map in grouped.items()
        ]
        card_rows.sort(
            key=lambda item: (
                item.rank_score,
                cls._max_card_decimal(item, 'ok_rate'),
                cls._sum_card_int(item, 'total_count'),
                item.signal_name,
            ),
            reverse=True,
        )

        return StockXgNightSuperCardsModel(
            trade_date=resolved_trade_date,
            limit=limit,
            dimensions=dimensions,
            rows=card_rows[:limit],
        )

    @classmethod
    def _build_card_row(
        cls, signal_name: str, source_map: dict[int, dict[str, Any]], trade_date: int
    ) -> StockXgNightSuperCardRowModel:
        cards: dict[str, StockXgNightCardModel] = {}
        for source_type, label in DIMENSIONS:
            row = source_map.get(source_type)
            if row:
                cards[str(source_type)] = StockXgNightCardModel(
                    exists=True,
                    source_type=source_type,
                    label=label,
                    trade_date=int(row['trade_date']),
                    signal_name=str(row['signal_name']),
                    total_count=int(row['total_count'] or 0),
                    ok_count=int(row['ok_count'] or 0),
                    ok_rate=cls._decimal(row['ok_rate']),
                    super_count=int(row['super_count'] or 0),
                    super_rate=cls._decimal(row['super_rate']),
                    target_percent=cls._decimal(row['target_percent']),
                    super_percent=cls._decimal(row['super_percent']),
                    window_days=int(row['window_days'] or 0),
                    updated_at=cls._datetime(row['updated_at']),
                )
            else:
                cards[str(source_type)] = StockXgNightCardModel(
                    exists=False,
                    source_type=source_type,
                    label=label,
                    trade_date=trade_date,
                    signal_name=signal_name,
                    empty_reason='当前选股器该维度暂无统计数据',
                )

        rank_score = max(
            (card.super_rate for card in cards.values() if card.exists and card.super_rate is not None),
            default=Decimal('0'),
        )
        return StockXgNightSuperCardRowModel(signal_name=signal_name, rank_score=rank_score, cards=cards)

    @staticmethod
    def _decimal(value: Any) -> Decimal:
        if value is None:
            return Decimal('0')
        return Decimal(str(value))

    @staticmethod
    def _datetime(value: Any) -> datetime | None:
        if value is None or isinstance(value, datetime):
            return value
        return datetime.fromisoformat(str(value))

    @staticmethod
    def _max_card_decimal(row: StockXgNightSuperCardRowModel, field_name: str) -> Decimal:
        return max(
            (
                getattr(card, field_name)
                for card in row.cards.values()
                if card.exists and getattr(card, field_name) is not None
            ),
            default=Decimal('0'),
        )

    @staticmethod
    def _sum_card_int(row: StockXgNightSuperCardRowModel, field_name: str) -> int:
        return sum(
            int(getattr(card, field_name) or 0)
            for card in row.cards.values()
            if card.exists and getattr(card, field_name) is not None
        )
