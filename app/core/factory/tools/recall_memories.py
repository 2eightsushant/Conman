from app.core.strategy.memory_retriever import retrieve
from app.core.strategy.memory_formatter import MemoryFormatter
from weaviate import WeaviateAsyncClient
from httpx import AsyncClient
from app.shared.logger import get_logger
import asyncio

logger = get_logger(__name__)

class recallMemory:
    def __init__(self):
        logger.info("Tool: recallMemory initialized")
        self.metadata = [
            {
                "type": "function",
                "function": {
                    "name": "recall_memories",
                    "description": "Get the memories of conversation between assistant and user related to the query. Only use this function when needed.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Reasoning"
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
        ]

    async def recall_memories(self, query: str, weaviate_client: WeaviateAsyncClient, http_client:AsyncClient) -> str:
        """
        Get the memories
        
        Args:
            query (str): Query to retrieve memories of conversation.
        
        Returns:
            str: Returns the memories of conversation between assistant and user related to the query in format: [{'time','content','score','emotion','importance','continues_from'}]
        """
        try:
            logger.info("Tool: RecallMemory called, retrieving the results...")
            context = {"session_id":"a4a33e50-c3ec-4672-b806-1c8ed51ad6d1", "emotion":"neutral"}
            top_results = await retrieve (query=query, context=context, weaviate_client=weaviate_client, http_client=http_client, top_k=30)
            retrieved = top_results.get("raw_reranked")
            if retrieved:
                formatter = MemoryFormatter(readable_time=True)
                formatted = formatter.format(reranked_chunks=retrieved, limit=3)
                return formatted
            else:
                logger.info("No memories found")
                return "No memories for the give query"
        except Exception as e:
            logger.error(f"Error fetching memories: {str(e)}")
            return f"Error fetching memories: {str(e)}"