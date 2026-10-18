"""prepare Memcached cards for review

Revision ID: 202610180019
Revises: 202610180018
"""

from alembic import op
import sqlalchemy as sa


revision = '202610180019'
down_revision = '202610180018'
branch_labels = None
depends_on = None


cards = (
    ('结论：Memcached 是简单的分布式内存 KV 缓存，用于承接热点读并降低数据库压力。\n\n要点：数据只在内存中保存；客户端按 key 路由到节点；常缓存查询结果和会话等短生命周期数据；服务重启或淘汰会丢失缓存。\n\n补充：它不是数据库，缓存失效必须能回源并重建数据。', '内存 KV 缓存；降低数据库压力；客户端路由；可回源重建'),
    ('结论：Memcached 集群通常由客户端一致性哈希实现分布，不是服务端节点间复制集群。\n\n要点：客户端维护节点列表；根据 key 哈希选择目标节点；新增或故障节点会影响部分 key 路由；一致性哈希减少迁移范围。\n\n补充：不同客户端实现的哈希算法和虚拟节点配置必须保持一致。', '客户端分片；一致性哈希；节点列表；虚拟节点'),
    ('结论：Memcached 以纯内存键值缓存、Slab 分配和淘汰策略换取简单高性能。\n\n要点：客户端请求读写 key；命中直接返回；未命中由应用回源；内存按 Slab class 管理；空间紧张时淘汰旧 item。\n\n补充：不提供复杂查询、持久化或服务端数据复制。', '内存 KV；Slab；缓存命中；淘汰；无持久化'),
    ('结论：Slab Allocation 将内存切成固定规格的块，减少碎片与频繁分配开销。\n\n要点：不同 slab class 对应不同 item 大小；每个 class 包含多个 page 和 chunk；item 选择能容纳它的最小 class；块大小不匹配会产生内部碎片。\n\n补充：应根据 value 大小分布调整 factor，而不是只盲目扩大内存。', 'Slab class；chunk；减少碎片；内部碎片；factor'),
    ('结论：Memcached 的典型访问是“按 key 查缓存，未命中回源，再写回缓存”。\n\n要点：客户端先用一致性哈希定位节点；get 命中直接返回；miss 时访问数据库或服务；将结果 set 回缓存并设置 TTL。\n\n补充：并发 miss 可能造成缓存击穿，需要互斥、限流或逻辑过期等保护。', 'Cache Aside；一致性哈希；缓存未命中；TTL；缓存击穿'),
    ('结论：Memcached 最大优势是协议简单、内存访问快、水平扩展成本低。\n\n要点：只关注 KV 缓存；服务端无复杂集群协调；客户端可自由增加节点；适合热点、可丢失、可重建的数据。\n\n补充：优势来自功能克制，不能要求它承担 Redis 的丰富结构与持久化能力。', '简单高性能；水平扩展；热点缓存；可丢失数据'),
    ('结论：MySQL 是持久化事实来源，Memcached 只是其前面的加速层。\n\n要点：MySQL 支持事务、查询和持久化；Memcached 只缓存结果；缓存 miss 必须回源 MySQL；更新后要处理缓存失效或更新。\n\n补充：不能以缓存写成功替代数据库写成功。', 'MySQL 数据源；Memcached 缓存层；回源；缓存失效'),
    ('结论：本地缓存延迟更低，共享 Memcached 一致性更好，两者适合分层组合。\n\n要点：Local cache 不经网络但每台机器有副本；Memcached 多实例共享数据；本地缓存更新和失效广播更复杂；可用两级缓存承接热点。\n\n补充：多级缓存需明确 TTL 和失效顺序，避免长期脏读。', '本地缓存；共享缓存；两级缓存；一致性；失效广播'),
    ('结论：Memcached 通过 TTL 和内存淘汰控制缓存生命周期。\n\n要点：写入可设置过期时间；到期 item 被视为失效；内存不足时从对应 Slab class 淘汰旧项；应用应把缓存看作随时可能丢失。\n\n补充：LRU 是近似策略且受 Slab class 影响，不能依赖其作为业务顺序。', 'TTL 过期；内存淘汰；LRU；缓存不可靠'),
    ('结论：Memcached 原生不做跨节点复制，冗余需由客户端或上层架构实现。\n\n要点：可为同一 key 写多个副本；故障时切换到备用节点；也可依赖数据库回源重建；副本数越多内存成本越高。\n\n补充：缓存冗余提升可用性，不应替代持久化数据的备份方案。', '原生无复制；多副本；故障切换；回源重建'),
    ('结论：Memcached 节点故障的基本策略是摘除、重哈希、回源和渐进恢复。\n\n要点：客户端健康检查识别不可用节点；把节点从哈希环移除；受影响 key miss 后访问数据源；节点恢复后逐步预热。\n\n补充：故障时可能发生缓存雪崩，应限制回源并保护数据库。', '节点摘除；重哈希；缓存雪崩；限流；预热'),
    ('结论：Memcached 数据导入导出应当按“缓存可重建”原则处理，而非追求数据库式备份。\n\n要点：可通过客户端或脚本批量读取再写入；导入时保留 TTL 语义；大批量操作要限速；更可靠的做法是从源数据重新预热。\n\n补充：缓存不是权威存储，导出期间的数据变化与过期允许丢失。', '缓存预热；批量导入导出；TTL；限速；非权威存储'),
    ('结论：导入导出间过期的缓存应视为无效，按正常 miss 流程回源重建。\n\n要点：TTL 到期后不应恢复旧值；重新读取权威数据源；再写入新缓存；必要时记录导入时间以避免把过期快照复活。\n\n补充：缓存正确性依赖失效策略，不依赖“尽量保留旧数据”。', 'TTL 失效；回源重建；避免复活旧值；缓存正确性'),
    ('结论：Memcached 原生缺少完善认证与加密，安全主要依赖网络边界。\n\n要点：部署在私网；通过防火墙和安全组限制来源；不要暴露 11211 到公网；可在受控网络中结合 SASL 等能力，取决于版本和构建。\n\n补充：缓存中不应存放未经保护的敏感信息。', '网络隔离；禁止公网暴露；11211；SASL；敏感数据'),
    ('结论：Memcached 使用多线程处理网络连接，但必须保证共享缓存操作并发安全。\n\n要点：主线程负责监听和分发；工作线程处理客户端请求；内部用锁协调共享结构；客户端可并发发起多个请求。\n\n补充：高并发瓶颈还可能在网络、CPU、内存带宽和热 key，不只是线程数。', '多线程网络 IO；工作线程；锁；热 key'),
    ('结论：Memcached key 最大长度通常为 250 字节，且应使用稳定、可控的 key 设计。\n\n要点：key 不能过长；建议包含业务前缀、版本和唯一标识；避免空格和不可控用户原文；变更结构时用版本前缀隔离旧缓存。\n\n补充：这是字节限制，不等于字符个数。', 'key 最大 250 字节；业务前缀；版本化；字节长度'),
    ('结论：Memcached 单个 item 默认常限制约 1MB，超大对象不应直接塞进缓存。\n\n要点：限制可在启动参数调整；大 value 会占用大 chunk 并造成内存浪费；更适合缓存小对象或拆分后的结果；大文件应使用对象存储等专用系统。\n\n补充：调整上限需同时评估网络包、内存碎片和热点影响。', '单 item 约 1MB；大对象；chunk 浪费；专用存储'),
    ('结论：提高 Memcached 内存利用率要从 value 大小分布、Slab class 和过期策略入手。\n\n要点：观察各 class 的命中率、淘汰和空闲 chunk；调整增长因子和页分配；设置合理 TTL；清除不再访问的大对象。\n\n补充：内存利用率高不等于命中率高，应同时看业务命中和回源压力。', 'Slab 分布；命中率；淘汰率；TTL；内存利用率'),
    ('结论：Memcached 二进制协议是更紧凑、机器友好的通信格式，是否使用取决于客户端与运维能力。\n\n要点：文本协议便于调试；二进制协议字段固定、解析效率好；功能和兼容性受客户端支持影响；协议选择不改变缓存一致性问题。\n\n补充：多数业务优先选维护良好的客户端，不必为协议本身过早优化。', '文本协议；二进制协议；客户端兼容；解析效率'),
    ('结论：Slab 分配器预分配固定大小 chunk，避免频繁 malloc/free 导致的碎片和锁竞争。\n\n要点：内存先切 page，再按 class 切 chunk；item 分配到合适 chunk；同 class 回收复用；大小不均会留下内部碎片。\n\n补充：不能跨 class 任意复用空间，因此缓存 value 大小变化大时要特别监控。', '预分配；page；chunk；复用；内部碎片'),
    ('结论：Memcached 单条命令通常是原子的，但多个命令组合不构成事务。\n\n要点：get/set/add/incr 等单操作由服务端串行保证原子性；check-then-set 存在竞态；可使用 gets/cas 做乐观比较更新；没有跨 key ACID 事务。\n\n补充：关键一致性逻辑应放在数据库或专用协调机制中。', '单命令原子；无事务；gets/cas；并发竞态'),
    ('结论：集群 session 共享可用集中式缓存、粘性会话或持久化存储，需在可用性与一致性间取舍。\n\n要点：共享 Memcached 让任意应用节点读 session；粘性 session 简单但故障切换差；副本或持久化可提升可靠性；session 应有 TTL。\n\n补充：登录态等安全敏感 session 要考虑篡改防护与失效同步。', '共享 session；粘性会话；TTL；故障切换；安全'),
    ('结论：Memcached 专注纯内存 KV 缓存，Redis 提供更多结构、持久化与高可用能力。\n\n要点：Memcached 使用 Slab、无原生持久化；Redis 支持字符串外的多种数据结构、RDB/AOF 和复制；两者都可做缓存；选型看数据模型与可靠性要求。\n\n补充：不要只按“Redis 功能更多”选型，简单热点缓存 Memcached 仍可胜任。', 'Memcached KV；Redis 数据结构；RDB/AOF；Slab；选型'),
)


def upgrade() -> None:
    assert len(cards) == 23
    connection = op.get_bind()
    category_id = connection.execute(sa.text("SELECT category_id FROM exam_category WHERE name = 'Memcached 面试题'")).scalar_one()
    for sort_no, (ai_summary, key_points) in enumerate(cards, 1):
        connection.execute(sa.text('UPDATE exam_card SET ai_summary=:ai_summary, key_points=:key_points, review_enabled=1 WHERE category_id=:category_id AND sort_no=:sort_no'), {'ai_summary': ai_summary, 'key_points': key_points, 'category_id': category_id, 'sort_no': sort_no})


def downgrade() -> None:
    connection = op.get_bind()
    category_id = connection.execute(sa.text("SELECT category_id FROM exam_category WHERE name = 'Memcached 面试题'")).scalar_one()
    connection.execute(sa.text("UPDATE exam_card SET ai_summary='', key_points='', review_enabled=0 WHERE category_id=:category_id"), {'category_id': category_id})
