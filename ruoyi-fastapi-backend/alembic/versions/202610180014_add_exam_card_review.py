"""add exam card review loop

Revision ID: 202610180014
Revises: 202610180013
"""
from alembic import op
import sqlalchemy as sa

revision = '202610180014'
down_revision = '202610180013'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column('exam_card', sa.Column('review_enabled', sa.Boolean(), nullable=False, server_default=sa.false()))
    op.create_table('exam_card_review', sa.Column('review_id', sa.BigInteger(), primary_key=True, autoincrement=True), sa.Column('user_id', sa.BigInteger(), nullable=False), sa.Column('card_id', sa.BigInteger(), nullable=False), sa.Column('state', sa.String(16), nullable=False), sa.Column('required_repetitions', sa.Integer(), nullable=False), sa.Column('completed_repetitions', sa.Integer(), nullable=False), sa.Column('interval_days', sa.Integer(), nullable=False), sa.Column('next_review_time', sa.DateTime()), sa.Column('last_review_time', sa.DateTime()), sa.Column('create_time', sa.DateTime(), nullable=False), sa.Column('update_time', sa.DateTime(), nullable=False), sa.UniqueConstraint('user_id', 'card_id', name='uk_exam_card_review_user_card'))
    op.create_index('ix_exam_card_review_user_id', 'exam_card_review', ['user_id'])
    op.create_index('ix_exam_card_review_card_id', 'exam_card_review', ['card_id'])
    op.create_table('exam_card_review_log', sa.Column('log_id', sa.BigInteger(), primary_key=True, autoincrement=True), sa.Column('user_id', sa.BigInteger(), nullable=False), sa.Column('card_id', sa.BigInteger(), nullable=False), sa.Column('rating', sa.String(8), nullable=False), sa.Column('reviewed_time', sa.DateTime(), nullable=False))
    op.create_index('ix_exam_card_review_log_user_id', 'exam_card_review_log', ['user_id'])
    op.create_index('ix_exam_card_review_log_card_id', 'exam_card_review_log', ['card_id'])
    op.create_index('ix_exam_card_review_log_reviewed_time', 'exam_card_review_log', ['reviewed_time'])
    op.execute("UPDATE exam_card SET review_enabled=1 WHERE category_id=(SELECT category_id FROM exam_category WHERE name='MyBatis 面试题')")

def downgrade() -> None:
    op.drop_table('exam_card_review_log')
    op.drop_table('exam_card_review')
    op.drop_column('exam_card', 'review_enabled')
