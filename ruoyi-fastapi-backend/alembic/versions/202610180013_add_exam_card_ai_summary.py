"""add AI summary to exam cards

Revision ID: 202610180013
Revises: 202610180012
"""

from alembic import op
import sqlalchemy as sa


revision = '202610180013'
down_revision = '202610180012'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('exam_card', sa.Column('ai_summary', sa.Text(), nullable=True))
    op.execute("UPDATE exam_card SET ai_summary = '' WHERE ai_summary IS NULL")
    op.alter_column('exam_card', 'ai_summary', existing_type=sa.Text(), nullable=False)


def downgrade() -> None:
    op.drop_column('exam_card', 'ai_summary')
