import ollama
import requests
import json

# Verify Ollama server and model availability
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

def get_current_weather(city: str) -> str:
    """
    Get the current weather for a given city using WeatherAPI.
    
    Args:
        city (str): The name of the city.
    
    Returns:
        str: A string describing the current weather or an error message.
    """
    try:
        if city=='New York':
            condition="Clear"
            temperature="22"
        else:
            condition="Rainy"
            temperature="15"
        return f"The current weather in {city} is {condition} with a temperature of {temperature}°C."
    except requests.exceptions.RequestException as e:
        return f"Error fetching weather data: {str(e)}"

# Define the tool schema for Ollama
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather for a specified city. Only use this function when the user explicitly asks for the weather.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The name of the city (e.g., Toronto)"
                    }
                },
                "required": ["city"]
            }
        }
    }
]

# Main execution
def main():
    # Check Ollama server and model
    try:
        check_ollama_server()
    except Exception as e:
        print(f"Setup error: {str(e)}")
        return

    # User query to test tool calling
    user_query = "What is the weather of New york?"

    # Call the Ollama chat API with the tool
    try:
        response = ollama.chat(
            model="llama3.2:3b",
            messages=[
                {"role": "system", "content": "You are a helpful assistant. You have access to a tool named `get_current_weather`. Only use this tool when the user clearly asks for weather. For everything else, reply directly with natural language. Do not invent other tools or call undefined functions."},
                {"role": "user", "content": user_query}
            ],
            tools=tools,
            options={
                "temperature": 0.7,  # Moderate randomness for consistent tool calling
                "num_ctx": 2048     # Context window size
            }
        )
        print(response)

        # Check if the response contains tool calls
        if response.get("message", {}).get("tool_calls"):
            tool_calls = response["message"]["tool_calls"]
            for tool_call in tool_calls:
                if tool_call["function"]["name"] == "get_current_weather":
                    city = tool_call["function"]["arguments"].get("city")
                    if not city:
                        print("Error: No city provided in tool call arguments.")
                        continue
                    print(f"Tool called: get_current_weather with city={city}")
                    weather_result = get_current_weather(city)
                    print(f"Weather result: {weather_result}")
                    
                    # Optional: Send tool result back to LLM for final response
                    follow_up_response = ollama.chat(
                        model="llama3.2:3b",
                        messages=[
                            {"role": "user", "content": user_query},
                            {"role": "assistant", "content": weather_result}
                        ]
                    )
                    print(f"Final LLM response: {follow_up_response['message']}")
                else:
                    print(f"Unknown tool called: {tool_call['function']['name']}")
        else:
            print(f"No tool called. LLM response: {response['message']['content']}")

    except Exception as e:
        print(f"Error during Ollama chat: {str(e)}")

if __name__ == "__main__":
    main()