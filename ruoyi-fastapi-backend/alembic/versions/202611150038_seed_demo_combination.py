"""seed a demo function combination"""

from alembic import op

revision = '202611150038'
down_revision = '202611150037'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        INSERT INTO func_combination_manage (project_id, combination_name, research_direction, description, function_ids, create_time, update_time)
        SELECT p.id, 'BTC综合结构示例', 'SMC', '用于综合图表测试的默认函数组合', JSON_ARRAY(
            (SELECT id FROM func_manage WHERE project_id=p.id AND func_name='swing_highs_lows' LIMIT 1),
            (SELECT id FROM func_manage WHERE project_id=p.id AND func_name='fvg' LIMIT 1),
            (SELECT id FROM func_manage WHERE project_id=p.id AND func_name='bos_choch' LIMIT 1),
            (SELECT id FROM func_manage WHERE project_id=p.id AND func_name='ob' LIMIT 1),
            (SELECT id FROM func_manage WHERE project_id=p.id AND func_name='liquidity' LIMIT 1),
            (SELECT id FROM func_manage WHERE project_id=p.id AND func_name='previous_high_low' LIMIT 1),
            (SELECT id FROM func_manage WHERE project_id=p.id AND func_name='sessions' LIMIT 1),
            (SELECT id FROM func_manage WHERE project_id=p.id AND func_name='retracements' LIMIT 1)
        ), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
        FROM project_manage p
        WHERE p.project_name='smart-money-concepts'
          AND NOT EXISTS (SELECT 1 FROM func_combination_manage c WHERE c.project_id=p.id AND c.combination_name='BTC综合结构示例')
    """)


def downgrade() -> None:
    op.execute("DELETE FROM func_combination_manage WHERE combination_name='BTC综合结构示例'")
