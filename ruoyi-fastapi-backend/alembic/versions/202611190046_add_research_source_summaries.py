"""add source summaries to research requirements"""

from alembic import op
import sqlalchemy as sa


revision = '202611190046'
down_revision = '202611190045'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('research_requirement', sa.Column('source_summary', sa.Text(), nullable=True))
    op.add_column('research_requirement', sa.Column('note_summary', sa.Text(), nullable=True))
    op.execute("""
        UPDATE research_requirement
        SET source_summary = '第0讲是 SMC 订单流入门。原文先区分课程所说的 SMC 与足迹图订单流，再用流动性、价格传递和成本回收的案例解释课程视角；最后给出学习路径，并提醒学习者独立思考。课程中的机构意图和成本回收属于解释框架，不是可直接证实的市场事实。',
            note_summary = '笔记将本讲整理为“把订单流术语转成可观察的结构、价格反应和交易计划条件”。它强调流动性、订单块和 FVG 都是概率性工具，必须保留替代解释、确认条件和失效条件，不能据此直接下交易结论。',
            core_viewpoints = '1. SMC 订单流是从流动性和市场结构理解价格的课程框架，不等同于足迹图订单流。\n2. “机构意图”“成本回收”等只能作为待验证解释，不能被当作事实。\n3. 判断应回到可见价格反应，并同时记录替代情景与失效条件。\n4. 学习路径应服务于独立判断，而不是照搬课程结论。'
        WHERE requirement_code = 'REQ-SMC-1331'
    """)


def downgrade() -> None:
    op.drop_column('research_requirement', 'note_summary')
    op.drop_column('research_requirement', 'source_summary')
