"""add exam learning batches

Revision ID: 202610180015
Revises: 202610180014
"""
from alembic import op
import sqlalchemy as sa

revision = '202610180015'
down_revision = '202610180014'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column('exam_card_review', sa.Column('learning_batch', sa.Integer(), nullable=False, server_default='0'))

def downgrade() -> None:
    op.drop_column('exam_card_review', 'learning_batch')
