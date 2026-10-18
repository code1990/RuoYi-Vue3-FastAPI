"""import Java concurrency part two cards from the Java interview PDF"""
from datetime import datetime
from alembic import op
import sqlalchemy as sa

revision = '202610180012'
down_revision = '202610180011'
branch_labels = None
depends_on = None

cards = (
('1、并发编程三要素？','原子性保证操作不可分割；可见性保证修改能被其他线程观察；有序性保证执行顺序满足 happens-before。','concept'),
('2、实现可见性的方法有哪些？','可用 volatile、synchronized/Lock、原子类、线程启动与结束规则及并发工具建立 happens-before 关系。','enumeration'),
('3、多线程的价值？','它可提高资源利用率、吞吐和响应性，但也增加同步、调试和容量治理成本。','concept'),
('4、创建线程的有哪些方式？','可继承 Thread、实现 Runnable、实现 Callable 并提交 ExecutorService；生产中优先后两者。','enumeration'),
('5、创建线程的三种方式对比？','Thread 耦合任务与线程；Runnable 无返回值；Callable 支持结果和受检异常。任务均应交由执行器管理。','comparison'),
('6、线程的状态流转图？','线程在 NEW、RUNNABLE、BLOCKED、WAITING、TIMED_WAITING、TERMINATED 间因调度、锁、等待和结束转换。','concept'),
('7、Java 线程具有哪些基本状态？','Thread.State 包含 NEW、RUNNABLE、BLOCKED、WAITING、TIMED_WAITING、TERMINATED 六种状态。','enumeration'),
('8、什么是线程池？有哪几种创建方式？','线程池复用线程执行任务。可用 ThreadPoolExecutor、ScheduledThreadPoolExecutor 或 Executors 工厂创建；生产应显式配置参数。','concept'),
('9、四种线程池的创建？','常见有 fixed、single、cached、scheduled；无界队列或无界线程数可能耗尽资源，需审慎使用工厂方法。','enumeration'),
('10、线程池的优点？','复用线程，限制并发，提供排队、拒绝、监控、取消和统一关闭能力。','concept'),
('11、常用的并发工具类有哪些？','常用有 CountDownLatch、CyclicBarrier、Semaphore、Exchanger、BlockingQueue、Future 和 CompletableFuture。','enumeration'),
('12、CyclicBarrier 和 CountDownLatch 的区别？','Latch 等待计数归零且通常一次性；Barrier 让一组线程互等并可复用。','comparison'),
('13、synchronized 的作用？','提供互斥、可见性和有序性；退出同步块会释放锁并将修改对随后获得同一锁的线程可见。','concept'),
('14、volatile 关键字的作用？','保证单次读写可见性和顺序约束，不保证复合读改写操作的原子性。','concept'),
('15、什么是 CAS？','CAS 比较内存值与预期值，相等时原子写入新值，是许多原子类的基础。','concept'),
('16、CAS 的问题？','可能有 ABA、长时间自旋消耗 CPU，且通常只能原子更新单一位置；可用版本戳、退避或锁缓解。','concept'),
('17、什么是 Future？','Future 表示异步任务结果，可查询、取消并通过 get 等待结果或异常。','concept'),
('18、什么是 AQS？','AbstractQueuedSynchronizer 是构建锁、信号量、闭锁等同步器的队列同步框架。','concept'),
('19、AQS 支持两种同步方式？','支持独占和共享两种获取模式，分别服务于互斥锁与读锁、信号量等。','comparison'),
('20、ReadWriteLock 是什么？','读写锁允许多个读者并发，写者独占；适合读多写少场景。','concept'),
('21、FutureTask 是什么？','FutureTask 包装 Callable，既是 Runnable 又是 Future，可执行并保存一次性结果。','concept'),
('22、synchronized 和 ReentrantLock 的区别？','前者语法简单且自动释放；后者支持公平、可中断、超时获取和多个 Condition，但必须 finally 解锁。','comparison'),
('23、什么是乐观锁和悲观锁？','悲观锁先互斥再修改；乐观锁以 CAS/版本号提交并在冲突时重试。','comparison'),
('24、线程 B 怎么知道线程 A 修改了变量？','通过 volatile、锁、原子类或并发工具建立可见性；普通共享字段不能保证及时可见。','concept'),
('25、synchronized、volatile、CAS 比较？','synchronized 适合复合临界区；volatile 仅保证可见性；CAS 支持无锁原子更新但需处理冲突与 ABA。','comparison'),
('26、sleep 和 wait 有什么区别？','sleep 不释放锁且只暂停；wait 必须持锁、会释放监视器并等待通知/超时/中断。','comparison'),
('27、ThreadLocal 是什么？有什么用？','它为每个线程保存独立变量副本；在线程池中使用后必须 remove。','concept'),
('28、为什么 wait/notify 要在同步块中调用？','必须持有同一监视器，才能原子地管理等待队列并避免丢失通知。','concept'),
('29、多线程同步有哪几种方法？','可用 synchronized、Lock、volatile、原子类、并发容器、条件变量和消息队列。','enumeration'),
('30、线程的调度策略？','由操作系统抢占式调度决定；Java 优先级只是提示，不可用于保证业务顺序。','concept'),
('31、ConcurrentHashMap 的并发度是什么？','JDK 8+ 使用 CAS 与细粒度同步，并发度参数不是实际并发上限。','concept'),
('32、Linux 环境下如何查找 CPU 最长的线程？','用 top -H 或 ps -L 找线程 ID，再转十六进制对应 jstack/jcmd Thread.print 的 nid。','scenario'),
('33、Java 死锁以及如何避免？','死锁是循环等待锁；按固定顺序加锁、缩短临界区、tryLock 超时和避免嵌套锁可降低风险。','scenario'),
('34、死锁的原因？','互斥、请求并保持、不可剥夺和循环等待四个条件同时成立会导致死锁。','concept'),
('35、怎么唤醒一个阻塞的线程？','使用 interrupt、条件变量 signal/notify 或关闭相应资源，取决于阻塞类型。','scenario'),
('36、不可变对象对多线程有什么帮助？','它无可变共享状态，天然线程安全，可减少锁与可见性问题。','concept'),
('37、什么是多线程的上下文切换？','调度器保存一个线程状态并恢复另一个线程状态；频繁切换会降低性能。','concept'),
('38、线程池队列已满会发生什么？','线程池会尝试创建非核心线程到最大数，仍无法接收时执行配置的拒绝策略。','scenario'),
('39、Java 中用到的线程调度算法是什么？','通常由操作系统进行抢占式调度，具体算法和公平性与平台有关。','concept'),
('40、什么是线程调度器和时间分片？','调度器分配 CPU；时间分片限制单次运行时间以支持抢占和响应。','concept'),
('41、什么是自旋？','线程在短时间内循环检查条件而不阻塞，适合等待很短的锁；过长会浪费 CPU。','concept'),
('42、Lock 接口是什么？相比同步有什么优势？','Lock 提供 tryLock、可中断获取、公平锁和 Condition；synchronized 更简洁且自动释放。','comparison'),
('43、单例模式的线程安全性？','可用枚举、静态内部类、饿汉初始化或正确的双重检查加 volatile 实现线程安全单例。','scenario'),
('44、Semaphore 有什么作用？','以许可数限制同时访问某资源的线程数，适合限流和连接池。','concept'),
('45、Executors 类是什么？','它是创建常见执行器的工具类；生产中优先显式 ThreadPoolExecutor 以避免无界资源。','concept'),
('46、线程类的构造方法、静态块由哪个线程调用？','由触发类初始化或对象创建的当前线程执行；不是由新建线程的 run 方法自动执行。','concept'),
('47、同步方法和同步块哪个更好？','同步块能缩小锁范围并指定锁对象；整个方法都需保护时同步方法更简洁。','comparison'),
('48、Java 线程数过多会造成什么异常？','会增加上下文切换和内存占用，严重时出现 OutOfMemoryError: unable to create new native thread 或系统资源耗尽。','scenario'),
)

def upgrade() -> None:
    assert len(cards) == 48
    category_id = op.get_bind().execute(sa.text("SELECT category_id FROM exam_category WHERE name='Java 并发编程（二）'")).scalar_one()
    table = sa.table('exam_card', *[sa.column(c) for c in ('category_id','question','answer','key_points','tags','card_type','difficulty','status','sort_no','create_time','update_time')])
    now = datetime.now()
    op.bulk_insert(table, [dict(category_id=category_id,question=q,answer=a,key_points='',tags='Java,并发编程',card_type=t,difficulty=3,status='published',sort_no=i,create_time=now,update_time=now) for i,(q,a,t) in enumerate(cards,1)])

def downgrade() -> None:
    category_id = op.get_bind().execute(sa.text("SELECT category_id FROM exam_category WHERE name='Java 并发编程（二）'")).scalar_one()
    op.get_bind().execute(sa.text('DELETE FROM exam_card WHERE category_id=:category_id AND sort_no BETWEEN 1 AND 48'), {'category_id': category_id})
