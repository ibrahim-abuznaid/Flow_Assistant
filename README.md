# AI Assistant for ActivePieces

An intelligent assistant that helps users work with ActivePieces (workflow automation platform) using AI-powered knowledge retrieval and web search.

## 🚀 **Production Deployment Ready!**

**✨ [DEPLOYMENT COMPLETE!](docs/deployment/DEPLOYMENT_COMPLETE.md)** - See what's new!

**Deployment Guides:**
- 📑 **[Deployment Index](docs/deployment/DEPLOYMENT_INDEX.md)** ⭐ - Start here! Choose your deployment path
- 🐙 **[Deploy from GitHub](docs/deployment/GITHUB_CLONE_DEPLOY.md)** - Clone repo and deploy (30 min)
- 🚀 **[Quick Deploy](docs/deployment/QUICK_DEPLOY.md)** - TL;DR deployment (3 commands!)
- 📦 **[Complete Guide](docs/deployment/DEPLOYMENT_GUIDE.md)** - Full step-by-step guide (30 min)
- 📋 **[Deployment Summary](docs/deployment/DEPLOYMENT_SUMMARY.md)** - What's included in deployment

**Other Resources:**
- 🐙 **[GitHub Setup Guide](docs/setup/GITHUB_SETUP.md)** - Upload to GitHub safely
- ✅ **[Setup Summary](docs/setup/SETUP_SUMMARY.md)** - What's new and ready

## 🌟 Features

- **PostgreSQL Knowledge Base**: Fast, scalable database queries for ActivePieces integrations and actions
- **RAG (Retrieval Augmented Generation)**: Semantic search through vector database for contextual answers
- **Web Search**: OpenAI Responses API (default) or Perplexity for real-time information
- **Persistent Memory**: Remembers conversation context across sessions
- **Multiple LLM Support**: Works with OpenAI GPT, Anthropic Claude, and Google Gemini
- **Beautiful UI**: Modern React interface with real-time chat
- **🆕 Code Generation Tool**: Built-in guidelines for generating TypeScript code pieces following ActivePieces best practices

## 📊 Knowledge Base

- **433 Pieces** (integrations)
- **2,681 Actions**
- **694 Triggers**
- **PostgreSQL Backend**: Powered by Activepieces pieces database

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

```bash
# Run the setup script
python scripts/deployment/setup.py

# Configure your API keys in .env
# Then prepare the knowledge base
python scripts/migration/prepare_knowledge_base.py

# Start the backend
uvicorn src.main:app --reload

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
   - Copy `env.example` to `.env`
   - Add your `OPENAI_API_KEY` (required)
   - Web search will use OpenAI by default (set `SEARCH_PROVIDER=perplexity` to use Perplexity instead)

4. **Setup Database**:
   - SQLite database is used by default (stored in `data/activepieces.db`)
   - No additional database setup required!

5. **Prepare Knowledge Base** (Optional - for vector search):
   ```bash
   python scripts/migration/prepare_knowledge_base.py
   ```

6. **Test Setup**:
   ```bash
   python tests/test_assistant.py
   ```

7. **Run Backend**:
   ```bash
   uvicorn src.main:app --reload
   ```

8. **Run Frontend** (in a separate terminal):
   ```bash
   cd frontend
   npm run dev
   ```

9. **Open Browser**:
   Navigate to `http://localhost:5173`

## 📖 Documentation

**📚 [Complete Documentation Index](docs/INDEX.md)** - All 60+ docs organized and indexed!

### Setup & Installation
- **[Quick Start](docs/setup/QUICKSTART.md)**: Detailed setup and usage guide
- **[Installation Guide](docs/setup/INSTALLATION.md)**: Step-by-step installation
- **[GitHub Setup](docs/setup/GITHUB_SETUP.md)**: Version control setup

### Deployment
- **[Easy Deployment Guide](docs/deployment/EASY_DEPLOYMENT_GUIDE.md)**: Simple production deployment
- **[Deployment Checklist](docs/deployment/DEPLOYMENT_CHECKLIST.md)**: Pre-deployment checklist
- **[Quick Start Production](docs/deployment/QUICK_START_PRODUCTION.md)**: Fast production setup

### Features & Guides
- **[AI Assistant Build Guide](docs/features/ai_assistant_build_guide.md)**: Complete development guide
- **[Planning Layer Guide](docs/features/PLANNING_LAYER_GUIDE.md)**: Query planning system
- **[Real-time Status](docs/features/REAL_TIME_STATUS_FEATURE.md)**: Live status updates
- **🆕 [Code Generation Guide](docs/features/CODE_GENERATION_GUIDE.md)**: TypeScript code generation for flow steps
- **🆕 [Quick Code Reference](QUICK_CODE_GENERATION_REFERENCE.md)**: Quick reference for code generation

### Troubleshooting
- **[Troubleshooting](docs/troubleshooting/TROUBLESHOOTING.md)**: Common issues and solutions
- **[Database Fixes](docs/troubleshooting/FIX_DATABASE_CONNECTION.md)**: Database connection issues
- **[Model Errors](docs/troubleshooting/FIX_MODEL_ERROR.md)**: LLM configuration fixes

### Project Info
- **[Repository Structure](STRUCTURE.md)**: Detailed structure guide (start here!)
- **[Reorganization Complete](docs/REORGANIZATION_COMPLETE.md)**: See how we organized 83+ files! ✨
- **[Project Overview](docs/PROJECT_OVERVIEW.md)**: Complete project documentation
- **[Project Summary](docs/PROJECT_SUMMARY.md)**: Quick project summary

## 🔧 API Endpoints

- `POST /chat`: Send a message to the assistant
- `GET /health`: Check server status
- `POST /reset`: Clear conversation history
- `GET /stats`: Get knowledge base statistics

## 📁 Project Structure

```
Flow_Assistant/
├── src/                        # Main application code
│   ├── main.py                # FastAPI application
│   ├── agent.py               # LLM agent
│   ├── flow_builder.py        # Flow guide generator
│   ├── tools.py               # Tool definitions
│   ├── db_config.py           # Database configuration
│   ├── memory.py              # Conversation memory
│   └── llm_config.py          # LLM initialization
│
├── tests/                      # Test suite
│   ├── test_assistant.py      # Main test suite
│   └── test_sessions.py       # Session management tests
│
├── docs/                       # Documentation
│   ├── setup/                 # Setup guides
│   ├── deployment/            # Deployment guides
│   ├── troubleshooting/       # Fix guides
│   ├── features/              # Feature documentation
│   └── migration/             # Migration guides
│
├── scripts/                    # Utility scripts
│   ├── migration/             # Data migration scripts
│   ├── deployment/            # Deployment scripts
│   └── maintenance/           # Maintenance utilities
│
├── config/                     # Configuration files
│   ├── nginx.conf.template    # Nginx configuration
│   └── systemd/               # Service files
│
├── data/                       # Data files
│   ├── activepieces.db        # SQLite database
│   ├── ap_faiss_index/        # Vector store
│   ├── chat_sessions/         # Session storage
│   └── pieces_knowledge_base.json
│
├── frontend/                   # React UI
│   ├── src/
│   │   ├── App.jsx           # Main component
│   │   └── App.css           # Styles
│   └── package.json          # Dependencies
│
├── run.py                      # Application launcher
├── requirements.txt            # Python dependencies
├── env.example                # Environment template
├── README.md                  # This file
└── LICENSE                    # MIT License
```

## 💡 Example Usage

Ask the assistant questions like:

- "Does ActivePieces have a Slack integration?"
- "How can I send an email using ActivePieces?"
- "What actions are available for Google Sheets?"
- "Show me all triggers for Gmail"
- "How do I filter data in a workflow?"

### 🆕 Code Generation

Ask the assistant to generate TypeScript code for flow steps:

- "Create code to fetch user data from an API"
- "Generate code to filter an array of objects"
- "Write code to send a POST request with authentication"
- "Create code to transform JSON data"

The assistant will automatically provide properly formatted TypeScript code following ActivePieces best practices.

## 🔑 Configuration

### Environment Variables

```ini
# AI Configuration
OPENAI_API_KEY=your_key_here          # Required
MODEL_PROVIDER=openai                  # openai, anthropic, google
MODEL_NAME=gpt-4o                     # Model to use

# Web Search Configuration
SEARCH_PROVIDER=openai                 # openai (default) or perplexity
# PERPLEXITY_API_KEY=your_key_here    # Only if using perplexity

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

### Web Search Configuration

**OpenAI Search (Default)**:
```ini
SEARCH_PROVIDER=openai  # or omit this line (openai is default)
# Uses OpenAI Responses API with web_search tool
# No additional API key needed
```

**Perplexity Search (Alternative)**:
```ini
SEARCH_PROVIDER=perplexity
PERPLEXITY_API_KEY=your_perplexity_key
```

## 🛠️ Technology Stack

**Backend**:
- FastAPI - Web framework
- LangChain - LLM orchestration
- OpenAI - Language models, embeddings & web search (Responses API)
- PostgreSQL - Primary knowledge database
- psycopg3 - PostgreSQL adapter
- FAISS - Vector database for semantic search
- Perplexity - Optional alternative web search

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

**📖 [Complete Deployment Guide](docs/deployment/DEPLOYMENT_GUIDE.md)** - Step-by-step guide that covers:

- ✅ Fresh Ubuntu setup (22.04/24.04)
- ✅ Backend, Frontend, Database, Vector Store, RAG
- ✅ Nginx reverse proxy with SSL/HTTPS
- ✅ Systemd services for auto-restart
- ✅ Firewall and security configuration
- ✅ Troubleshooting and monitoring
- ✅ Performance optimization

**Quick Deploy Options**:

1. **From GitHub** (Recommended - 30 minutes):
   - **[DEPLOY_FROM_GITHUB.md](DEPLOY_FROM_GITHUB.md)** 👈 **Copy-paste commands!**
   - Clone your repo and deploy step-by-step
   - All commands ready to copy

2. **Automated** (One command):
   ```bash
   curl -fsSL https://raw.githubusercontent.com/yourusername/Flow_Assistant/main/scripts/deployment/deploy_digitalocean.sh | sudo bash
   ```

3. **Detailed Manual**:
   - See **[Complete Deployment Guide](docs/deployment/DEPLOYMENT_GUIDE.md)** for full walkthrough

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

