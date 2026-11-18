"""add SMC requirement and feature tables"""

from alembic import op
import sqlalchemy as sa


revision = '202611180039'
down_revision = '202611150038'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'smc_requirement',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('requirement_code', sa.String(30), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('source_document_id', sa.BigInteger(), nullable=True),
        sa.Column('source_note_id', sa.BigInteger(), nullable=True),
        sa.Column('problem', sa.Text(), nullable=True),
        sa.Column('goal', sa.Text(), nullable=True),
        sa.Column('scope', sa.Text(), nullable=True),
        sa.Column('acceptance', sa.Text(), nullable=True),
        sa.Column('priority', sa.String(10), nullable=False, server_default='P1'),
        sa.Column('status', sa.String(30), nullable=False, server_default='draft'),
        sa.Column('created_by', sa.String(50), nullable=True),
        sa.Column('create_time', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('update_time', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.text('CURRENT_TIMESTAMP')),
        sa.UniqueConstraint('requirement_code', name='uk_smc_requirement_code'),
        comment='SMC需求表',
    )
    op.create_table(
        'smc_feature',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('requirement_id', sa.BigInteger(), nullable=False),
        sa.Column('feature_code', sa.String(30), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('logic', sa.Text(), nullable=True),
        sa.Column('input_data', sa.Text(), nullable=True),
        sa.Column('output_data', sa.Text(), nullable=True),
        sa.Column('open_source_project', sa.String(200), nullable=True),
        sa.Column('open_source_function', sa.String(200), nullable=True),
        sa.Column('open_source_logic', sa.Text(), nullable=True),
        sa.Column('reuse_scope', sa.Text(), nullable=True),
        sa.Column('localization_gap', sa.Text(), nullable=True),
        sa.Column('localization_plan', sa.Text(), nullable=True),
        sa.Column('code_location', sa.String(500), nullable=True),
        sa.Column('acceptance', sa.Text(), nullable=True),
        sa.Column('status', sa.String(30), nullable=False, server_default='draft'),
        sa.Column('owner', sa.String(50), nullable=True),
        sa.Column('created_by', sa.String(50), nullable=True),
        sa.Column('create_time', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('update_time', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['requirement_id'], ['smc_requirement.id'], name='fk_smc_feature_requirement'),
        sa.UniqueConstraint('feature_code', name='uk_smc_feature_code'),
        comment='SMC功能实现表',
    )
    op.create_index('ix_smc_feature_requirement_id', 'smc_feature', ['requirement_id'])

    op.execute("""
        INSERT INTO sys_menu
            (menu_name, parent_id, order_num, path, component, query, route_name,
             is_frame, is_cache, menu_type, visible, status, perms, icon,
             create_by, create_time, update_by, update_time, remark)
        SELECT 'SMC需求管理', menu_id, 7, 'smc-requirement', 'project-research/smc/requirement/index',
               '', '', 1, 0, 'C', '0', '0', 'smc:requirement:list', 'documentation',
               'admin', CURRENT_TIMESTAMP, 'admin', CURRENT_TIMESTAMP, 'SMC需求管理菜单'
        FROM sys_menu WHERE path='project-research'
          AND NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms='smc:requirement:list')
    """)
    op.execute("""
        INSERT INTO sys_menu
            (menu_name, parent_id, order_num, path, component, query, route_name,
             is_frame, is_cache, menu_type, visible, status, perms, icon,
             create_by, create_time, update_by, update_time, remark)
        SELECT 'SMC功能管理', menu_id, 8, 'smc-feature', 'project-research/smc/feature/index',
               '', '', 1, 0, 'C', '0', '0', 'smc:feature:list', 'operation',
               'admin', CURRENT_TIMESTAMP, 'admin', CURRENT_TIMESTAMP, 'SMC功能管理菜单'
        FROM sys_menu WHERE path='project-research'
          AND NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms='smc:feature:list')
    """)
    for name, perm in [
        ('SMC需求新增', 'smc:requirement:add'), ('SMC需求修改', 'smc:requirement:edit'), ('SMC需求删除', 'smc:requirement:remove'),
        ('SMC功能新增', 'smc:feature:add'), ('SMC功能修改', 'smc:feature:edit'), ('SMC功能删除', 'smc:feature:remove'),
    ]:
        parent_perm = 'smc:requirement:list' if 'requirement' in perm else 'smc:feature:list'
        op.execute(f"""
            INSERT INTO sys_menu
                (menu_name, parent_id, order_num, path, component, query, route_name,
                 is_frame, is_cache, menu_type, visible, status, perms, icon,
                 create_by, create_time, update_by, update_time, remark)
            SELECT '{name}', menu_id, 1, '', '', '', '', 1, 0, 'F', '0', '0', '{perm}', '#',
                   'admin', CURRENT_TIMESTAMP, 'admin', CURRENT_TIMESTAMP, ''
            FROM sys_menu WHERE perms='{parent_perm}'
              AND NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms='{perm}')
        """)
    op.execute("""
        INSERT INTO sys_role_menu (role_id, menu_id)
        SELECT 1, menu_id FROM sys_menu
        WHERE (perms LIKE 'smc:requirement:%' OR perms LIKE 'smc:feature:%')
          AND NOT EXISTS (SELECT 1 FROM sys_role_menu r WHERE r.role_id=1 AND r.menu_id=sys_menu.menu_id)
    """)


def downgrade() -> None:
    op.execute("DELETE FROM sys_role_menu WHERE menu_id IN (SELECT menu_id FROM sys_menu WHERE perms LIKE 'smc:requirement:%' OR perms LIKE 'smc:feature:%')")
    op.execute("DELETE FROM sys_menu WHERE perms LIKE 'smc:requirement:%' OR perms LIKE 'smc:feature:%'")
    op.drop_index('ix_smc_feature_requirement_id', table_name='smc_feature')
    op.drop_table('smc_feature')
    op.drop_table('smc_requirement')
