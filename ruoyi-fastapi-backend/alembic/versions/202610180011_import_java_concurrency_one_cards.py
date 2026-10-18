"""import Java concurrency part one cards from the Java interview PDF

Revision ID: 202610180011
Revises: 202610180010
"""

from datetime import datetime

from alembic import op
import sqlalchemy as sa


revision = '202610180011'
down_revision = '202610180010'
branch_labels = None
depends_on = None


cards = (
    ('1、在 Java 中守护线程和用户线程区别？', '用户线程未结束时 JVM 不会退出；守护线程用于后台服务，所有用户线程结束后 JVM 可以退出，不应用它承载必须完成的业务。', 'comparison'),
    ('2、线程与进程的区别？', '进程是资源分配与隔离单位，线程是 CPU 调度单位。线程共享进程内存，创建和切换更轻，但同步与隔离更复杂。', 'comparison'),
    ('3、什么是多线程中的上下文切换？', 'CPU 保存当前线程状态并恢复另一线程状态的过程。频繁切换会消耗 CPU 缓存和调度开销，应控制线程数与任务粒度。', 'concept'),
    ('4、死锁、活锁与饥饿有什么区别？', '死锁是线程循环等待资源且永不前进；活锁是不断重试却无进展；饥饿是线程长期得不到运行或资源机会。', 'comparison'),
    ('5、Java 中用到的线程调度算法是什么？', 'Java 线程调度由操作系统决定，通常是抢占式、基于优先级的调度；优先级只是提示，不能依赖其保证顺序或公平性。', 'concept'),
    ('6、什么是线程组，为什么不推荐使用？', 'ThreadGroup 用于组织线程并批量管理，但 API 能力有限且易误用。现代程序使用 ExecutorService、结构化并发或应用自身的生命周期管理。', 'concept'),
    ('7、为什么使用 Executor 框架？', '它把任务提交与线程管理分离，支持复用线程、限制并发、排队、取消、监控和统一关闭，避免散落的 new Thread。', 'concept'),
    ('8、Executor 和 Executors 的区别？', 'Executor 是执行任务的接口；Executors 是创建常见 ExecutorService 的工具类。生产中通常显式构造 ThreadPoolExecutor 以配置队列、容量和拒绝策略。', 'comparison'),
    ('9、如何找出 Windows 和 Linux 上 CPU 使用时间最长的线程？', 'Linux 可用 top -H、ps -L 或 jstack 与线程 ID 对照；Windows 可用任务管理器、Process Explorer 或 jcmd/jstack。定位后结合线程栈和采样确认热点。', 'scenario'),
    ('10、什么是原子操作？Java 有哪些原子类？', '原子操作不可被其他线程观察到中间状态。java.util.concurrent.atomic 提供 AtomicInteger、AtomicLong、AtomicReference、数组和字段更新器等 CAS 工具。', 'concept'),
    ('11、Lock 接口是什么？相比 synchronized 有何优势？', 'Lock 提供显式 lock/unlock、tryLock、可中断获取和多个 Condition 等能力；synchronized 语法更简单且自动释放。两者均需正确处理可见性与异常。', 'comparison'),
    ('12、什么是 Executors 框架？', 'Executors 是创建 ExecutorService、ScheduledExecutorService 等执行器的工具类，封装固定、缓存、单线程和定时线程池等常见模式。', 'concept'),
    ('13、什么是阻塞队列？如何实现生产者消费者？', 'BlockingQueue 在队列空/满时阻塞取放操作。生产者 put，消费者 take；它封装等待通知，通常优于手写 wait/notify。', 'scenario'),
    ('14、什么是 Callable 和 Future？', 'Callable 表示可返回结果且可抛异常的任务；Future 表示异步计算结果，可 get、取消和查询状态。', 'comparison'),
    ('15、什么是 FutureTask？如何用 ExecutorService 启动？', 'FutureTask 同时实现 Runnable 和 Future，可包装 Callable 后由 executor.execute 或 submit 执行，并通过 get 获取结果。', 'scenario'),
    ('16、什么是并发容器？', '并发容器是为多线程访问设计的集合，例如 ConcurrentHashMap、ConcurrentLinkedQueue、CopyOnWriteArrayList 和 BlockingQueue，避免对整个集合粗粒度加锁。', 'concept'),
    ('17、多线程同步和互斥有哪些实现方式？', '可使用 synchronized、Lock/ReentrantLock、ReadWriteLock、Semaphore、原子类、并发容器和消息传递。应优先选择最小且清晰的同步范围。', 'enumeration'),
    ('18、什么是竞争条件？如何发现和解决？', '结果依赖线程交错执行时发生竞争条件。通过压测、线程分析和代码审查发现；通过不可变对象、封装共享状态、锁、原子操作或消息传递解决。', 'scenario'),
    ('19、如何使用和分析 thread dump？', '通过 jstack、jcmd Thread.print 或监控工具获取，重点检查 RUNNABLE 热点、BLOCKED 锁等待、WAITING/TIMED_WAITING、死锁以及相同栈的大量线程。', 'scenario'),
    ('20、为什么 start() 会执行 run()，不能直接调用 run()？', 'start() 创建并调度新线程，JVM 在新线程中调用 run()；直接调用 run() 只是当前线程的普通方法调用，不会产生并发。', 'concept'),
    ('21、如何唤醒阻塞线程？', '视阻塞原因而定：可 interrupt 支持中断的阻塞操作，使用条件变量 signal/notify，或关闭队列、Socket 等资源。不要使用已废弃的 stop。', 'scenario'),
    ('22、CyclicBarrier 和 CountDownLatch 有什么区别？', 'CountDownLatch 等待计数减到零，通常一次性；CyclicBarrier 让一组线程在屏障处互相等待，可复用，并可执行屏障动作。', 'comparison'),
    ('23、什么是不可变对象，对写并发有何帮助？', '状态创建后不可改变的对象是不可变对象。它天然线程安全，读共享无需锁，能显著减少同步和可见性问题。', 'concept'),
    ('24、什么是多线程中的上下文切换？', '上下文切换是调度器保存一个线程寄存器、栈等状态并恢复另一个线程状态的过程；过多切换会降低吞吐与尾延迟。', 'concept'),
    ('25、Java 中用到的线程调度算法是什么？', '线程调度由 JVM 所在操作系统实现，通常为抢占式调度；不要以 Thread 优先级构建正确性或公平性逻辑。', 'concept'),
    ('26、什么是线程组，为什么不推荐使用？', '线程组是早期批量管理机制，缺少可靠的生命周期和异常管理能力；线程池和任务执行器是更合适的替代方案。', 'concept'),
    ('27、为什么 Executor 框架比手工创建线程好？', '线程池可复用线程、控制并发和队列、统一异常处理与关闭，并提供定时、取消、监控等能力，避免无界创建线程耗尽资源。', 'concept'),
    ('28、Java 中有几种方法可以实现一个线程？', '可继承 Thread、实现 Runnable、实现 Callable 并提交给 ExecutorService；实践中优先使用 Runnable/Callable 与执行器，避免把任务与线程耦合。', 'enumeration'),
    ('29、如何停止一个正在运行的线程？', '使用协作式取消：设置中断标记或取消标志，任务定期检查并清理退出；阻塞操作应响应 InterruptedException 并恢复或结束。', 'scenario'),
    ('30、notify() 和 notifyAll() 有什么区别？', 'notify 随机唤醒一个等待同一监视器的线程；notifyAll 唤醒全部。存在多个等待条件时通常配合 while 使用 notifyAll 更安全。', 'comparison'),
    ('31、什么是 Daemon 线程？有什么意义？', '守护线程为用户线程提供后台服务，如垃圾回收。JVM 不等待守护线程完成，因此不应依赖其完成数据落盘、支付或释放关键资源。', 'concept'),
    ('32、Java 如何实现多线程之间的通信和协作？', '可用共享内存配合 synchronized、volatile、Lock/Condition、wait/notify，也可使用 BlockingQueue、Future、CountDownLatch 等高层并发工具。', 'enumeration'),
    ('33、什么是可重入锁 ReentrantLock？', '同一线程可重复获得同一把锁而不自我死锁，计数在相同次数 unlock 后归零。它支持公平锁、可中断获取和多个 Condition。', 'concept'),
    ('34、线程进入某对象的 synchronized 实例方法后，其他线程能进入该对象其他方法吗？', '不能进入该对象其他 synchronized 实例方法，因为它们共用同一对象监视器；可以进入未同步方法，静态 synchronized 则锁的是 Class 对象。', 'scenario'),
    ('35、乐观锁和悲观锁是什么？如何实现？', '悲观锁先获取互斥锁再修改，适合冲突高场景；乐观锁先读后以版本号或 CAS 提交，冲突时重试，适合读多写少。', 'comparison'),
    ('36、SynchronizedMap 和 ConcurrentHashMap 有什么区别？', 'SynchronizedMap 常以单一监视器保护整个 Map；ConcurrentHashMap 采用更细粒度并发控制与无锁读路径，吞吐更高，且迭代器弱一致。', 'comparison'),
    ('37、CopyOnWriteArrayList 适用于什么场景？', '适合读多写极少、迭代期间需要稳定快照的场景。每次写会复制底层数组，因此不适合大列表或高频写入。', 'scenario'),
    ('38、什么叫线程安全？Servlet 是线程安全吗？', '线程安全表示多个线程按任意交错访问仍满足正确性。Servlet 容器会并发调用同一实例，应避免保存请求相关的可变实例字段。', 'concept'),
    ('39、volatile 有什么用？应用场景？', 'volatile 保证单次读写的可见性和一定顺序，不保证复合操作原子性。适合状态标志、配置引用和安全发布，不适合 i++ 计数。', 'concept'),
    ('40、为什么代码会重排序？', '编译器和 CPU 为优化性能会在不改变单线程语义前提下重排指令；happens-before、volatile、锁和 final 字段规则约束跨线程可见顺序。', 'concept'),
    ('41、wait 和 sleep 有什么不同？', 'wait 必须持有监视器，释放锁并等待 notify/超时/中断；sleep 不释放锁，只暂停当前线程指定时间，且是 Thread 静态方法。', 'comparison'),
    ('42、如何用 Java 实现阻塞队列？', '生产环境直接使用 ArrayBlockingQueue 或 LinkedBlockingQueue。手写实现需用锁保护队列，并用两个 Condition 在空/满时 await 与 signal，且在循环中检查条件。', 'scenario'),
    ('43、线程运行时发生异常会怎样？', '未捕获异常会终止该线程并交给 UncaughtExceptionHandler；线程池任务的异常需从 Future.get 或统一异常处理器观察，不能静默丢失。', 'concept'),
    ('44、如何在两个线程间共享数据？', '将数据放在受同步保护的共享对象中，或通过 BlockingQueue、Future、CompletableFuture 等消息/结果通道传递；避免无保护的可变共享字段。', 'scenario'),
    ('45、Java 中 notify 和 notifyAll 有什么区别？', 'notify 唤醒一个等待者，notifyAll 唤醒全部等待者并竞争锁。二者都必须在持有同一监视器时调用，且等待端应使用 while。', 'comparison'),
    ('46、为什么 wait、notify 和 notifyAll 不在 Thread 类里？', '它们协调的是对象监视器和等待队列，而非某个线程自身；任何对象都能作为锁，因此方法定义在 Object。', 'concept'),
    ('47、什么是 ThreadLocal 变量？', 'ThreadLocal 为每个线程保存独立副本，常用于上下文和非线程安全对象隔离。在线程池中必须 remove，防止任务间泄漏和内存泄漏。', 'concept'),
    ('48、interrupted 和 isInterrupted 方法的区别？', 'Thread.interrupted() 是静态方法，检查当前线程并清除中断标志；isInterrupted() 检查指定线程且不清除标志。', 'comparison'),
    ('49、为什么 wait 和 notify 要在同步块中调用？', '必须持有对象监视器以原子地检查条件、释放锁并进入等待队列，避免通知丢失和竞态；否则会抛 IllegalMonitorStateException。', 'concept'),
    ('50、为什么应该在循环中检查等待条件？', '线程被唤醒后条件可能仍不成立，且允许伪唤醒。应使用 while (!condition) wait()，而不是 if。', 'concept'),
    ('51、同步集合与并发集合有什么区别？', '同步集合通常为每个操作加同一把锁，复合操作仍需外部同步；并发集合针对高并发设计，提供更细粒度控制、弱一致迭代或原子复合方法。', 'comparison'),
    ('52、什么是线程池？为什么使用它？', '线程池复用工作线程执行任务，减少创建开销，并通过核心数、最大数、队列和拒绝策略控制资源与背压。', 'concept'),
    ('53、怎么检测一个线程是否拥有锁？', '对 intrinsic lock 没有通用业务级检测 API；调试可用 Thread.holdsLock(object)，生产设计应避免依赖检测，使用清晰的锁所有权约定。', 'scenario'),
    ('54、如何获取线程堆栈？', '可使用 jstack、jcmd Thread.print、JFR、Java Flight Recorder 或 ThreadMXBean；线上优先使用低风险采样和可观测性工具。', 'scenario'),
    ('55、JVM 中哪个参数控制线程栈大小？', '使用 -Xss 设置每个线程的栈大小。值过小会 StackOverflowError，过大将限制可创建线程数，应结合调用深度和内存预算设置。', 'concept'),
    ('56、Thread 类中的 yield 方法有什么作用？', 'yield 提示调度器当前线程愿意让出 CPU，但没有任何保证；它不释放锁，也不应用于同步或正确性控制。', 'concept'),
    ('57、ConcurrentHashMap 的并发度是什么？', '旧实现用 concurrencyLevel 提示分段数；JDK 8+ 改为节点级 CAS 与 synchronized 等机制，该参数不应被视为实际并发上限。', 'concept'),
    ('58、Java 中 Semaphore 是什么？', 'Semaphore 以许可数限制并发访问，例如连接池或限流。acquire 获取许可，release 归还许可，可选择公平模式。', 'concept'),
    ('59、线程池中 submit 和 execute 有何区别？', 'execute 接收 Runnable 且异常交由线程的未捕获异常处理；submit 返回 Future，可提交 Runnable/Callable，任务异常通常在 Future.get 时得到。', 'comparison'),
    ('60、什么是阻塞式方法？', '阻塞方法在条件不满足时暂停当前线程，例如 Object.wait、Thread.sleep、BlockingQueue.take、Future.get 和 I/O。调用方需考虑超时、取消和线程池耗尽。', 'concept'),
    ('61、Java 中的 ReadWriteLock 是什么？', 'ReadWriteLock 将读锁与写锁分离，可允许多个读者并发而写者独占。读多写少时可能提高吞吐，简单场景不一定优于互斥锁。', 'concept'),
    ('62、volatile 变量和 atomic 变量有什么不同？', 'volatile 提供可见性与顺序保证，不提供读改写原子性；Atomic 类基于 CAS 支持原子更新，但复合不变量仍可能需要锁。', 'comparison'),
    ('63、可以直接调用 Thread 的 run 方法吗？', '可以，但它只在当前线程同步执行。要创建并发执行必须调用 start。', 'concept'),
    ('64、如何让正在运行的线程暂停一段时间？', '使用 Thread.sleep、ScheduledExecutorService 或定时器；若任务可取消，应正确处理 InterruptedException。不要使用 suspend/resume。', 'scenario'),
    ('65、如何理解线程优先级？', '优先级是调度提示，平台实现不同且可能被忽略。业务不能依赖优先级保证执行顺序，应通过同步与队列表达需求。', 'concept'),
    ('66、什么是线程调度器和时间分片？', '线程调度器选择可运行线程使用 CPU；时间分片为线程分配有限时间片以实现抢占和公平。具体策略由操作系统决定。', 'concept'),
    ('67、如何确保 main 所在线程是 Java 程序最后结束的线程？', '让 main 等待非守护工作线程完成，例如 Future.get、Thread.join、CountDownLatch.await，再关闭 ExecutorService；不要依赖 sleep。', 'scenario'),
    ('68、线程之间如何通信？', '可用共享状态加锁/条件变量，也可用 BlockingQueue、Future、CompletableFuture、CountDownLatch、CyclicBarrier 等并发工具进行协作。', 'enumeration'),
    ('69、为什么线程通信方法定义在 Object 类里？', '等待与通知针对对象监视器及其等待队列，任何对象都可充当监视器，因此方法属于 Object 而非 Thread。', 'concept'),
    ('70、为什么 wait、notify、notifyAll 必须在同步方法或同步块中调用？', '调用者必须拥有对应对象监视器，确保条件检查和等待/通知协调正确；否则 JVM 抛 IllegalMonitorStateException。', 'concept'),
    ('71、为什么 Thread 的 sleep 和 yield 是静态方法？', '它们作用于当前正在执行的线程，而不是某个任意 Thread 对象；声明为静态方法可避免误以为能暂停或让出其他线程。', 'concept'),
    ('72、如何确保线程安全？', '优先无共享状态与不可变对象；必须共享时封装状态，并用锁、原子类、volatile 或并发容器建立正确 happens-before 关系；通过压测和代码审查验证。', 'scenario'),
    ('73、同步方法和同步块，哪个更好？', '同步块可精确缩小锁定范围并指定锁对象，通常更灵活；同步方法更简洁且适用于整个方法都需同一把锁的情况。正确性优先于形式。', 'comparison'),
    ('74、如何创建守护线程？', '在线程 start 前调用 setDaemon(true)。守护线程可能因 JVM 退出被直接终止，因此应避免用于关键任务。', 'scenario'),
    ('75、什么是 Java Timer 类？如何创建定时任务？', 'Timer 可按固定延迟或固定频率执行 TimerTask，但单线程且异常会影响后续任务。现代应用优先使用 ScheduledExecutorService。', 'concept'),
)


def upgrade() -> None:
    assert len(cards) == 75
    category_id = op.get_bind().execute(sa.text("SELECT category_id FROM exam_category WHERE name='Java 并发编程（一）'")).scalar_one()
    table = sa.table('exam_card', *[sa.column(column) for column in ('category_id', 'question', 'answer', 'key_points', 'tags', 'card_type', 'difficulty', 'status', 'sort_no', 'create_time', 'update_time')])
    now = datetime.now()
    op.bulk_insert(table, [dict(category_id=category_id, question=question, answer=answer, key_points='', tags='Java,并发编程', card_type=card_type, difficulty=3, status='published', sort_no=index, create_time=now, update_time=now) for index, (question, answer, card_type) in enumerate(cards, 1)])


def downgrade() -> None:
    category_id = op.get_bind().execute(sa.text("SELECT category_id FROM exam_category WHERE name='Java 并发编程（一）'")).scalar_one()
    op.get_bind().execute(sa.text('DELETE FROM exam_card WHERE category_id=:category_id AND sort_no BETWEEN 1 AND 75'), {'category_id': category_id})
