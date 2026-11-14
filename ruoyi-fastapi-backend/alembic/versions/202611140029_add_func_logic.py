"""add detailed function logic"""

from alembic import op
import sqlalchemy as sa


revision = '202611140029'
down_revision = '202611140028'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('func_manage', sa.Column('logic', sa.Text(), nullable=True, comment='详细实现逻辑'))


def downgrade() -> None:
    op.drop_column('func_manage', 'logic')
