"""add english content tables

Revision ID: 202610070002
Revises: 202610070001
"""

from alembic import op
import sqlalchemy as sa


revision = '202610070002'
down_revision = '202610070001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('english_book', sa.Column('book_id', sa.BigInteger(), primary_key=True, autoincrement=True), sa.Column('title', sa.String(100), nullable=False), sa.Column('description', sa.String(500), nullable=False, server_default=''), sa.Column('cover_url', sa.String(500), nullable=False, server_default=''), sa.Column('source_url', sa.String(500), nullable=False, server_default=''), sa.Column('status', sa.String(16), nullable=False, server_default='draft'), sa.Column('sort_no', sa.Integer(), nullable=False, server_default='0'), sa.Column('create_time', sa.DateTime(), nullable=False), sa.Column('update_time', sa.DateTime(), nullable=False))
    op.create_table('english_unit', sa.Column('unit_id', sa.BigInteger(), primary_key=True, autoincrement=True), sa.Column('book_id', sa.BigInteger(), nullable=False, index=True), sa.Column('title', sa.String(100), nullable=False), sa.Column('sort_no', sa.Integer(), nullable=False, server_default='0'))
    op.create_table('english_word', sa.Column('word_id', sa.BigInteger(), primary_key=True, autoincrement=True), sa.Column('word', sa.String(100), nullable=False, unique=True), sa.Column('phonetic_uk', sa.String(200), nullable=False, server_default=''), sa.Column('phonetic_us', sa.String(200), nullable=False, server_default=''), sa.Column('meaning_zh', sa.Text(), nullable=False), sa.Column('part_of_speech', sa.String(100), nullable=False, server_default=''), sa.Column('example_en', sa.Text(), nullable=False), sa.Column('example_zh', sa.Text(), nullable=False), sa.Column('source_url', sa.String(500), nullable=False, server_default=''))
    op.create_table('english_book_word', sa.Column('relation_id', sa.BigInteger(), primary_key=True, autoincrement=True), sa.Column('book_id', sa.BigInteger(), nullable=False, index=True), sa.Column('unit_id', sa.BigInteger(), nullable=False, index=True), sa.Column('word_id', sa.BigInteger(), nullable=False, index=True), sa.Column('sort_no', sa.Integer(), nullable=False, server_default='0'), sa.UniqueConstraint('book_id', 'unit_id', 'word_id', name='uk_english_book_word'))
    op.create_table('english_media_asset', sa.Column('media_id', sa.BigInteger(), primary_key=True, autoincrement=True), sa.Column('media_type', sa.String(16), nullable=False), sa.Column('storage_path', sa.String(500), nullable=False, unique=True), sa.Column('source_url', sa.String(500), nullable=False, server_default=''), sa.Column('sha256', sa.String(64), nullable=False, server_default=''), sa.Column('file_size', sa.BigInteger(), nullable=False, server_default='0'), sa.Column('duration', sa.Float()), sa.Column('status', sa.String(16), nullable=False, server_default='ready'), sa.Column('create_time', sa.DateTime(), nullable=False))
    op.create_table('english_word_pronunciation', sa.Column('pronunciation_id', sa.BigInteger(), primary_key=True, autoincrement=True), sa.Column('word_id', sa.BigInteger(), nullable=False, index=True), sa.Column('accent', sa.String(4), nullable=False), sa.Column('phonetic', sa.String(200), nullable=False, server_default=''), sa.Column('media_id', sa.BigInteger(), nullable=False), sa.UniqueConstraint('word_id', 'accent', name='uk_english_word_pronunciation'))
    op.create_table('english_word_animation', sa.Column('animation_id', sa.BigInteger(), primary_key=True, autoincrement=True), sa.Column('word_id', sa.BigInteger(), nullable=False, unique=True), sa.Column('animation_type', sa.String(32), nullable=False, server_default='template'), sa.Column('animation_config', sa.Text(), nullable=False), sa.Column('media_id', sa.BigInteger()), sa.Column('status', sa.String(16), nullable=False, server_default='draft'))


def downgrade() -> None:
    for name in ('english_word_animation', 'english_word_pronunciation', 'english_media_asset', 'english_book_word', 'english_word', 'english_unit', 'english_book'):
        op.drop_table(name)
