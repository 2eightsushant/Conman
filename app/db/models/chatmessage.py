from sqlalchemy import Column, Integer, ForeignKey, String, Text, Enum, DateTime, UniqueConstraint, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime
import enum
import uuid

class MessageRole(enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(Enum(MessageRole), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    position = Column(Integer, nullable=False)  # o1, i1 → position = 1
    created_at = Column(DateTime, default=datetime.now)
    is_vectorized = Column(Boolean, default=False)

    session = relationship("ChatSession", back_populates="messages")
    __table_args__ = (UniqueConstraint('session_id', 'position', 'role', name='uq_session_position_role'),)