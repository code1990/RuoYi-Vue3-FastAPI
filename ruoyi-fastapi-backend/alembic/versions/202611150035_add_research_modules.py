"""add backtest simulation and review modules"""

from alembic import op
import sqlalchemy as sa

revision = '202611150035'
down_revision = '202611150034'
branch_labels = None
depends_on = None


def _menu(name, order_num, path, component, perm, icon):
    add_perm = perm.replace(':list', ':add')
    remove_perm = perm.replace(':list', ':remove')
    op.execute(f"""
        INSERT INTO sys_menu (menu_name,parent_id,order_num,path,component,query,route_name,is_frame,is_cache,menu_type,visible,status,perms,icon,create_by,create_time,update_by,update_time,remark)
        SELECT '{name}', menu_id, {order_num}, '{path}', '{component}', '', '', 1, 0, 'C', '0', '0', '{perm}', '{icon}', 'admin', CURRENT_TIMESTAMP, 'admin', CURRENT_TIMESTAMP, '{name}菜单'
        FROM sys_menu WHERE path='project-research' AND NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms='{perm}')
    """)
    for label, n, child_perm in [('新增', 1, add_perm), ('删除', 2, remove_perm)]:
        op.execute(f"""
            INSERT INTO sys_menu (menu_name,parent_id,order_num,path,component,query,route_name,is_frame,is_cache,menu_type,visible,status,perms,icon,create_by,create_time,update_by,update_time,remark)
            SELECT '{name}{label}', menu_id, {n}, '', '', '', '', 1, 0, 'F', '0', '0', '{child_perm}', '#', 'admin', CURRENT_TIMESTAMP, 'admin', CURRENT_TIMESTAMP, ''
            FROM sys_menu WHERE perms='{perm}' AND NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms='{child_perm}')
        """)


def upgrade() -> None:
    op.create_table('research_backtest',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('combination_id', sa.BigInteger(), nullable=False), sa.Column('name', sa.String(200), nullable=False),
        sa.Column('symbol', sa.String(50), nullable=False), sa.Column('timeframe', sa.String(20), nullable=False),
        sa.Column('start_time', sa.DateTime()), sa.Column('end_time', sa.DateTime()), sa.Column('initial_capital', sa.Numeric(18, 4), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'), sa.Column('total_return', sa.Numeric(18, 4), server_default='0'),
        sa.Column('win_rate', sa.Numeric(8, 4), server_default='0'), sa.Column('max_drawdown', sa.Numeric(18, 4), server_default='0'),
        sa.Column('trade_count', sa.BigInteger(), server_default='0'), sa.Column('result_data', sa.JSON()), sa.Column('created_by', sa.String(50)),
        sa.Column('create_time', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')), sa.Column('update_time', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['combination_id'], ['func_combination_manage.id']))
    op.create_table('research_sim_account',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True), sa.Column('account_name', sa.String(100), nullable=False, unique=True),
        sa.Column('initial_balance', sa.Numeric(18, 4), nullable=False), sa.Column('available_balance', sa.Numeric(18, 4), nullable=False),
        sa.Column('total_pnl', sa.Numeric(18, 4), nullable=False, server_default='0'), sa.Column('status', sa.String(20), nullable=False, server_default='active'),
        sa.Column('created_by', sa.String(50)), sa.Column('create_time', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')), sa.Column('update_time', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')))
    op.create_table('research_review',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True), sa.Column('source_type', sa.String(20), nullable=False), sa.Column('source_id', sa.BigInteger(), nullable=False),
        sa.Column('rating', sa.String(20), nullable=False), sa.Column('reason', sa.Text()), sa.Column('lesson', sa.Text()), sa.Column('tags', sa.String(200)), sa.Column('created_by', sa.String(50)),
        sa.Column('create_time', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')), sa.Column('update_time', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')))
    _menu('回测', 4, 'backtest', 'project-research/backtest/index', 'research:backtest:list', 'trend-charts')
    _menu('模拟交易', 5, 'simulation', 'project-research/simulation/index', 'research:simulation:list', 'odometer')
    _menu('复盘', 6, 'review', 'project-research/review/index', 'research:review:list', 'reading')
    op.execute("""INSERT INTO sys_role_menu (role_id, menu_id) SELECT 1, menu_id FROM sys_menu WHERE perms LIKE 'research:%' AND NOT EXISTS (SELECT 1 FROM sys_role_menu r WHERE r.role_id=1 AND r.menu_id=sys_menu.menu_id)""")


def downgrade() -> None:
    op.execute("DELETE FROM sys_role_menu WHERE menu_id IN (SELECT menu_id FROM sys_menu WHERE perms LIKE 'research:%')")
    op.execute("DELETE FROM sys_menu WHERE perms LIKE 'research:%'")
    op.drop_table('research_review')
    op.drop_table('research_sim_account')
    op.drop_table('research_backtest')
