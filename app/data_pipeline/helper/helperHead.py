from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import func
from app.db.models.ingestion_head import IngestionHead
from app.db.models.chatmessage import ChatMessage
from app.shared.logger import get_logger

logger = get_logger(__name__)

def gethead(db, session_id: UUID):
    '''Gets head pointing to last vectorized message'''
    logger.info(f"Getting head for session {session_id}")
    try:
        head = db.query(IngestionHead).filter_by(session_id=session_id).first()
        current_head = head.current_position if head else 0
        max_position = db.query(func.max(ChatMessage.position)).filter_by(session_id=session_id).scalar() or 0
        return head, current_head, max_position
    except Exception as e:
        logger.error(f"Getting head failed for session {session_id}: {str(e)}")
        raise


def updatehead(db, session_id: UUID, head, max_position):
    '''Updates head to last vectorized message with advisory lock'''
    logger.info(f"Updating head for session {session_id}")

    lock_id = hash(str(session_id)) % 2**31
    db.execute(f"SELECT pg_advisory_lock({lock_id})")
    try:
        if not head:
            head = IngestionHead(
                session_id=session_id,
                current_position=max_position
            )
            db.add(head)
        else:
            head.current_position = max_position
        logger.info(f"Updated head to {max_position} for session {session_id}")
    except Exception as e:
        logger.error(f"Updating head failed for session {session_id}: {str(e)}")
        raise
    finally:
        db.execute(f"SELECT pg_advisory_unlock({lock_id})")

    

def update_is_vectorized(db, messages):
    '''Mark messages as vectorized'''
    try:
        for message in messages:
            message.is_vectorized = True
        logger.info(f"Marked {len(messages)} messages as vectorized")
    except Exception as e:
        logger.error(f"Failed to update messages is_vectorized flag: {str(e)}")
        raise