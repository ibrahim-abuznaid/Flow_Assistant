"""
FastAPI backend for the AI Assistant.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import json
import asyncio
from queue import Queue
from threading import Thread
from typing import Any, Dict, Optional

from src.agent import get_agent, clear_agent_cache
from src.general_responder import generate_general_response
from src.memory import (
    log_interaction,
    clear_history,
    get_all_sessions,
    load_session,
    clear_session,
    create_memory,
    serialize_memory_to_chat_history,
)
from src.query_utils import is_activepieces_query

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="ActivePieces AI Assistant",
    description="An intelligent assistant for ActivePieces workflow automation platform",
    version="1.0.0"
)

# Configure CORS - support both development and production
# In production, set ALLOWED_ORIGINS env var: "https://yourdomain.com,https://www.yourdomain.com"
allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",") if os.getenv("ALLOWED_ORIGINS") else [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://localhost:5000",
]

# Remove empty strings from the list
allowed_origins = [origin.strip() for origin in allowed_origins if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    build_flow_mode: Optional[bool] = False


class ChatResponse(BaseModel):
    reply: str


class ErrorResponse(BaseModel):
    error: str


class HealthResponse(BaseModel):
    status: str
    message: str


def _get_recent_history_messages(session_id: Optional[str], limit: int = 8) -> list[str]:
    """Fetch up to `limit` most recent message strings for context-aware routing."""
    if not session_id:
        return []

    try:
        session_data = load_session(session_id)
    except Exception:
        return []

    if not session_data:
        return []

    messages = session_data.get("messages", [])
    if not messages:
        return []

    recent = messages[-limit:]
    return [msg.get("message", "") for msg in recent if msg.get("message")]


# Custom callback handler for tracking agent status
from langchain.callbacks.base import BaseCallbackHandler
from threading import Event

class CancellationException(Exception):
    """Exception raised when request is cancelled."""
    pass

class StatusCallbackHandler(BaseCallbackHandler):
    """Callback handler that tracks agent status and emits updates."""
    
    def __init__(self, status_queue: Queue, cancellation_event: Event):
        self.status_queue = status_queue
        self.cancellation_event = cancellation_event
        self.cancellation_logged = False
    
    def _check_cancellation(self):
        """Check if the request has been cancelled and raise exception if so."""
        if self.cancellation_event.is_set():
            if not self.cancellation_logged:
                print("⚠️  Agent execution cancelled by client")
                self.cancellation_logged = True
            raise CancellationException("Request cancelled by client")
    
    def on_agent_action(self, action: Any, **kwargs) -> None:
        """Called when agent takes an action (uses a tool)."""
        try:
            # Check for cancellation before tool execution
            self._check_cancellation()
            
            tool_name = action.tool
            tool_input = action.tool_input
            
            # Map tool names to friendly status messages
            status_messages = {
                "check_activepieces_tool": "🔍 Checking ActivePieces database...",
                "search_activepieces_docs_tool": "📚 Searching knowledge base...",
                "web_search_tool": "🌐 Searching the web...",
                "get_code_generation_guidelines_tool": "📝 Getting code guidelines..."
            }
            
            status = status_messages.get(tool_name, f"⚙️ Using {tool_name}...")
            self.status_queue.put({"type": "status", "message": status, "tool": tool_name})
        except CancellationException:
            raise  # Re-raise to stop execution
    
    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs) -> None:
        """Called when tool starts."""
        try:
            self._check_cancellation()
        except CancellationException:
            raise
    
    def on_tool_end(self, output: str, **kwargs) -> None:
        """Called when a tool finishes."""
        try:
            self._check_cancellation()
            self.status_queue.put({"type": "status", "message": "💭 Thinking...", "tool": None})
        except CancellationException:
            raise
    
    def on_llm_start(self, serialized: Dict[str, Any], prompts: list[str], **kwargs) -> None:
        """Called when LLM starts."""
        try:
            self._check_cancellation()
        except CancellationException:
            raise
    
    def on_agent_finish(self, finish: Any, **kwargs) -> None:
        """Called when agent finishes."""
        try:
            if not self.cancellation_event.is_set():
                self.status_queue.put({"type": "status", "message": "✨ Finalizing response...", "tool": None})
        except Exception:
            pass  # Ignore errors during finish


@app.on_event("startup")
async def startup_event():
    """Initialize the agent and knowledge base on startup."""
    print("\n" + "="*60)
    print("🚀 Starting ActivePieces AI Assistant")
    print("="*60)
    
    # Check if vector store exists
    if not os.path.exists("data/ap_faiss_index"):
        print("\n⚠️  WARNING: Vector store not found!")
        print("Please run: python scripts/migration/prepare_knowledge_base.py")
        print("="*60 + "\n")
    else:
        print("✓ Vector store found")
    
    # Initialize agent (lazy loading will happen on first request)
    print("✓ Agent initialization ready")
    print("="*60 + "\n")


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint."""
    return {
        "status": "ok",
        "message": "ActivePieces AI Assistant API is running"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "message": "Service is operational"
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint. Accepts a user message and returns the assistant's response.
    """
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    user_message = request.message.strip()
    session_id = request.session_id
    build_flow_mode = request.build_flow_mode
    history_context = _get_recent_history_messages(session_id)
    is_ap_query = is_activepieces_query(user_message, history=history_context)
    
    try:
        print(f"\n{'='*60}")
        print(f"User: {user_message}")
        print(f"Build Flow Mode: {build_flow_mode}")
        print(f"{'='*60}")

        if not is_ap_query:
            print("Detected general query - using lightweight responder")
            assistant_reply = generate_general_response(user_message, session_id=session_id)
            print(f"\nAssistant (general): {assistant_reply}")
            print(f"{'='*60}\n")
            log_interaction(user_message, assistant_reply, session_id=session_id)
            return {"reply": assistant_reply}
        agent = get_agent(session_id=session_id)
        result = agent.invoke({"input": user_message})
        assistant_reply = result.get("output", "I apologize, but I couldn't generate a response.")
        
        print(f"\nAssistant: {assistant_reply}")
        print(f"{'='*60}\n")
        
        # Log the interaction (with original query, not enhanced)
        log_interaction(user_message, assistant_reply, session_id=session_id)
        
        return {"reply": assistant_reply}
    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}\n")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing your request: {str(e)}"
        )


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Streaming chat endpoint. Accepts a user message and streams status updates and response.
    """
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    user_message = request.message.strip()
    user_session_id = request.session_id  # Capture session_id from request
    build_flow_mode = request.build_flow_mode  # Capture build_flow_mode from request
    history_context = _get_recent_history_messages(user_session_id)
    is_ap_query = is_activepieces_query(user_message, history=history_context)

    if not is_ap_query:
        print(f"\n{'='*60}")
        print(f"User: {user_message}")
        print(f"Build Flow Mode: {build_flow_mode}")
        print("Detected general query - answering without workflow tools")
        print(f"{'='*60}")
        async def general_event_generator():
            status_payload = {
                "type": "status",
                "message": "�Y'� Answering directly...",
                "tool": None
            }
            yield f"data: {json.dumps(status_payload, ensure_ascii=False)}\n\n"

            try:
                reply = generate_general_response(user_message, session_id=user_session_id)
            except Exception as e:
                reply = f"Sorry, I couldn't generate an answer because: {e}"

            log_interaction(user_message, reply, session_id=user_session_id)

            print(f"\nAssistant (general): {reply}")
            print(f"{'='*60}\n")

            done_payload = {"type": "done", "reply": reply}
            yield f"data: {json.dumps(done_payload, ensure_ascii=False)}\n\n"

        return StreamingResponse(
            general_event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
    
    async def event_generator():
        from threading import Event
        
        status_queue = Queue()
        result_container = {"output": None, "error": None}
        cancellation_event = Event()  # Used to signal cancellation to agent
        
        CHUNK_THRESHOLD = 6000
        CHUNK_SIZE = 3000

        def enqueue_reply(reply: str):
            """Send reply to client using chunked updates if necessary."""
            if reply is None:
                status_queue.put({"type": "done"})
                return

            if len(reply) > CHUNK_THRESHOLD:
                total_chunks = (len(reply) + CHUNK_SIZE - 1) // CHUNK_SIZE
                status_queue.put({"type": "chunk_start", "total_chunks": total_chunks})

                for idx in range(total_chunks):
                    start = idx * CHUNK_SIZE
                    end = start + CHUNK_SIZE
                    chunk = reply[start:end]
                    status_queue.put({
                        "type": "chunk",
                        "data": chunk,
                        "index": idx,
                        "total": total_chunks
                    })

                status_queue.put({"type": "chunk_end"})
                status_queue.put({"type": "done"})
            else:
                status_queue.put({"type": "done", "reply": reply})

        def run_agent():
            try:
                print(f"\n{'='*60}")
                print(f"User: {user_message}")
                print(f"Build Flow Mode: {build_flow_mode}")
                print(f"{'='*60}")
                
                if build_flow_mode:
                    from src.flow_builder import build_flow

                    status_queue.put({"type": "status", "message": "🚀 Starting Flow Builder...", "tool": None})
                    status_queue.put({"type": "status", "message": "🔍 Analyzing your flow request...", "tool": None})

                    contextual_request = user_message
                    if user_session_id:
                        try:
                            memory_snapshot = create_memory(session_id=user_session_id)
                            history_items = serialize_memory_to_chat_history(memory_snapshot, limit=8)
                        except Exception:
                            history_items = []

                        if history_items:
                            formatted_history = "\n".join(
                                f"{item['role'].upper()}: {item['content']}"
                                for item in history_items
                            )
                            contextual_request = (
                                "Continue assisting the user based on this conversation history:\n"
                                f"{formatted_history}\n\n"
                                f"Latest user request: {user_message}\n"
                                "Provide an updated or additional flow guide that respects the ongoing context."
                            )

                    flow_result = build_flow(contextual_request)
                    clarifying_questions = flow_result.get("clarifying_questions", [])
                    assistant_reply = flow_result.get("guide", "I apologize, but I couldn't generate a flow guide.")

                    if clarifying_questions:
                        optional_questions = [q for q in clarifying_questions if q.get("optional", True)]
                        if optional_questions:
                            questions_text = "\n\n---\n\n**💡 Optional Clarifications** (you can provide these for more specific guidance):\n\n"
                            for i, q in enumerate(optional_questions, 1):
                                questions_text += f"{i}. {q.get('question', '')}\n"
                            assistant_reply += questions_text

                    result_container["output"] = assistant_reply

                    print(f"\nFlow Guide Generated (length: {len(assistant_reply)})")
                    print(f"{'='*60}\n")

                    log_interaction(user_message, assistant_reply, session_id=user_session_id)
                    enqueue_reply(assistant_reply)

                else:
                    callback = StatusCallbackHandler(status_queue, cancellation_event)
                    status_queue.put({"type": "status", "message": "🚀 Starting...", "tool": None})
                    status_queue.put({"type": "status", "message": "🤖 Processing query...", "tool": None})

                    agent = get_agent(session_id=user_session_id)
                    result = agent.invoke({"input": user_message}, config={"callbacks": [callback]})

                    assistant_reply = result.get("output", "I apologize, but I couldn't generate a response.")
                    result_container["output"] = assistant_reply

                    print(f"\nAssistant: {assistant_reply}")
                    print(f"{'='*60}\n")

                    log_interaction(user_message, assistant_reply, session_id=user_session_id)
                    enqueue_reply(assistant_reply)

            except CancellationException:
                print("✓ Agent execution stopped successfully")
                status_queue.put({"type": "cancelled", "message": "Request cancelled"})

            except Exception as e:
                if "cancel" in str(e).lower() or cancellation_event.is_set():
                    print("✓ Agent execution stopped successfully")
                    status_queue.put({"type": "cancelled", "message": "Request cancelled"})
                else:
                    print(f"\n⚠️ Error: {str(e)}\n")
                    result_container["error"] = str(e)
                    status_queue.put({"type": "error", "message": str(e)})
        # Start agent in background thread
        agent_thread = Thread(target=run_agent, daemon=True)
        agent_thread.start()
        
        # Stream status updates
        try:
            client_disconnected = False
            while True:
                # Check if there are updates
                if not status_queue.empty():
                    update = status_queue.get()
                    
                    try:
                        yield f"data: {json.dumps(update, ensure_ascii=False)}\n\n"
                    except (GeneratorExit, StopAsyncIteration):
                        # Client disconnected - signal cancellation
                        print("🛑 Client disconnected - cancelling agent execution")
                        cancellation_event.set()
                        client_disconnected = True
                        break
                    
                    # Break if done, error, or cancelled
                    if update["type"] in ["done", "error", "cancelled"]:
                        break
                else:
                    # Small delay to prevent busy waiting
                    await asyncio.sleep(0.1)
                    
                    # Check if thread is still alive
                    if not agent_thread.is_alive() and status_queue.empty():
                        break
            
            if client_disconnected:
                print("⏳ Waiting for agent thread to stop...")
                agent_thread.join(timeout=2)  # Wait up to 2 seconds
                if agent_thread.is_alive():
                    print("⚠️  Agent thread still running after cancellation")
                else:
                    print("✓ Agent thread stopped successfully")
        
        except GeneratorExit:
            # Client disconnected - signal cancellation
            print("🛑 Client disconnected (GeneratorExit) - cancelling agent execution")
            cancellation_event.set()
            agent_thread.join(timeout=2)
        
        finally:
            # Ensure cancellation is signaled
            if not cancellation_event.is_set():
                cancellation_event.set()
            
            # Give thread a moment to stop
            if agent_thread.is_alive():
                agent_thread.join(timeout=1)
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@app.post("/reset")
async def reset_conversation():
    """
    Reset the conversation by clearing chat history.
    """
    try:
        clear_history()
        
        # Reset cached agent executors to ensure a clean slate
        clear_agent_cache()
        
        return {
            "status": "success",
            "message": "Conversation history has been cleared"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error clearing history: {str(e)}"
        )


@app.get("/sessions")
async def list_sessions():
    """
    Get all chat sessions with metadata.
    """
    try:
        sessions = get_all_sessions()
        return {"sessions": sessions}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving sessions: {str(e)}"
        )


@app.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """
    Get a specific session's full chat history.
    """
    try:
        session_data = load_session(session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")
        return session_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving session: {str(e)}"
        )


@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """
    Delete a specific session.
    """
    try:
        clear_session(session_id)
        clear_agent_cache(session_id=session_id)
        return {"status": "success", "message": f"Session {session_id} deleted"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting session: {str(e)}"
        )


@app.get("/stats")
async def get_stats():
    """
    Get statistics about the knowledge base from SQLite database.
    """
    try:
        import sqlite3
        import os
        from datetime import datetime
        
        # Connect to the activepieces database
        db_path = os.path.join('activepieces-pieces-db', 'activepieces-pieces.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get counts from database
        cursor.execute('SELECT COUNT(*) FROM pieces')
        total_pieces = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM actions')
        total_actions = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM triggers')
        total_triggers = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_pieces": total_pieces,
            "total_actions": total_actions,
            "total_triggers": total_triggers,
            "generated_at": datetime.now().isoformat(),
            "version": "2.0.0"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving stats: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
