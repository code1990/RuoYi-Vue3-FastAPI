"""add function visualization capability flag"""

from alembic import op
import sqlalchemy as sa


revision = '202611150032'
down_revision = '202611140031'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('func_manage', sa.Column('visual_enabled', sa.Boolean(), nullable=False, server_default=sa.text('0'), comment='是否支持可视化'))
    op.execute("""
        UPDATE func_manage
        SET visual_enabled = 1
        WHERE func_name IN ('swing_highs_lows', 'fvg', 'bos_choch', 'ob', 'liquidity', 'previous_high_low', 'sessions', 'retracements')
    """)


def downgrade() -> None:
    op.drop_column('func_manage', 'visual_enabled')
