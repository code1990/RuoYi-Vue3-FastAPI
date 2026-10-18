"""add exam knowledge card tables and Java seed cards

Revision ID: 202610180001
Revises: 202610090002
"""

from alembic import op
import sqlalchemy as sa


revision = '202610180001'
down_revision = '202610090002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'exam_category',
        sa.Column('category_id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('parent_id', sa.BigInteger(), nullable=False, server_default='0'),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('sort_no', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('status', sa.String(16), nullable=False, server_default='published'),
        sa.Column('create_time', sa.DateTime(), nullable=False),
        sa.Column('update_time', sa.DateTime(), nullable=False),
        sa.UniqueConstraint('parent_id', 'name', name='uk_exam_category_parent_name'),
    )
    op.create_index('ix_exam_category_parent_id', 'exam_category', ['parent_id'])
    op.create_table(
        'exam_card',
        sa.Column('card_id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('category_id', sa.BigInteger(), nullable=False),
        sa.Column('question', sa.String(500), nullable=False),
        sa.Column('answer', sa.Text(), nullable=False),
        sa.Column('key_points', sa.Text(), nullable=False),
        sa.Column('tags', sa.String(500), nullable=False, server_default=''),
        sa.Column('card_type', sa.String(32), nullable=False, server_default='concept'),
        sa.Column('difficulty', sa.Integer(), nullable=False, server_default='3'),
        sa.Column('status', sa.String(16), nullable=False, server_default='published'),
        sa.Column('sort_no', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('create_time', sa.DateTime(), nullable=False),
        sa.Column('update_time', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_exam_card_category_id', 'exam_card', ['category_id'])

    op.execute("INSERT INTO exam_category(parent_id,name,sort_no,status,create_time,update_time) VALUES (0,'Java',1,'published',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP)")
    for sort_no, name in enumerate(('MyBatis', 'ZooKeeper', 'Dubbo', 'Elasticsearch', 'Memcached', 'Redis', 'MySQL', 'Java 并发编程', 'Spring', 'Spring Boot', 'Spring Cloud', 'RabbitMQ', 'Kafka', 'Linux'), 1):
        op.execute(
            "INSERT INTO exam_category(parent_id,name,sort_no,status,create_time,update_time) "
            f"SELECT category_id,'{name}',{sort_no},'published',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP FROM exam_category WHERE parent_id=0 AND name='Java'"
        )

    cards = (
        ('什么是 MyBatis？', 'MyBatis 是半 ORM 持久层框架，封装 JDBC 的连接、参数设置和结果集处理；开发者仍可通过 XML 或注解编写并控制原生 SQL。', '半 ORM；封装 JDBC；XML 或注解；原生 SQL 控制', 'MyBatis,ORM,JDBC', 'concept'),
        ('MyBatis 的主要优点有哪些？', 'SQL 灵活可控；减少 JDBC 样板代码；兼容主流数据库；易与 Spring 集成；支持 XML 映射、对象关系映射和动态 SQL。', 'SQL 灵活；减少样板；兼容性；Spring 集成；动态 SQL', 'MyBatis,SQL,Spring', 'enumeration'),
        ('MyBatis 的主要缺点是什么？', '复杂场景下 SQL 编写和维护工作量较大；SQL 与特定数据库语法结合时，数据库迁移成本会提高。', 'SQL 编写成本；数据库迁移性', 'MyBatis,SQL', 'comparison'),
        ('什么场景更适合使用 MyBatis？', '需要精细控制 SQL、查询复杂、性能敏感，或需求变化较多的互联网业务系统，通常更适合使用 MyBatis。', '复杂 SQL；性能敏感；精细控制；需求变化', 'MyBatis,架构选型,SQL', 'scenario'),
        ('MyBatis 与 Hibernate 的核心取舍是什么？', 'MyBatis 给予开发者更高的 SQL 控制能力和灵活性，但需要维护更多 SQL；Hibernate 自动化程度更高，适合稳定的对象关系映射场景。', 'SQL 控制；自动化程度；维护成本；适用场景', 'MyBatis,Hibernate,ORM', 'comparison'),
    )
    for sort_no, (question, answer, key_points, tags, card_type) in enumerate(cards, 1):
        values = (question, answer, key_points, tags, card_type)
        escaped = [value.replace("'", "''") for value in values]
        op.execute(
            "INSERT INTO exam_card(category_id,question,answer,key_points,tags,card_type,difficulty,status,sort_no,create_time,update_time) "
            "SELECT category_id,'{}','{}','{}','{}','{}',3,'published',{},CURRENT_TIMESTAMP,CURRENT_TIMESTAMP "
            "FROM exam_category WHERE name='MyBatis'".format(*escaped, sort_no)
        )


def downgrade() -> None:
    op.drop_index('ix_exam_card_category_id', table_name='exam_card')
    op.drop_table('exam_card')
    op.drop_index('ix_exam_category_parent_id', table_name='exam_category')
    op.drop_table('exam_category')
