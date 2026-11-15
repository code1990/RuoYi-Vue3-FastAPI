"""add project rating and symbol adaptation"""

from alembic import op
import sqlalchemy as sa

revision = '202611150037'
down_revision = '202611150036'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('project_manage', sa.Column('star', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('project_manage', sa.Column('symbol_adaptation', sa.String(500), nullable=True))


def downgrade() -> None:
    op.drop_column('project_manage', 'symbol_adaptation')
    op.drop_column('project_manage', 'star')
