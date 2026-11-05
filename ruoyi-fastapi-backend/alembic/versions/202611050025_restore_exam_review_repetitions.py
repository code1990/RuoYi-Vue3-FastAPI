"""restore exam review repetitions

Revision ID: 202611050025
Revises: 202610270024
"""

from alembic import op


revision = '202611050025'
down_revision = '202610270024'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        UPDATE exam_card_review review
        JOIN exam_card_review_log log
          ON log.user_id = review.user_id
         AND log.card_id = review.card_id
         AND log.reviewed_time = review.last_review_time
        SET review.state = CASE WHEN log.rating = 'again' THEN 'learning' ELSE 'review' END,
            review.review_round = CASE WHEN log.rating = 'again' THEN 0 ELSE review.review_round END,
            review.next_review_time = CASE WHEN log.rating = 'again' THEN NULL ELSE NOW() END
        WHERE review.state = 'learning' AND review.review_round > 0
    """)


def downgrade() -> None:
    pass
