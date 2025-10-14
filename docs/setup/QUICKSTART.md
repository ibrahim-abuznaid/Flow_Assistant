# Quick Start Guide

This guide will help you get the ActivePieces AI Assistant up and running quickly.

## Prerequisites

- Python 3.9 or higher
- Node.js 16+ and npm (for frontend)
- OpenAI API key (required)
- Perplexity API key (optional, for web search)

## Step 1: Setup

Run the automated setup script:

```bash
python setup.py
```

This will:
- Check Python version
- Create `.env` file from template
- Install Python dependencies
- Install frontend dependencies

## Step 2: Configure API Keys

Edit the `.env` file and add your API keys:

```ini
OPENAI_API_KEY=sk-your-actual-openai-key-here
PERPLEXITY_API_KEY=your-perplexity-key-here  # Optional
MODEL_PROVIDER=openai
MODEL_NAME=gpt-4-turbo-preview
```

## Step 3: Prepare Knowledge Base

Create the vector store from the Pieces knowledge base:

```bash
python prepare_knowledge_base.py
```

This will:
- Load the `pieces_knowledge_base.json` file
- Create embeddings for all pieces, actions, and triggers
- Save the FAISS vector store to `ap_faiss_index/`

**Note:** This step requires an OpenAI API key and will make API calls to create embeddings. It may take a few minutes depending on the size of your knowledge base.

## Step 4: Run the Backend

Start the FastAPI server:

```bash
uvicorn main:app --reload
```

The backend will be available at: `http://localhost:8000`

You can test it by visiting:
- `http://localhost:8000/health` - Health check
- `http://localhost:8000/stats` - Knowledge base statistics

## Step 5: Run the Frontend

In a new terminal, start the React development server:

```bash
cd frontend
npm run dev
```

The frontend will be available at: `http://localhost:5173`

## Usage

1. Open your browser to `http://localhost:5173`
2. Start chatting with the AI assistant!

### Example Questions

Try asking:
- "Does ActivePieces have a Slack integration?"
- "How can I send an email using ActivePieces?"
- "What actions are available for Google Sheets?"
- "Show me all triggers for Gmail"
- "How do I filter data in a workflow?"

## API Endpoints

### POST /chat
Send a message to the assistant:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Does ActivePieces have a Slack integration?"}'
```

### POST /reset
Clear conversation history:

```bash
curl -X POST http://localhost:8000/reset
```

### GET /stats
Get knowledge base statistics:

```bash
curl http://localhost:8000/stats
```

## Troubleshooting

### "Vector store not found" error
- Make sure you ran `python prepare_knowledge_base.py`
- Check that `ap_faiss_index/` directory exists

### "OpenAI API key not found" error
- Verify your `.env` file has `OPENAI_API_KEY` set
- Make sure the key is valid and has credits

### Frontend can't connect to backend
- Ensure the backend is running on port 8000
- Check CORS settings in `main.py`
- Verify the API_BASE_URL in `frontend/src/App.jsx`

### Import errors
- Make sure you installed all dependencies: `pip install -r requirements.txt`
- Try creating a fresh virtual environment

## Project Structure

```
.
├── main.py                      # FastAPI backend
├── agent.py                     # Agent configuration
├── tools.py                     # Tool definitions
├── memory.py                    # Memory persistence
├── llm_config.py               # LLM initialization
├── prepare_knowledge_base.py   # Knowledge base setup
├── pieces_knowledge_base.json  # ActivePieces data
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (create this)
├── chat_history.json          # Conversation history (auto-created)
├── ap_faiss_index/            # Vector store (auto-created)
└── frontend/                  # React UI
    ├── src/
    │   ├── App.jsx           # Main React component
    │   ├── App.css           # Styles
    │   └── main.jsx          # Entry point
    └── package.json          # Frontend dependencies
```

## Advanced Configuration

### Using Different LLM Providers

#### Anthropic Claude
```ini
MODEL_PROVIDER=anthropic
MODEL_NAME=claude-3-opus-20240229
ANTHROPIC_API_KEY=your-anthropic-key
```

Install: `pip install langchain-anthropic`

#### Google Gemini
```ini
MODEL_PROVIDER=google
MODEL_NAME=gemini-pro
GOOGLE_API_KEY=your-google-key
```

Install: `pip install langchain-google-genai`

### Customizing the Agent

Edit `agent.py` to modify:
- System prompt
- Agent behavior
- Tool usage
- Memory settings

### Customizing the UI

Edit `frontend/src/App.jsx` and `frontend/src/App.css` to:
- Change colors and styling
- Add new features
- Modify layout

## Next Steps

- Explore the codebase to understand how it works
- Customize the system prompt in `agent.py`
- Add more tools in `tools.py`
- Enhance the UI in `frontend/src/`
- Deploy to production (see deployment guide)

## Support

For issues or questions:
1. Check the main README.md
2. Review the build guide: `ai_assistant_build_guide.md`
3. Check the code comments for detailed explanations

Happy automating! 🚀

