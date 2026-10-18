"""align Java exam categories with the PDF table of contents

Revision ID: 202610180002
Revises: 202610180001
"""

from alembic import op
import sqlalchemy as sa


revision = '202610180002'
down_revision = '202610180001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    connection = op.get_bind()
    parent_id = connection.execute(sa.text("SELECT category_id FROM exam_category WHERE parent_id=0 AND name='Java'")).scalar_one()
    op.execute(sa.text("UPDATE exam_category SET name='Java 并发编程（一）', sort_no=8 WHERE parent_id=:parent_id AND name='Java 并发编程'").bindparams(parent_id=parent_id))
    op.execute(sa.text("UPDATE exam_category SET name='Spring 面试题（一）', sort_no=12 WHERE parent_id=:parent_id AND name='Spring'").bindparams(parent_id=parent_id))
    for sort_no, name in ((9, 'Java 并发编程（二）'), (10, 'Java 面试题（一）'), (11, 'Java 面试题（二）'), (13, 'Spring 面试题（二）'), (14, '微服务 面试题')):
        exists = connection.execute(sa.text("SELECT 1 FROM exam_category WHERE parent_id=:parent_id AND name=:name").bindparams(parent_id=parent_id, name=name)).scalar()
        if not exists:
            op.execute(sa.text("INSERT INTO exam_category(parent_id,name,sort_no,status,create_time,update_time) VALUES (:parent_id,:name,:sort_no,'published',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP)").bindparams(parent_id=parent_id, name=name, sort_no=sort_no))
    for sort_no, name in enumerate((
        'MyBatis', 'ZooKeeper', 'Dubbo', 'Elasticsearch', 'Memcached', 'Redis', 'MySQL', 'Java 并发编程（一）',
        'Java 并发编程（二）', 'Java 面试题（一）', 'Java 面试题（二）', 'Spring 面试题（一）', 'Spring 面试题（二）',
        '微服务 面试题', 'Linux', 'Spring Boot', 'Spring Cloud', 'RabbitMQ', 'Kafka',
    ), 1):
        op.execute(sa.text("UPDATE exam_category SET sort_no=:sort_no WHERE parent_id=:parent_id AND name=:name").bindparams(sort_no=sort_no, parent_id=parent_id, name=name))


def downgrade() -> None:
    connection = op.get_bind()
    parent_id = connection.execute(sa.text("SELECT category_id FROM exam_category WHERE parent_id=0 AND name='Java'")).scalar_one()
    op.execute(sa.text("DELETE FROM exam_category WHERE parent_id=:parent_id AND name IN ('Java 并发编程（二）','Java 面试题（一）','Java 面试题（二）','Spring 面试题（二）','微服务 面试题')").bindparams(parent_id=parent_id))
    op.execute(sa.text("UPDATE exam_category SET name='Java 并发编程' WHERE parent_id=:parent_id AND name='Java 并发编程（一）'").bindparams(parent_id=parent_id))
    op.execute(sa.text("UPDATE exam_category SET name='Spring' WHERE parent_id=:parent_id AND name='Spring 面试题（一）'").bindparams(parent_id=parent_id))
