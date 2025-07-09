from app.conn.localsession import SessionLocal
from sqlalchemy.dialects.postgresql import UUID
from app.db.models.chatmessage import ChatMessage
from .helper.helperHead import gethead, updatehead, updateIsVectorized
from contextlib import contextmanager
from app.shared.logger import get_logger

logger = get_logger(__name__)

@contextmanager
def db_session():
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
            head, current_head, max_position = gethead(db, session_id)
            messages = db.query(ChatMessage)\
            .filter(ChatMessage.session_id == session_id)\
            .filter(ChatMessage.position > current_head)\
            .order_by(ChatMessage.position.asc())\
            .all()

            # docs = convert_messages_to_docs(messages)
            # push_to_vector_db(docs, session_id)

            updatehead(db, session_id, head, max_position)
            updateIsVectorized(db, session_id, messages)

    
    except Exception as e:
        logger.error(f"Ingestion of messages to vector database failed for session{session_id}: {str(e)}")
            

