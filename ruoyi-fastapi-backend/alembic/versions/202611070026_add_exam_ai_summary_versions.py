"""add exam AI summary versions

Revision ID: 202611070026
Revises: 202611050025
"""

from alembic import op
import sqlalchemy as sa


revision = '202611070026'
down_revision = '202611050025'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('exam_card', sa.Column('active_ai_summary_version_id', sa.BigInteger(), nullable=True))
    op.create_table(
        'exam_card_ai_summary_version',
        sa.Column('summary_version_id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('card_id', sa.BigInteger(), nullable=False),
        sa.Column('version_no', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(100), nullable=False),
        sa.Column('ai_summary', sa.Text(), nullable=False),
        sa.Column('create_time', sa.DateTime(), nullable=False),
        sa.Column('update_time', sa.DateTime(), nullable=False),
        sa.UniqueConstraint('card_id', 'version_no', name='uk_exam_card_ai_summary_version_card_version'),
    )
    op.create_index('ix_exam_card_ai_summary_version_card_id', 'exam_card_ai_summary_version', ['card_id'])
    op.execute("""
        INSERT INTO exam_card_ai_summary_version(card_id, version_no, title, ai_summary, create_time, update_time)
        SELECT card_id, 1, '原始总结', ai_summary, create_time, update_time
        FROM exam_card
        WHERE ai_summary <> ''
    """)
    op.execute("""
        UPDATE exam_card card
        JOIN exam_card_ai_summary_version version
          ON version.card_id = card.card_id AND version.version_no = 1
        SET card.active_ai_summary_version_id = version.summary_version_id
    """)
    op.execute("""
        INSERT INTO sys_menu(menu_name,parent_id,order_num,path,component,query,route_name,is_frame,is_cache,menu_type,visible,status,perms,icon,create_by,create_time,update_by,update_time,remark)
        SELECT '编辑AI总结方案', menu_id, 2, '', '', '', '', 1, 0, 'F', '0', '0', 'exam:card:edit', '#', 'admin', CURRENT_TIMESTAMP, 'admin', CURRENT_TIMESTAMP, '管理题目AI总结方案'
        FROM sys_menu
        WHERE perms = 'exam:card:list'
          AND NOT EXISTS(SELECT 1 FROM sys_menu WHERE perms = 'exam:card:edit')
    """)
    op.execute("""
        INSERT INTO sys_role_menu(role_id, menu_id)
        SELECT 1, menu_id FROM sys_menu WHERE perms = 'exam:card:edit'
        AND NOT EXISTS(SELECT 1 FROM sys_role_menu x WHERE x.role_id = 1 AND x.menu_id = sys_menu.menu_id)
    """)


def downgrade() -> None:
    op.execute("DELETE FROM sys_role_menu WHERE menu_id IN (SELECT menu_id FROM sys_menu WHERE perms = 'exam:card:edit')")
    op.execute("DELETE FROM sys_menu WHERE perms = 'exam:card:edit'")
    op.drop_index('ix_exam_card_ai_summary_version_card_id', table_name='exam_card_ai_summary_version')
    op.drop_table('exam_card_ai_summary_version')
    op.drop_column('exam_card', 'active_ai_summary_version_id')
