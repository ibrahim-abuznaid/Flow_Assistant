"""
FastAPI backend for the AI Assistant.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os

from agent import get_agent
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
        
        # Run the agent
        print(f"\n{'='*60}")
        print(f"User: {user_message}")
        print(f"{'='*60}")
        
        result = agent.invoke({"input": user_message})
        assistant_reply = result.get("output", "I apologize, but I couldn't generate a response.")
        
        print(f"\nAssistant: {assistant_reply}")
        print(f"{'='*60}\n")
        
        # Log the interaction
        log_interaction(user_message, assistant_reply)
        
        return {"reply": assistant_reply}
    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}\n")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing your request: {str(e)}"
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

