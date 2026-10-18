"""raise hard card repetitions

Revision ID: 202610180023
Revises: 202610180022
"""

from alembic import op


revision = '202610180023'
down_revision = '202610180022'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE exam_card SET difficulty = CASE WHEN card_type = 'scenario' THEN 6 ELSE 3 END WHERE status = 'published'")
    op.execute("UPDATE exam_card_review review JOIN exam_card card ON card.card_id = review.card_id SET review.required_repetitions = GREATEST(review.required_repetitions, 5, card.difficulty + 2) WHERE review.state = 'learning'")


def downgrade() -> None:
    op.execute("UPDATE exam_card SET difficulty = CASE WHEN card_type = 'scenario' THEN 4 ELSE 3 END WHERE status = 'published'")
