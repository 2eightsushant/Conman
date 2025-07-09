from app.conn.localsession import SessionLocal
from sqlalchemy.dialects.postgresql import UUID
from app.db.models import ChatMessage, ChatSession, User
from .helper.helperHead import gethead, updatehead, update_is_vectorized
from app.core.strategy.chunker import DialogChunker
from app.schemas.db_models import HeadResponse, MessageModel
from typing import Optional, List, Generator
from app.core.strategy.get_emotions import RoBertEmotionGo
from sqlalchemy.orm import Session
from contextlib import contextmanager
from app.shared.logger import get_logger

logger = get_logger(__name__)

@contextmanager
def db_session() -> Generator[Session, None, None]:
    '''Context manager for database session with proper cleanup'''
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def ingest_ready_messages(session_id: UUID):
    """Ingest messages to vector database for a session with advisory lock"""
    logger.info(f"Starting ingestion for session {session_id}")

    try:
        with db_session() as db:
            head_response: HeadResponse = gethead(db, session_id)
            messages: List[MessageModel] = db.query(
                ChatMessage.session_id,
                User.name,
                ChatMessage.role,
                ChatMessage.content,
                ChatMessage.position,
                ChatMessage.created_at
                )\
            .join(ChatSession, ChatMessage.session_id==ChatSession.id)\
            .join(User, ChatSession.user_id==User.id)\
            .filter(ChatMessage.session_id == session_id)\
            .filter(ChatMessage.position > head_response.current_head)\
            .order_by(ChatMessage.position.asc())\
            .all()

            messages_dict = [
                {
                    "session_id" : message.session_id,
                    "name" : message.name,
                    "role" : message.role.value,
                    "content" : message.content,
                    "session_position" : message.position,
                    "message_created_at" : message.created_at,
                }
                for message in messages
            ]

            chunker = DialogChunker()
            emotion_model = RoBertEmotionGo(k=2)
            chunks = chunker.chunk(messages=messages_dict, emotion_model=emotion_model)

            print(chunks[5])

            # docs = convert_messages_to_docs(messages)
            # push_to_vector_db(docs, session_id)

            # updatehead(db, session_id, head_response)
            # updateIsVectorized(db, session_id, messages)

    
    except Exception as e:
        logger.error(f"Ingestion of messages to vector database failed for session{session_id}: {str(e)}")
            


def main():
    sid = 'd025e2b3-8f51-452f-b152-105084c664b2'
    ingest_ready_messages(sid)

if __name__== "__main__":
    main()