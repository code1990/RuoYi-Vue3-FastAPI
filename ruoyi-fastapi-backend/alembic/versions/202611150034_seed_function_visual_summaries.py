"""seed summaries for built-in visual functions"""

from alembic import op
import sqlalchemy as sa


revision = '202611150034'
down_revision = '202611150033'
branch_labels = None
depends_on = None


def upgrade() -> None:
    summaries = {
        'swing_highs_lows': '高点/低点标记',
        'fvg': '失衡区间块',
        'bos_choch': '结构突破与变化标记',
        'ob': '订单块区间',
        'liquidity': '流动性水平线',
        'previous_high_low': '前高/前低水平线',
        'sessions': '交易时段区块',
        'retracements': '当前与最大回撤曲线',
    }
    for name, summary in summaries.items():
        op.execute(sa.text('UPDATE func_manage SET visual_summary = :summary WHERE func_name = :name AND (visual_summary IS NULL OR visual_summary = "")').bindparams(summary=summary, name=name))


def downgrade() -> None:
    op.execute('UPDATE func_manage SET visual_summary = NULL WHERE func_name IN (\'swing_highs_lows\', \'fvg\', \'bos_choch\', \'ob\', \'liquidity\', \'previous_high_low\', \'sessions\', \'retracements\')')
