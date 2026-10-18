"""prepare Dubbo cards for review

Revision ID: 202610180017
Revises: 202610180016
"""

from alembic import op
import sqlalchemy as sa


revision = '202610180017'
down_revision = '202610180016'
branch_labels = None
depends_on = None


cards = (
    ('结论：Dubbo 是 Java 服务化场景的高性能 RPC 与服务治理框架。\n\n要点：封装远程调用、注册发现、负载均衡、容错、协议和序列化；调用方像调用本地接口一样调用远程服务；降低微服务间通信与治理的复杂度。\n\n补充：它解决的是服务间调用与治理，不替代数据库、消息队列或完整业务架构。', 'RPC 服务治理；注册发现；负载均衡；集群容错'),
    ('结论：Dubbo 从服务定义到网络传输分为十层，各层可通过 SPI 扩展。\n\n要点：Service 和 Config 定义服务；Proxy 生成代理；Registry 管理发现；Cluster 负责容错；Protocol、Exchange、Transport、Serialize 处理通信。\n\n补充：面试重点是理解调用链，不必机械背诵每层实现细节。', '十层架构；Proxy 代理；Registry 注册中心；Cluster 容错；Protocol 通信'),
    ('结论：Dubbo 默认常使用 Netty 作为底层通信框架。\n\n要点：Netty 基于 NIO，适合高并发网络通信；历史版本也可选 Mina；上层 RPC 逻辑与具体传输框架通过扩展点解耦。\n\n补充：具体默认值受 Dubbo 版本和配置影响，排查时应以运行配置为准。', 'Netty；NIO；Mina；传输层 SPI'),
    ('结论：Dubbo 的同步调用默认会等待结果，但可配置异步调用。\n\n要点：同步调用对业务代码直观；异步调用可先发请求、后通过 Future 获取结果；底层 NIO 允许多个请求并行处理。\n\n补充：异步不等于服务端一定更快，仍要处理超时、异常和线程上下文。', '默认同步；异步 Future；NIO 并行；超时异常'),
    ('结论：Dubbo 常配合 ZooKeeper 作为注册中心，现代项目也常使用 Nacos 等实现。\n\n要点：注册中心保存服务地址并向消费者推送变化；ZooKeeper 临时节点可感知提供者上下线；Redis、Multicast、Simple 多为历史或特定场景方案。\n\n补充：注册中心选型需结合高可用、运维能力和生态，不能只背“推荐 ZooKeeper”。', 'ZooKeeper 注册中心；服务发现；临时节点；Nacos 选型'),
    ('结论：序列化决定 RPC 参数和结果的编码效率与兼容性。\n\n要点：历史 Dubbo 常见 Hessian、Dubbo、Java 序列化等实现；应关注性能、跨语言、演进兼容和安全；具体可用实现取决于版本与配置。\n\n补充：不要反序列化不可信数据，Java 原生序列化通常不宜作为公网协议。', '序列化；Hessian；兼容性；反序列化安全'),
    ('结论：Dubbo 提供者失效感知通常依赖注册中心的临时节点与心跳。\n\n要点：Provider 注册临时节点；会话断开或心跳超时后节点被删除；注册中心通知 Consumer 更新地址列表。\n\n补充：这只能处理实例可达性，业务级故障仍需超时、重试和熔断策略。', '临时节点；心跳；服务下线；地址通知'),
    ('结论：服务上线兼容旧调用方应采用版本化和灰度发布，而非直接替换接口。\n\n要点：新旧版本可同时提供；消费者按 version 或路由选择；确认旧流量完成迁移后再下线旧版本。\n\n补充：接口字段演进也要保持向后兼容，避免只做服务端版本号而破坏序列化。', '多版本发布；灰度路由；兼容旧客户端；平滑下线'),
    ('结论：分布式调用链过长时，应通过链路追踪定位一次请求经过的服务。\n\n要点：在入口生成 traceId；跨服务传播上下文；采集耗时、错误与调用关系；Zipkin 是常见历史方案之一。\n\n补充：现代实现可用 SkyWalking、OpenTelemetry 等，关键是全链路关联而非具体产品。', '链路追踪；traceId；Zipkin；耗时与错误定位'),
    ('结论：Dubbo 核心配置覆盖服务暴露、引用、注册、协议与监控。\n\n要点：service 暴露服务，reference 引用服务，protocol 配置通信，registry 指定注册中心；application、provider、consumer、method 等补充全局与细粒度参数。\n\n补充：配置优先级和版本差异较多，生产排查需看最终生效配置。', 'service；reference；protocol；registry；配置优先级'),
    ('结论：Dubbo 协议是典型高性能 RPC 协议，但协议选择应服从互操作需求。\n\n要点：dubbo:// 适合 Dubbo Java 服务间调用；也可接入 HTTP、REST、Thrift、Hessian 等；不同协议在性能、跨语言和网关兼容性上取舍不同。\n\n补充：不要把历史协议列表当成所有版本的可用清单，应以当前版本文档为准。', 'dubbo 协议；RPC；跨语言；协议选型'),
    ('结论：Dubbo 支持点对点直连，绕过注册中心直接调用指定提供者。\n\n要点：可通过 URL 或配置指定服务地址；适合本地调试、故障隔离和临时验证；调用链不再依赖注册中心推送地址。\n\n补充：直连不适合长期生产配置，会绕过负载均衡和正常服务治理。', '点对点直连；绕过注册中心；调试；不宜长期使用'),
    ('结论：Dubbo 服务注册发现是 Provider 注册、Consumer 订阅、地址通知和负载调用的闭环。\n\n要点：Provider 启动后注册服务；Consumer 订阅并缓存地址；注册中心变更时推送通知；Consumer 按负载均衡选择实例。\n\n补充：消费者通常保留本地地址缓存，注册中心短暂不可用不应立刻中断所有调用。', 'Provider 注册；Consumer 订阅；地址通知；负载均衡'),
    ('结论：Dubbo 集群容错策略决定调用失败后的处理方式。\n\n要点：Failover 重试其他节点；Failfast 立即失败；Failsafe 忽略异常；Failback 后台重发；Forking 并发竞速；Broadcast 逐个调用。\n\n补充：重试必须考虑接口幂等性，写操作盲目 Failover 可能造成重复执行。', 'Failover；Failfast；Failsafe；Failback；幂等性'),
    ('结论：Dubbo 降级通过 Mock 在远程调用不可用时返回兜底结果或本地逻辑。\n\n要点：可配置 mock="return null" 等简单返回；也可实现接口对应的 Mock 类；常与超时、重试、限流和熔断组合。\n\n补充：降级结果要对业务可解释，不能把关键写操作静默伪装为成功。', 'Mock 降级；兜底返回；超时重试；关键写操作'),
    ('结论：Dubbo 常见故障应从服务暴露、注册中心连通性和消费者订阅三处排查。\n\n要点：找不到服务先看 Provider 是否成功暴露和注册；连接失败检查注册中心地址、网络与认证；调用异常再检查超时、路由和负载。\n\n补充：不要只依赖注解是否存在，应结合治理台、日志和注册中心实际节点确认。', '服务暴露；注册中心连通；消费者订阅；治理台排查'),
    ('结论：Dubbo Monitor 通过 Provider 与 Consumer 的 Filter 采集调用指标并聚合上报。\n\n要点：MonitorFilter 位于调用链；记录次数、耗时和异常；指标按时间窗口聚合后上报监控服务；再用于展示和告警。\n\n补充：历史 SimpleMonitor 实现已较旧，生产应接入统一指标与可观测性平台。', 'MonitorFilter；调用指标；时间聚合；监控告警'),
    ('结论：Dubbo 大量使用可扩展设计模式实现组件替换与调用编排。\n\n要点：SPI/工厂用于扩展加载；Filter 链体现责任链与装饰；注册订阅是观察者；代理层使用动态代理与自适应扩展。\n\n补充：回答设计模式要能对应到具体模块，避免只罗列模式名称。', 'SPI 工厂；Filter 责任链；观察者；动态代理'),
    ('结论：Dubbo XML 配置通过 Spring Schema 扩展解析为 Spring Bean。\n\n要点：Spring 读取 dubbo namespace；NamespaceHandler 接收标签；BeanDefinitionParser 将标签属性转换为 BeanDefinition；容器随后实例化配置对象。\n\n补充：Spring Boot 场景多改用注解或配置文件，但底层思路仍是将配置绑定为 Bean。', 'Spring Schema；NamespaceHandler；BeanDefinitionParser；配置转 Bean'),
    ('结论：Dubbo SPI 比 JDK SPI 更适合框架运行时按需扩展。\n\n要点：JDK SPI 往往一次加载全部实现；Dubbo SPI 支持按名称、按需延迟加载；还能提供 IOC、AOP 与 Adaptive 自适应扩展。\n\n补充：扩展点加载失败时要检查 SPI 描述文件路径和实现类依赖。', 'Dubbo SPI；延迟加载；Adaptive；IOC/AOP'),
    ('结论：Dubbo 本身不提供完整分布式事务语义，业务需选择合适的一致性方案。\n\n要点：跨服务事务可采用 TCC、Saga、可靠消息或本地事务表；不同方案在一致性、复杂度和补偿成本上取舍不同；RPC 成功不代表整个业务事务提交。\n\n补充：原题的“暂不支持”是历史表述，面试应强调业务一致性方案而非版本结论。', '分布式事务；TCC；Saga；可靠消息；补偿'),
    ('结论：Dubbo 可在服务引用侧启用结果缓存，适合稳定且可容忍短暂陈旧的数据。\n\n要点：缓存可减少重复远程调用；声明式配置能快速启用；需关注缓存键、过期、失效与一致性。\n\n补充：不能缓存强一致写后读、权限敏感或实时性很高的数据。', '结果缓存；声明式配置；缓存失效；一致性边界'),
    ('结论：服务升级兼容旧版本的核心是新旧服务并存、按版本路由和逐步迁移流量。\n\n要点：Provider 同时注册不同 version；Consumer 显式引用所需版本；旧客户端不受新接口影响；迁移完成再下线旧版本。\n\n补充：版本策略应覆盖接口、序列化字段和依赖服务，不只是 Dubbo 配置项。', 'version 路由；新旧并存；逐步迁移；接口兼容'),
    ('结论：Dubbo 运行必须依赖 Java 运行环境，其余组件依部署方式和功能选择。\n\n要点：JDK 提供运行时、网络与反射能力；注册中心、监控、Web 容器或 Spring 都可能是可选依赖；实际依赖以构建文件和当前版本为准。\n\n补充：面试不要照搬旧资料的 jar 列表，应说明“核心运行时 + 按功能引入扩展”。', 'JDK 运行时；可选组件；构建依赖；版本差异'),
    ('结论：Dubbo 的 telnet 命令用于服务运行后的诊断与管理。\n\n要点：可查看暴露服务和方法，如 ls；可辅助验证提供者是否正常启动；适合受控网络中的临时排障。\n\n补充：生产环境应限制管理端口访问，不要把 telnet 暴露给公网。', 'telnet 诊断；ls 服务列表；运行后验证；端口安全'),
    ('结论：Dubbo 支持通过 Mock 实现服务降级，避免依赖故障级联扩散。\n\n要点：可配置固定返回值或自定义 Mock 类；失败时切换到本地兜底；应结合超时、重试、限流和熔断形成完整策略。\n\n补充：降级必须监控触发率，并为恢复后的一致性补偿预留方案。', 'Mock 降级；本地兜底；防级联故障；触发监控'),
    ('结论：Dubbo 优雅停机应先停止接收新流量，再等待在途调用结束。\n\n要点：JVM ShutdownHook 可触发下线流程；Provider 从注册中心注销并等待请求完成；普通 kill 可触发 Hook，kill -9 无法执行清理。\n\n补充：容器编排环境还需设置足够的 termination grace period。', '优雅停机；ShutdownHook；注销服务；kill -9 不触发'),
    ('结论：Dubbox 是 Dubbo 历史停更时期的社区扩展分支，曾补充 REST 等能力。\n\n要点：它源于早期 Dubbo 维护变化；扩展了部分协议与开源组件；现代项目通常直接评估 Apache Dubbo 的当前版本。\n\n补充：这是历史知识点，选型不应再简单以 Dubbo 与 Dubbox 二选一。', 'Dubbox 历史分支；REST 扩展；Apache Dubbo；版本口径'),
    ('结论：Dubbo 偏高性能 RPC，Spring Cloud 是覆盖更广的微服务组件体系。\n\n要点：Dubbo 强调接口代理、二进制 RPC 与服务治理；Spring Cloud 常围绕 HTTP、注册、配置、网关和容错整合；两者可结合而非绝对替代。\n\n补充：不要用“Dubbo 性能一定更高、Spring Cloud 一定更稳定”作绝对结论，应看协议和实现。', 'Dubbo RPC；Spring Cloud 生态；HTTP；可组合使用'),
)


def upgrade() -> None:
    assert len(cards) == 29
    connection = op.get_bind()
    category_id = connection.execute(sa.text("SELECT category_id FROM exam_category WHERE name = 'Dubbo 面试题'")).scalar_one()
    for sort_no, (ai_summary, key_points) in enumerate(cards, 1):
        connection.execute(sa.text('UPDATE exam_card SET ai_summary=:ai_summary, key_points=:key_points, review_enabled=1 WHERE category_id=:category_id AND sort_no=:sort_no'), {'ai_summary': ai_summary, 'key_points': key_points, 'category_id': category_id, 'sort_no': sort_no})


def downgrade() -> None:
    connection = op.get_bind()
    category_id = connection.execute(sa.text("SELECT category_id FROM exam_category WHERE name = 'Dubbo 面试题'")).scalar_one()
    connection.execute(sa.text("UPDATE exam_card SET ai_summary='', key_points='', review_enabled=0 WHERE category_id=:category_id"), {'category_id': category_id})
