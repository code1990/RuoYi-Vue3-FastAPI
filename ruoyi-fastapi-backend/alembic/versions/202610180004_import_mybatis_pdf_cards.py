"""import all MyBatis questions from the PDF chapter

Revision ID: 202610180004
Revises: 202610180003
"""

from datetime import datetime

from alembic import op
import sqlalchemy as sa


revision = '202610180004'
down_revision = '202610180003'
branch_labels = None
depends_on = None


cards = (
    ('1、什么是 Mybatis？', 'Mybatis 是一个半 ORM（对象关系映射）框架，内部封装了 JDBC。开发时只需关注 SQL 语句本身，不需要处理加载驱动、创建连接和创建 statement 等过程；可直接编写原生 SQL，严格控制执行性能和灵活度。MyBatis 可使用 XML 或注解配置映射，将 POJO 映射为数据库记录，避免大量 JDBC 代码。', 'concept'),
    ('2、Mybaits 的优点：', '基于 SQL 语句编程，灵活且不影响现有应用或数据库设计；SQL 写在 XML 中，便于统一管理并支持动态 SQL 和复用。相比 JDBC 可减少大量冗余代码，无需手动开关连接；兼容 JDBC 支持的数据库；可与 Spring 集成，并提供对象与数据库字段的映射标签。', 'enumeration'),
    ('3、MyBatis 框架的缺点：', 'SQL 语句编写工作量较大，字段多、关联表多时对开发人员的 SQL 功底要求较高。SQL 依赖数据库，导致数据库移植性较差，不能随意更换数据库。', 'comparison'),
    ('4、MyBatis 框架适用场合：', 'MyBatis 专注于 SQL 本身，是足够灵活的 DAO 层解决方案。性能要求高或需求变化较多的项目（如互联网项目）适合使用 MyBatis。', 'scenario'),
    ('5、MyBatis 与 Hibernate 有哪些不同？', 'MyBatis 不完全是 ORM 框架，需要程序员编写 SQL；可严格控制 SQL 性能，灵活度高，但难以做到数据库无关，多数据库需维护多套映射文件。Hibernate 对象/关系映射能力强、数据库无关性好，对关系模型要求高的软件使用 Hibernate 可节省代码、提高效率。', 'comparison'),
    ('6、#{}和${}的区别是什么？', '#{} 是预编译处理：MyBatis 将其替换为 ?，通过 PreparedStatement 的 set 方法赋值。${} 是字符串替换，直接替换变量值。使用 #{} 可以有效防止 SQL 注入，提高系统安全性。', 'comparison'),
    ('7、当实体类中的属性名和表中的字段名不一样 ，怎么办 ？', '可在查询 SQL 中为字段定义别名，使其与实体类属性名一致；也可通过 <resultMap> 映射数据库字段名与实体类属性名的一一对应关系。', 'scenario'),
    ('8、 模糊查询 like 语句该怎么写?', '第一种是在 Java 代码中添加 SQL 通配符，再将参数以 #{value} 传入。第二种是在 SQL 语句中拼接通配符，但会引起 SQL 注入风险。', 'scenario'),
    ('9、通常一个 Xml 映射文件，都会写一个 Dao 接口与之对应，\n\n请问，这个 Dao 接口的工作原理是什么？Dao 接口里的方法，\n\n参数不同时，方法能重载吗？', 'Dao 接口即 Mapper 接口。接口全限名是映射文件 namespace，接口方法名是 Statement 的 id，方法参数传给 SQL。Mapper 接口没有实现类；MyBatis 以“全限名+方法名”定位 MapperStatement，并通过 JDK 动态代理生成 proxy，拦截接口方法后执行 SQL。接口方法不能重载，因为定位策略只使用全限名和方法名。', 'concept'),
    ('10、Mybatis 是如何进行分页的？分页插件的原理是什么？', 'MyBatis 使用 RowBounds 对结果集进行内存分页，不是物理分页；可在 SQL 中直接写物理分页参数，也可使用分页插件。分页插件通过 MyBatis 插件接口拦截待执行 SQL，按数据库 dialect 重写 SQL 并添加物理分页语句和参数。', 'concept'),
    ('11、Mybatis 是如何将 sql 执行结果封装为目标对象并返回的？\n\n都有哪些映射形式？', '可使用 <resultMap> 逐一定义数据库列名和对象属性名的映射，也可使用 SQL 列别名使其等于对象属性名。有映射关系后，MyBatis 通过反射创建对象并为属性赋值；找不到映射关系的属性无法完成赋值。', 'concept'),
    ('12、如何执行批量插入?', '先定义 insert 语句，再以 ExecutorType.BATCH 打开 SqlSession，循环调用 Mapper 的 insert 方法，最后 commit；发生异常时 rollback，finally 中关闭 SqlSession。', 'scenario'),
    ('13、如何获取自动生成的(主)键值?', 'insert 方法返回受影响行数。使用自增长策略时，insert 执行完成后生成的键值会设置到传入的参数对象中；可在 insert 标签配置 useGeneratedKeys="true" 和 keyProperty。', 'scenario'),
    ('14、在 mapper 中如何传递多个参数?', '可使用 #{0}、#{1} 按参数位置接收；可使用 @Param 注解指定名称；也可将多个参数封装为 Map 作为单个参数传递，通常推荐封装 Map。', 'enumeration'),
    ('15、Mybatis 动态 sql 有什么用？执行原理？有哪些动态 sql？', '动态 SQL 可在 XML 映射文件中以标签形式编写，根据表达式值完成逻辑判断并动态拼接 SQL。MyBatis 提供 trim、where、set、foreach、if、choose、when、otherwise、bind 九种动态 SQL 标签。', 'concept'),
    ('16、Xml 映射文件中，\n            除了常见的 select|insert|updae|delete\n\n标签之外，还有哪些标签？', '还有 <resultMap>、<parameterMap>、<sql>、<include>、<selectKey>，以及九个动态 SQL 标签。其中 <sql> 是 SQL 片段标签，<include> 用于引入 SQL 片段，<selectKey> 用于不支持自增的主键生成策略。', 'enumeration'),
    ('17、 Mybatis 的 Xml 映射文件中 ， 不同的 Xml 映射文件 ， id 是否可以重复 ？', '配置 namespace 时，不同 XML 映射文件的 id 可以重复；没有配置 namespace 时 id 不能重复。原因是 namespace+id 作为 Map<String, MapperStatement> 的 key；没有 namespace 时，重复 id 会相互覆盖。', 'concept'),
    ('18、为什么说 Mybatis 是半自动 ORM 映射工具？它与全自动\n\n的区别在哪里？', 'Hibernate 属于全自动 ORM，查询关联对象或集合时可根据对象关系模型直接获取。MyBatis 查询关联对象或集合时需要手动编写 SQL，因此称为半自动 ORM 映射工具。', 'comparison'),
    ('19、 一对一、一对多的关联查询 ？', '一对一可在 resultMap 中使用 association 映射关联对象；一对多可使用 collection 映射关联集合。通过 resultMap 将实体字段与数据表字段建立映射。', 'scenario'),
    ('20、MyBatis 实现一对一有几种方式?具体怎么操作的？', '有联合查询和嵌套查询。联合查询一次查询多个表，在 resultMap 的 association 节点配置一对一对象；嵌套查询先查一个表，再根据外键查询另一个表，也通过 association 配置，额外查询由 select 属性指定。', 'comparison'),
    ('21、MyBatis 实现一对多有几种方式,怎么操作的？', '有联合查询和嵌套查询。联合查询一次查询多个表，在 resultMap 的 collection 节点配置一对多对象；嵌套查询先查一个表，再根据外键查询其他表，也通过 collection 配置，额外查询由 select 节点指定。', 'comparison'),
    ('22、Mybatis 是否支持延迟加载？如果支持，它的实现原理是\n\n什么？', 'MyBatis 仅支持 association 关联对象和 collection 关联集合的延迟加载，可通过 lazyLoadingEnabled 配置。其使用 CGLIB 创建目标对象代理；调用目标方法时，拦截器发现关联对象为空便发送预先保存的查询 SQL，查询后设置属性并继续调用。', 'concept'),
    ('23、Mybatis 的一级、二级缓存:', '一级缓存是基于 PerpetualCache 的 HashMap 本地缓存，作用域为 Session，Session flush 或 close 后清空，默认开启。二级缓存机制相同但作用域为 Mapper（Namespace），默认关闭，可自定义存储源；开启二级缓存的对象需实现 Serializable。执行 C/U/D 后，默认会清除相应作用域下 select 的缓存。', 'comparison'),
    ('24、什么是 MyBatis 的接口绑定？有哪些实现方式？', '接口绑定是在 MyBatis 中定义接口，并将接口方法与 SQL 语句绑定，直接调用接口方法。可通过方法上的 @Select、@Update 等注解绑定，也可在 XML 中写 SQL 并指定 namespace 为接口全路径；SQL 简单时用注解，复杂时一般使用 XML。', 'enumeration'),
    ('25、使用 MyBatis 的 mapper 接口调用时有哪些要求？', 'Mapper 接口方法名须与 mapper.xml 中每个 SQL 的 id 相同；输入参数类型须与 parameterType 相同；输出参数类型须与 resultType 相同；mapper.xml 的 namespace 即 Mapper 接口类路径。', 'enumeration'),
    ('26、Mapper 编写有哪几种方式？', '有三种方式：接口实现类继承 SqlSessionDaoSupport；使用 org.mybatis.spring.mapper.MapperFactoryBean；使用 Mapper 扫描器 MapperScannerConfigurer。后两种均要求 mapper.xml 的 namespace 为 Mapper 接口地址，接口方法名与 statement id 一致。', 'enumeration'),
    ('27、简述 Mybatis 的插件运行原理，以及如何编写一个插件。', 'MyBatis 仅可针对 ParameterHandler、ResultSetHandler、StatementHandler、Executor 四种接口编写插件。它使用 JDK 动态代理为需拦截接口生成代理对象，执行指定方法时进入 InvocationHandler 的 invoke。编写插件需实现 Interceptor 并重写 intercept()，再以注解指定拦截的接口和方法，并在配置文件中配置插件。', 'concept'),
)


def upgrade() -> None:
    # The prior five rows were generated seed data; replace only that seed range.
    connection = op.get_bind()
    category_id = connection.execute(sa.text("SELECT category_id FROM exam_category WHERE name='MyBatis 面试题'")).scalar_one()
    connection.execute(sa.text('DELETE FROM exam_card WHERE category_id=:category_id AND sort_no BETWEEN 1 AND 5'), {'category_id': category_id})
    table = sa.table('exam_card', sa.column('category_id'), sa.column('question'), sa.column('answer'), sa.column('key_points'), sa.column('tags'), sa.column('card_type'), sa.column('difficulty'), sa.column('status'), sa.column('sort_no'), sa.column('create_time'), sa.column('update_time'))
    now = datetime.now()
    op.bulk_insert(table, [dict(category_id=category_id, question=question, answer=answer, key_points='', tags='MyBatis', card_type=card_type, difficulty=3, status='published', sort_no=index, create_time=now, update_time=now) for index, (question, answer, card_type) in enumerate(cards, 1)])


def downgrade() -> None:
    category_id = op.get_bind().execute(sa.text("SELECT category_id FROM exam_category WHERE name='MyBatis 面试题'")).scalar_one()
    op.get_bind().execute(sa.text('DELETE FROM exam_card WHERE category_id=:category_id AND sort_no BETWEEN 1 AND 27'), {'category_id': category_id})
