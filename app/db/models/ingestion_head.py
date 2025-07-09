from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base
import uuid
from datetime import datetime


class IngestionHead(Base):
    __tablename__ = "ingestion_heads"
    session_id = Column(UUID(as_uuid=True), ForeignKey("chat_sessions.id"), primary_key=True)
    current_position = Column(Integer, nullable=False, default=0)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    session = relationship("ChatSession", back_populates="ingestion_head")
    __table_args__ = (UniqueConstraint('session_id', name='uq_session_head'),)