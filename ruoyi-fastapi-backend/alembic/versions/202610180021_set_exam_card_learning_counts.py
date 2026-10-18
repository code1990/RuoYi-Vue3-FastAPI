"""set exam card learning difficulty

Revision ID: 202610180021
Revises: 202610180020
"""

from alembic import op


revision = '202610180021'
down_revision = '202610180020'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE exam_card SET difficulty = CASE card_type WHEN 'enumeration' THEN 2 WHEN 'scenario' THEN 4 ELSE 3 END WHERE status = 'published'")
    op.execute("UPDATE exam_card_review review JOIN exam_card card ON card.card_id = review.card_id SET review.required_repetitions = GREATEST(4, card.difficulty + 2) WHERE review.state = 'learning'")


def downgrade() -> None:
    op.execute("UPDATE exam_card SET difficulty = 3 WHERE status = 'published'")
    op.execute("UPDATE exam_card_review SET required_repetitions = 5 WHERE state = 'learning'")
