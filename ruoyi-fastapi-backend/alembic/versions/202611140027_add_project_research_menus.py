"""add project research menus

Revision ID: 202611140027
Revises: 202611070026
"""

from alembic import op


revision = '202611140027'
down_revision = '202611070026'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        INSERT INTO sys_menu
            (menu_name, parent_id, order_num, path, component, query, route_name,
             is_frame, is_cache, menu_type, visible, status, perms, icon,
             create_by, create_time, update_by, update_time, remark)
        SELECT '项目研究', 0, 5, 'project-research', 'Layout', '', '',
               1, 0, 'M', '0', '0', '', 'code', 'admin', CURRENT_TIMESTAMP,
               'admin', CURRENT_TIMESTAMP, '项目研究目录'
        WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE path = 'project-research')
    """)
    op.execute("""
        INSERT INTO sys_menu
            (menu_name, parent_id, order_num, path, component, query, route_name,
             is_frame, is_cache, menu_type, visible, status, perms, icon,
             create_by, create_time, update_by, update_time, remark)
        SELECT '项目管理', menu_id, 1, 'project', 'project-research/project/index',
               '', '', 1, 0, 'C', '0', '0', 'project:manage:list', 'folder',
               'admin', CURRENT_TIMESTAMP, 'admin', CURRENT_TIMESTAMP, '项目管理菜单'
        FROM sys_menu
        WHERE path = 'project-research'
          AND NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'project:manage:list')
    """)
    op.execute("""
        INSERT INTO sys_menu
            (menu_name, parent_id, order_num, path, component, query, route_name,
             is_frame, is_cache, menu_type, visible, status, perms, icon,
             create_by, create_time, update_by, update_time, remark)
        SELECT '函数管理', menu_id, 2, 'function', 'project-research/function/index',
               '', '', 1, 0, 'C', '0', '0', 'function:manage:list', 'code',
               'admin', CURRENT_TIMESTAMP, 'admin', CURRENT_TIMESTAMP, '函数管理菜单'
        FROM sys_menu
        WHERE path = 'project-research'
          AND NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'function:manage:list')
    """)
    op.execute("""
        INSERT INTO sys_role_menu (role_id, menu_id)
        SELECT 1, menu_id
        FROM sys_menu
        WHERE (perms IN ('project:manage:list', 'function:manage:list')
               OR path = 'project-research')
          AND NOT EXISTS (
              SELECT 1 FROM sys_role_menu r
              WHERE r.role_id = 1 AND r.menu_id = sys_menu.menu_id
          )
    """)


def downgrade() -> None:
    op.execute("""
        DELETE FROM sys_role_menu
        WHERE menu_id IN (
            SELECT menu_id FROM sys_menu
            WHERE path = 'project-research'
               OR perms IN ('project:manage:list', 'function:manage:list')
        )
    """)
    op.execute("""
        DELETE FROM sys_menu
        WHERE path = 'project-research'
           OR perms IN ('project:manage:list', 'function:manage:list')
    """)
