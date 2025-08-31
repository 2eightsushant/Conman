import asyncio
import requests
from ollama import AsyncClient
from app.shared.logger import get_logger
from httpx import TimeoutException
from app.prompts.prompt_loader import load_prompt

logger = get_logger(__name__)
LIMIT = 3

async def check_ollama_server():
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        response.raise_for_status()
        models = response.json().get("models", [])
        if any(model["name"] == "llama3.2:3b" for model in models):
            logger.info("Model llama3.2:3b is available.")
        else:
            logger.error("Model llama3.2:3b not found")
            raise Exception("Model llama3.2:3b not found. Run 'ollama pull llama3.2:3b'.")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Ollama server not reachable at http://localhost:11434: {str(e)}")
    
async def chat(conversation, tools):
    response = await AsyncClient().chat(
                model="llama3.2:3b",
                messages=conversation,
                tools=tools.metadata,
                options={"temperature": 0.7, "num_ctx": 2048}
            )
    return response

async def process_tool_call(tool_call, tools, weaviate_client, http_client, session_id):
    """Handle a single tool call request (e.g., recall_memories)."""
    fn_name = tool_call["function"]["name"]
    args = tool_call["function"].get("arguments", {})
    query = args.get("query")

    if fn_name == "recall_memories" and query:
        logger.info(f"Tool called: recall_memories('{query}')")
        try:
            # Run with timeout safeguard
            memories = await tools.recall_memories(query, weaviate_client, http_client, session_id)
        except TimeoutException:
            logger.error("Timeout while recalling memories")
            return None

        print(memories)
        return {
            "role": "tool",
            "tool_call_id": tool_call.get("id"),
            "name": "recall_memories",
            "content": "\n\nRecalled past conversations:\n\n" + memories,
        }

    logger.warning(f"Unsupported tool call: {fn_name}")
    return None


async def infer(user_query: str, weaviate_client, http_client, tools, session_id):
    """
    Orchestrates inference:
    1. Starts conversation
    2. Loops until no tools called or LIMIT reached
    3. Returns assistant response
    """
    version = "v1.0.0"
    try:
        logger.info("Checking ollama server...")
        await check_ollama_server()
    except Exception as e:
        logger.error("Ollama server unreachable")
        return {"error": "Ollama server unreachable", "details": str(e)}
    
    system_prompt = await load_prompt(version=version, key="path")

    conversation = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_query}
    ]

    for step in range(LIMIT):
        logger.info(f"Chat round {step + 1}/{LIMIT}")
        try:
            response = await chat(conversation, tools)
        except Exception as e:
            logger.error(f"Ollama chat error: {str(e)}")
            return {"error": "Chat failure", "details": str(e)}

        message = response.get("message", {})
        tool_calls = message.get("tool_calls", [])

        if not tool_calls:
            logger.info("No tools called, chat cycle ended")
            return {
                "answer": message.get("content", ""),
            }

        # Process tool calls sequentially
        for tool_call in tool_calls:
            tool_response = await process_tool_call(tool_call, tools, weaviate_client, http_client, session_id)
            if tool_response:
                # Inject tool response back into conversation
                conversation.extend([
                    {"role": "assistant", "content": message.get("content", "")},
                    tool_response,
                ])
            else:
                logger.warning("Skipping invalid/failed tool call")

    # If loop exits without return
    return {"error": "Tool call limit reached", "conversation": conversation}