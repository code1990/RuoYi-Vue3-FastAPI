"""fix codex created_thread bool

Revision ID: 202607090001
Revises: 202607080001
Create Date: 2026-07-09 00:01:00
"""

from alembic import op
import sqlalchemy as sa


revision = '202607090001'
down_revision = '202607080001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name
    if dialect == 'mysql':
        op.execute(
            """
            ALTER TABLE conversation_task
            MODIFY COLUMN created_thread TINYINT(1) NULL
            COMMENT '是否为本次任务新建线程；1=新建，0=复用'
            """
        )
    else:
        op.alter_column(
            'conversation_task',
            'created_thread',
            existing_type=sa.String(length=128),
            type_=sa.Boolean(),
            existing_nullable=True,
            existing_comment='创建任务的线程ID',
            comment='是否为本次任务新建线程',
        )


def downgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name
    if dialect == 'mysql':
        op.execute(
            """
            ALTER TABLE conversation_task
            MODIFY COLUMN created_thread VARCHAR(128) NULL
            COMMENT '创建任务的线程ID'
            """
        )
    else:
        op.alter_column(
            'conversation_task',
            'created_thread',
            existing_type=sa.Boolean(),
            type_=sa.String(length=128),
            existing_nullable=True,
            existing_comment='是否为本次任务新建线程',
            comment='创建任务的线程ID',
        )
