"""align Java exam categories with the PDF table of contents

Revision ID: 202610180002
Revises: 202610180001
"""

from alembic import op


revision = '202610180002'
down_revision = '202610180001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    parent = "(SELECT category_id FROM exam_category WHERE parent_id=0 AND name='Java')"
    op.execute(f"UPDATE exam_category SET name='Java 并发编程（一）', sort_no=8 WHERE parent_id={parent} AND name='Java 并发编程'")
    op.execute(f"UPDATE exam_category SET name='Spring 面试题（一）', sort_no=12 WHERE parent_id={parent} AND name='Spring'")
    for sort_no, name in ((9, 'Java 并发编程（二）'), (10, 'Java 面试题（一）'), (11, 'Java 面试题（二）'), (13, 'Spring 面试题（二）'), (14, '微服务 面试题')):
        op.execute(
            "INSERT INTO exam_category(parent_id,name,sort_no,status,create_time,update_time) "
            f"SELECT category_id,'{name}',{sort_no},'published',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP FROM exam_category "
            f"WHERE parent_id=0 AND name='Java' AND NOT EXISTS(SELECT 1 FROM exam_category child WHERE child.parent_id=exam_category.category_id AND child.name='{name}')"
        )
    for sort_no, name in enumerate((
        'MyBatis', 'ZooKeeper', 'Dubbo', 'Elasticsearch', 'Memcached', 'Redis', 'MySQL', 'Java 并发编程（一）',
        'Java 并发编程（二）', 'Java 面试题（一）', 'Java 面试题（二）', 'Spring 面试题（一）', 'Spring 面试题（二）',
        '微服务 面试题', 'Linux', 'Spring Boot', 'Spring Cloud', 'RabbitMQ', 'Kafka',
    ), 1):
        op.execute(f"UPDATE exam_category SET sort_no={sort_no} WHERE parent_id={parent} AND name='{name}'")


def downgrade() -> None:
    parent = "(SELECT category_id FROM exam_category WHERE parent_id=0 AND name='Java')"
    op.execute(f"DELETE FROM exam_category WHERE parent_id={parent} AND name IN ('Java 并发编程（二）','Java 面试题（一）','Java 面试题（二）','Spring 面试题（二）','微服务 面试题')")
    op.execute(f"UPDATE exam_category SET name='Java 并发编程' WHERE parent_id={parent} AND name='Java 并发编程（一）'")
    op.execute(f"UPDATE exam_category SET name='Spring' WHERE parent_id={parent} AND name='Spring 面试题（一）'")
