import asyncio
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.future import select
from app.db.models import ChatMessage, ChatSession, User
from .helper.helperHead import gethead, updatehead, update_is_vectorized
from app.core.strategy.chunker import DialogChunker
from weaviate import WeaviateAsyncClient
from httpx import AsyncClient
from app.schemas.db_models import HeadResponse, MessageModel
from sqlalchemy.orm import joinedload
from app.data_pipeline.push_to_weaviate import ingest_chunk
from weaviate.util import generate_uuid5
from tqdm import tqdm
from app.conn.postgre_conn import get_db
from app.conn.clients import post_json
from app.shared.logger import get_logger

logger = get_logger(__name__)
vectorizer_url = "http://127.0.0.1:8083/vectorize"

async def ingest_ready_messages(session_id: UUID, client: WeaviateAsyncClient, http_client: AsyncClient):
    """Ingest messages to vector database for a session with advisory lock"""
    logger.info(f"Starting ingestion for session {session_id}")

    try:
        async with get_db() as db:
            head_response: HeadResponse = await gethead(db, session_id)
            stmt = select(ChatMessage)\
            .join(ChatSession, ChatMessage.session_id == ChatSession.id)\
            .join(User, ChatSession.user_id == User.id)\
            .filter(ChatMessage.session_id == session_id)\
            .filter(ChatMessage.position > head_response.current_head)\
            .options(joinedload(ChatMessage.session).joinedload(ChatSession.user))\
            .order_by(ChatMessage.position.asc())
            results = await db.execute(stmt)
            messages = results.scalars().all()

            if not messages:
                logger.info("No new messages")
                return

            messages_dict = [
                {
                    "session_id" : message.session_id,
                    "name" : message.session.user.name,
                    "role" : message.role.value,
                    "content" : message.content,
                    "session_position" : message.position,
                    "message_created_at" : message.created_at,
                }
                for message in messages
            ]
            await client.connect()
            chunker = DialogChunker()
            chunks = await chunker.chunk(messages=messages_dict, http_client=http_client)
            # if client.collections.exists("DialogMemory"):
            #     logger.debug("Deleting collection")
            #     client.collections.delete("DialogMemory")
            collection = client.collections.get("DialogMemory")

            tasks = []
            for chunk in tqdm(chunks, desc="Pushing chunks to Weaviate"):
                try:
                    exists = await collection.data.exists(chunk["id"])
                    if not exists:
                        logger.info(f"Inserting new chunk: {chunk['id']}")
                        vector_resp = await post_json(http_client, vectorizer_url, {"text": [chunk['content']]})
                        vector = vector_resp['vector'][0]
                        tasks.append(ingest_chunk(client=client, chunk=chunk, embedding=vector))
                    else:
                        logger.info(f"Chunk {chunk['id']} already exists, skipping.")
                except Exception as e:
                    logger.error(f"Chunk ingestion failed for {chunk['id']}: {str(e)}")
            results = await asyncio.gather(*tasks, return_exceptions=True)
            if all(not isinstance(r, Exception) for r in results):
                await updatehead(db, session_id, head_response)
                await update_is_vectorized(db, messages)
            else:
                logger.warning("Some chunk ingestions failed; not updating head")

    except Exception as e:
        logger.error(f"Ingestion of messages to vector database failed for session{session_id}: {str(e)}")
            

def main():
    sid = 'a4a33e50-c3ec-4672-b806-1c8ed51ad6d1'
    async def runner():
        async with AsyncClient() as http_client, WeaviateAsyncClient("http://localhost:8080") as wv_client:
            await ingest_ready_messages(sid, wv_client, http_client)
    asyncio.run(runner())

if __name__== "__main__":
    main()