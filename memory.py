"""
Memory management for persistent chat history.
"""
import json
import os
from typing import List, Dict
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage


HISTORY_FILE = "chat_history.json"


def load_chat_history() -> List[Dict[str, str]]:
    """Load chat history from file."""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load chat history: {e}")
            return []
    return []


def save_chat_history(history: List[Dict[str, str]]):
    """Save chat history to file."""
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Warning: Could not save chat history: {e}")


def create_memory() -> ConversationBufferMemory:
    """
    Create a ConversationBufferMemory instance and load previous history if available.
    """
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="output"
    )
    
    # Load previous history
    history = load_chat_history()
    
    if history:
        print(f"✓ Loaded {len(history)} messages from chat history")
        
        # Restore messages to memory
        for msg in history:
            if msg["role"] == "user":
                memory.chat_memory.add_message(HumanMessage(content=msg["message"]))
            elif msg["role"] == "assistant":
                memory.chat_memory.add_message(AIMessage(content=msg["message"]))
    
    return memory


def log_interaction(user_message: str, assistant_message: str):
    """
    Log a user-assistant interaction to the persistent history.
    """
    history = load_chat_history()
    
    history.append({
        "role": "user",
        "message": user_message
    })
    
    history.append({
        "role": "assistant",
        "message": assistant_message
    })
    
    save_chat_history(history)


def clear_history():
    """Clear the chat history file."""
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)
        print("✓ Chat history cleared")

