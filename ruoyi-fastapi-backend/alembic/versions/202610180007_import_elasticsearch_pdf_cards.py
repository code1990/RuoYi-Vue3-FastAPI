"""import Elasticsearch PDF chapter cards

Revision ID: 202610180007
Revises: 202610180006
"""
from datetime import datetime
from alembic import op
import sqlalchemy as sa

revision = '202610180007'
down_revision = '202610180006'
branch_labels = None
depends_on = None

cards = (
('1、elasticsearch 了解多少，说说你们公司 es 的集群架构，索引数据大小，分片有多少，以及一些调优手段。', 'ES 是分布式搜索引擎。索引按日期滚动、使用别名、冷热分离和生命周期管理；写入时可临时设副本为 0、关闭 refresh、使用 bulk，完成后恢复；查询避免 wildcard 和超大 terms，合理使用 keyword、时间索引和路由。'),
('2、elasticsearch 的倒排索引是什么', '倒排索引记录词项到文档列表的映射，支持从词快速定位文档；词典可用前缀树等结构压缩，查询速度高。'),
('3、elasticsearch 索引数据多了怎么办，如何调优，部署', '从动态索引、存储和部署三层处理：按业务滚动索引、合理分片副本和生命周期；使用 SSD、冷热分离；节点角色分离并监控资源。'),
('4、elasticsearch 是如何实现 master 选举的', '仅 master 候选节点可当选；通过最小主节点数防止脑裂，候选节点投票并选出主节点。'),
('5、详细描述一下 Elasticsearch 索引文档的过程', '协调节点按路由将请求转给主分片，主分片写入后复制到副本，副本确认后响应；写入经内存缓冲、translog、refresh/flush 形成 Lucene 段。'),
('6、详细描述一下 Elasticsearch 搜索的过程？', '协调节点向各分片副本发查询，各分片本地查询并返回优先队列，协调节点合并排序后取回需要的文档。'),
('7、Elasticsearch 在部署时，对 Linux 的设置有哪些优化方法', '关闭 swap；堆内存设为 min(节点内存/2,32GB)；提高文件句柄；按业务调整线程池；优先 RAID10/SSD。'),
('8、lucence 内部结构是什么？', 'Lucene 索引由多个不可变 Segment 组成；每个 Segment 是完整倒排索引，后台合并小段以控制搜索开销。'),
('9、Elasticsearch 是如何实现 Master 选举的？', 'ZenDiscovery 负责发现和选举；候选 master 节点按 nodeId 排序并投票，达到 n/2+1 后当选。'),
('10、Elasticsearch 中的节点（比如共 20 个），其中的 10 个选择了一个 master，另外 10 个选择了另一个 master，怎么办？', '候选 master 至少 3 个时设置最少投票数防脑裂；候选只有两个时只保留一个 master 候选。'),
('11、客户端在和集群连接时，如何选择特定的节点执行请求的？', 'TransportClient 可连接一个或多个节点；可设置 sniff 自动发现集群节点，并由客户端选择连接。'),
('12、详细描述一下 Elasticsearch 索引文档的过程。', '文档写入 Memory Buffer 和 translog；refresh 使其可搜索，flush 将段持久化并清空 translog；后台合并 Segment。'),
('13、详细描述一下 Elasticsearch 更新和删除文档的过程。', '文档不可变：删除通过 .del 标记，更新等同删除旧文档再创建新版本；版本号用于并发控制。'),
('14、详细描述一下 Elasticsearch 搜索的过程。', '采用 Query Then Fetch：查询阶段各分片返回文档 ID 与排序值，协调节点全局排序，取回阶段拉取最终文档。'),
('15、在 Elasticsearch 中，是怎么根据一个词找到对应的倒排索引的？', '通过词典结构定位词项，再读取对应倒排列表；词典常用 Trie/FST 等结构压缩。'),
('16、Elasticsearch 在部署时，对 Linux 的设置有哪些优化方法？', '选择足够内存和多核 CPU、优先 SSD、避免跨数据中心；禁用交换，堆不超过 32GB，提高文件描述符并谨慎调整 GC/线程池。'),
('17、对于 GC 方面，在使用 Elasticsearch 时要注意什么？', '倒排词典常驻内存；监控 segment 与缓存，避免超大结果集和聚合；结合实际场景监控 heap，超大集群可拆分。'),
('18、Elasticsearch 对于大数据量（上亿量级）的聚合如何实现？', '可使用 cardinality 等近似聚合，估算字段基数以降低大规模聚合成本。'),
('19、在并发情况下，Elasticsearch 如果保证读写一致？', '使用版本号进行乐观并发控制；写一致性可设 quorum/one/all，读复制默认 sync。'),
('20、如何监控 Elasticsearch 集群状态？', '通过集群健康、节点、索引、分片和 JVM/GC 指标监控，并设置告警。'),
('21、介绍下你们电商搜索的整体技术架构。', '通常由数据采集/同步、索引构建、ES 集群、搜索服务、缓存与监控组成。'),
('22、介绍一下你们的个性化搜索方案？', '结合用户画像、行为和商品特征进行召回与排序，并通过离线/实时特征更新。'),
('23、是否了解字典树？', 'Trie 由字符路径组成，根到节点形成字符串，子节点字符不重复；适合前缀匹配和词典查询。'),
('24、拼写纠错是如何实现的？', '通常基于编辑距离生成候选词，可配合 BK 树按距离范围高效查找。'),
)
def upgrade() -> None:
    assert len(cards)==24
    cid=op.get_bind().execute(sa.text("SELECT category_id FROM exam_category WHERE name='Elasticsearch 面试题'")).scalar_one(); t=sa.table('exam_card',*[sa.column(x) for x in ('category_id','question','answer','key_points','tags','card_type','difficulty','status','sort_no','create_time','update_time')]); now=datetime.now()
    op.bulk_insert(t,[dict(category_id=cid,question=q,answer=a,key_points='',tags='Elasticsearch',card_type='concept',difficulty=3,status='published',sort_no=i,create_time=now,update_time=now) for i,(q,a) in enumerate(cards,1)])
def downgrade() -> None:
    cid=op.get_bind().execute(sa.text("SELECT category_id FROM exam_category WHERE name='Elasticsearch 面试题'")).scalar_one(); op.get_bind().execute(sa.text('DELETE FROM exam_card WHERE category_id=:cid AND sort_no BETWEEN 1 AND 24'),{'cid':cid})
