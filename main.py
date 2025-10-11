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
from typing import Any, Dict

from agent import get_agent, run_agent_with_planning
from memory import log_interaction, clear_history

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


class ChatResponse(BaseModel):
    reply: str


class ErrorResponse(BaseModel):
    error: str


class HealthResponse(BaseModel):
    status: str
    message: str


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
    
    def _check_cancellation(self):
        """Check if the request has been cancelled and raise exception if so."""
        if self.cancellation_event.is_set():
            print("⚠️  Agent execution cancelled by client")
            raise CancellationException("Request cancelled by client")
    
    def on_agent_action(self, action: Any, **kwargs) -> None:
        """Called when agent takes an action (uses a tool)."""
        # Check for cancellation before tool execution
        self._check_cancellation()
        
        tool_name = action.tool
        tool_input = action.tool_input
        
        # Map tool names to friendly status messages
        status_messages = {
            "check_activepieces": "🔍 Checking ActivePieces database...",
            "search_activepieces_docs": "📚 Searching knowledge base...",
            "web_search": "🌐 Searching the web..."
        }
        
        status = status_messages.get(tool_name, f"⚙️ Using {tool_name}...")
        self.status_queue.put({"type": "status", "message": status, "tool": tool_name})
    
    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs) -> None:
        """Called when tool starts."""
        # Check for cancellation before tool starts
        self._check_cancellation()
    
    def on_tool_end(self, output: str, **kwargs) -> None:
        """Called when a tool finishes."""
        # Check for cancellation after tool execution
        self._check_cancellation()
        self.status_queue.put({"type": "status", "message": "💭 Thinking...", "tool": None})
    
    def on_llm_start(self, serialized: Dict[str, Any], prompts: list[str], **kwargs) -> None:
        """Called when LLM starts."""
        # Check for cancellation before LLM call
        self._check_cancellation()
    
    def on_agent_finish(self, finish: Any, **kwargs) -> None:
        """Called when agent finishes."""
        self.status_queue.put({"type": "status", "message": "✨ Finalizing response...", "tool": None})


@app.on_event("startup")
async def startup_event():
    """Initialize the agent and knowledge base on startup."""
    print("\n" + "="*60)
    print("🚀 Starting ActivePieces AI Assistant")
    print("="*60)
    
    # Check if vector store exists
    if not os.path.exists("ap_faiss_index"):
        print("\n⚠️  WARNING: Vector store not found!")
        print("Please run: python prepare_knowledge_base.py")
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
    
    try:
        # Get the agent
        agent = get_agent()
        
        # Run the agent with planning layer
        print(f"\n{'='*60}")
        print(f"User: {user_message}")
        print(f"{'='*60}")
        
        result = run_agent_with_planning(user_message, agent)
        assistant_reply = result.get("output", "I apologize, but I couldn't generate a response.")
        
        print(f"\nAssistant: {assistant_reply}")
        print(f"{'='*60}\n")
        
        # Log the interaction (with original query, not enhanced)
        log_interaction(user_message, assistant_reply)
        
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
    
    async def event_generator():
        from threading import Event
        
        status_queue = Queue()
        result_container = {"output": None, "error": None}
        cancellation_event = Event()  # Used to signal cancellation to agent
        
        def run_agent():
            try:
                # Get the agent
                agent = get_agent()
                
                # Create callback handler with cancellation support
                callback = StatusCallbackHandler(status_queue, cancellation_event)
                
                # Send initial status
                status_queue.put({"type": "status", "message": "🚀 Starting...", "tool": None})
                
                # Add planning status
                status_queue.put({"type": "status", "message": "🧠 Planning query execution...", "tool": None})
                
                # Run the agent with planning layer
                print(f"\n{'='*60}")
                print(f"User: {user_message}")
                print(f"{'='*60}")
                
                # Import planner for guided input
                from planner import create_guided_input
                guided_input = create_guided_input(user_message)
                
                # Execute agent with enhanced input and callbacks
                result = agent.invoke(
                    {"input": guided_input["enhanced_input"]},
                    config={"callbacks": [callback]}
                )
                
                assistant_reply = result.get("output", "I apologize, but I couldn't generate a response.")
                result_container["output"] = assistant_reply
                
                print(f"\nAssistant: {assistant_reply}")
                print(f"{'='*60}\n")
                
                # Log the interaction (with original query)
                log_interaction(user_message, assistant_reply)
                
                # Signal completion
                status_queue.put({"type": "done", "reply": assistant_reply})
                
            except CancellationException:
                # Request was cancelled - don't log as error
                print(f"✓ Agent execution stopped successfully")
                status_queue.put({"type": "cancelled", "message": "Request cancelled"})
                
            except Exception as e:
                # Check if it's a cancellation-related error
                if "cancel" in str(e).lower() or cancellation_event.is_set():
                    print(f"✓ Agent execution stopped successfully")
                    status_queue.put({"type": "cancelled", "message": "Request cancelled"})
                else:
                    print(f"\n❌ Error: {str(e)}\n")
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
                        yield f"data: {json.dumps(update)}\n\n"
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
        
        # Reset the agent by clearing the global instance
        from agent import _agent
        if _agent is not None:
            _agent.memory.clear()
        
        return {
            "status": "success",
            "message": "Conversation history has been cleared"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error clearing history: {str(e)}"
        )


@app.get("/stats")
async def get_stats():
    """
    Get statistics about the knowledge base.
    """
    try:
        import json
        
        with open("pieces_knowledge_base.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        metadata = data.get("metadata", {})
        
        return {
            "total_pieces": metadata.get("totalPieces", 0),
            "total_actions": metadata.get("totalActions", 0),
            "total_triggers": metadata.get("totalTriggers", 0),
            "generated_at": metadata.get("generatedAt", ""),
            "version": metadata.get("version", "")
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

