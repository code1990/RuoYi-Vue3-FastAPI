"""add function visualization summary"""

from alembic import op
import sqlalchemy as sa


revision = '202611150033'
down_revision = '202611150032'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('func_manage', sa.Column('visual_summary', sa.String(200), nullable=True, comment='可视化简述'))


def downgrade() -> None:
    op.drop_column('func_manage', 'visual_summary')
