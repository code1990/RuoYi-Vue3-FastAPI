"""keep five-recall learning baseline

Revision ID: 202610180022
Revises: 202610180021
"""

from alembic import op


revision = '202610180022'
down_revision = '202610180021'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE exam_card SET difficulty = CASE WHEN card_type = 'scenario' THEN 4 ELSE 3 END WHERE status = 'published'")
    op.execute("UPDATE exam_card_review review JOIN exam_card card ON card.card_id = review.card_id SET review.required_repetitions = GREATEST(review.required_repetitions, 5, card.difficulty + 2) WHERE review.state = 'learning'")


def downgrade() -> None:
    op.execute("UPDATE exam_card SET difficulty = CASE card_type WHEN 'enumeration' THEN 2 WHEN 'scenario' THEN 4 ELSE 3 END WHERE status = 'published'")
