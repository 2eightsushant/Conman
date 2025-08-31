from uuid import UUID
from weaviate import WeaviateAsyncClient
from app.shared.logger import get_logger

logger = get_logger(__name__)

async def ingest_chunk(client: WeaviateAsyncClient, chunk: dict, embedding: list):
    """Ingest chunks to weaviate db"""
    try:
        collection = client.collections.get("DialogMemory")

        metadata = chunk["metadata"]
        temporal = metadata.get("temporal_context", {})

        logger.info(f"Ingesting chunks to Weaviate: {chunk['id']}")
        await collection.data.insert(
            properties={
                "content": chunk["content"],
                "session_id": UUID(str(metadata["session_id"])),
                "username": metadata.get("username"),
                "speakers": metadata.get("speakers"),
                "emotions": metadata.get("emotions"),
                "timestamp": metadata.get("timestamp"),
                "temporal_context": {
                    "start_index": temporal.get("start_index", -1),
                    "end_index": temporal.get("end_index", -1),
                    "session_position": temporal.get("session_position", []),
                    "message_indices": temporal.get("message_indices", []),
                    "prev_chunk_id": temporal.get("prev_chunk_id", None),
                    "time_span_seconds": temporal.get("time_span_seconds", 0.0)
                }
            },
            uuid=chunk["id"],
            vector=embedding
        )
        logger.info("Ingestion successfull.")
    except Exception as e:
        logger.warning(f"Ingestion of chunks {chunk['id']} failed: {str(e)}")