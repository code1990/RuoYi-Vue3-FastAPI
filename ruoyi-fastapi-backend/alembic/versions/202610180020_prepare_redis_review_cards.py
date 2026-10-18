"""prepare Redis cards for review

Revision ID: 202610180020
Revises: 202610180019
"""
from alembic import op
import sqlalchemy as sa

revision='202610180020'; down_revision='202610180019'; branch_labels=None; depends_on=None

cards=(
('结论：Redis 是内存数据结构服务器，可做缓存、队列与实时数据处理。\n\n要点：支持持久化、复制、过期和多种结构；数据主要在内存操作；常作为数据库前的高性能层。\n\n补充：它不天然提供关系数据库级强事务，关键数据仍要有权威存储。','内存数据库；数据结构；持久化；复制；过期'),
('结论：Redis 核心结构是 String、Hash、List、Set、ZSet，并扩展 Geo、HyperLogLog、Stream 等。\n\n要点：按访问模型选择结构；Hash 适合对象字段；ZSet 适合排序；Stream 适合可消费消息。\n\n补充：错误的数据结构选择会造成内存浪费和复杂查询。','String；Hash；List；Set；ZSet；Stream'),
('结论：Redis 的价值在于内存速度、丰富结构和单命令原子性。\n\n要点：可承接高频读写；支持 TTL、发布订阅和持久化；减少数据库压力；命令串行执行便于保证单操作原子。\n\n补充：高性能不等于无需治理，仍要设计失效、限流和容量。','内存速度；数据结构；原子命令；TTL；缓存'),
('结论：Redis 比 Memcached 提供更多数据结构、持久化和高可用能力。\n\n要点：Redis 支持 RDB/AOF、复制和复杂结构；Memcached 专注纯内存 KV 缓存；二者都可做热点缓存。\n\n补充：简单缓存场景不必因功能多就强制选 Redis。','数据结构；RDB/AOF；高可用；Memcached；选型'),
('结论：Memcached 与 Redis 的选择取决于数据模型、可靠性和运维需求。\n\n要点：Memcached 简单、纯内存、Slab 分配；Redis 结构丰富且可持久化；两者分布式与协议实现不同。\n\n补充：不要用单一性能结论替代实际压测和业务边界。','Memcached；Redis；持久化；数据模型；压测'),
('结论：Redis 命令执行传统上以单线程事件循环为核心，避免共享数据锁竞争。\n\n要点：单线程不等于只能处理一个连接；I/O 多路复用处理并发；新版本可把部分网络 I/O 交给线程。\n\n补充：慢命令、大 key 与阻塞操作仍会卡住主线程。','单线程事件循环；I/O 多路复用；慢命令；大 key'),
('结论：Redis String 单值最大约为 512MB，但不应把它当作大文件存储。\n\n要点：大 value 会占用内存和网络；影响复制、持久化与延迟；应拆分或转对象存储。\n\n补充：容量上限是协议能力，不是推荐的建模大小。','String；512MB；大 value；内存；对象存储'),
('结论：RDB 是快照，AOF 是写命令日志，二者在恢复速度与数据安全间取舍。\n\n要点：RDB 文件紧凑、恢复快；AOF 丢数据窗口更小但文件更大；AOF rewrite 控制体积。\n\n补充：生产常组合使用，并按可接受的数据丢失窗口配置 fsync。','RDB 快照；AOF 日志；fsync；rewrite；数据丢失窗口'),
('结论：Redis 性能治理要避免阻塞主线程、复制压力和不合理持久化。\n\n要点：排查慢命令和大 key；避免高峰期重操作；保证主从低延迟；按重要性配置副本和 AOF。\n\n补充：先观察 CPU、延迟、内存和复制积压，再针对性调整。','慢命令；大 key；复制；持久化；延迟监控'),
('结论：Redis 结合惰性删除和定期删除平衡过期键清理的 CPU 与内存成本。\n\n要点：惰性删除在访问时检查 TTL；定期删除抽样扫描；纯定时删除会耗 CPU；纯惰性删除会占内存。\n\n补充：过期键不保证在 TTL 到点瞬间物理删除。','惰性删除；定期删除；TTL；CPU；内存'),
('结论：maxmemory 淘汰策略决定内存满后哪些键可被驱逐。\n\n要点：allkeys 面向所有键；volatile 只面向有 TTL 的键；LRU/LFU/TTL/random 选择候选；noeviction 拒绝写入。\n\n补充：策略必须匹配缓存数据与非缓存数据的混合方式。','maxmemory；allkeys；volatile；LRU/LFU；noeviction'),
('结论：Redis 数据放内存是为了低延迟高吞吐，持久化用于故障恢复而非主读写路径。\n\n要点：内存访问远快于磁盘；数据集受可用内存约束；maxmemory 防止 OOM；RDB/AOF 异步落盘。\n\n补充：应为系统页缓存和复制缓冲预留资源。','内存性能；maxmemory；RDB/AOF；容量规划'),
('结论：主从复制先全量同步，之后通过复制流持续传递增量写入。\n\n要点：首次同步发送 RDB；副本加载后重放增量；断线后可尝试部分重同步；复制默认异步。\n\n补充：复制不是强一致保障，故障时仍可能丢最后写入。','全量同步；RDB；部分重同步；复制流；异步复制'),
('结论：Pipeline 将多条无依赖命令批量发送，主要节省网络往返时间。\n\n要点：客户端一次写入多条命令；服务端按顺序执行；批量读取结果；提高吞吐。\n\n补充：Pipeline 不具备事务语义，批次过大也会占用内存和阻塞服务端。','Pipeline；网络往返；批量命令；吞吐；非事务'),
('结论：Sentinel 解决自动故障转移，Redis Cluster 解决分片扩展并同时提供副本高可用。\n\n要点：Sentinel 监控主从并选主；Cluster 将 key 映射到哈希槽；每个分片可有副本；客户端需支持重定向。\n\n补充：两者目标不同，不能把 Sentinel 当作分片方案。','Sentinel；Redis Cluster；哈希槽；故障转移；分片'),
('结论：Cluster 在关键槽位没有可用主节点时可能拒绝完整服务。\n\n要点：每个槽需由主节点负责；主故障无合格副本会丢槽；cluster-require-full-coverage 会影响整体可用性。\n\n补充：应配置副本并演练节点故障与网络分区。','哈希槽；主节点故障；副本；full coverage；演练'),
('结论：Java 常用 Jedis、Lettuce、Redisson，分别偏命令 API、异步连接和分布式对象。\n\n要点：Jedis 连接模型直接；Lettuce 基于 Netty 且支持异步/响应式；Redisson 提供锁、队列等抽象。\n\n补充：选型要匹配线程模型、集群支持和业务抽象需求。','Jedis；Lettuce；Redisson；异步；分布式对象'),
('结论：Jedis 接近原生命令，Redisson 提供更高层分布式 Java 对象。\n\n要点：Jedis 简洁直接；Redisson 封装锁、Map、队列等；高级抽象降低编码成本但要理解底层语义。\n\n补充：不能把 Redisson 当作所有 Redis 命令的等价替代。','Jedis；Redisson；原生命令；分布式锁；抽象'),
('结论：Redis 认证应采用 ACL、强密码和网络隔离的组合，而非只设置 requirepass。\n\n要点：客户端用 AUTH；ACL 可按用户限制命令和 key；禁止公网暴露；保护配置文件和密钥。\n\n补充：旧版 requirepass 是单密码模型，生产更推荐 ACL 最小权限。','AUTH；ACL；requirepass；网络隔离；最小权限'),
('结论：Redis Cluster 使用固定 16384 个哈希槽实现 key 的分片路由。\n\n要点：CRC16(key) 对 16384 取模得到槽；每个主节点负责一部分槽；hash tag 可让多个 key 落在同槽。\n\n补充：多 key 操作跨槽会受限，建模时要提前规划 hash tag。','16384 槽；CRC16；分片；hash tag；跨槽限制'),
('结论：Cluster 每个分片由一个主节点写入、一个或多个副本复制，主故障后副本可提升。\n\n要点：主负责槽与写请求；副本接收复制流；故障检测后选举副本；客户端按新拓扑重定向。\n\n补充：副本提升不保证未复制写入一定保留。','主副复制；分片；副本提升；故障转移'),
('结论：Redis Cluster 默认异步复制，主节点宕机时最后一小段写入可能丢失。\n\n要点：主可先响应客户端再复制；网络分区的旧主可能继续写；WAIT 可降低风险；副本与超时配置影响窗口。\n\n补充：需要强一致的资金等数据不应只依赖 Redis。','异步复制；写丢失；WAIT；网络分区；强一致'),
('结论：Cluster 节点间通过主从复制流同步各自主分片的数据。\n\n要点：主节点持续向副本发送命令；副本断线后请求部分或全量同步；复制链路健康影响故障恢复质量。\n\n补充：复制拓扑越复杂，延迟和运维风险越高。','主从复制；复制流；部分同步；复制延迟'),
('结论：16384 是槽位数量，不是 Redis Cluster 推荐或最大节点数量。\n\n要点：节点数受每节点槽数、容量、网络和运维复杂度限制；节点过多会增加集群通信成本；应按分片容量规划。\n\n补充：槽位数足够支持大量节点，不代表部署大量节点有收益。','16384 槽位；节点规划；容量；集群通信'),
('结论：Redis Cluster 固定使用 DB 0，逻辑隔离应采用 key 前缀或独立集群。\n\n要点：SELECT 在 Cluster 中不可用于多 DB；前缀区分租户或业务；独立集群隔离更强；ACL 可补充权限边界。\n\n补充：不要把单机多 DB 的习惯直接带到 Cluster。','Cluster DB 0；key 前缀；独立集群；ACL；隔离'),
('结论：连通性检查至少验证网络、认证和基本读写，不应只看端口开放。\n\n要点：redis-cli ping 应返回 PONG；有认证需先 AUTH；Cluster 还要验证路由；生产探针应避免破坏性命令。\n\n补充：PONG 不代表复制、内存或业务 key 一切正常。','redis-cli ping；PONG；AUTH；Cluster 路由；健康检查'),
('结论：Redis 事务是命令队列的顺序执行，不提供关系数据库式回滚。\n\n要点：MULTI 开始入队；EXEC 按序执行且不被插入；DISCARD 放弃队列；运行时错误不会撤销已执行命令。\n\n补充：需要条件更新时配合 WATCH 或 Lua 脚本。','MULTI；EXEC；DISCARD；无回滚；WATCH'),
('结论：MULTI、EXEC、DISCARD、WATCH、UNWATCH 是 Redis 事务与乐观锁核心命令。\n\n要点：MULTI 入队；EXEC 提交；DISCARD 取消；WATCH 监视键变化；UNWATCH 取消监视。\n\n补充：WATCH 失败后事务不执行，客户端应重新读取并重试。','MULTI；EXEC；DISCARD；WATCH；UNWATCH'),
('结论：EXPIRE/PEXPIRE 设置 TTL，PERSIST 移除 TTL 使 key 恢复永久有效。\n\n要点：秒和毫秒单位不同；TTL 可查询剩余时间；重写 key 可能改变过期行为；过期删除是惰性与定期结合。\n\n补充：缓存 key 通常必须设置 TTL，避免无限增长。','EXPIRE；PEXPIRE；PERSIST；TTL；缓存增长'),
('结论：Redis 内存优化依赖正确结构、控制 key/value、TTL 与大 key 治理。\n\n要点：小字段可用 Hash 聚合；压缩值和缩短 key；设置 maxmemory 与淘汰策略；用 MEMORY USAGE 识别热点大对象。\n\n补充：聚合过度也会形成大 Hash，需要在访问与内存间平衡。','Hash 聚合；TTL；maxmemory；大 key；MEMORY USAGE'),
('结论：内存超过 maxmemory 时，Redis 按淘汰策略删除键，或在 noeviction 下拒绝写入。\n\n要点：写操作触发回收；策略决定候选集合与算法；淘汰到满足限制或无法淘汰；大命令可突然放大压力。\n\n补充：maxmemory 要预留复制缓冲和碎片空间。','maxmemory；淘汰策略；noeviction；内存碎片'),
('结论：降低 Redis 内存应减少小 key 元数据、压缩值、设置 TTL 并治理大对象。\n\n要点：用 Hash/List/Set 聚合小对象；使用紧凑编码；清理无界集合；按业务设置过期；监控内存与碎片率。\n\n补充：不要只追求压缩，序列化和 CPU 成本也要评估。','小 key；紧凑编码；TTL；大 key；碎片率'),
('结论：Redis 内存满后的结果由 maxmemory-policy 决定。\n\n要点：有淘汰策略时会驱逐符合条件的 key；noeviction 时写命令返回错误；读请求通常仍可执行；应用应监控拒绝数。\n\n补充：不能把 OOM 后的淘汰当作正常数据生命周期管理。','内存满；淘汰；noeviction；写错误；监控'),
('结论：Redis 可存 key 和集合元素的数量理论很高，实际容量由内存和延迟预算决定。\n\n要点：每个 key 有对象和字典开销；集合元素有额外元数据；大数量会影响 fork、持久化和复制；容量需压测估算。\n\n补充：不要只引用理论上限，面试应说明容量规划方法。','容量规划；内存开销；集合元素；压测；持久化'),
('结论：有限 Redis 容量要通过淘汰策略、TTL 和访问特征让热点数据留下。\n\n要点：设置合理 maxmemory；选择 allkeys-lru 或 allkeys-lfu 等；给缓存 key TTL；通过预热和指标验证命中率。\n\n补充：LRU/LFU 是近似算法，热点识别仍需业务观测。','热点数据；allkeys-lru；LFU；TTL；命中率'),
('结论：Redis 适合缓存、计数、排行榜、会话、轻量队列和发布订阅等低延迟场景。\n\n要点：String/Hash 做缓存；ZSet 做排行榜；INCR 做计数；Stream 做消息；TTL 管理会话。\n\n补充：可靠消息、强一致事务和超大数据应评估更专用系统。','缓存；计数器；排行榜；Stream；会话'),
('结论：海量 key 查前缀必须用 SCAN 分批遍历，禁止线上 KEYS 全量扫描。\n\n要点：SCAN 用游标逐步返回；MATCH 过滤模式；结果可能重复需客户端去重；要限速并允许中断恢复。\n\n补充：SCAN 不是快照，遍历期间键可能新增或删除。','SCAN；MATCH；游标；去重；禁止 KEYS'),
('结论：大量 key 同时过期会造成缓存雪崩和回源尖峰，应给 TTL 加随机抖动。\n\n要点：基础 TTL 上附加随机值；过期分散降低 CPU 压力；结合预热、限流与降级保护数据源；监控命中率突降。\n\n补充：随机范围应符合业务可接受的新鲜度。','缓存雪崩；TTL 抖动；限流；预热；降级'),
('结论：Redis 可实现简单异步队列，但可靠消息应优先 Stream 或专业 MQ。\n\n要点：List 用 RPUSH/BLPOP 实现阻塞消费；ZSet 可按 score 做延迟队列；Pub/Sub 不保留离线消息；Stream 有消费组与确认。\n\n补充：需要顺序、重试、死信和高可靠时应明确消息语义。','List 队列；BLPOP；ZSet 延迟；Stream；Pub/Sub'),
('结论：Redis 分布式锁应使用 SET NX PX、唯一 token 与 Lua 原子释放。\n\n要点：SET 仅在不存在时加锁并设置 TTL；token 标识持有者；释放前校验 token 再删除；长任务需考虑续期。\n\n补充：主从切换下仍有一致性边界，业务必须保证幂等。','SET NX PX；唯一 token；Lua 释放；TTL；幂等'),
)

def upgrade():
    assert len(cards)==40
    c=op.get_bind(); cid=c.execute(sa.text("SELECT category_id FROM exam_category WHERE name='Redis 面试题'")).scalar_one()
    for i,(summary,points) in enumerate(cards,1): c.execute(sa.text('UPDATE exam_card SET ai_summary=:s,key_points=:p,review_enabled=1 WHERE category_id=:c AND sort_no=:i'),{'s':summary,'p':points,'c':cid,'i':i})
def downgrade():
    c=op.get_bind(); cid=c.execute(sa.text("SELECT category_id FROM exam_category WHERE name='Redis 面试题'")).scalar_one(); c.execute(sa.text("UPDATE exam_card SET ai_summary='',key_points='',review_enabled=0 WHERE category_id=:c"),{'c':cid})
