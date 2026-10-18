"""import MySQL interview cards from the Java interview PDF

Revision ID: 202610180010
Revises: 202610180009
"""

from datetime import datetime

from alembic import op
import sqlalchemy as sa


revision = '202610180010'
down_revision = '202610180009'
branch_labels = None
depends_on = None


cards = (
    ('1、MySQL 中有哪几种锁？', '按粒度常见有表锁、行锁和页锁。表锁开销小但并发低；行锁并发高但开销更大且可能死锁；实际能力由存储引擎决定，InnoDB 以行级锁和意向锁为主。', 'comparison'),
    ('2、MySQL 中有哪些不同的表格？', 'MySQL 的表由存储引擎实现。现代项目通常使用 InnoDB；MyISAM、MEMORY、CSV 等引擎适用于特定场景，是否可用取决于安装版本和配置。', 'concept'),
    ('3、简述 MyISAM 和 InnoDB 的区别。', 'InnoDB 支持事务、行级锁、外键和崩溃恢复，主键为聚簇索引，适用于高并发读写；MyISAM 不支持事务和行级锁，通常适用于以读为主且无需事务的历史场景。', 'comparison'),
    ('4、InnoDB 支持的四种事务隔离级别及区别？', '从低到高为 READ UNCOMMITTED、READ COMMITTED、REPEATABLE READ、SERIALIZABLE。级别越高隔离越强、并发通常越低；InnoDB 默认 REPEATABLE READ，并通过 MVCC 与锁实现一致性读。', 'comparison'),
    ('5、CHAR 和 VARCHAR 的区别？', 'CHAR 是定长类型，适合长度稳定的值；VARCHAR 是变长类型，节省可变长度文本空间。两者上限、排序规则和行格式均会影响实际存储，应按字段语义选择。', 'comparison'),
    ('6、主键和候选键有什么区别？', '候选键是能唯一标识一行的最小属性集合；主键是从候选键中选定的一个，表只能有一个主键。未被选中的候选键通常用 UNIQUE 约束表示。', 'comparison'),
    ('7、myisamchk 是用来做什么的？', 'myisamchk 用于检查、修复和维护 MyISAM 表。它不适用于 InnoDB；现代 InnoDB 维护应使用官方工具、备份恢复和引擎诊断手段。', 'concept'),
    ('8、如果一个表有一列定义为 TIMESTAMP，将发生什么？', 'TIMESTAMP 存储时间点并受会话时区转换影响；是否自动填充或更新取决于 DEFAULT CURRENT_TIMESTAMP、ON UPDATE CURRENT_TIMESTAMP 等显式定义。不要依赖旧版本的隐式行为。', 'concept'),
    ('9、怎么看到为表定义的所有索引？', '使用 SHOW INDEX FROM 表名，或查询 information_schema.statistics。执行计划可用 EXPLAIN/EXPLAIN ANALYZE 验证索引是否实际被使用。', 'scenario'),
    ('10、LIKE 声明中的 % 和 _ 是什么意思？', '% 匹配任意长度字符串，_ 匹配单个字符。前导 % 通常不能有效利用普通 B-tree 索引；需要转义通配符时应使用 ESCAPE 或正确的参数处理。', 'concept'),
    ('11、列对比运算符是什么？', '常用比较运算符有 =、<>/!=、<、<=、>、>=，以及 BETWEEN、IN、LIKE、IS NULL 等。NULL 不能用 = 比较，应使用 IS NULL 或 MySQL 的 <=>。', 'enumeration'),
    ('12、BLOB 和 TEXT 有什么区别？', 'BLOB 用于二进制数据，TEXT 用于文本数据并受字符集和排序规则影响。两者通常都在行外存储大值，索引时可能需要前缀长度或全文索引。', 'comparison'),
    ('13、mysql_fetch_array 和 mysql_fetch_object 的区别是什么？', '它们属于已废弃的旧 PHP mysql 扩展：前者返回数组，后者返回对象。新项目应使用 PDO 或 mysqli 的预处理语句，避免旧扩展和字符串拼接 SQL。', 'comparison'),
    ('14、MyISAM 表格将在哪里存储，并且还提供其存储格式？', 'MyISAM 通常以 .frm（旧版本）、.MYD 和 .MYI 等文件保存表定义、数据与索引，具体格式随版本变化。新系统优先使用 InnoDB，不应依赖底层文件直接操作。', 'concept'),
    ('15、MySQL 如何优化 DISTINCT？', '先确认 DISTINCT 是否必要；为筛选与去重列设计合适索引，减少参与去重的行数和列数。用 EXPLAIN ANALYZE 验证是否发生临时表、文件排序及其成本。', 'scenario'),
    ('16、如何显示前 50 行？', '使用 SELECT ... LIMIT 50；需要分页时配合稳定且有索引的 ORDER BY。深分页优先采用基于上次游标值的 keyset pagination。', 'scenario'),
    ('17、可以使用多少列创建索引？', '联合索引列数受 MySQL 版本和引擎限制，现代 InnoDB 上限通常为 16 列。实际设计应遵循查询条件和最左前缀原则，而不是追求索引列数。', 'concept'),
    ('18、NOW() 和 CURRENT_DATE() 有什么区别？', 'NOW() 返回当前日期和时间；CURRENT_DATE() 返回当前日期，时间部分为零。函数结果还受数据类型和会话时区影响。', 'comparison'),
    ('19、什么是非标准字符串类型？', 'MySQL 提供 TINYTEXT、TEXT、MEDIUMTEXT、LONGTEXT 等不同容量的文本类型；应按最大长度、字符集、索引和查询需求选择，不把大文本滥用于可索引短字段。', 'enumeration'),
    ('20、什么是通用 SQL 函数？', '常用函数包括 CONCAT、LENGTH、CURRENT_DATE/CURRENT_TIME、NOW、YEAR/MONTH/DAY、HOUR/MINUTE/SECOND、DATEDIFF 等。对索引列套函数可能破坏索引使用，应结合生成列或改写条件。', 'enumeration'),
    ('21、MySQL 支持事务吗？', '支持，但是否具备事务能力取决于存储引擎。InnoDB 支持 ACID、提交、回滚、保存点与隔离级别；应把相关更新放在短事务中并正确处理异常。', 'concept'),
    ('22、MySQL 里记录货币用什么字段类型好？', '使用 DECIMAL(p,s)，例如 DECIMAL(18,2)，避免 FLOAT/DOUBLE 的二进制浮点误差。金额的精度、币种和最小单位应由业务明确。', 'scenario'),
    ('23、MySQL 有关权限的表都有哪几个？', '权限数据保存在 mysql 系统库中，包括 user、db、tables_priv、columns_priv、procs_priv 等；具体表随版本变化。权限管理应使用 GRANT/REVOKE，而不是直接修改系统表。', 'enumeration'),
    ('24、列的字符串类型可以是什么？', '常见字符串类型有 CHAR、VARCHAR、TEXT 系列、BINARY、VARBINARY、BLOB 系列，以及 ENUM、SET。选择时同时考虑长度、字符集、比较规则和索引需求。', 'enumeration'),
    ('25、MySQL 作发布系统存储且日增五万条，预计运行三年，怎么优化？', '先按查询与写入模式设计表、索引和归档策略；控制单表增长并在需要时分区或分库分表；使用读写分离、缓存与批量写入；持续以慢日志和执行计划定位瓶颈，而非预先过度拆分。', 'scenario'),
    ('26、锁的优化策略。', '缩短事务和锁持有时间，使用合适索引缩小锁定范围，按一致顺序访问资源，降低热点竞争，并对死锁进行重试和监控。', 'scenario'),
    ('27、索引的底层实现原理和优化。', 'InnoDB 的常规索引使用 B+Tree：聚簇索引叶子存整行数据，二级索引叶子存主键值。优化重点是让索引匹配过滤、排序和连接条件，并避免低选择性或冗余索引。', 'concept'),
    ('28、什么情况下设置了索引但无法使用？', '常见原因包括前导通配符 LIKE、对列施加函数或表达式、隐式类型转换、联合索引不满足最左前缀、选择性太低及优化器估算成本更高。应以 EXPLAIN 验证。', 'scenario'),
    ('29、实践中如何优化 MySQL？', '从 SQL 与索引、表结构、事务与锁、连接池和服务器配置、硬件与架构五个层面排查；先量化慢查询和资源瓶颈，再做可验证的改动。', 'enumeration'),
    ('30、优化数据库的方法。', '选择合适字段类型和约束，减少无效宽度；设计必要索引；写出可利用索引的 SQL；合理使用 JOIN、事务与批处理；通过慢查询日志、EXPLAIN 和监控持续迭代。', 'enumeration'),
    ('31、索引、主键、唯一索引、联合索引的区别及对性能的影响？', '索引用于加速检索但会增加写入和存储成本；主键唯一且不能为空；唯一索引约束唯一性；联合索引按列顺序支持最左前缀查询。读多写少的查询路径更受益，写入需维护每个索引。', 'comparison'),
    ('32、数据库中的事务是什么？', '事务是一组不可分割的操作，满足原子性、一致性、隔离性和持久性（ACID）。它应尽量短小，显式提交或回滚，并处理死锁或序列化失败的重试。', 'concept'),
    ('33、SQL 注入漏洞产生的原因？如何防止？', '将未可信输入拼接到 SQL 中会改变语义而产生注入。必须使用参数化查询/预处理语句、最小数据库权限和输入校验；不要仅依赖转义或黑名单。', 'scenario'),
    ('34、如何为表字段选择合适的数据类型？', '按数据语义、最大范围、精度、字符集和访问模式选择最小够用类型；金额用 DECIMAL，时间使用合适的日期时间类型；避免把结构化数据塞入文本字段。', 'scenario'),
    ('35、如何存储日期和时间？', 'DATE 适合日期，TIME 适合时长/时间，DATETIME 适合无时区本地日期时间，TIMESTAMP 适合时间点且会受时区转换。统一时区策略并明确精度，避免字符串存储。', 'comparison'),
    ('36、关于索引需要掌握哪些问题？', '需要理解索引目的、写入与空间代价、建立原则及不宜建索引的情况：高选择性、常用于过滤/排序/连接的列更适合；小表、低选择性列、频繁写入且查询收益低的列不宜滥建。', 'concept'),
    ('37、解释 MySQL 外连接、内连接与自连接的区别。', 'INNER JOIN 仅返回匹配行；LEFT/RIGHT OUTER JOIN 保留一侧未匹配行并以 NULL 填充另一侧；自连接是同一张表以不同别名参与连接，适用于层级或关联行查询。', 'comparison'),
    ('38、MySQL 中的事务回滚机制概述。', 'InnoDB 通过 undo log 支持 ROLLBACK 和 MVCC：事务未提交前可撤销其修改，崩溃恢复时也能回滚未完成事务。已提交事务不能用普通 ROLLBACK 撤销。', 'concept'),
    ('39、SQL 语言包括哪几部分？每部分有哪些关键字？', '通常分为 DDL（CREATE、ALTER、DROP）、DML（INSERT、UPDATE、DELETE）、DQL（SELECT）和 DCL/TCL（GRANT、REVOKE、COMMIT、ROLLBACK、SAVEPOINT）。', 'enumeration'),
    ('40、完整性约束包括哪些？', '包括实体完整性（主键）、域完整性（类型、NOT NULL、CHECK 等）和参照完整性（外键）。约束应由数据库保证，而非只依赖应用层。', 'enumeration'),
    ('41、什么是锁？', '锁是并发控制机制，用于协调多个事务对共享数据的访问。常见有共享锁、排他锁、意向锁和行/表级锁；不当使用会造成等待、死锁或吞吐下降。', 'concept'),
    ('42、什么叫视图？游标是什么？', '视图是基于查询定义的虚拟表，用于封装查询和权限边界；游标用于逐行处理结果集，通常存在于存储程序中。集合式 SQL 通常优于逐行游标。', 'comparison'),
    ('43、什么是存储过程？用什么来调用？', '存储过程是保存在数据库端、可接收参数并执行 SQL 的程序单元，可通过 CALL 调用。它适合靠近数据的固定逻辑，但会增加数据库耦合、版本管理和测试成本。', 'concept'),
    ('44、如何通俗地理解三个范式？', '第一范式要求字段原子；第二范式要求非主属性完全依赖整个候选键；第三范式要求非主属性不传递依赖主键。范式减少冗余，实践中可为性能在明确约束下适度反范式化。', 'concept'),
    ('45、什么是基本表？什么是视图？', '基本表是实际存储数据的表；视图是由查询定义的逻辑表。视图可简化查询和隐藏列，但是否可更新取决于其定义。', 'comparison'),
    ('46、视图的优点？', '视图可复用复杂查询、隐藏敏感列、为不同用户提供稳定接口并降低部分查询复杂度。它不是性能优化的万能手段，复杂视图仍需检查执行计划。', 'enumeration'),
    ('47、NULL 是什么意思？', 'NULL 表示未知、缺失或不适用，不等于 0、空字符串或 FALSE。比较 NULL 应使用 IS NULL/IS NOT NULL，聚合和三值逻辑也会受其影响。', 'concept'),
    ('48、主键、外键和索引的区别？', '主键唯一标识行且不能为空；外键维护表间参照完整性；索引用于加速访问但不必唯一。主键通常建立索引，外键列通常也应有索引以提高关联和约束检查效率。', 'comparison'),
    ('49、如何确保表格里的字段只接受特定范围里的值？', '使用合适数据类型、NOT NULL、CHECK 约束、UNIQUE、FOREIGN KEY、ENUM（谨慎）等数据库约束，并在应用层做友好校验。不能只依赖前端验证。', 'scenario'),
    ('50、说说 SQL 语句优化有哪些方法？', '只查询所需列；让 WHERE、JOIN、ORDER BY 与索引匹配；避免前导模糊匹配、隐式转换和索引列函数；控制返回行数；用 EXPLAIN ANALYZE、慢日志和真实数据验证优化效果。', 'enumeration'),
)


def upgrade() -> None:
    assert len(cards) == 50
    category_id = op.get_bind().execute(sa.text("SELECT category_id FROM exam_category WHERE name='MySQL 面试题'")).scalar_one()
    table = sa.table('exam_card', *[sa.column(column) for column in ('category_id', 'question', 'answer', 'key_points', 'tags', 'card_type', 'difficulty', 'status', 'sort_no', 'create_time', 'update_time')])
    now = datetime.now()
    op.bulk_insert(table, [dict(category_id=category_id, question=question, answer=answer, key_points='', tags='MySQL', card_type=card_type, difficulty=3, status='published', sort_no=index, create_time=now, update_time=now) for index, (question, answer, card_type) in enumerate(cards, 1)])


def downgrade() -> None:
    category_id = op.get_bind().execute(sa.text("SELECT category_id FROM exam_category WHERE name='MySQL 面试题'")).scalar_one()
    op.get_bind().execute(sa.text('DELETE FROM exam_card WHERE category_id=:category_id AND sort_no BETWEEN 1 AND 50'), {'category_id': category_id})
