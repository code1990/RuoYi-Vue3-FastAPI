"""import Dubbo PDF chapter cards

Revision ID: 202610180006
Revises: 202610180005
"""

from datetime import datetime
from alembic import op
import sqlalchemy as sa

revision = '202610180006'
down_revision = '202610180005'
branch_labels = None
depends_on = None

cards = (
('1、为什么要用 Dubbo？', '服务化后服务调用、依赖、协议、序列化、发现和路由变复杂；Dubbo 将这些服务治理能力封装起来。', 'concept'),
('2、Dubbo 的整体架构设计有哪些分层?', 'Service、Config、Proxy、Registry、Cluster、Monitor、Protocol、Exchange、Transport、Serialize 十层。', 'enumeration'),
('3、默认使用的是什么通信框架，还有别的选择吗?', '默认且推荐 Netty，也可使用 Mina。', 'enumeration'),
('4、服务调用是阻塞的吗？', '默认阻塞，也可异步。Dubbo 基于 NIO 并行调用，异步调用返回 Future。', 'concept'),
('5、一般使用什么注册中心？还有别的选择吗？', '推荐 ZooKeeper；另有 Redis、Multicast、Simple，但不推荐。', 'enumeration'),
('6、默认使用什么序列化框架，你知道的还有哪些？', '推荐 Hessian；还有 Dubbo、FastJson、Java 自带序列化。', 'enumeration'),
('7、服务提供者能实现失效踢出是什么原理？', '基于 ZooKeeper 临时节点原理。', 'concept'),
('8、服务上线怎么不影响旧版本？', '采用多版本开发。', 'scenario'),
('9、如何解决服务调用链过长的问题？', '结合 Zipkin 实现分布式服务追踪。', 'scenario'),
('10、说说核心的配置有哪些？', 'dubbo:service、reference、protocol、application、module、registry、monitor、provider、consumer、method、argument。', 'enumeration'),
('11、Dubbo 推荐用什么协议？', '推荐 dubbo://；还支持 rmi、hessian、http、webservice、thrift、memcached、redis、rest。', 'enumeration'),
('12、同一个服务多个注册的情况下可以直连某一个服务吗？', '可以点对点直连，修改配置或通过 telnet 直连。', 'scenario'),
('13、画一画服务注册与发现的流程图？', 'Provider 启动时向注册中心注册；Consumer 订阅服务并获取地址列表；Consumer 按负载均衡调用 Provider；注册中心变更时通知 Consumer。', 'concept'),
('14、Dubbo 集群容错有几种方案？', 'Failover（默认重试）、Failfast（立即报错）、Failsafe（忽略异常）、Failback（定时重发）、Forking（并行一个成功即返）、Broadcast（逐个调用）。', 'enumeration'),
('15、Dubbo 服务降级，失败重试怎么做？', '在 dubbo:reference 设置 mock="return null"，或 mock=true 后编写“接口名+Mock”类实现降级逻辑。', 'scenario'),
('16、Dubbo 使用过程中都遇到了些什么问题？', '找不到服务时检查实现类是否有 @Service；连接不到注册中心时检查配置中的地址。', 'scenario'),
('17、Dubbo Monitor 实现原理？', 'Consumer 和 Provider 的 Filter 链均有 MonitorFilter；其发送统计给 DubboMonitor，默认按分钟聚合并定时发给 SimpleMonitorService，后者写队列、日志并定时绘图。', 'concept'),
('18、Dubbo 用到哪些设计模式？', '工厂模式（SPI 扩展）、装饰器/责任链（Filter 链）、观察者（注册订阅通知）、动态代理（Adaptive 扩展）。', 'enumeration'),
('19、Dubbo 配置文件是如何加载到 Spring 中的？', 'Spring 启动读取默认和 Dubbo Schema；Schema 对应 NamespaceHandler，经 BeanDefinitionParser 解析为 Bean。', 'concept'),
('20、Dubbo SPI 和 Java SPI 区别？', 'JDK SPI 一次加载全部扩展，可能浪费资源；Dubbo SPI 支持不改源码扩展、按需延迟加载、IOC/AOP 及 Spring Bean。', 'comparison'),
('21、Dubbo 支持分布式事务吗？', '原文称暂不支持，可结合 tcc-transaction 等 TCC 补偿事务框架。', 'concept'),
('22、Dubbo 可以对结果进行缓存吗？', '支持声明式缓存：<dubbo:reference cache="true" />。', 'scenario'),
('23、服务上线怎么兼容旧版本？', '用 version 过渡；不同版本服务同时注册，版本不同的服务互不引用。', 'scenario'),
('24、Dubbo 必须依赖的包有哪些？', '必须依赖 JDK，其他为可选。', 'concept'),
('25、Dubbo telnet 命令能做什么？', '服务发布后可用 telnet 调试和管理；如 ls 查看服务和方法列表。', 'scenario'),
('26、Dubbo 支持服务降级吗？', '支持：reference 配置 mock="return null"，或 mock=true 配合接口名+Mock 类。', 'scenario'),
('27、Dubbo 如何优雅停机？', '通过 JDK ShutdownHook；kill PID 可触发，kill -9 不会触发。', 'concept'),
('28、Dubbo 和 Dubbox 之间的区别？', 'Dubbox 是 Dubbo 停止维护后，当当网的扩展项目，增加 REST 调用并更新开源组件。', 'comparison'),
('29、Dubbo 和 Spring Cloud 的区别？', 'Dubbo 主要是 RPC 服务治理，组件选择自由；Spring Cloud 基于 REST 并整合注册、网关、断路器、配置、追踪等组件，兼容性与稳定性更强。', 'comparison'),
)

def upgrade() -> None:
    assert len(cards) == 29
    category_id = op.get_bind().execute(sa.text("SELECT category_id FROM exam_category WHERE name='Dubbo 面试题'")).scalar_one()
    table = sa.table('exam_card', sa.column('category_id'), sa.column('question'), sa.column('answer'), sa.column('key_points'), sa.column('tags'), sa.column('card_type'), sa.column('difficulty'), sa.column('status'), sa.column('sort_no'), sa.column('create_time'), sa.column('update_time'))
    now = datetime.now()
    op.bulk_insert(table, [dict(category_id=category_id, question=q, answer=a, key_points='', tags='Dubbo', card_type=t, difficulty=3, status='published', sort_no=i, create_time=now, update_time=now) for i, (q, a, t) in enumerate(cards, 1)])

def downgrade() -> None:
    category_id = op.get_bind().execute(sa.text("SELECT category_id FROM exam_category WHERE name='Dubbo 面试题'")).scalar_one()
    op.get_bind().execute(sa.text('DELETE FROM exam_card WHERE category_id=:category_id AND sort_no BETWEEN 1 AND 29'), {'category_id': category_id})
