"""add research strategy management"""

from alembic import op
import sqlalchemy as sa

revision = '202611150036'
down_revision = '202611150035'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'research_strategy',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('combination_id', sa.BigInteger(), nullable=False),
        sa.Column('strategy_name', sa.String(200), nullable=False),
        sa.Column('description', sa.String(500)),
        sa.Column('status', sa.String(20), nullable=False, server_default='enabled'),
        sa.Column('created_by', sa.String(50)),
        sa.Column('create_time', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('update_time', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['combination_id'], ['func_combination_manage.id'], name='fk_research_strategy_combination'),
    )
    op.create_index('ix_research_strategy_combination_id', 'research_strategy', ['combination_id'])
    op.execute("""UPDATE sys_menu SET order_num = order_num + 1 WHERE parent_id = (SELECT menu_id FROM (SELECT menu_id FROM sys_menu WHERE path='project-research' LIMIT 1) AS root_menu) AND order_num >= 4 AND menu_type = 'C'""")
    op.execute("""
        INSERT INTO sys_menu (menu_name,parent_id,order_num,path,component,query,route_name,is_frame,is_cache,menu_type,visible,status,perms,icon,create_by,create_time,update_by,update_time,remark)
        SELECT '交易策略', menu_id, 4, 'strategy', 'project-research/strategy/index', '', '', 1, 0, 'C', '0', '0', 'research:strategy:list', 'guide', 'admin', CURRENT_TIMESTAMP, 'admin', CURRENT_TIMESTAMP, '交易策略菜单'
        FROM sys_menu WHERE path='project-research' AND NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms='research:strategy:list')
    """)
    for label, n, perm in [('新增', 1, 'research:strategy:add'), ('删除', 2, 'research:strategy:remove')]:
        op.execute(f"""
            INSERT INTO sys_menu (menu_name,parent_id,order_num,path,component,query,route_name,is_frame,is_cache,menu_type,visible,status,perms,icon,create_by,create_time,update_by,update_time,remark)
            SELECT '策略{label}', menu_id, {n}, '', '', '', '', 1, 0, 'F', '0', '0', '{perm}', '#', 'admin', CURRENT_TIMESTAMP, 'admin', CURRENT_TIMESTAMP, ''
            FROM sys_menu WHERE perms='research:strategy:list' AND NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms='{perm}')
        """)
    op.execute("""INSERT INTO sys_role_menu (role_id, menu_id) SELECT 1, menu_id FROM sys_menu WHERE perms LIKE 'research:strategy:%' AND NOT EXISTS (SELECT 1 FROM sys_role_menu r WHERE r.role_id=1 AND r.menu_id=sys_menu.menu_id)""")


def downgrade() -> None:
    op.execute("DELETE FROM sys_role_menu WHERE menu_id IN (SELECT menu_id FROM sys_menu WHERE perms LIKE 'research:strategy:%')")
    op.execute("DELETE FROM sys_menu WHERE perms LIKE 'research:strategy:%'")
    op.drop_index('ix_research_strategy_combination_id', table_name='research_strategy')
    op.drop_table('research_strategy')
