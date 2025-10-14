"""
Memory management for session-based chat history.
"""
import json
import os
from typing import List, Dict, Optional
from datetime import datetime
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage


SESSIONS_DIR = "data/chat_sessions"
SESSIONS_INDEX_FILE = "data/sessions_index.json"

# In-memory storage for current sessions (not persisted across server restarts)
_active_sessions = {}


def ensure_sessions_dir():
    """Ensure the sessions directory exists."""
    if not os.path.exists(SESSIONS_DIR):
        os.makedirs(SESSIONS_DIR)


def load_sessions_index() -> Dict:
    """Load the sessions index from file."""
    if os.path.exists(SESSIONS_INDEX_FILE):
        try:
            with open(SESSIONS_INDEX_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load sessions index: {e}")
            return {}
    return {}


def save_sessions_index(index: Dict):
    """Save the sessions index to file."""
    try:
        with open(SESSIONS_INDEX_FILE, "w", encoding="utf-8") as f:
            json.dump(index, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Warning: Could not save sessions index: {e}")


def create_session(session_id: str) -> Dict:
    """Create a new session."""
    ensure_sessions_dir()
    
    session_data = {
        "session_id": session_id,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "messages": []
    }
    
    # Save session file
    session_file = os.path.join(SESSIONS_DIR, f"{session_id}.json")
    try:
        with open(session_file, "w", encoding="utf-8") as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Warning: Could not create session file: {e}")
    
    # Update index
    index = load_sessions_index()
    index[session_id] = {
        "created_at": session_data["created_at"],
        "updated_at": session_data["updated_at"],
        "message_count": 0
    }
    save_sessions_index(index)
    
    return session_data


def load_session(session_id: str) -> Optional[Dict]:
    """Load a session by ID."""
    session_file = os.path.join(SESSIONS_DIR, f"{session_id}.json")
    if os.path.exists(session_file):
        try:
            with open(session_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load session {session_id}: {e}")
            return None
    return None


def save_session(session_data: Dict):
    """Save a session to file."""
    ensure_sessions_dir()
    
    session_id = session_data["session_id"]
    session_data["updated_at"] = datetime.now().isoformat()
    
    session_file = os.path.join(SESSIONS_DIR, f"{session_id}.json")
    try:
        with open(session_file, "w", encoding="utf-8") as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
        
        # Update index
        index = load_sessions_index()
        index[session_id] = {
            "created_at": session_data["created_at"],
            "updated_at": session_data["updated_at"],
            "message_count": len(session_data["messages"])
        }
        save_sessions_index(index)
    except Exception as e:
        print(f"Warning: Could not save session {session_id}: {e}")


def get_all_sessions() -> List[Dict]:
    """Get all sessions sorted by most recent."""
    index = load_sessions_index()
    sessions = []
    
    for session_id, metadata in index.items():
        # Load full session to get first message preview
        session_data = load_session(session_id)
        if session_data and session_data.get("messages"):
            first_message = session_data["messages"][0].get("message", "")[:100]
            sessions.append({
                "session_id": session_id,
                "created_at": metadata["created_at"],
                "updated_at": metadata["updated_at"],
                "message_count": metadata["message_count"],
                "preview": first_message
            })
    
    # Sort by updated_at (most recent first)
    sessions.sort(key=lambda x: x["updated_at"], reverse=True)
    return sessions


def create_memory(session_id: Optional[str] = None) -> ConversationBufferMemory:
    """
    Create a ConversationBufferMemory instance for a session.
    If session_id is None, creates an in-memory only session.
    """
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="output"
    )
    
    # Load session history if session_id provided
    if session_id:
        session_data = load_session(session_id)
        if session_data:
            messages = session_data.get("messages", [])
            if messages:
                print(f"✓ Loaded {len(messages)} messages for session {session_id}")
                
                # Restore messages to memory
                for msg in messages:
                    if msg["role"] == "user":
                        memory.chat_memory.add_message(HumanMessage(content=msg["message"]))
                    elif msg["role"] == "assistant":
                        memory.chat_memory.add_message(AIMessage(content=msg["message"]))
        else:
            # Create new session
            create_session(session_id)
            print(f"✓ Created new session {session_id}")
    
    return memory


def log_interaction(user_message: str, assistant_message: str, session_id: Optional[str] = None):
    """
    Log a user-assistant interaction to the session.
    If session_id is provided, saves to persistent storage.
    """
    if not session_id:
        return  # No persistence for sessions without ID
    
    # Load or create session
    session_data = load_session(session_id)
    if not session_data:
        session_data = create_session(session_id)
    
    # Add messages
    session_data["messages"].append({
        "role": "user",
        "message": user_message,
        "timestamp": datetime.now().isoformat()
    })
    
    session_data["messages"].append({
        "role": "assistant",
        "message": assistant_message,
        "timestamp": datetime.now().isoformat()
    })
    
    # Save session
    save_session(session_data)


def clear_session(session_id: str):
    """Clear a specific session."""
    session_file = os.path.join(SESSIONS_DIR, f"{session_id}.json")
    if os.path.exists(session_file):
        os.remove(session_file)
        
        # Update index
        index = load_sessions_index()
        if session_id in index:
            del index[session_id]
            save_sessions_index(index)
        
        print(f"✓ Session {session_id} cleared")


def delete_all_sessions():
    """Delete all sessions (for cleanup/reset)."""
    # Remove all session files
    if os.path.exists(SESSIONS_DIR):
        for file in os.listdir(SESSIONS_DIR):
            if file.endswith(".json"):
                os.remove(os.path.join(SESSIONS_DIR, file))
    
    # Clear index
    if os.path.exists(SESSIONS_INDEX_FILE):
        os.remove(SESSIONS_INDEX_FILE)
    
    print("✓ All sessions cleared")


# For backward compatibility with old system
def clear_history():
    """Clear old chat history file if it exists."""
    old_file = "data/chat_history.json"
    if os.path.exists(old_file):
        os.remove(old_file)
        print("✓ Old chat history cleared")

