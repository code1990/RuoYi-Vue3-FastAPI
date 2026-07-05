from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class StockXgNightDao:
    """
    夜盘选股统计数据库操作层
    """

    @classmethod
    async def get_latest_trade_date(cls, db: AsyncSession) -> int | None:
        result = await db.execute(text('SELECT MAX(trade_date) AS trade_date FROM stock_xg_night_super_stat'))
        row = result.mappings().first()
        if not row or row['trade_date'] is None:
            return None
        return int(row['trade_date'])

    @classmethod
    async def get_super_stat_rows(cls, db: AsyncSession, trade_date: int) -> list[dict[str, Any]]:
        result = await db.execute(
            text(
                """
                SELECT
                    trade_date,
                    source_type,
                    signal_name,
                    total_count,
                    ok_count,
                    ok_rate,
                    super_count,
                    super_rate,
                    target_percent,
                    super_percent,
                    window_days,
                    updated_at
                FROM stock_xg_night_super_stat
                WHERE trade_date = :trade_date
                  AND source_type IN (60, 240, 300)
                ORDER BY trade_date DESC, signal_name, source_type
                """
            ),
            {'trade_date': trade_date},
        )
        return [dict(row) for row in result.mappings().all()]
