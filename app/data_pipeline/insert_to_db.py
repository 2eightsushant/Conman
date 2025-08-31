import uuid
from app.conn.postgre_conn import get_db
from app.db.models import ChatMessage
from app.schemas.db_models import HeadResponse
from app.data_pipeline.helper.helperHead import gethead
from app.db.models.chatmessage import MessageRole
from app.shared.logger import get_logger

logger = get_logger("insert_to_db")

async def insert_chat(query: str, response: str, session_id: uuid.UUID):
    async with get_db() as db:
        try:
            head_response: HeadResponse = await gethead(db, session_id)
            messages = [
                    ChatMessage(
                        id=uuid.uuid4(),
                        session_id=session_id,
                        role=MessageRole.USER,
                        content=query,
                        position=head_response.max_position + 1
                    ),
                    ChatMessage(
                        id=uuid.uuid4(),
                        session_id=session_id,
                        role=MessageRole.ASSISTANT,
                        content=response,
                        position=head_response.max_position + 1
                    )
            ]
            db.add_all(messages)
            await db.commit()
            print("Chat successfully inserted to db")
            logger.info("Chat successfully inserted to db")
        
        except Exception as e:
            print(f"Error inserting chat to db: {e}")
            logger.error(f"Error inserting chat to db: {e}")