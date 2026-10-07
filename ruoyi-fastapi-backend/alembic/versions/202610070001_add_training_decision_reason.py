"""add training decision reason

Revision ID: 202610070001
Revises: 202607090001
Create Date: 2026-10-07 16:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = '202610070001'
down_revision = '202607090001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if 'future_training_decision' in inspector.get_table_names() and 'reason' not in {column['name'] for column in inspector.get_columns('future_training_decision')}:
        op.add_column('future_training_decision', sa.Column('reason', sa.String(length=500), nullable=False, server_default=''))


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if 'future_training_decision' in inspector.get_table_names() and 'reason' in {column['name'] for column in inspector.get_columns('future_training_decision')}:
        op.drop_column('future_training_decision', 'reason')
