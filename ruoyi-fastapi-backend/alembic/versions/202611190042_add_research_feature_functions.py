"""link research features to multiple existing functions"""

from alembic import op
import sqlalchemy as sa


revision = '202611190042'
down_revision = '202611190041'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('research_feature', sa.Column('function_ids', sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column('research_feature', 'function_ids')
