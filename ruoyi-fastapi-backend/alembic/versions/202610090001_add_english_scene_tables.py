"""add english scene tables

Revision ID: 202610090001
Revises: 202610070002
"""

from alembic import op
import sqlalchemy as sa


revision = '202610090001'
down_revision = '202610070002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('english_scene', sa.Column('scene_id', sa.BigInteger(), primary_key=True, autoincrement=True), sa.Column('title', sa.String(100), nullable=False), sa.Column('description', sa.String(500), nullable=False, server_default=''), sa.Column('cover_url', sa.String(500), nullable=False, server_default=''), sa.Column('animation_media_id', sa.BigInteger()), sa.Column('status', sa.String(16), nullable=False, server_default='draft'), sa.Column('sort_no', sa.Integer(), nullable=False, server_default='0'), sa.Column('create_time', sa.DateTime(), nullable=False), sa.Column('update_time', sa.DateTime(), nullable=False))
    op.create_table('english_scene_word', sa.Column('relation_id', sa.BigInteger(), primary_key=True, autoincrement=True), sa.Column('scene_id', sa.BigInteger(), nullable=False, index=True), sa.Column('word_id', sa.BigInteger(), nullable=False, index=True), sa.Column('sort_no', sa.Integer(), nullable=False, server_default='0'), sa.UniqueConstraint('scene_id', 'word_id', name='uk_english_scene_word'))


def downgrade() -> None:
    op.drop_table('english_scene_word')
    op.drop_table('english_scene')
