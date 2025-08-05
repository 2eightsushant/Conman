import ollama
import requests
import json
from app.core.strategy.memory_retriever import retrieve
from app.core.strategy.memory_formatter import MemoryFormatter

LIMIT = 3

def check_ollama_server():
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        response.raise_for_status()
        models = response.json().get("models", [])
        if any(model["name"] == "llama3.2:3b" for model in models):
            print("Model llama3.2:3b is available.")
        else:
            raise Exception("Model llama3.2:3b not found. Run 'ollama pull llama3.2:3b'.")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Ollama server not reachable at http://localhost:11434: {str(e)}")

def recall_memories(query: str) -> str:
    """
    Get the memories
    
    Args:
        query (str): Query to retrieve memories of conversation.
    
    Returns:
        str: Returns the memories of conversation between assistant and user related to the query in format: [{'time','content','score','emotion','importance','continues_from'}]
    """
    try:
        context = {"session_id":"a4a33e50-c3ec-4672-b806-1c8ed51ad6d1", "emotion":"neutral"}
        response = retrieve(query, context, top_k=3)
        # print(response)
        if response:
            formatter = MemoryFormatter(readable_time=True)
            formatted = formatter.format(reranked_chunks=response["raw_reranked"], limit=3)
            return formatted
        else:
            return "No memories for the give query"
    except Exception as e:
        return f"Error fetching memories: {str(e)}"

tools = [
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


def main():
    try:
        check_ollama_server()
    except Exception as e:
        print(f"Setup error: {str(e)}")
        return

    user_query = "Did I talked about chest tightness ? If yes when ?"
    # user_query = "What is the capital of Nepal ?"
    conversation = [
        {"role": "system", "content": (
            "You are an assistant with human-like memory powers via tool calls. "
            "When a user asks something, always reflect first. If the answer may depend on past conversations, call the `recall_memories` tool. "
            "If you recall memories, treat them as factual. Directly quote the user’s previous words when they match the current question or topic. "
            "Recalled memories/conversations will be in format:[{'time'(when converstaion happened),'content'(converstation between you and user),'score'(cognitive score, focus on highest score),'emotion'(emotions related to conversation),'importance'(importance of conversation),'continues_from'}]"
            "Always include a rough time (e.g., 'a few hours ago', 'yesterday', etc.) when referring to remembered events. "
            "Understand the emotion(data from emotion key) of the recalled converstaion and respond wisely"
            "Be specific and grounded. Avoid vague summaries or paraphrasing when exact memory is available. "
            "If no relevant memory is recalled, answer naturally. Do not make assumptions or fabricate memory content. "
            "Do not call `recall_memories` again if you’ve already called it for the same query."
        )},
        {"role": "user", "content": user_query}
    ]

    for tool_id in range(LIMIT):
        try:
            response = ollama.chat(
                model="llama3.2:3b",
                messages=conversation,
                tools=tools,
                options={"temperature": 0.7, "num_ctx": 2048}
            )

            message = response.get("message", {})
            tool_calls = message.get("tool_calls")

            if tool_calls:
                for tool_call in tool_calls:
                    fn_name = tool_call["function"]["name"]
                    args = tool_call["function"].get("arguments", {})
                    query = args.get("query")

                    if fn_name == "recall_memories" and query:
                        print(f"Tool called: recall_memories('{query}')")
                        memories = recall_memories(query)
                        print("Recalled memories:", memories)
                        recalled_blocks = [
                                f"(~{mem['time']})\n{mem['content']}" for mem in memories
                            ]

                        # Inject tool result into history
                        tool_response = {
                            "role": "tool",
                            "tool_call_id": tool_id,
                            "name": "recall_memories",
                            "content": "\n\nRecalled past conversations:\n\n" + "\n\n".join(recalled_blocks)
                        }

                        conversation.extend([
                            {"role": "assistant", "content": message.get("content", "")},
                            tool_response
                        ])
            else:
                # If no tool call, output assistant response and stop
                print(f"LLM Response:\n{message.get('content', '')}")
                break

        except Exception as e:
            print(f"Error during Ollama chat: {str(e)}")
            break

if __name__ == "__main__":
    main()