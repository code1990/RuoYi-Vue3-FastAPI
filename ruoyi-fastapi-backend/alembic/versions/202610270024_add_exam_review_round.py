"""add exam review round

Revision ID: 202610270024
Revises: 202610180023
"""

import sqlalchemy as sa
from alembic import op


revision = '202610270024'
down_revision = '202610180023'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('exam_card_review', sa.Column('review_round', sa.Integer(), nullable=False, server_default='0'))
    op.execute("UPDATE exam_card_review SET review_round = 1, completed_repetitions = 0 WHERE state = 'review'")


def downgrade() -> None:
    op.drop_column('exam_card_review', 'review_round')
