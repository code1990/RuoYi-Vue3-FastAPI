from sqlalchemy import BIGINT, TEXT, BigInteger, Boolean, Column, ForeignKey, Index, String

from config.database import Base


class CodexConversation(Base):
    """
    Codex 对话主表
    """

    __tablename__ = 'conversation'
    __table_args__ = (
        Index('idx_conversation_workspace_updated', 'workspace_id', 'updated_at_ms'),
        Index('idx_conversation_thread_id', 'thread_id'),
        {'comment': 'Codex 对话主表'},
    )

    id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment='主键ID')
    conversation_id = Column(String(64), nullable=False, unique=True, comment='会话ID')
    workspace_id = Column(String(128), nullable=True, comment='工作区ID')
    thread_id = Column(String(128), nullable=True, comment='线程ID')
    title = Column(String(255), nullable=True, comment='标题')
    requirement = Column(TEXT, nullable=True, comment='需求内容')
    status = Column(String(32), nullable=True, comment='会话状态')
    operator = Column(String(64), nullable=True, comment='操作者')
    last_message_preview = Column(TEXT, nullable=True, comment='最后一条消息预览')
    final_summary = Column(TEXT, nullable=True, comment='最终总结')
    last_error = Column(TEXT, nullable=True, comment='最后错误')
    created_at_ms = Column(BIGINT, nullable=True, comment='创建时间毫秒时间戳')
    updated_at_ms = Column(BIGINT, nullable=True, comment='更新时间毫秒时间戳')


class CodexConversationMessage(Base):
    """
    Codex 对话消息表
    """

    __tablename__ = 'conversation_message'
    __table_args__ = (
        Index('idx_conversation_message_conversation_seq', 'conversation_id', 'sequence_no'),
        Index('idx_conversation_message_thread_turn', 'thread_id', 'turn_id'),
        {'comment': 'Codex 对话消息表'},
    )

    id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment='主键ID')
    conversation_id = Column(
        String(64),
        ForeignKey('conversation.conversation_id', onupdate='CASCADE', ondelete='CASCADE'),
        nullable=False,
        comment='会话ID',
    )
    thread_id = Column(String(128), nullable=True, comment='线程ID')
    turn_id = Column(String(128), nullable=True, comment='轮次ID')
    role = Column(String(32), nullable=True, comment='消息角色')
    message_type = Column(String(64), nullable=True, comment='消息类型')
    content = Column(TEXT, nullable=True, comment='消息内容')
    payload_json = Column(TEXT, nullable=True, comment='扩展负载JSON')
    sequence_no = Column(BigInteger, nullable=True, comment='消息顺序号')
    created_at_ms = Column(BIGINT, nullable=True, comment='创建时间毫秒时间戳')


class CodexConversationEvent(Base):
    """
    Codex 对话事件表
    """

    __tablename__ = 'conversation_event'
    __table_args__ = (
        Index('idx_conversation_event_conversation_time', 'conversation_id', 'created_at_ms'),
        Index('idx_conversation_event_thread_turn', 'thread_id', 'turn_id'),
        {'comment': 'Codex 对话事件表'},
    )

    id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment='主键ID')
    conversation_id = Column(
        String(64),
        ForeignKey('conversation.conversation_id', onupdate='CASCADE', ondelete='CASCADE'),
        nullable=False,
        comment='会话ID',
    )
    thread_id = Column(String(128), nullable=True, comment='线程ID')
    turn_id = Column(String(128), nullable=True, comment='轮次ID')
    event_type = Column(String(64), nullable=True, comment='事件类型')
    event_status = Column(String(32), nullable=True, comment='事件状态')
    payload_json = Column(TEXT, nullable=True, comment='事件负载JSON')
    created_at_ms = Column(BIGINT, nullable=True, comment='创建时间毫秒时间戳')


class CodexConversationTask(Base):
    """
    Codex 对话任务表
    """

    __tablename__ = 'conversation_task'
    __table_args__ = (
        Index('idx_conversation_task_conversation_submitted', 'conversation_id', 'submitted_at_ms'),
        Index('idx_conversation_task_task_id', 'task_id'),
        {'comment': 'Codex 对话任务表'},
    )

    id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment='主键ID')
    conversation_id = Column(
        String(64),
        ForeignKey('conversation.conversation_id', onupdate='CASCADE', ondelete='CASCADE'),
        nullable=False,
        comment='会话ID',
    )
    task_id = Column(String(128), nullable=False, unique=True, comment='任务ID')
    workspace_id = Column(String(128), nullable=True, comment='工作区ID')
    thread_id = Column(String(128), nullable=True, comment='线程ID')
    turn_id = Column(String(128), nullable=True, comment='轮次ID')
    status = Column(String(32), nullable=True, comment='任务状态')
    created_thread = Column(Boolean, nullable=True, comment='是否为本次任务新建线程')
    submitted_at_ms = Column(BIGINT, nullable=True, comment='提交时间毫秒时间戳')
    completed_at_ms = Column(BIGINT, nullable=True, comment='完成时间毫秒时间戳')
    last_error = Column(TEXT, nullable=True, comment='最后错误')
