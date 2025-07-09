from pydantic import BaseModel, UUID4
from typing import List, Optional
from datetime import datetime

class ChatMessageModel(BaseModel):
    id: UUID4
    session_id: UUID4
    role: str
    content: str
    position: int
    created_at: datetime
    is_vectorized: bool

    model_config = {
        "from_attributes" : True
    }

class ChatSessionModel(BaseModel):
    id: UUID4
    user_id: UUID4
    started_at: datetime
    ended_at: datetime

    model_config = {
        "from_attributes" : True
    }

class IngestionHeadModel(BaseModel):
    session_id: UUID4
    current_position: int
    updated_at: Optional[datetime]

    model_config = {
        "from_attributes" : True
    }

class HeadResponse(BaseModel):
    head: Optional[IngestionHeadModel]
    current_head: Optional[int]
    max_position: Optional[int]

class MessageModel(BaseModel):
    session_id: UUID4
    name: str
    role: str
    content: str
    position: int
    created_at: datetime
