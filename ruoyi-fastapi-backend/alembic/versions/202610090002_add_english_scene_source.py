"""add english scene source

Revision ID: 202610090002
Revises: 202610090001
"""

from alembic import op
import sqlalchemy as sa


revision = '202610090002'
down_revision = '202610090001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('english_scene', sa.Column('source_url', sa.String(500), nullable=False, server_default=''))


def downgrade() -> None:
    op.drop_column('english_scene', 'source_url')
