from ollama import chat
import json

tool_map = {
    "get_datetime": get_datetime,
    "list_documents": list_documents
}

def ollama_chat(messages, tools):
    try:
        response = chat(
            model="qwen3:8b",
            messages=messages,
            tools=tools,
            stream=False
        )
        return response

    except Exception as e:
        return {
            "error": f"LLM communication error: {str(e)}"
        }
