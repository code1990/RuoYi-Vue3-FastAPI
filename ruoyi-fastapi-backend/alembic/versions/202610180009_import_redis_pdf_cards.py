"""import Redis interview cards from the Java interview PDF

Revision ID: 202610180009
Revises: 202610180008
"""

from datetime import datetime

from alembic import op
import sqlalchemy as sa


revision = '202610180009'
down_revision = '202610180008'
branch_labels = None
depends_on = None


cards = (
    ('1、什么是 Redis？', 'Redis 是遵循 BSD 协议的开源高性能 key-value 数据库。它在内存中操作数据，同时支持持久化、string、list、set、zset、hash 等数据结构，以及主从复制、发布订阅和键过期等能力。', 'concept'),
    ('2、Redis 的数据类型？', '基础数据类型包括 string、hash、list、set、zset（sorted set）；还可使用 HyperLogLog、Geo、Pub/Sub 和模块扩展能力。', 'enumeration'),
    ('3、使用 Redis 有哪些好处？', '数据在内存中，访问速度快；支持丰富数据结构；单条命令具备原子性，MULTI/EXEC 可组织事务；还支持过期、缓存和消息等特性。', 'enumeration'),
    ('4、Redis 相比 Memcached 有哪些优势？', 'Redis 支持更丰富的数据结构，通常性能很高，并支持 RDB/AOF 持久化；Memcached 的值主要是简单字符串且不提供持久化。', 'comparison'),
    ('5、Memcache 与 Redis 的区别都有哪些？', 'Memcache 主要是纯内存缓存，数据类型较简单；Redis 支持多种数据结构和持久化。两者的底层实现、通信协议和分布式方案也不同，应按数据模型、可靠性和运维要求选择。', 'comparison'),
    ('6、Redis 是单进程单线程的？', '传统 Redis 命令执行以单线程事件循环为主，通过串行化处理避免多线程锁竞争；现代版本可将部分网络 I/O 交给线程，但命令执行模型仍需按具体版本理解。', 'concept'),
    ('7、一个字符串类型的值能存储最大容量是多少？', 'Redis string 单个值最大可达 512MB。', 'concept'),
    ('8、Redis 的持久化机制是什么？各自的优缺点？', 'RDB 在指定时间点生成数据快照，文件紧凑、恢复较快，但两次快照间故障可能丢失数据；AOF 追加记录写命令，耐久性可通过 appendfsync 配置提高，但文件通常更大、恢复更慢，并需重写控制体积。', 'comparison'),
    ('9、Redis 常见性能问题和解决方案？', '避免在高压力主库执行阻塞性快照或大键操作；根据数据重要性配置 AOF 和副本；让主从网络稳定、低延迟；避免复制拓扑过深或在主库承受高压时盲目增加从库。', 'scenario'),
    ('10、Redis 过期键的删除策略？', '定时删除在过期时立刻删除，耗 CPU；惰性删除在访问键时检查并删除，可能占用内存；定期删除按周期抽样检查。Redis 结合惰性删除和定期删除平衡内存与 CPU。', 'comparison'),
    ('11、Redis 的回收策略（淘汰策略）？', '达到 maxmemory 后可使用 volatile-lru、volatile-ttl、volatile-random、allkeys-lru、allkeys-random 或 noeviction 等策略。volatile 仅在设置过期时间的键中选择，allkeys 面向全部键。', 'enumeration'),
    ('12、为什么 Redis 需要把所有数据放到内存中？', 'Redis 将数据放入内存以获得高读写性能，再异步持久化到磁盘；若主要依赖磁盘 I/O，性能会显著下降。因此数据集规模需受可用内存与 maxmemory 约束。', 'concept'),
    ('13、Redis 的同步机制了解么？', '主从首次同步时，主节点生成 RDB 快照并把期间的写入保存在复制流中；副本加载快照后再重放增量命令。后续通过复制流持续同步，实际还需处理断线重连和部分重同步。', 'concept'),
    ('14、Pipeline 有什么好处，为什么要用 pipeline？', 'Pipeline 将多条彼此无因果依赖的命令一次发送，减少多次网络往返，提高吞吐量。批次大小应受客户端内存、命令耗时和服务端阻塞风险约束。', 'scenario'),
    ('15、是否使用过 Redis 集群，集群的原理是什么？', 'Sentinel 侧重高可用，可在主节点故障时完成故障转移；Redis Cluster 侧重水平扩展，把键按哈希槽分片到多个主节点，并可为主节点配置副本。', 'comparison'),
    ('16、Redis 集群方案什么情况下会导致整个集群不可用？', '若某些哈希槽没有可用的主节点负责，且集群配置为全覆盖槽位，集群会停止对外提供完整服务；例如无副本时某个负责槽位的节点故障。', 'scenario'),
    ('17、Redis 支持的 Java 客户端都有哪些？', '常见 Java 客户端包括 Jedis、Lettuce 和 Redisson。选择时应结合连接模型、异步/响应式支持、集群能力与所需分布式对象能力评估。', 'enumeration'),
    ('18、Jedis 与 Redisson 对比有什么优缺点？', 'Jedis 提供较直接的 Redis 命令式 API；Redisson 在 Redis 之上提供分布式 Java 对象和同步器，方便业务使用但并非所有原生命令的直接映射。应根据是否需要高级分布式抽象选择。', 'comparison'),
    ('19、Redis 如何设置密码及验证密码？', '可通过 requirepass 配置认证密码，客户端使用 AUTH 认证；生产环境应使用 ACL 细分用户权限，并限制网络访问和保护配置文件中的密钥。', 'scenario'),
    ('20、说说 Redis 哈希槽的概念？', 'Redis Cluster 将键空间划分为 16384 个哈希槽。键经 CRC16 计算后对 16384 取模决定槽位，每个主节点负责其中一部分槽。', 'concept'),
    ('21、Redis 集群的主从复制模型是怎样的？', '集群中的每个分片由一个主节点负责写入，可配置一个或多个副本节点复制该主节点的数据；主节点故障后，合格副本可被提升为新主节点。', 'concept'),
    ('22、Redis 集群会有写操作丢失吗？为什么？', '可能。复制默认异步，主节点在副本确认前宕机时，尚未复制的写入可能丢失；网络分区下旧主节点也可能接受写入后被故障转移。可用 WAIT、合理副本与超时配置降低风险，但不能替代强一致存储。', 'scenario'),
    ('23、Redis 集群之间是如何复制的？', '主节点向副本节点进行异步复制；副本持续接收主节点的复制流以保持数据尽量同步。', 'concept'),
    ('24、Redis 集群最大节点个数是多少？', 'Redis Cluster 的哈希槽数量是 16384，实际节点数受槽位分配、内存、网络和运维能力限制；不能把槽位数简单等同于推荐节点数。', 'concept'),
    ('25、Redis 集群如何选择数据库？', 'Redis Cluster 不支持跨节点的多逻辑数据库选择，集群模式固定使用 DB 0；应用隔离通常使用 key 前缀或独立集群。', 'concept'),
    ('26、怎么测试 Redis 的连通性？', '可使用 redis-cli ping，正常返回 PONG；生产探活还应验证认证、目标数据库/集群路由及实际读写权限。', 'scenario'),
    ('27、怎么理解 Redis 事务？', '事务通过 MULTI 将命令入队，EXEC 按顺序执行；执行过程不会被其他客户端命令穿插。Redis 事务不提供关系数据库式回滚，运行时命令错误不会自动撤销其他已执行命令。', 'concept'),
    ('28、Redis 事务相关的命令有哪几个？', '主要命令是 MULTI、EXEC、DISCARD 和 WATCH；UNWATCH 可显式取消对键的监视。', 'enumeration'),
    ('29、Redis key 的过期时间和永久有效分别怎么设置？', '使用 EXPIRE 或 PEXPIRE 设置过期时间；使用 PERSIST 移除已有过期时间，使键恢复为永久有效。', 'scenario'),
    ('30、Redis 如何做内存优化？', '合理选择数据结构并控制 key/value 长度；将同一对象的多个小字段聚合到 hash；设置 TTL 和 maxmemory 策略；识别并拆分大键，结合 MEMORY USAGE、INFO MEMORY 等命令持续观测。', 'scenario'),
    ('31、Redis 回收进程如何工作的？', '写入使内存超过 maxmemory 时，Redis 会依据配置的淘汰策略回收键，直到满足内存限制或无法淘汰；一次大命令也可能迅速触发这一过程。', 'concept'),
    ('32、都有哪些办法可以降低 Redis 的内存使用情况呢？', '使用紧凑的数据结构和合适编码，将多个小键归并到 hash、list、set 或 zset；压缩或缩短值，设置合理 TTL，避免大键和无界集合，并定期清理不再使用的数据。', 'enumeration'),
    ('33、Redis 的内存用完了会发生什么？', '达到 maxmemory 后，若配置淘汰策略会按策略驱逐键；若为 noeviction，可能占用更多内存的写命令会返回错误，读取通常仍可进行。', 'concept'),
    ('34、一个 Redis 实例最多能存放多少 keys？List、Set、Sorted Set 最多能存放多少元素？', '理论上键和集合元素的上限很高，实际受可用内存、Redis 编译与运行环境、单键大小和业务延迟要求约束。容量规划应以压测和内存预算为准，而不是只依赖理论上限。', 'concept'),
    ('35、MySQL 里有 2000w 数据，Redis 中只存 20w 的数据，如何保证 Redis 中的数据都是热点数据？', '配置合适的 maxmemory 和淘汰策略，例如访问明显冷热分层时使用 allkeys-lru 或 LFU 策略；同时通过 TTL、访问统计和缓存预热/失效机制，让低频数据自然淘汰。', 'scenario'),
    ('36、Redis 最适合的场景？', '常见场景包括会话缓存、页面/对象缓存、队列、计数器与排行榜、发布订阅等。是否采用 Redis 还取决于数据一致性、可靠投递和持久化要求。', 'enumeration'),
    ('37、假如 Redis 里面有 1 亿个 key，其中有 10w 个 key 是以某个固定前缀开头的，如果将它们全部找出来？', '不要在线上使用 KEYS 扫描海量键，因为它可能阻塞事件循环。使用带 MATCH 的 SCAN 分批遍历，并在客户端去重、限速和处理游标中断。', 'scenario'),
    ('38、如果有大量的 key 需要设置同一时间过期，一般需要注意什么？', '大量键同一时刻过期会造成 CPU 和回源压力尖峰。应在基础 TTL 上加入随机抖动，使过期时间分散，并结合缓存预热与限流防止缓存雪崩。', 'scenario'),
    ('39、使用过 Redis 做异步队列么，你是怎么用的？', '简单队列可用 list：生产者 RPUSH，消费者使用阻塞的 BLPOP/BRPOP；延迟队列可用 zset 以时间戳作为 score。Pub/Sub 不保存离线消息，需可靠投递时应使用 Streams 或专业消息队列。', 'scenario'),
    ('40、使用过 Redis 分布式锁么，它是什么回事？', '使用带 NX、PX 的 SET 原子获取带过期时间的锁，并为持有者设置随机唯一值；释放时必须以 Lua 脚本“校验值后删除”，避免删掉他人锁。锁续期、主从切换和业务幂等仍需按一致性要求设计。', 'scenario'),
)


def upgrade() -> None:
    assert len(cards) == 40
    category_id = op.get_bind().execute(
        sa.text("SELECT category_id FROM exam_category WHERE name='Redis 面试题'")
    ).scalar_one()
    table = sa.table(
        'exam_card',
        *[sa.column(column) for column in ('category_id', 'question', 'answer', 'key_points', 'tags', 'card_type', 'difficulty', 'status', 'sort_no', 'create_time', 'update_time')],
    )
    now = datetime.now()
    op.bulk_insert(table, [
        dict(category_id=category_id, question=question, answer=answer, key_points='', tags='Redis', card_type=card_type, difficulty=3, status='published', sort_no=index, create_time=now, update_time=now)
        for index, (question, answer, card_type) in enumerate(cards, 1)
    ])


def downgrade() -> None:
    category_id = op.get_bind().execute(
        sa.text("SELECT category_id FROM exam_category WHERE name='Redis 面试题'")
    ).scalar_one()
    op.get_bind().execute(
        sa.text('DELETE FROM exam_card WHERE category_id=:category_id AND sort_no BETWEEN 1 AND 40'),
        {'category_id': category_id},
    )
