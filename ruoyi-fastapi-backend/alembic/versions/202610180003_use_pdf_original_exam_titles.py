"""use original PDF chapter titles for Java exam categories

Revision ID: 202610180003
Revises: 202610180002
"""

from alembic import op
import sqlalchemy as sa


revision = '202610180003'
down_revision = '202610180002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    connection = op.get_bind()
    parent_id = connection.execute(sa.text("SELECT category_id FROM exam_category WHERE parent_id=0 AND name='Java'")).scalar_one()
    titles = (
        ('MyBatis', 'MyBatis 面试题'), ('ZooKeeper', 'ZooKeeper 面试题'), ('Dubbo', 'Dubbo 面试题'),
        ('Elasticsearch', 'Elasticsearch 面试题'), ('Memcached', 'Memcached 面试题'), ('Redis', 'Redis 面试题'),
        ('MySQL', 'MySQL 面试题'), ('Linux', 'Linux 面试题'), ('Spring Boot', 'Spring Boot 面试题'),
        ('Spring Cloud', 'Spring Cloud 面试题'), ('RabbitMQ', 'RabbitMQ 面试题'), ('Kafka', 'kafka 面试题'),
    )
    for current_name, original_title in titles:
        op.execute(sa.text("UPDATE exam_category SET name=:original_title WHERE parent_id=:parent_id AND name=:current_name").bindparams(original_title=original_title, parent_id=parent_id, current_name=current_name))


def downgrade() -> None:
    connection = op.get_bind()
    parent_id = connection.execute(sa.text("SELECT category_id FROM exam_category WHERE parent_id=0 AND name='Java'")).scalar_one()
    titles = (
        ('MyBatis 面试题', 'MyBatis'), ('ZooKeeper 面试题', 'ZooKeeper'), ('Dubbo 面试题', 'Dubbo'),
        ('Elasticsearch 面试题', 'Elasticsearch'), ('Memcached 面试题', 'Memcached'), ('Redis 面试题', 'Redis'),
        ('MySQL 面试题', 'MySQL'), ('Linux 面试题', 'Linux'), ('Spring Boot 面试题', 'Spring Boot'),
        ('Spring Cloud 面试题', 'Spring Cloud'), ('RabbitMQ 面试题', 'RabbitMQ'), ('kafka 面试题', 'Kafka'),
    )
    for original_title, current_name in titles:
        op.execute(sa.text("UPDATE exam_category SET name=:current_name WHERE parent_id=:parent_id AND name=:original_title").bindparams(current_name=current_name, parent_id=parent_id, original_title=original_title))
