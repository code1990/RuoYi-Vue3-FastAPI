"""add function combination management"""

from alembic import op
import sqlalchemy as sa


revision = '202611140031'
down_revision = '202611140030'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'func_combination_manage',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('project_id', sa.BigInteger(), nullable=False),
        sa.Column('combination_name', sa.String(200), nullable=False),
        sa.Column('research_direction', sa.String(50), nullable=True),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('function_ids', sa.JSON(), nullable=True),
        sa.Column('create_time', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('update_time', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['project_id'], ['project_manage.id'], name='fk_func_combination_project'),
        sa.UniqueConstraint('project_id', 'combination_name', name='uk_func_combination_project_name'),
        comment='函数组合管理表',
    )
    op.execute("""
        INSERT INTO sys_menu (menu_name,parent_id,order_num,path,component,query,route_name,is_frame,is_cache,menu_type,visible,status,perms,icon,create_by,create_time,update_by,update_time,remark)
        SELECT '函数组合管理', menu_id, 3, 'function-combination', 'project-research/combination/index', '', '', 1, 0, 'C', '0', '0', 'function:combination:list', 'share', 'admin', CURRENT_TIMESTAMP, 'admin', CURRENT_TIMESTAMP, '函数组合管理菜单'
        FROM sys_menu WHERE path='project-research' AND NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms='function:combination:list')
    """)
    for name, order_num, perm in [('组合新增', 1, 'function:combination:add'), ('组合修改', 2, 'function:combination:edit'), ('组合删除', 3, 'function:combination:remove')]:
        op.execute(f"""
            INSERT INTO sys_menu (menu_name,parent_id,order_num,path,component,query,route_name,is_frame,is_cache,menu_type,visible,status,perms,icon,create_by,create_time,update_by,update_time,remark)
            SELECT '{name}', menu_id, {order_num}, '', '', '', '', 1, 0, 'F', '0', '0', '{perm}', '#', 'admin', CURRENT_TIMESTAMP, 'admin', CURRENT_TIMESTAMP, ''
            FROM sys_menu WHERE perms='function:combination:list' AND NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms='{perm}')
        """)
    op.execute("""
        INSERT INTO sys_role_menu (role_id, menu_id)
        SELECT 1, menu_id FROM sys_menu
        WHERE perms LIKE 'function:combination:%'
          AND NOT EXISTS (SELECT 1 FROM sys_role_menu r WHERE r.role_id=1 AND r.menu_id=sys_menu.menu_id)
    """)


def downgrade() -> None:
    op.execute("DELETE FROM sys_role_menu WHERE menu_id IN (SELECT menu_id FROM sys_menu WHERE perms LIKE 'function:combination:%')")
    op.execute("DELETE FROM sys_menu WHERE perms LIKE 'function:combination:%'")
    op.drop_table('func_combination_manage')
