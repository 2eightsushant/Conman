from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import func, text
from app.db.models.ingestion_head import IngestionHead
from app.db.models.chatmessage import ChatMessage
from app.schemas.db_models import HeadResponse, MessageModel, IngestionHeadModel
from typing import Optional, List
from app.shared.logger import get_logger

logger = get_logger(__name__)

def gethead(db, session_id: UUID | str) -> HeadResponse:
    '''Gets head pointing to last vectorized message'''
    logger.info(f"Getting head for session {session_id}")
    try:
        head: [IngestionHeadModel] = db.query(IngestionHead).filter_by(session_id=session_id).first() # type: ignore
        current_head: Optional[int] = head.current_position if head else 0
        max_position: Optional[int] = db.query(func.max(ChatMessage.position)).filter_by(session_id=session_id).scalar() or 0
        return HeadResponse(head=head, current_head=current_head, max_position=max_position)
    except Exception as e:
        logger.error(f"Getting head failed for session {session_id}: {str(e)}")
        raise


def updatehead(db, session_id: UUID | str, head: HeadResponse) -> None:
    '''Updates head to last vectorized message with advisory lock'''
    logger.info(f"Updating head for session {session_id}")

    lock_id = hash(str(session_id)) % 2**31
    db.execute(text(f"SELECT pg_advisory_lock({lock_id})"))
    try:
        if not head.head:
            ihead = IngestionHead(
                session_id=session_id,
                current_position=head.max_position
            )
            db.add(ihead)
        else:
            head.head.current_position = head.max_position
        logger.info(f"Updated head to {head.max_position} for session {session_id}")
    except Exception as e:
        logger.error(f"Updating head failed for session {session_id}: {str(e)}")
        raise
    finally:
        db.execute(text(f"SELECT pg_advisory_unlock({lock_id})"))

    

def update_is_vectorized(db, messages: List[MessageModel]) -> None:
    '''Mark messages as vectorized'''
    try:
        for message in messages:
            message.is_vectorized = True
        logger.info(f"Marked {len(messages)} messages as vectorized")
    except Exception as e:
        logger.error(f"Failed to update messages is_vectorized flag: {str(e)}")
        raise