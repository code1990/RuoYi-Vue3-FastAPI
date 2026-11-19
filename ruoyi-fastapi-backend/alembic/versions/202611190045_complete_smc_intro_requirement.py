"""complete the SMC introduction requirement and feature plan"""

from alembic import op


revision = '202611190045'
down_revision = '202611190044'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        UPDATE research_requirement
        SET title = 'SMC解释缺少证据、替代情景与失效条件，研究结论不可复盘',
            core_concepts = '本讲的“订单流”是 SMC 的市场解释框架，不等同于足迹图订单流；课程涉及流动性、价格传递、成本回收、订单块与溢价/折价。',
            core_viewpoints = '机构意图与成本回收只能作为解释假设，不能当作已证实事实或交易指令；应以可见价格反应、替代情景和失效条件验证。',
            problem = '学习者会把价格事实、课程解释和交易建议混为一谈，无法回看当时依据，也无法在结果不符时定位判断失效的原因。',
            goal = '提供一张可复盘的 SMC 研究卡：保存事实、解释假设、来源证据、主/替代情景、确认条件、失效条件和事后结果。',
            scope = '使用流程：从原文或笔记摘录一段依据 → 手工记录周期、位置和可观察价格事实 → 写主情景与至少一个替代情景 → 写确认与失效条件 → 事后补充结果。
边界：不自动推断机构意图、不生成买卖信号、不代替人工交易决策。',
            acceptance = '1. 可从原文和笔记保存可定位的证据摘录；
2. 每张研究卡必须区分事实与解释，并至少包含一个替代情景；
3. 主/替代情景均须填写确认条件和失效条件；
4. 可在事后补充结果并回看当时记录；
5. 页面不得输出买卖建议或确定性机构意图。',
            status = 'review'
        WHERE requirement_code = 'REQ-SMC-1331'
    """)
    _insert_feature('FUNC-SMC-1331-01', '来源证据摘录与定位', '从原文或AI笔记摘录支撑判断的段落，并保留来源、位置与人工备注。', '原文/笔记、摘录内容、位置、备注', '可追溯的证据条目', '证据条目能回到正确的原文或笔记来源。')
    _insert_feature('FUNC-SMC-1331-02', '研究情景与失效条件记录', '将价格事实、解释假设、主情景、替代情景、确认条件和失效条件保存为同一研究卡。', '周期、位置、事实、证据条目、情景与条件', '可复盘的研究卡', '研究卡无法保存时不得标记为完成；卡片须至少含一个替代情景和失效条件。')
    _insert_feature('FUNC-SMC-1331-03', '研究结果回看', '在事件后补充结果，并与事前情景和失效条件对照，不覆盖原始记录。', '研究卡、结果、复盘说明', '事前事后对照记录', '补充结果后仍可查看原始情景、证据和条件。')


def _insert_feature(code: str, title: str, logic: str, input_data: str, output_data: str, acceptance: str) -> None:
    op.execute(f"""
        INSERT INTO research_feature
            (requirement_id, feature_code, title, logic, input_data, output_data, acceptance, status, created_by, create_time, update_time)
        SELECT id, '{code}', '{title}', '{logic}', '{input_data}', '{output_data}', '{acceptance}', 'draft', 'system', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
        FROM research_requirement
        WHERE requirement_code = 'REQ-SMC-1331'
          AND NOT EXISTS (SELECT 1 FROM research_feature WHERE feature_code = '{code}')
    """)


def downgrade() -> None:
    op.execute("DELETE FROM research_feature WHERE feature_code IN ('FUNC-SMC-1331-01', 'FUNC-SMC-1331-02', 'FUNC-SMC-1331-03')")
