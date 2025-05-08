from typing import List, Union
from langchain_core.messages import AIMessage, HumanMessage

def format_chat_history(chat_history: List[Union[AIMessage, HumanMessage]]) -> List[dict]:
    """Format chat history for display in Streamlit."""
    formatted_history = []
    for message in chat_history:
        if isinstance(message, HumanMessage):
            formatted_history.append({"role": "user", "content": message.content})
        elif isinstance(message, AIMessage):
            formatted_history.append({"role": "assistant", "content": message.content})
    return formatted_history