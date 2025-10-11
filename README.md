# AI Assistant for ActivePieces

An intelligent assistant that helps users work with ActivePieces (workflow automation platform) using AI-powered knowledge retrieval and web search.

## 🚀 **NEW: Production Deployment Ready!**

**Quick Links:**
- 📦 **[Deploy to Ubuntu in 15 min](QUICK_START_PRODUCTION.md)** ⭐ 
- 📚 **[Deployment Guide Index](DEPLOYMENT_GUIDE_INDEX.md)** - All deployment docs
- 🐙 **[GitHub Setup Guide](GITHUB_SETUP.md)** - Upload to GitHub safely
- ✅ **[Setup Summary](SETUP_SUMMARY.md)** - What's new and ready

## 🌟 Features

- **PostgreSQL Knowledge Base**: Fast, scalable database queries for ActivePieces integrations and actions
- **RAG (Retrieval Augmented Generation)**: Semantic search through vector database for contextual answers
- **Web Search**: Integration with Perplexity API for real-time information
- **Persistent Memory**: Remembers conversation context across sessions
- **Multiple LLM Support**: Works with OpenAI GPT, Anthropic Claude, and Google Gemini
- **Beautiful UI**: Modern React interface with real-time chat

## 📊 Knowledge Base

- **433 Pieces** (integrations)
- **2,681 Actions**
- **694 Triggers**
- **PostgreSQL Backend**: Powered by Activepieces pieces database

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

```bash
# Run the setup script
python setup.py

# Configure your API keys in .env
# Then prepare the knowledge base
python prepare_knowledge_base.py

# Start the backend
uvicorn main:app --reload

# In a new terminal, start the frontend
cd frontend
npm run dev
```

### Option 2: Manual Setup

1. **Create Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   cd frontend
   npm install
   cd ..
   ```

3. **Configure Environment**:
   - Copy `.env.example` to `.env`
   - Add your API keys (OpenAI required, Perplexity optional)
   - Configure PostgreSQL connection (see below)

4. **Setup PostgreSQL Database**:
   - Ensure PostgreSQL is running on `localhost:5433`
   - Database should be configured per `AGENT_CONNECTION_GUIDE.md`
   - Default connection: `postgresql://postgres:7777@localhost:5433/activepieces_pieces`

5. **Prepare Knowledge Base** (Optional - for vector search):
   ```bash
   python prepare_knowledge_base.py
   ```

6. **Test Database Connection**:
   ```bash
   python db_config.py
   ```

7. **Run Backend**:
   ```bash
   uvicorn main:app --reload
   ```

8. **Run Frontend** (in a separate terminal):
   ```bash
   cd frontend
   npm run dev
   ```

9. **Open Browser**:
   Navigate to `http://localhost:5173`

## 📖 Documentation

- **[QUICKSTART.md](QUICKSTART.md)**: Detailed setup and usage guide
- **[ai_assistant_build_guide.md](ai_assistant_build_guide.md)**: Complete development guide
- **[POSTGRES_MIGRATION.md](POSTGRES_MIGRATION.md)**: PostgreSQL integration details
- **[AGENT_CONNECTION_GUIDE.md](AGENT_CONNECTION_GUIDE.md)**: Database connection guide

## 🔧 API Endpoints

- `POST /chat`: Send a message to the assistant
- `GET /health`: Check server status
- `POST /reset`: Clear conversation history
- `GET /stats`: Get knowledge base statistics

## 📁 Project Structure

```
.
├── main.py                      # FastAPI application
├── agent.py                     # LLM agent setup
├── tools.py                     # Tool definitions (check, search, web)
├── db_config.py                 # PostgreSQL connection manager
├── memory.py                    # Memory persistence
├── llm_config.py               # LLM initialization
├── prepare_knowledge_base.py   # Vector store preparation
├── setup.py                    # Automated setup script
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
├── POSTGRES_MIGRATION.md       # PostgreSQL migration docs
├── AGENT_CONNECTION_GUIDE.md   # Database connection guide
└── frontend/                  # React UI
    ├── src/
    │   ├── App.jsx           # Main component
    │   └── App.css           # Styles
    └── package.json          # Frontend dependencies
```

## 💡 Example Usage

Ask the assistant questions like:

- "Does ActivePieces have a Slack integration?"
- "How can I send an email using ActivePieces?"
- "What actions are available for Google Sheets?"
- "Show me all triggers for Gmail"
- "How do I filter data in a workflow?"

## 🔑 Configuration

### Environment Variables

```ini
# AI Configuration
OPENAI_API_KEY=your_key_here          # Required
PERPLEXITY_API_KEY=your_key_here      # Optional
MODEL_PROVIDER=openai                  # openai, anthropic, google
MODEL_NAME=gpt-4-turbo-preview        # Model to use

# Database Configuration (Optional - uses defaults if not set)
DB_HOST=localhost                      # Default: localhost
DB_PORT=5433                          # Default: 5433
DB_NAME=activepieces_pieces           # Default: activepieces_pieces
DB_USER=postgres                      # Default: postgres
DB_PASSWORD=7777                      # Default: 7777
```

### Switching LLM Providers

**OpenAI (Default)**:
```ini
MODEL_PROVIDER=openai
MODEL_NAME=gpt-4-turbo-preview
```

**Anthropic Claude**:
```ini
MODEL_PROVIDER=anthropic
MODEL_NAME=claude-3-opus-20240229
ANTHROPIC_API_KEY=your_key
```

**Google Gemini**:
```ini
MODEL_PROVIDER=google
MODEL_NAME=gemini-pro
GOOGLE_API_KEY=your_key
```

## 🛠️ Technology Stack

**Backend**:
- FastAPI - Web framework
- LangChain - LLM orchestration
- OpenAI - Language models & embeddings
- PostgreSQL - Primary knowledge database
- psycopg3 - PostgreSQL adapter
- FAISS - Vector database for semantic search
- Perplexity - Web search

**Frontend**:
- React - UI framework
- Vite - Build tool
- Axios - HTTP client

## 🤝 Contributing

This project was built following the guide in `ai_assistant_build_guide.md`. Feel free to extend it with:

- Additional tools
- More LLM providers
- Enhanced UI features
- Better error handling
- Streaming responses

## 🚢 Deployment

### Local Development
See the **Quick Start** section above for local development setup.

### Production Deployment (Ubuntu/DigitalOcean)

For deploying to a production Ubuntu server (DigitalOcean, AWS, etc.):

1. **See [DEPLOYMENT.md](DEPLOYMENT.md)** for comprehensive deployment guide
2. **Quick Deploy**: Use the automated deployment script:
   ```bash
   sudo ./deploy_ubuntu.sh
   ```

The deployment includes:
- ✅ Nginx reverse proxy configuration
- ✅ Systemd services for auto-restart
- ✅ SSL/HTTPS setup guide (Let's Encrypt)
- ✅ PostgreSQL database setup
- ✅ Firewall configuration
- ✅ Production optimization tips

### GitHub Repository Setup

Before pushing to GitHub:

1. **Ensure `.env` is not tracked:**
   ```bash
   git status  # .env should not appear
   ```

2. **Configure your repository:**
   ```bash
   git remote add origin https://github.com/yourusername/Flow_Assistant.git
   ```

3. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push -u origin main
   ```

4. **Configure environment variables** on your server using `.env.example` as a template

### Environment Setup for Deployment

1. Copy `.env.example` to `.env`
2. Fill in your API keys and database credentials
3. Never commit `.env` to version control!

## 📝 License

MIT License - feel free to use this project for your own purposes!

## 🙏 Acknowledgments

Built with:
- [LangChain](https://langchain.com) - LLM framework
- [FastAPI](https://fastapi.tiangolo.com) - Web framework
- [React](https://react.dev) - UI library
- [ActivePieces](https://activepieces.com) - Workflow automation platform

