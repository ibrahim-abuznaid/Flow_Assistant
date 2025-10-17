"""
Lightweight responder for generic, non-ActivePieces queries.
Preserves session context so follow-up questions remain coherent.
"""
from typing import Any, List, Optional
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from langchain_core.messages import BaseMessage

from src.llm_config import get_llm
from src.memory import create_memory

GENERAL_SYSTEM_PROMPT = (
    "You are a friendly, concise assistant handling general questions that are "
    "not related to ActivePieces or workflow automation. Conversation snippets "
    "from this session appear before the latest user query. Use them to maintain "
    "context, remember names, and stay consistent. If the question is nonsensical "
    "or you do not have enough information, reply briefly and say so. Keep responses "
    "under four sentences unless the user explicitly asks for more detail."
)


def _extract_content(message: Optional[Any]) -> str:
    if message is None:
        return ""
    content = getattr(message, "content", "")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict):
                parts.append(str(item.get("text") or item.get("content") or ""))
            else:
                parts.append(str(item))
        return " ".join(part for part in parts if part).strip()
    return str(content)


def _get_recent_history(session_id: Optional[str], limit: int = 8) -> List[BaseMessage]:
    if not session_id:
        return []

    try:
        memory = create_memory(session_id=session_id)
    except Exception:
        return []

    chat_memory = getattr(memory, "chat_memory", None)
    if chat_memory is None:
        return []

    messages: List[BaseMessage] = getattr(chat_memory, "messages", [])
    if not messages:
        return []

    recent = messages[-limit:]
    history: List[BaseMessage] = []

    for message in recent:
        text = _extract_content(message)
        if not text:
            continue
        if isinstance(message, HumanMessage):
            history.append(HumanMessage(content=text))
        elif isinstance(message, AIMessage):
            history.append(AIMessage(content=text))

    return history


def generate_general_response(user_query: str, session_id: Optional[str] = None) -> str:
    """
    Generate a concise reply for a generic question using the configured LLM.
    """
    llm = get_llm()
    messages: List[BaseMessage] = [SystemMessage(content=GENERAL_SYSTEM_PROMPT)]
    messages.extend(_get_recent_history(session_id))
    messages.append(HumanMessage(content=user_query))

    result = llm.invoke(messages)
    response_text = _extract_content(result).strip()
    return response_text or "I'm here! Let me know how I can help."
