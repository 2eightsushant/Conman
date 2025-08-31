from app.core.strategy.memory_retriever import retrieve
from app.core.strategy.memory_formatter import MemoryFormatter
from weaviate import WeaviateAsyncClient
from httpx import AsyncClient
from ollama import AsyncClient as OllamaAsyncClient
from app.prompts.prompt_loader import load_prompt
from app.shared.logger import get_logger

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

    async def recall_memories(self, query: str, weaviate_client: WeaviateAsyncClient, http_client:AsyncClient, session_id: str) -> str:
        """
        Get the memories
        
        Args:
            query (str): Query to retrieve memories of conversation.
        
        Returns:
            str: Returns the memories of conversation between assistant and user related to the query in format: [{'time','content','score','emotion','importance','continues_from'}]
        """
        try:
            logger.info("Tool: RecallMemory called, retrieving the results...")
            context = {"session_id":session_id, "emotion":"neutral"}
            top_results = await retrieve (query=query, context=context, weaviate_client=weaviate_client, http_client=http_client, top_k=30)
            retrieved = top_results.get("raw_reranked")
            if retrieved:
                formatter = MemoryFormatter(readable_time=True)
                formatted = formatter.format(reranked_chunks=retrieved, limit=3)
                recalled_blocks = [
                    f"(Time:{mem['time']}, Emotions:{mem['emotion']}, Importance:{mem['importance']})\n{mem['content']}" for mem in formatted
                ]                
                
                system_prompt = await load_prompt(version="v1.0.0", key="path_reflect")
                
                memory = "\n\nRecalled past conversations:\n\n" + "\n\n".join(recalled_blocks)
                print(memory)
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "query": query},
                    {"role": "user", "content": memory}
                ]
                logger.info("Running reflector...")
                response = await OllamaAsyncClient().chat(
                    model="llama3.2:3b",
                    messages=messages,
                    options={"temperature": 0.7, "num_ctx": 2048}
                )
                logger.info("Reflecting success!")
                response = response.get("message", {})
                return response.get("content", "")
                
            else:
                logger.info("No memories found")
                return "No memories for the give query"
        except Exception as e:
            logger.error(f"Error fetching memories: {str(e)}")
            return f"Error fetching memories: {str(e)}"