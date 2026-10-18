"""prepare ZooKeeper cards for review

Revision ID: 202610180016
Revises: 202610180015
"""

from alembic import op
import sqlalchemy as sa


revision = '202610180016'
down_revision = '202610180015'
branch_labels = None
depends_on = None


cards = (
    ('结论：ZooKeeper 是面向分布式系统的协调服务，不是通用数据库。\n\n要点：提供命名、配置发布、集群管理、选主、分布式锁和队列；通过 znode、Watcher 和 zxid 协调状态；保障顺序一致性、原子性、单一视图、可靠性与最终一致性。\n\n补充：适合少量协调数据与通知，不适合存储大对象或高吞吐业务数据。', '分布式协调服务；znode 与 Watcher；zxid 全局有序；不适合大数据存储'),
    ('结论：ZooKeeper 的核心能力是分层 znode 文件系统和一次性事件通知。\n\n要点：znode 组织协调数据与服务实例；客户端可读取、创建、删除节点；Watcher 在节点变化时异步通知客户端。\n\n补充：文件系统解决状态存放，通知机制解决状态变化感知，两者组合支撑协调场景。', 'znode 文件系统；Watcher 通知；状态存放；状态变化感知'),
    ('结论：ZooKeeper 文件系统是内存中的分层 znode 树，强调低延迟协调而非大文件存储。\n\n要点：每个 znode 可保存数据并拥有子节点；层级结构便于命名和组织；数据常驻内存以换取高吞吐、低延迟。\n\n补充：单节点数据通常限制为 1MB，不能把它当作文件服务或业务数据库。', '分层 znode 树；内存存储；低延迟协调；单节点约 1MB'),
    ('结论：ZAB 是 ZooKeeper 保证高可用和事务顺序的原子广播协议。\n\n要点：系统分为崩溃恢复与消息广播两阶段；无 Leader 时先选举并同步数据；Leader 提交 Proposal 前需获得过半确认。\n\n补充：它服务于主备协调场景，不应笼统等同于通用共识算法实现。', 'ZAB 原子广播；崩溃恢复；消息广播；过半确认'),
    ('结论：znode 的类型由持久性和是否自动编号两维决定。\n\n要点：PERSISTENT 需手动删除；EPHEMERAL 随会话失效删除；SEQUENTIAL 会追加单调递增序号；两种维度可组合。\n\n补充：临时顺序节点常用于服务发现、分布式锁和 Leader 选举。', '持久节点；临时节点；顺序节点；临时顺序节点'),
    ('结论：Watcher 是一次性、轻量级的变更通知机制。\n\n要点：客户端在 getData、exists 或 getChildren 时注册；节点创建、删除或数据变更触发通知；回调由客户端串行处理，触发后需重新注册。\n\n补充：Watcher 只提示变化，不携带完整状态，收到通知后通常应重新读取数据。', '一次性触发；需重新注册；轻量通知；客户端串行回调'),
    ('结论：客户端注册 Watcher 本质是在读请求中附带监听器并在本地保存映射。\n\n要点：getData、getChildren、exists 可传入 Watcher；请求经 WatchRegistration 和 Packet 发往服务端；响应后由 ZKWatcherManager 管理本地监听器。\n\n补充：注册成功不代表永久有效，事件触发一次后监听关系即被移除。', '读请求注册；WatchRegistration；ZKWatcherManager；一次性监听'),
    ('结论：服务端通过 WatcherManager 按路径保存连接，并在事件发生时投递通知。\n\n要点：注册时保存节点路径和 ServerCnxn；触发时构造 WatchedEvent；按路径取出并删除 Watcher，再通过 TCP 连接发送。\n\n补充：删除监听器体现 Watcher 一次性语义，也避免重复通知。', 'WatcherManager；路径到连接；WatchedEvent；触发后删除'),
    ('结论：客户端收到事件后由网络线程转交事件线程执行回调。\n\n要点：SendThread 接收服务端通知；EventThread 调用业务 Watcher；回调是异步且串行的；触发过的 Watcher 自动失效。\n\n补充：回调中应避免耗时操作，以免阻塞后续事件处理。', 'SendThread；EventThread；异步串行；回调避免耗时'),
    ('结论：ZooKeeper ACL 以“模式 + 身份 + 权限”控制 znode 访问。\n\n要点：认证模式有 IP、Digest、World、Super；权限包含 CREATE、DELETE、READ、WRITE、ADMIN；可按节点配置不同 ACL。\n\n补充：World 相当于开放访问，生产环境应谨慎使用并优先最小权限。', 'ACL 三要素；IP/Digest/World/Super；CRUD 管理权限；最小权限'),
    ('结论：Chroot 为客户端提供逻辑命名空间隔离。\n\n要点：客户端连接串指定根路径；后续操作自动限制在该子树；不同应用可共享同一 ZooKeeper 集群。\n\n补充：Chroot 只隔离路径视图，不替代 ACL 等访问控制。', 'Chroot 命名空间；路径隔离；共享集群；不替代 ACL'),
    ('结论：ZooKeeper 通过按超时时间分桶的策略高效管理大量会话。\n\n要点：会话按下一次过期时间归类；过期时间向 tickTime 对齐；服务端按桶批量扫描与失效处理。\n\n补充：tickTime 是时间粒度，实际过期通常不是精确到客户端设置的毫秒时刻。', '会话分桶；tickTime；过期时间对齐；批量失效'),
    ('结论：Leader 负责事务顺序，Follower 参与投票，Observer 扩展读能力但不影响法定人数。\n\n要点：Leader 是事务唯一调度者；Follower 处理读请求并转发写请求、参与选举；Observer 也可处理读和转发写，但不投票。\n\n补充：Observer 适合跨机房或读压力扩展，不能提高写事务的多数派能力。', 'Leader 事务调度；Follower 投票；Observer 不投票；多数派'),
    ('结论：LOOKING、FOLLOWING、LEADING、OBSERVING 表示服务器在选举或集群中的角色状态。\n\n要点：LOOKING 正在寻找 Leader；FOLLOWING 是跟随者；LEADING 是当前主节点；OBSERVING 是不参与投票的观察者。\n\n补充：排障时先看节点状态，可快速判断是否发生选主或角色异常。', 'LOOKING 选主；FOLLOWING 跟随；LEADING 主节点；OBSERVING 观察者'),
    ('结论：Leader 选举完成后，Learner 必须先同步到一致状态再对外服务。\n\n要点：Follower 和 Observer 作为 Learner 向 Leader 注册；同步策略含 DIFF、TRUNC、TRUNC+DIFF、SNAP；选择取决于 peerLastZxid 与事务日志范围。\n\n补充：日志差距小优先增量同步，差距大或无法衔接时使用快照。', 'Learner 同步；DIFF 增量；TRUNC 截断；SNAP 快照'),
    ('结论：ZooKeeper 使用单调递增 zxid 和多数派提交保证事务全局顺序。\n\n要点：zxid 高位是 Leader epoch，低位为递增计数；Leader 为 Proposal 分配 zxid；过半节点确认后才提交与应用。\n\n补充：zxid 反映事务先后，不等同于业务时间戳。', 'zxid 全局递增；epoch；Proposal；过半提交'),
    ('结论：分布式系统设置 Master 是为让只能执行一次的任务有唯一执行者。\n\n要点：多个节点重复执行会浪费资源或产生冲突；通过 Leader 选举选出 Master；其余节点共享执行结果或作为备份。\n\n补充：必须处理 Master 宕机后的重新选举与幂等，避免任务被重复执行。', '唯一执行者；Leader 选举；共享结果；故障切换'),
    ('结论：ZooKeeper 集群依赖多数派存活，部署应使用奇数台并至少三台。\n\n要点：Follower 宕机不影响其余节点服务；Leader 宕机会重新选举；3 台可容忍 1 台故障，2 台任意宕一台即失去多数派。\n\n补充：节点数增加提升容错但也增加写确认成本，常用 3 或 5 台。', '多数派存活；至少 3 台；Leader 重选；奇数节点'),
    ('结论：ZooKeeper 与 Nginx 的负载均衡定位不同，不能简单替代。\n\n要点：ZooKeeper 更常做服务发现与动态协调；Nginx 直接承载流量转发并可配置权重；Nginx 通常拥有更高的数据面吞吐。\n\n补充：常见组合是 ZooKeeper 管理服务实例，Nginx 或客户端负责实际请求分发。', '服务发现；流量转发；Nginx 高吞吐；可组合使用'),
    ('结论：ZooKeeper 支持单机、伪集群和正式集群三种常见部署方式。\n\n要点：单机用于本地开发；伪集群在一台机器模拟多个实例；集群部署多个独立节点以获得高可用。\n\n补充：生产环境应使用奇数节点的正式集群，伪集群不能验证真实网络故障。', '单机开发；伪集群测试；正式集群；生产高可用'),
    ('结论：ZooKeeper 正式集群最少 3 台，遵循 2N+1 的奇数节点原则。\n\n要点：写事务和选主都需要超过半数；3 台多数派为 2；可容忍 1 台宕机；2 台集群不能容忍任意一台故障。\n\n补充：5 台可容忍 2 台故障，但并不意味着节点越多越适合。', '2N+1；最少 3 台；多数派；3 台容忍 1 台'),
    ('结论：ZooKeeper 扩容可通过滚动重启完成，新版本还支持动态重配置。\n\n要点：全量重启简单但会中断服务；逐台重启时要始终保留多数派；3.5 起支持动态扩容能力。\n\n补充：扩容前应评估成员变更过程中的多数派，避免同时下线过多节点。', '滚动重启；保留多数派；动态重配置；3.5+'),
    ('结论：Watch 不是永久订阅，而是一次性触发器。\n\n要点：节点变化后服务端通知并移除 Watch；永久监听在高频变更和大量客户端下会造成网络与服务端压力；客户端通常只需获知最新状态。\n\n补充：需要持续监听时，业务应在回调后重新读取并注册 Watch。', '一次性 Watch；触发即失效；回调后重注册；避免通知风暴'),
    ('结论：Java 生态常用 ZooKeeper 原生客户端、ZkClient 和 Apache Curator。\n\n要点：原生客户端贴近协议但使用较繁琐；ZkClient 简化连接与监听；Curator 提供更成熟的重试、选举、锁和缓存封装。\n\n补充：业务开发通常优先 Curator，仍需理解会话失效与 Watch 一次性语义。', '原生客户端；ZkClient；Curator；重试与封装'),
    ('结论：Chubby 是 Google 的分布式锁服务，ZooKeeper 是开源的分布式协调服务。\n\n要点：Chubby 使用 Paxos 且未开源；ZooKeeper 使用 ZAB；两者都面向协调、选主和一致性状态管理。\n\n补充：不能说 ZooKeeper 是 Chubby 的完整开源实现，它们在协议和工程设计上不同。', 'Chubby；Paxos；ZooKeeper；ZAB 协议'),
    ('结论：ZooKeeper 常用命令围绕 znode 的查询、创建、修改和删除。\n\n要点：ls 查看子节点；get 读取数据；set 更新数据；create 创建节点；delete 删除节点。\n\n补充：生产环境操作前应先确认节点类型与版本，避免误删临时节点或覆盖配置。', 'ls；get；set；create；delete'),
    ('结论：ZAB 和 Paxos 都依赖多数派确认，但解决的问题与协议流程不同。\n\n要点：两者都有 Leader 协调和任期标识；ZAB 使用 epoch 与广播事务，服务于主备高可用；Paxos 使用 ballot 构建通用一致性状态机。\n\n补充：面试中应说明“相似的多数派思想”，不要直接断言两者完全相同。', '多数派确认；ZAB epoch；Paxos ballot；主备高可用'),
    ('结论：ZooKeeper 典型用于管理分布式系统中的小规模协调状态。\n\n要点：配置发布订阅、服务注册发现、负载均衡、集群管理、Master 选举、分布式锁和队列；常结合临时顺序节点与 Watcher；节点上下线可被及时感知。\n\n补充：它不是消息队列或关系数据库，应把业务大数据放在专用存储中。', '配置中心；服务发现；Master 选举；分布式锁；临时顺序节点'),
)


def upgrade() -> None:
    assert len(cards) == 28
    connection = op.get_bind()
    category_id = connection.execute(sa.text("SELECT category_id FROM exam_category WHERE name = 'ZooKeeper 面试题'")).scalar_one()
    for sort_no, (ai_summary, key_points) in enumerate(cards, 1):
        connection.execute(
            sa.text('UPDATE exam_card SET ai_summary = :ai_summary, key_points = :key_points, review_enabled = 1 WHERE category_id = :category_id AND sort_no = :sort_no'),
            {'ai_summary': ai_summary, 'key_points': key_points, 'category_id': category_id, 'sort_no': sort_no},
        )


def downgrade() -> None:
    connection = op.get_bind()
    category_id = connection.execute(sa.text("SELECT category_id FROM exam_category WHERE name = 'ZooKeeper 面试题'")).scalar_one()
    connection.execute(sa.text("UPDATE exam_card SET ai_summary = '', key_points = '', review_enabled = 0 WHERE category_id = :category_id"), {'category_id': category_id})
