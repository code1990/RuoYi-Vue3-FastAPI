"""add codex conversation tables

Revision ID: 202607080001
Revises:
Create Date: 2026-07-08 00:01:00
"""

from collections.abc import Iterable

from alembic import op
import sqlalchemy as sa


revision = '202607080001'
down_revision = None
branch_labels = None
depends_on = None


def _has_table(inspector: sa.Inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names()


def _existing_indexes(inspector: sa.Inspector, table_name: str) -> set[str]:
    return {item['name'] for item in inspector.get_indexes(table_name)}


def _existing_unique_constraints(inspector: sa.Inspector, table_name: str) -> set[str]:
    return {item['name'] for item in inspector.get_unique_constraints(table_name)}


def _existing_foreign_keys(inspector: sa.Inspector, table_name: str) -> set[str]:
    return {item['name'] for item in inspector.get_foreign_keys(table_name) if item.get('name')}


def _create_indexes_if_missing(
    inspector: sa.Inspector,
    table_name: str,
    indexes: Iterable[tuple[str, list[str], bool]],
) -> None:
    existing_indexes = _existing_indexes(inspector, table_name)
    existing_uniques = _existing_unique_constraints(inspector, table_name)
    for name, columns, unique in indexes:
        if unique:
            if name in existing_uniques:
                continue
            op.create_unique_constraint(name, table_name, columns)
            continue
        if name in existing_indexes:
            continue
        op.create_index(name, table_name, columns, unique=False)


def _create_foreign_key_if_missing(
    inspector: sa.Inspector,
    table_name: str,
    constraint_name: str,
    local_columns: list[str],
    remote_table: str,
    remote_columns: list[str],
) -> None:
    if constraint_name in _existing_foreign_keys(inspector, table_name):
        return
    op.create_foreign_key(
        constraint_name,
        table_name,
        remote_table,
        local_columns,
        remote_columns,
        onupdate='CASCADE',
        ondelete='CASCADE',
    )


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not _has_table(inspector, 'conversation'):
        op.create_table(
            'conversation',
            sa.Column('id', sa.BigInteger(), primary_key=True, nullable=False, autoincrement=True, comment='主键ID'),
            sa.Column('conversation_id', sa.String(length=64), nullable=False, comment='会话ID'),
            sa.Column('workspace_id', sa.String(length=128), nullable=True, comment='工作区ID'),
            sa.Column('thread_id', sa.String(length=128), nullable=True, comment='线程ID'),
            sa.Column('title', sa.String(length=255), nullable=True, comment='标题'),
            sa.Column('requirement', sa.Text(), nullable=True, comment='需求内容'),
            sa.Column('status', sa.String(length=32), nullable=True, comment='会话状态'),
            sa.Column('operator', sa.String(length=64), nullable=True, comment='操作者'),
            sa.Column('last_message_preview', sa.Text(), nullable=True, comment='最后一条消息预览'),
            sa.Column('final_summary', sa.Text(), nullable=True, comment='最终总结'),
            sa.Column('last_error', sa.Text(), nullable=True, comment='最后错误'),
            sa.Column('created_at_ms', sa.BigInteger(), nullable=True, comment='创建时间毫秒时间戳'),
            sa.Column('updated_at_ms', sa.BigInteger(), nullable=True, comment='更新时间毫秒时间戳'),
            comment='Codex 对话主表',
        )
        inspector = sa.inspect(bind)
    _create_indexes_if_missing(
        inspector,
        'conversation',
        [
            ('uk_conversation_id', ['conversation_id'], True),
            ('idx_conversation_workspace_updated', ['workspace_id', 'updated_at_ms'], False),
            ('idx_conversation_thread_id', ['thread_id'], False),
        ],
    )

    if not _has_table(inspector, 'conversation_message'):
        op.create_table(
            'conversation_message',
            sa.Column('id', sa.BigInteger(), primary_key=True, nullable=False, autoincrement=True, comment='主键ID'),
            sa.Column('conversation_id', sa.String(length=64), nullable=False, comment='会话ID'),
            sa.Column('thread_id', sa.String(length=128), nullable=True, comment='线程ID'),
            sa.Column('turn_id', sa.String(length=128), nullable=True, comment='轮次ID'),
            sa.Column('role', sa.String(length=32), nullable=True, comment='消息角色'),
            sa.Column('message_type', sa.String(length=64), nullable=True, comment='消息类型'),
            sa.Column('content', sa.Text(), nullable=True, comment='消息内容'),
            sa.Column('payload_json', sa.Text(), nullable=True, comment='扩展负载JSON'),
            sa.Column('sequence_no', sa.BigInteger(), nullable=True, comment='消息顺序号'),
            sa.Column('created_at_ms', sa.BigInteger(), nullable=True, comment='创建时间毫秒时间戳'),
            comment='Codex 对话消息表',
        )
        inspector = sa.inspect(bind)
    _create_indexes_if_missing(
        inspector,
        'conversation_message',
        [
            ('idx_conversation_message_conversation_seq', ['conversation_id', 'sequence_no'], False),
            ('idx_conversation_message_thread_turn', ['thread_id', 'turn_id'], False),
        ],
    )
    _create_foreign_key_if_missing(
        inspector,
        'conversation_message',
        'fk_conversation_message_conversation_id',
        ['conversation_id'],
        'conversation',
        ['conversation_id'],
    )

    if not _has_table(inspector, 'conversation_event'):
        op.create_table(
            'conversation_event',
            sa.Column('id', sa.BigInteger(), primary_key=True, nullable=False, autoincrement=True, comment='主键ID'),
            sa.Column('conversation_id', sa.String(length=64), nullable=False, comment='会话ID'),
            sa.Column('thread_id', sa.String(length=128), nullable=True, comment='线程ID'),
            sa.Column('turn_id', sa.String(length=128), nullable=True, comment='轮次ID'),
            sa.Column('event_type', sa.String(length=64), nullable=True, comment='事件类型'),
            sa.Column('event_status', sa.String(length=32), nullable=True, comment='事件状态'),
            sa.Column('payload_json', sa.Text(), nullable=True, comment='事件负载JSON'),
            sa.Column('created_at_ms', sa.BigInteger(), nullable=True, comment='创建时间毫秒时间戳'),
            comment='Codex 对话事件表',
        )
        inspector = sa.inspect(bind)
    _create_indexes_if_missing(
        inspector,
        'conversation_event',
        [
            ('idx_conversation_event_conversation_time', ['conversation_id', 'created_at_ms'], False),
            ('idx_conversation_event_thread_turn', ['thread_id', 'turn_id'], False),
        ],
    )
    _create_foreign_key_if_missing(
        inspector,
        'conversation_event',
        'fk_conversation_event_conversation_id',
        ['conversation_id'],
        'conversation',
        ['conversation_id'],
    )

    if not _has_table(inspector, 'conversation_task'):
        op.create_table(
            'conversation_task',
            sa.Column('id', sa.BigInteger(), primary_key=True, nullable=False, autoincrement=True, comment='主键ID'),
            sa.Column('conversation_id', sa.String(length=64), nullable=False, comment='会话ID'),
            sa.Column('task_id', sa.String(length=128), nullable=False, comment='任务ID'),
            sa.Column('workspace_id', sa.String(length=128), nullable=True, comment='工作区ID'),
            sa.Column('thread_id', sa.String(length=128), nullable=True, comment='线程ID'),
            sa.Column('turn_id', sa.String(length=128), nullable=True, comment='轮次ID'),
            sa.Column('status', sa.String(length=32), nullable=True, comment='任务状态'),
            sa.Column('created_thread', sa.Boolean(), nullable=True, comment='是否为本次任务新建线程'),
            sa.Column('submitted_at_ms', sa.BigInteger(), nullable=True, comment='提交时间毫秒时间戳'),
            sa.Column('completed_at_ms', sa.BigInteger(), nullable=True, comment='完成时间毫秒时间戳'),
            sa.Column('last_error', sa.Text(), nullable=True, comment='最后错误'),
            comment='Codex 对话任务表',
        )
        inspector = sa.inspect(bind)
    _create_indexes_if_missing(
        inspector,
        'conversation_task',
        [
            ('uk_conversation_task_id', ['task_id'], True),
            ('idx_conversation_task_conversation_submitted', ['conversation_id', 'submitted_at_ms'], False),
            ('idx_conversation_task_task_id', ['task_id'], False),
        ],
    )
    _create_foreign_key_if_missing(
        inspector,
        'conversation_task',
        'fk_conversation_task_conversation_id',
        ['conversation_id'],
        'conversation',
        ['conversation_id'],
    )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    for table_name, constraint_name in (
        ('conversation_task', 'fk_conversation_task_conversation_id'),
        ('conversation_event', 'fk_conversation_event_conversation_id'),
        ('conversation_message', 'fk_conversation_message_conversation_id'),
    ):
        if _has_table(inspector, table_name) and constraint_name in _existing_foreign_keys(inspector, table_name):
            op.drop_constraint(constraint_name, table_name, type_='foreignkey')
            inspector = sa.inspect(bind)
    for table_name in ('conversation_task', 'conversation_event', 'conversation_message', 'conversation'):
        if _has_table(inspector, table_name):
            op.drop_table(table_name)
            inspector = sa.inspect(bind)
