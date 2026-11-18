"""generalize research requirement and feature management"""

from alembic import op


revision = '202611180040'
down_revision = '202611180039'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.rename_table('smc_requirement', 'research_requirement')
    op.rename_table('smc_feature', 'research_feature')
    op.execute('ALTER TABLE research_feature DROP FOREIGN KEY fk_smc_feature_requirement')
    op.drop_index('ix_smc_feature_requirement_id', table_name='research_feature')
    op.drop_constraint('uk_smc_requirement_code', 'research_requirement', type_='unique')
    op.drop_constraint('uk_smc_feature_code', 'research_feature', type_='unique')
    op.create_unique_constraint('uk_research_requirement_code', 'research_requirement', ['requirement_code'])
    op.create_unique_constraint('uk_research_feature_code', 'research_feature', ['feature_code'])
    op.create_index('ix_research_feature_requirement_id', 'research_feature', ['requirement_id'])
    op.create_foreign_key('fk_research_feature_requirement', 'research_feature', 'research_requirement', ['requirement_id'], ['id'])
    op.execute("ALTER TABLE research_requirement COMMENT = '项目研究需求表'")
    op.execute("ALTER TABLE research_feature COMMENT = '项目研究功能实现表'")
    op.execute("""
        UPDATE sys_menu
        SET menu_name='需求管理', path='requirement', component='project-research/requirement/index',
            perms='research:requirement:list', remark='项目研究需求管理菜单'
        WHERE perms='smc:requirement:list'
    """)
    op.execute("""
        UPDATE sys_menu
        SET menu_name='功能管理', path='feature', component='project-research/feature/index',
            perms='research:feature:list', remark='项目研究功能管理菜单'
        WHERE perms='smc:feature:list'
    """)
    for name, old_perm, new_perm in [
        ('需求新增', 'smc:requirement:add', 'research:requirement:add'),
        ('需求修改', 'smc:requirement:edit', 'research:requirement:edit'),
        ('需求删除', 'smc:requirement:remove', 'research:requirement:remove'),
        ('功能新增', 'smc:feature:add', 'research:feature:add'),
        ('功能修改', 'smc:feature:edit', 'research:feature:edit'),
        ('功能删除', 'smc:feature:remove', 'research:feature:remove'),
    ]:
        op.execute(f"UPDATE sys_menu SET menu_name='{name}', perms='{new_perm}' WHERE perms='{old_perm}'")


def downgrade() -> None:
    op.execute("UPDATE sys_menu SET menu_name='SMC需求管理', path='smc-requirement', component='project-research/smc/requirement/index', perms='smc:requirement:list', remark='SMC需求管理菜单' WHERE perms='research:requirement:list'")
    op.execute("UPDATE sys_menu SET menu_name='SMC功能管理', path='smc-feature', component='project-research/smc/feature/index', perms='smc:feature:list', remark='SMC功能管理菜单' WHERE perms='research:feature:list'")
    for name, old_perm, new_perm in [
        ('SMC需求新增', 'research:requirement:add', 'smc:requirement:add'),
        ('SMC需求修改', 'research:requirement:edit', 'smc:requirement:edit'),
        ('SMC需求删除', 'research:requirement:remove', 'smc:requirement:remove'),
        ('SMC功能新增', 'research:feature:add', 'smc:feature:add'),
        ('SMC功能修改', 'research:feature:edit', 'smc:feature:edit'),
        ('SMC功能删除', 'research:feature:remove', 'smc:feature:remove'),
    ]:
        op.execute(f"UPDATE sys_menu SET menu_name='{name}', perms='{new_perm}' WHERE perms='{old_perm}'")
    op.drop_constraint('fk_research_feature_requirement', 'research_feature', type_='foreignkey')
    op.drop_index('ix_research_feature_requirement_id', table_name='research_feature')
    op.drop_constraint('uk_research_feature_code', 'research_feature', type_='unique')
    op.drop_constraint('uk_research_requirement_code', 'research_requirement', type_='unique')
    op.create_unique_constraint('uk_smc_requirement_code', 'research_requirement', ['requirement_code'])
    op.create_unique_constraint('uk_smc_feature_code', 'research_feature', ['feature_code'])
    op.create_index('ix_smc_feature_requirement_id', 'research_feature', ['requirement_id'])
    op.create_foreign_key('fk_smc_feature_requirement', 'research_feature', 'research_requirement', ['requirement_id'], ['id'])
    op.rename_table('research_feature', 'smc_feature')
    op.rename_table('research_requirement', 'smc_requirement')
