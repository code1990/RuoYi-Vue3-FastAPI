"""add project research direction"""

from alembic import op
import sqlalchemy as sa


revision = '202611140030'
down_revision = '202611140029'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('project_manage', sa.Column('research_direction', sa.String(50), nullable=True, comment='研究方向'))
    op.execute("UPDATE project_manage SET research_direction='SMC' WHERE project_name='smart-money-concepts'")


def downgrade() -> None:
    op.drop_column('project_manage', 'research_direction')
