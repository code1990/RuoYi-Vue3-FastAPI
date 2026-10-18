"""import ZooKeeper PDF chapter cards

Revision ID: 202610180005
Revises: 202610180004
"""

from datetime import datetime

from alembic import op
import sqlalchemy as sa


revision = '202610180005'
down_revision = '202610180004'
branch_labels = None
depends_on = None


cards = (
    ('1. ZooKeeper 面试题？', 'ZooKeeper 是开源分布式协调服务，可用于数据发布/订阅、负载均衡、命名服务、分布式协调/通知、集群管理、Master 选举、分布式锁和队列。它保证顺序一致性、原子性、单一视图、可靠性与最终一致性；更新有全局有序的 zxid。', 'concept'),
    ('2. ZooKeeper 提供了什么？', '提供文件系统和通知机制。', 'enumeration'),
    ('3. Zookeeper 文件系统', '提供多层级 znode 命名空间；所有节点都可关联数据。为高吞吐、低延迟在内存维护树状目录，因此不适合大数据存储，单节点数据上限为 1M。', 'concept'),
    ('4. ZAB 协议？', 'ZAB 是 ZooKeeper 专用的支持崩溃恢复的原子广播协议，包含崩溃恢复和消息广播两种模式。集群无可用 Leader 时先选举、同步；过半节点完成同步后进入消息广播，由 Leader 处理事务提案。', 'concept'),
    ('5. 四种类型的数据节点 Znode', 'PERSISTENT：手动删除前永久存在；EPHEMERAL：会话失效即删除；PERSISTENT_SEQUENTIAL：持久节点加父节点维护的自增序号；EPHEMERAL_SEQUENTIAL：临时节点加自增序号。', 'enumeration'),
    ('6. Zookeeper Watcher 机制 -- 数据变更通知', '客户端可在 Znode 注册 Watcher，指定事件发生后服务端向客户端发送通知。流程为客户端注册、服务端处理、客户端回调。Watcher 一次性、客户端串行执行、通知轻量；注册使用 getData/exists/getChildren，触发事件为 create/delete/setData。', 'concept'),
    ('7. 客户端注册 Watcher 实现', '调用 getData()/getChildren()/exist() 传入 Watcher；请求封装到 WatchRegistration 和 Packet 发往服务端；收到响应后注册到 ZKWatcherManager，完成注册。', 'scenario'),
    ('8. 服务端处理 Watcher 实现', '服务端接收请求后将节点路径和 ServerCnxn 存入 WatcherManager。事件触发时封装 WatchedEvent、按路径查询 Watcher，提取并删除对应 Watcher，再通过 ServerCnxn 的 TCP 连接调用 process 发送通知。', 'scenario'),
    ('9. 客户端回调 Watcher', '客户端 SendThread 接收事件通知，交由 EventThread 回调 Watcher。客户端 Watcher 同样是一次性的，触发后即失效。', 'concept'),
    ('10. ACL 权限控制机制', 'ACL 包含权限模式、授权对象和权限。模式包括 IP、Digest、World、Super；权限包括 CREATE、DELETE、READ、WRITE、ADMIN。UGO 是 Linux/Unix 常用的粗粒度权限控制方式。', 'enumeration'),
    ('11. Chroot 特性', '3.2.0 后支持。客户端可设置自己的命名空间，后续服务端操作被限制在该空间；适合多个应用共享一个 ZooKeeper 集群时做隔离。', 'concept'),
    ('12. 会话管理', '采用分桶策略管理会话，按下次超时时间分组。ExpirationTime_ = currentTime + sessionTimeout；ExpirationTime = (ExpirationTime_ / ExpirationInterval + 1) * ExpirationInterval，其中 ExpirationInterval 默认是 tickTime。', 'concept'),
    ('13. 服务器角色', 'Leader 是事务请求唯一调度和处理者；Follower 处理非事务请求、转发事务请求并参与投票和选举；Observer 处理非事务请求并转发事务请求，但不参与投票。', 'comparison'),
    ('14. Zookeeper 下 Server 工作状态', 'LOOKING：寻找 Leader；FOLLOWING：Follower；LEADING：Leader；OBSERVING：Observer。', 'enumeration'),
    ('15. 数据同步', 'Leader 选举完成后 Learner（Follower、Observer）向 Leader 注册，经历数据同步和同步确认。同步包括 DIFF、TRUNC+DIFF、TRUNC、SNAP：根据 Learner 的 peerLastZxid 与 Leader committedLog 的范围选择。', 'concept'),
    ('16. zookeeper 是如何保证事务的顺序一致性的？', '使用全局递增事务 ID zxid。zxid 高 32 位为 Leader 周期 epoch，低 32 位递增计数；Proposal 带 zxid，Leader 向其他服务器发起事务请求，超过半数成功后执行。', 'concept'),
    ('17. 分布式集群中为什么会有 Master？', '部分业务逻辑只需一台机器执行，其他机器共享结果，以减少重复计算、提高性能，因此需要通过 Leader 选举产生 Master。', 'concept'),
    ('18. zk 节点宕机如何处理？', '推荐不少于 3 台。Follower 宕机时其余节点继续服务，副本数据不丢失；Leader 宕机时重新选举。只要超过半数节点正常即可服务：3 节点可挂 1 台，2 节点不能挂任一台。', 'scenario'),
    ('19. zookeeper 负载均衡和 nginx 负载均衡区别', 'ZooKeeper 负载均衡可调控；Nginx 主要调权重，更多控制需插件。Nginx 吞吐量更大，应按业务选择。', 'comparison'),
    ('20. Zookeeper 有哪几种几种部署模式？', '单机模式、伪集群模式、集群模式。', 'enumeration'),
    ('21. 集群最少要几台机器，集群规则是怎样的?', '规则为 2N+1（N>0），最少 3 台。', 'concept'),
    ('22. 集群支持动态添加机器吗？', '可通过全部重启或逐个重启扩容；逐个重启在过半存活原则下不影响服务，是常用方式。3.5 版本开始支持动态扩容。', 'scenario'),
    ('23. Zookeeper 对节点的 watch 监听通知是永久的吗？为什么\n不是永久的?', '不是。Watch 是一次性触发器，节点变化后服务端通知客户端即失效。若永久且服务端频繁变动、客户端很多，会给网络和服务器带来很大压力；客户端通常只需最新数据。', 'concept'),
    ('24. Zookeeper 的 java 客户端都有哪些？', 'ZooKeeper 自带客户端、ZkClient 与 Apache Curator。', 'enumeration'),
    ('25. chubby 是什么，和 zookeeper 比你怎么看？', 'Chubby 是 Google 的、完整实现 Paxos 的非开源系统；ZooKeeper 可视为其开源实现，使用 ZAB 协议，是 Paxos 的变种。', 'comparison'),
    ('26. 说几个 zookeeper 常用的命令。', 'ls、get、set、create、delete 等。', 'enumeration'),
    ('27. ZAB 和 Paxos 算法的联系与区别？', '两者都有 Leader 协调 Follower，Leader 等待超过半数正确反馈后提交 Proposal，均有标识 Leader 周期的值（ZAB 的 epoch、Paxos 的 Ballot）。ZAB 用于构建 ZooKeeper 这类高可用主备系统；Paxos 用于构建分布式一致性状态机。', 'comparison'),
    ('28. Zookeeper 的典型应用场景', '典型场景：数据发布/订阅（配置中心）、负载均衡、命名服务、分布式协调/通知、集群管理、Master 选举、分布式锁、分布式队列。可利用 znode 和 Watcher 进行配置动态更新、机器上下线通知与临时顺序节点选主。', 'scenario'),
)


def upgrade() -> None:
    assert len(cards) == 28
    connection = op.get_bind()
    category_id = connection.execute(sa.text("SELECT category_id FROM exam_category WHERE name='ZooKeeper 面试题'")).scalar_one()
    table = sa.table('exam_card', sa.column('category_id'), sa.column('question'), sa.column('answer'), sa.column('key_points'), sa.column('tags'), sa.column('card_type'), sa.column('difficulty'), sa.column('status'), sa.column('sort_no'), sa.column('create_time'), sa.column('update_time'))
    now = datetime.now()
    op.bulk_insert(table, [dict(category_id=category_id, question=question, answer=answer, key_points='', tags='ZooKeeper', card_type=card_type, difficulty=3, status='published', sort_no=index, create_time=now, update_time=now) for index, (question, answer, card_type) in enumerate(cards, 1)])


def downgrade() -> None:
    category_id = op.get_bind().execute(sa.text("SELECT category_id FROM exam_category WHERE name='ZooKeeper 面试题'")).scalar_one()
    op.get_bind().execute(sa.text('DELETE FROM exam_card WHERE category_id=:category_id AND sort_no BETWEEN 1 AND 28'), {'category_id': category_id})
