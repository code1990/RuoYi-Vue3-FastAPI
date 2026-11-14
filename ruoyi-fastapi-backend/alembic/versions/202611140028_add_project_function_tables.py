"""add project and function management tables"""

from alembic import op
import sqlalchemy as sa


revision = '202611140028'
down_revision = '202611140027'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'project_manage',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('project_name', sa.String(200), nullable=False),
        sa.Column('repo_url', sa.String(500), nullable=True),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('language', sa.String(20), nullable=True),
        sa.Column('version', sa.String(100), nullable=True),
        sa.Column('created_by', sa.String(50), nullable=True),
        sa.Column('create_time', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('update_time', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.text('CURRENT_TIMESTAMP')),
        sa.UniqueConstraint('project_name', name='uk_project_manage_name'),
        comment='项目管理表',
    )
    op.create_table(
        'func_manage',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('project_id', sa.BigInteger(), nullable=False),
        sa.Column('func_name', sa.String(100), nullable=False),
        sa.Column('func_desc', sa.String(500), nullable=True),
        sa.Column('language', sa.String(20), nullable=False),
        sa.Column('func_type', sa.String(20), nullable=False),
        sa.Column('func_code', sa.Text(), nullable=False),
        sa.Column('params_template', sa.JSON(), nullable=True),
        sa.Column('func_tags', sa.String(200), nullable=True),
        sa.Column('file_path', sa.String(500), nullable=True),
        sa.Column('class_name', sa.String(100), nullable=True),
        sa.Column('created_by', sa.String(50), nullable=True),
        sa.Column('create_time', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('update_time', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['project_id'], ['project_manage.id'], name='fk_func_manage_project'),
        sa.UniqueConstraint('project_id', 'func_name', name='uk_func_manage_project_name'),
        comment='函数管理表',
    )
    op.create_index('ix_func_manage_project_id', 'func_manage', ['project_id'])
    op.execute("""
        INSERT INTO sys_menu (menu_name,parent_id,order_num,path,component,query,route_name,is_frame,is_cache,menu_type,visible,status,perms,icon,create_by,create_time,update_by,update_time,remark)
        SELECT '项目新增', menu_id, 1, '', '', '', '', 1, 0, 'F', '0', '0', 'project:manage:add', '#', 'admin', CURRENT_TIMESTAMP, 'admin', CURRENT_TIMESTAMP, ''
        FROM sys_menu WHERE perms='project:manage:list' AND NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms='project:manage:add')
    """)
    op.execute("""
        INSERT INTO sys_menu (menu_name,parent_id,order_num,path,component,query,route_name,is_frame,is_cache,menu_type,visible,status,perms,icon,create_by,create_time,update_by,update_time,remark)
        SELECT '项目修改', menu_id, 2, '', '', '', '', 1, 0, 'F', '0', '0', 'project:manage:edit', '#', 'admin', CURRENT_TIMESTAMP, 'admin', CURRENT_TIMESTAMP, ''
        FROM sys_menu WHERE perms='project:manage:list' AND NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms='project:manage:edit')
    """)
    op.execute("""
        INSERT INTO sys_menu (menu_name,parent_id,order_num,path,component,query,route_name,is_frame,is_cache,menu_type,visible,status,perms,icon,create_by,create_time,update_by,update_time,remark)
        SELECT '项目删除', menu_id, 3, '', '', '', '', 1, 0, 'F', '0', '0', 'project:manage:remove', '#', 'admin', CURRENT_TIMESTAMP, 'admin', CURRENT_TIMESTAMP, ''
        FROM sys_menu WHERE perms='project:manage:list' AND NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms='project:manage:remove')
    """)
    for name, order_num, perm in [('函数新增', 1, 'function:manage:add'), ('函数修改', 2, 'function:manage:edit'), ('函数删除', 3, 'function:manage:remove')]:
        op.execute(f"""
            INSERT INTO sys_menu (menu_name,parent_id,order_num,path,component,query,route_name,is_frame,is_cache,menu_type,visible,status,perms,icon,create_by,create_time,update_by,update_time,remark)
            SELECT '{name}', menu_id, {order_num}, '', '', '', '', 1, 0, 'F', '0', '0', '{perm}', '#', 'admin', CURRENT_TIMESTAMP, 'admin', CURRENT_TIMESTAMP, ''
            FROM sys_menu WHERE perms='function:manage:list' AND NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms='{perm}')
        """)
    op.execute("""
        INSERT INTO sys_role_menu (role_id, menu_id)
        SELECT 1, menu_id FROM sys_menu
        WHERE perms IN ('project:manage:add','project:manage:edit','project:manage:remove','function:manage:add','function:manage:edit','function:manage:remove')
          AND NOT EXISTS (SELECT 1 FROM sys_role_menu r WHERE r.role_id=1 AND r.menu_id=sys_menu.menu_id)
    """)


def downgrade() -> None:
    op.execute("DELETE FROM sys_role_menu WHERE menu_id IN (SELECT menu_id FROM sys_menu WHERE perms LIKE 'project:manage:%' OR perms LIKE 'function:manage:%')")
    op.execute("DELETE FROM sys_menu WHERE perms LIKE 'project:manage:%' OR perms LIKE 'function:manage:%'")
    op.drop_index('ix_func_manage_project_id', table_name='func_manage')
    op.drop_table('func_manage')
    op.drop_table('project_manage')
