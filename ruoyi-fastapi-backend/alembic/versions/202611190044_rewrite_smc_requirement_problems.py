"""rewrite seeded course titles as requirement problems"""

from alembic import op


revision = '202611190044'
down_revision = '202611190043'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        UPDATE research_requirement
        SET title = problem,
            acceptance = CONCAT('验收：能够支持', goal, '；记录必须关联原文与笔记来源，且在人工确认前不得作为交易指令。')
        WHERE requirement_code LIKE 'REQ-SMC-%'
          AND problem IS NOT NULL
          AND goal IS NOT NULL
    """)


def downgrade() -> None:
    # Seeded course titles are intentionally not restored: they are source metadata, not requirements.
    pass
