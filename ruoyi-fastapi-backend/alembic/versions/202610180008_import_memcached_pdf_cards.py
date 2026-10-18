"""import Memcached cards
Revision ID: 202610180008
Revises: 202610180007
"""
from datetime import datetime
from alembic import op
import sqlalchemy as sa
revision='202610180008'; down_revision='202610180007'; branch_labels=None; depends_on=None
titles=('Memcached 是什么，有什么作用？','Memcached 服务分布式集群如何实现？','Memcached 服务特点及工作原理是什么？','简述 Memcached 内存管理机制原理？','memcached 是怎么工作的？','memcached 最大的优势是什么？','memcached 和 MySQL 的 query','memcached 和服务器的 local cache（比如 PHP 的 APC、）','memcached 的 cache 机制是怎样的？','memcached 如何实现冗余机制？','memcached 如何处理容错的？','如何将 memcached 中 item 批量导入导出？','如果缓存数据在导出导入之间过期了，您又怎么处理这些？','memcached 是如何做身份验证的？','memcached 的多线程是什么？如何使用它们？','memcached 能接受的 key 的最大长度是多少？','memcached 最大能存储多大的单个 item？','memcached 能够更有效地使用内存吗？','什么是二进制协议，我该关注吗？','memcached 的内存分配器是如何工作的？为什么不适用','memcached 是原子的吗？','如何实现集群中的 session 共享存储？','memcached 与 redis 的区别？')
answers=('高性能分布式内存对象缓存，用于减轻数据库压力、加速热点数据访问。','客户端通过一致性哈希选择节点，服务端本身不互相通信。','键值缓存，内存存储，基于 slab 分配与 LRU 淘汰。','Slab Allocation 将内存分为不同大小的 slab class，减少碎片。','客户端按 key 定位节点，命中直接返回，未命中回源并写入缓存。','简单、高性能、水平扩展容易。','MySQL 是持久化数据源；Memcached 用于缓存查询结果。','Local cache 更快但各节点不一致；Memcached 可共享缓存。','缓存有过期时间；空间不足时按 LRU 淘汰。','原生不复制，通常由客户端一致性哈希或多副本实现。','节点故障时客户端摘除节点并重哈希，必要时回源数据库。','可用工具或自定义脚本遍历导出再导入。','过期数据应视为失效，重新回源生成。','原生协议不提供完善身份验证，应放内网并通过网络隔离保护。','多线程用于网络 IO，缓存操作通过锁保证并发安全。','最大 250 字节。','默认最大 1MB，可通过配置调整。','合理设置 slab class、过期策略和内存上限以降低浪费。','更高效、更易解析的协议，按客户端能力选择。','Slab 分配器预分配固定大小块，避免频繁 malloc/free 和碎片。','单个命令是原子的，但多命令组合不是事务。','可用粘性 session、session 复制、共享 session 或持久化 session。','Redis 支持更多数据结构和持久化；Memcached 仅内存 KV、无持久化，使用 slab。')
def upgrade():
 assert len(titles)==len(answers)==23
 cid=op.get_bind().execute(sa.text("SELECT category_id FROM exam_category WHERE name='Memcached 面试题'")).scalar_one(); t=sa.table('exam_card',*[sa.column(x) for x in ('category_id','question','answer','key_points','tags','card_type','difficulty','status','sort_no','create_time','update_time')]); now=datetime.now(); op.bulk_insert(t,[dict(category_id=cid,question=f'{i}、{q}',answer=a,key_points='',tags='Memcached',card_type='concept',difficulty=3,status='published',sort_no=i,create_time=now,update_time=now) for i,(q,a) in enumerate(zip(titles,answers),1)])
def downgrade():
 cid=op.get_bind().execute(sa.text("SELECT category_id FROM exam_category WHERE name='Memcached 面试题'")).scalar_one();op.get_bind().execute(sa.text('DELETE FROM exam_card WHERE category_id=:cid'),{'cid':cid})
