"""prepare Elasticsearch cards for review

Revision ID: 202610180018
Revises: 202610180017
"""

from alembic import op
import sqlalchemy as sa


revision = '202610180018'
down_revision = '202610180017'
branch_labels = None
depends_on = None


cards = (
    ('结论：ES 集群设计应围绕索引生命周期、分片规模、写入吞吐和查询模式综合优化。\n\n要点：按时间或业务滚动索引并用别名切换；结合冷热分层、ILM、合理主副分片；写入用 Bulk、控制 refresh；查询避免昂贵通配符与超大聚合。\n\n补充：没有通用分片数，需根据数据量、节点资源和压测结果调整。', '滚动索引；ILM 冷热分层；Bulk 写入；分片规划；查询压测'),
    ('结论：倒排索引把“词项到文档”的关系预先建立，使全文检索不必逐篇扫描。\n\n要点：分析器将文本拆成 term；词典定位 term；倒排列表记录包含该 term 的文档和位置信息；查询先查词再取文档。\n\n补充：它适合关键词搜索，与数据库常见的正向记录索引方向相反。', '词项 term；词典；倒排列表；全文检索'),
    ('结论：ES 数据增长后要从索引设计、资源与集群角色三层调优。\n\n要点：按时间或业务拆分并管理生命周期；设置合适分片和副本；使用 SSD、冷热数据分层；必要时分离 master、data、ingest 等角色。\n\n补充：先用监控定位瓶颈，再扩容或调参，避免只靠增加分片。', '索引生命周期；分片副本；SSD；冷热分层；节点角色'),
    ('结论：现代 ES 主节点选举由选举配置和多数派投票保证集群只有一个 master。\n\n要点：只有 master-eligible 节点参与；候选节点通过投票形成多数派；当选 master 负责集群状态；多数派规则防止网络分区脑裂。\n\n补充：旧版 minimum_master_nodes 是历史配置，7+ 应使用正确的初始主节点引导设置。', 'master-eligible；多数派投票；集群状态；防脑裂'),
    ('结论：文档写入先经协调节点路由到主分片，再复制到副本并最终对外确认。\n\n要点：routing 决定主分片；主分片写 Lucene 和 translog；副本执行相同操作；refresh 后新段才对搜索可见。\n\n补充：写入成功、可搜索和安全落盘是不同时间点，不能混为一谈。', '协调节点；routing；主副分片；translog；refresh'),
    ('结论：ES 分布式搜索通常采用 Query Then Fetch，在各分片查询后由协调节点合并结果。\n\n要点：协调节点向相关分片发 query；每个分片返回候选 ID 与排序值；协调节点全局归并；再 fetch 最终命中文档。\n\n补充：深分页会放大各分片候选集，应使用 search_after 或 PIT 等方案。', 'Query Then Fetch；分片查询；协调归并；深分页'),
    ('结论：ES 部署的 Linux 优化重点是避免交换、控制 JVM 堆和提高文件及内存映射限制。\n\n要点：关闭 swap；堆通常不超过节点内存一半且不盲目超过约 32GB；提高文件描述符与 vm.max_map_count；优先 SSD。\n\n补充：具体参数应按 ES 版本官方检查项配置，不能只复制旧调优清单。', '关闭 swap；JVM 堆；文件描述符；vm.max_map_count；SSD'),
    ('结论：Lucene 索引由多个不可变 Segment 组成，写入生成新段、后台再合并。\n\n要点：每个 Segment 都有独立倒排索引；不可变使并发读高效；删除先标记；Merge 将小段合成大段并回收删除文档。\n\n补充：大量小 Segment 会增加搜索与文件开销，Merge 也会带来 I/O 压力。', 'Lucene Segment；不可变；删除标记；后台 Merge'),
    ('结论：ES 的主选举核心是候选主节点的发现、投票和多数派确认。\n\n要点：节点先发现符合条件的候选者；选举产生一个 master；master 发布集群状态；失联后重新选举并要求法定多数。\n\n补充：Zen Discovery、按 nodeId 排序等是旧版本实现细节，回答时应先说明版本。', '主节点选举；节点发现；多数派；版本差异'),
    ('结论：网络分区出现两个“主”候选群时，必须依靠多数派避免脑裂和双写。\n\n要点：只有获得法定多数的一侧可维持主节点；部署至少 3 个 master-eligible 节点；另一侧失去多数后停止主控能力。\n\n补充：不能用“20 台分成 10 对 10”硬选一边，正确做法是让两边都不能形成多数。', '网络分区；脑裂；法定多数；至少三主候选'),
    ('结论：客户端应连接多个协调入口，并让请求路由能力由集群和客户端策略共同承担。\n\n要点：可配置多个 seed 节点；REST 客户端通常做负载均衡与故障切换；sniffing 可发现节点但需考虑网络拓扑；请求可先到协调节点。\n\n补充：TransportClient 已废弃，现代 ES 优先使用官方 Java API Client 或 REST Client。', '多个 seed 节点；协调节点；sniffing；TransportClient 已废弃'),
    ('结论：ES 写入经历内存缓冲、translog、refresh、flush 和 Segment 合并等阶段。\n\n要点：写操作先记录 translog；refresh 打开新搜索视图；flush 将提交点持久化并截断 translog；后台 Merge 优化段结构。\n\n补充：refresh 频率影响近实时性和写入性能，批量导入时可临时降低 refresh 成本。', '内存缓冲；translog；refresh；flush；Segment 合并'),
    ('结论：ES 文档和 Segment 不可原地修改，更新本质是写新版本、删除旧版本。\n\n要点：删除先打标记；更新重新索引完整文档；后台 Merge 最终回收旧内容；可用 seq_no 与 primary_term 做乐观并发控制。\n\n补充：高频局部更新代价不低，建模时应避免把 ES 当作高频事务数据库。', '不可变文档；删除标记；重建索引；乐观并发控制'),
    ('结论：Query Then Fetch 先只传输轻量排序结果，再获取最终文档以降低网络开销。\n\n要点：Query 阶段每分片计算匹配与排序；协调节点确定全局 top N；Fetch 阶段向命中分片拉取 _source；最终组装响应。\n\n补充：排序、聚合和高 from 值会增加分片工作量，是搜索性能排查重点。', 'Query 阶段；Fetch 阶段；全局 top N；排序开销'),
    ('结论：从词找到倒排索引要经过词典定位和倒排列表读取两个关键步骤。\n\n要点：分析器产生 term；词典使用 FST 等压缩结构定位 term；读取 posting list 获取文档 ID；再结合跳表、位置和评分完成查询。\n\n补充：Trie 是理解前缀结构的基础，Lucene 实际词典实现常以 FST 为主。', '分析器；FST 词典；posting list；跳表；评分'),
    ('结论：ES Linux 调优应优先满足官方 bootstrap 检查，再进行针对性容量优化。\n\n要点：禁用交换、合理堆内存、提高文件与 mmap 限制；选用 SSD 与可靠磁盘；避免跨数据中心部署单一集群；监控 CPU、I/O、堆与 GC。\n\n补充：线程池和 GC 参数不应随意手调，先确认是否真是线程或 GC 瓶颈。', 'bootstrap 检查；swap；mmap；SSD；GC 监控'),
    ('结论：ES 的 GC 问题通常源于堆压力、聚合过大、缓存和 Segment 过多，而非单纯选择某个 GC。\n\n要点：持续监控 heap 使用和 GC 停顿；限制超大 bucket、分页和 fielddata；控制 Segment 数；为操作系统页缓存保留足够内存。\n\n补充：堆满会触发长暂停甚至节点失联，优先优化查询和映射再盲目加堆。', 'heap 监控；大聚合；fielddata；Segment；页缓存'),
    ('结论：超大数据量聚合要避免精确计算所有唯一值，可采用近似算法和预聚合。\n\n要点：cardinality 使用 HyperLogLog++ 近似去重；控制 terms 聚合 bucket 数；可按时间分区、离线预聚合或使用 transform；评估误差和内存预算。\n\n补充：近似值适合分析，不适合作为财务等必须精确的结果。', 'cardinality；HyperLogLog++；近似聚合；bucket 控制；预聚合'),
    ('结论：ES 通过主分片顺序、复制机制和乐观并发控制实现读写一致性边界。\n\n要点：同一分片写入由主分片串行协调；副本复制后提供读取；用 seq_no/primary_term 防止并发覆盖；refresh 前搜索可能看不到最新写入。\n\n补充：ES 是近实时搜索，不应承诺传统数据库式的任意时刻强一致读。', '主分片顺序；副本复制；seq_no；primary_term；近实时'),
    ('结论：ES 监控应覆盖集群健康、分片、节点资源、JVM 和业务查询写入指标。\n\n要点：关注 green/yellow/red、未分配分片、磁盘水位；监控 CPU、I/O、heap、GC、线程池拒绝；跟踪索引延迟和查询慢日志。\n\n补充：告警应区分短暂波动与持续异常，避免只盯 cluster health 一个指标。', 'cluster health；未分配分片；磁盘水位；JVM GC；慢日志'),
    ('结论：电商搜索通常是数据同步、索引构建、检索服务、缓存和观测系统组成的链路。\n\n要点：商品库变更经 CDC、MQ 或任务同步到索引；搜索服务封装召回与排序；缓存承接热点；ES 集群提供检索；监控保障质量。\n\n补充：关键难点是数据一致性、重建索引、灰度切换和搜索相关性，不只是搭建 ES。', '数据同步；索引构建；搜索服务；缓存；相关性'),
    ('结论：个性化搜索在基础文本相关性之上，利用用户和商品特征做召回与排序。\n\n要点：用户画像和行为形成特征；多路召回获取候选；排序模型综合相关性、偏好和业务规则；实时与离线特征分别更新。\n\n补充：需关注冷启动、特征泄漏、可解释性和在线 A/B 实验。', '用户画像；多路召回；排序模型；实时特征；A/B 实验'),
    ('结论：Trie（字典树）用公共前缀共享节点，适合前缀匹配和词典检索。\n\n要点：从根到节点构成字符串；同一节点子边字符不同；查找复杂度与词长相关；可用于自动补全和敏感词匹配。\n\n补充：节点多时内存开销大，工程中常用压缩 Trie 或 FST 优化。', 'Trie 字典树；公共前缀；前缀匹配；自动补全；FST'),
    ('结论：拼写纠错通常先生成候选词，再按编辑距离和词频等信号排序。\n\n要点：编辑距离衡量插入、删除、替换成本；BK 树支持按距离范围检索；词频、上下文和业务词典用于重排候选。\n\n补充：搜索纠错应避免过度纠正，可给用户保留原词查询入口。', '编辑距离；BK 树；候选词；词频排序；过度纠正'),
)


def upgrade() -> None:
    assert len(cards) == 24
    connection = op.get_bind()
    category_id = connection.execute(sa.text("SELECT category_id FROM exam_category WHERE name = 'Elasticsearch 面试题'")).scalar_one()
    for sort_no, (ai_summary, key_points) in enumerate(cards, 1):
        connection.execute(sa.text('UPDATE exam_card SET ai_summary=:ai_summary, key_points=:key_points, review_enabled=1 WHERE category_id=:category_id AND sort_no=:sort_no'), {'ai_summary': ai_summary, 'key_points': key_points, 'category_id': category_id, 'sort_no': sort_no})


def downgrade() -> None:
    connection = op.get_bind()
    category_id = connection.execute(sa.text("SELECT category_id FROM exam_category WHERE name = 'Elasticsearch 面试题'")).scalar_one()
    connection.execute(sa.text("UPDATE exam_card SET ai_summary='', key_points='', review_enabled=0 WHERE category_id=:category_id"), {'category_id': category_id})
