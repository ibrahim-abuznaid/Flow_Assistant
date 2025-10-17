# 🏗️ Architecture Overview

Understanding what you're deploying and how all the pieces fit together.

---

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User's Browser                          │
│                    (https://yourdomain.com)                     │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTPS (443)
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                          Nginx                                  │
│                    (Reverse Proxy + SSL)                        │
│                                                                 │
│  ┌──────────────────┐           ┌────────────────────────┐    │
│  │  Static Files    │           │    API Proxy           │    │
│  │  /               │           │    /api/               │    │
│  │  (React SPA)     │           │                        │    │
│  └──────────────────┘           └────────┬───────────────┘    │
└───────────────────────────────────────────┼────────────────────┘
                                            │ HTTP (8000)
                                            │
┌───────────────────────────────────────────▼────────────────────┐
│                   FastAPI Backend                              │
│                   (Python/Uvicorn)                             │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              LangChain Agent                            │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │  │
│  │  │   Planning   │  │     Tools    │  │    Memory    │ │  │
│  │  │     Layer    │  │              │  │   (Sessions) │ │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘ │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│  Tools Access:                                                  │
│  ├─▶ Database Tool (SQLite queries)                           │
│  ├─▶ Vector Search Tool (FAISS/RAG)                           │
│  ├─▶ Web Search Tool (OpenAI/Perplexity)                      │
│  └─▶ Code Generation Tool (Guidelines)                        │
└─────────────────────────────────────────────────────────────────┘
          │                    │                    │
          ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  SQLite DB      │  │  FAISS Vector   │  │  Chat Sessions  │
│  (12 MB file)   │  │     Store       │  │  (JSON files)   │
│                 │  │                 │  │                 │
│  • 433 pieces   │  │  • index.faiss  │  │  • session_*.   │
│  • 2681 actions │  │  • index.pkl    │  │    json         │
│  • 694 triggers │  │  • Embeddings   │  │  • sessions_    │
│  • 10K props    │  │                 │  │    index.json   │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

---

## 🔄 Request Flow

### Frontend Request Flow

```
1. User opens https://yourdomain.com
   ↓
2. Nginx serves static files from /var/www/Flow_Assistant/frontend/dist/
   ↓
3. Browser loads React app (index.html + JavaScript)
   ↓
4. React app initializes, fetches stats from /api/stats
   ↓
5. User ready to chat
```

### Chat Request Flow

```
1. User types message → clicks Send
   ↓
2. Frontend sends POST to /api/chat/stream
   ↓
3. Nginx proxies to backend (port 8000)
   ↓
4. FastAPI receives request
   ↓
5. Agent processes request:
   a) Planning Layer analyzes query
   b) Determines which tools to use
   c) Executes tools (database, RAG, web search)
   d) Generates response
   ↓
6. Backend streams response via SSE
   ↓
7. Frontend displays response in real-time
   ↓
8. Session saved to JSON file
```

---

## 📦 Component Details

### 1. Frontend (React + Vite)

**Location**: `/var/www/Flow_Assistant/frontend/`

**Technology Stack**:
- React 18.3 - UI framework
- Vite 6.0 - Build tool & dev server
- Axios - HTTP client
- React Markdown - Markdown rendering
- Syntax Highlighter - Code highlighting

**Key Features**:
- Chat interface with message history
- Real-time status updates (SSE)
- Session management (load previous conversations)
- Build Flow mode toggle
- Statistics display
- Code copy functionality

**Build Output**: `frontend/dist/` (served by Nginx)

**Environment Config**: `.env.production` with `VITE_API_URL`

---

### 2. Backend (FastAPI + LangChain)

**Location**: `/var/www/Flow_Assistant/src/`

**Technology Stack**:
- FastAPI 0.115+ - Web framework
- Uvicorn - ASGI server
- LangChain 0.3+ - LLM orchestration
- OpenAI API - Language models
- Python 3.11+

**Key Components**:

#### a) FastAPI Application (`main.py`)
- REST API endpoints
- CORS configuration
- SSE streaming for real-time updates
- Session management
- Error handling

**Endpoints**:
- `GET /` - Root/health
- `GET /health` - Health check
- `POST /chat` - Synchronous chat
- `POST /chat/stream` - Streaming chat (SSE)
- `GET /stats` - Database statistics
- `GET /sessions` - List all sessions
- `GET /sessions/{id}` - Get session details
- `DELETE /sessions/{id}` - Delete session
- `POST /reset` - Clear history (deprecated)

#### b) Agent System (`agent.py`)
- LangChain agent with tool calling
- Conversation memory (per-session)
- Streamlined decision logic
- Tool execution orchestration

**Agent Configuration**:
- Max iterations: 25
- Max execution time: 120 seconds
- Handles parsing errors gracefully
- Verbose logging

#### c) Flow Builder (`flow_builder.py`)
- Specialized workflow guide generator
- GPT-5-mini powered planning for Build Flow Mode
- Searches pieces, actions, and triggers
- Performs optional web research for missing info
- Outputs detailed step-by-step guides

#### d) Tool System (`tools.py`)
- **check_activepieces**: Verify if pieces/actions/triggers exist
- **search_activepieces_docs**: RAG search through vector store
- **web_search**: Real-time info via OpenAI/Perplexity
- **get_code_generation_guidelines**: TypeScript code guidelines

#### e) Memory System (`memory.py`)
- Session-based conversation history
- Persistent storage (JSON files)
- Session index for quick lookup
- Load previous conversations
- Clear individual sessions

#### f) Database Config (`db_config.py`)
- SQLite connection management
- Context managers for safe operations
- Row to dict conversion
- JSON field parsing
- Connection testing

#### g) ActivePieces DB Helper (`activepieces_db.py`)
- Dedicated database query helper
- Full-text search support
- Piece/action/trigger lookups
- Input property retrieval
- Top pieces ranking

---

### 3. Database (SQLite)

**Location**: `/var/www/Flow_Assistant/data/activepieces.db`

**Size**: ~12 MB

**Schema**:

```
pieces (433 rows)
├── id (INTEGER PRIMARY KEY)
├── name (TEXT) - Slug name (e.g., 'gmail')
├── display_name (TEXT) - Display name (e.g., 'Gmail')
├── description (TEXT)
├── version (TEXT)
├── auth_type (TEXT) - OAuth2, ApiKey, SecretText, etc.
├── categories (TEXT JSON) - Array of categories
└── authors (TEXT JSON) - Array of authors

actions (2,681 rows)
├── id (INTEGER PRIMARY KEY)
├── piece_id (INTEGER FK → pieces.id)
├── name (TEXT) - Action slug
├── display_name (TEXT) - Action display name
├── description (TEXT)
└── requires_auth (INTEGER BOOLEAN)

triggers (694 rows)
├── id (INTEGER PRIMARY KEY)
├── piece_id (INTEGER FK → pieces.id)
├── name (TEXT) - Trigger slug
├── display_name (TEXT) - Trigger display name
├── description (TEXT)
├── trigger_type (TEXT) - POLLING, WEBHOOK, etc.
└── requires_auth (INTEGER BOOLEAN)

action_properties (10,118 rows)
├── id (INTEGER PRIMARY KEY)
├── action_id (INTEGER FK → actions.id)
├── name (TEXT) - Property name
├── display_name (TEXT) - Display name
├── description (TEXT)
├── type (TEXT) - text, number, dropdown, array, object, etc.
├── required (INTEGER BOOLEAN)
└── default_value (TEXT)

trigger_properties (~1,000 rows)
├── Similar structure to action_properties
└── trigger_id (INTEGER FK → triggers.id)
```

**Indexes**:
- Full-text search indexes on pieces, actions, triggers
- Foreign key indexes for performance
- View: `pieces_with_capabilities` (joins pieces with counts)

**No Server Required**: SQLite is file-based, no daemon needed!

---

### 4. Vector Store (FAISS)

**Location**: `/var/www/Flow_Assistant/data/ap_faiss_index/`

**Files**:
- `index.faiss` - FAISS vector index (binary)
- `index.pkl` - Pickled document store and mappings

**Technology**:
- FAISS (Facebook AI Similarity Search)
- OpenAI text-embedding-ada-002 (1536 dimensions)
- In-memory document store

**Purpose**:
- Semantic search for "how to" questions
- RAG (Retrieval Augmented Generation)
- Find relevant documentation snippets
- Context-aware answers

**Usage Pattern**:
1. User asks: "How do I send emails?"
2. Query embedded → vector (1536 dimensions)
3. FAISS finds 6 most similar vectors
4. Returns relevant document chunks
5. LLM uses chunks as context
6. Generates informed answer

---

### 5. Session Storage

**Location**: `/var/www/Flow_Assistant/data/chat_sessions/`

**Files**:
- `session_{timestamp}_{id}.json` - Individual session files
- `sessions_index.json` - Quick lookup index

**Session File Structure**:
```json
{
  "session_id": "session_1760601982922_uq86zkh2r",
  "created_at": "2025-01-15T10:30:00",
  "updated_at": "2025-01-15T10:45:00",
  "messages": [
    {
      "role": "user",
      "message": "Does ActivePieces have Slack?",
      "timestamp": "2025-01-15T10:30:00"
    },
    {
      "role": "assistant",
      "message": "Yes, ActivePieces has a Slack integration...",
      "timestamp": "2025-01-15T10:30:05"
    }
  ]
}
```

**Index File Structure**:
```json
{
  "session_1760601982922_uq86zkh2r": {
    "created_at": "2025-01-15T10:30:00",
    "updated_at": "2025-01-15T10:45:00",
    "message_count": 10
  }
}
```

---

### 6. Nginx

**Location**: `/etc/nginx/sites-available/flow-assistant`

**Responsibilities**:
- Serve frontend static files
- Reverse proxy API requests to backend
- Handle SSL/TLS termination
- SSE (Server-Sent Events) streaming
- Compression (gzip)
- Security headers

**Routes**:
- `/` → Static files (React SPA)
- `/api/*` → Proxy to backend (port 8000)
- `/api/chat/stream` → SSE streaming (special config)

**Performance Features**:
- Gzip compression
- Keep-alive connections
- Buffering control for SSE
- Caching headers
- Connection pooling

---

### 7. Systemd Service

**Location**: `/etc/systemd/system/flow-assistant-backend.service`

**Purpose**:
- Auto-start backend on boot
- Auto-restart on crashes
- Logging to files
- Process management

**Configuration**:
- User: `deploy`
- Working Directory: `/var/www/Flow_Assistant`
- Command: `uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 2`
- Restart Policy: Always (10s delay)

**Logs**:
- stdout → `/var/log/flow-assistant-backend.log`
- stderr → `/var/log/flow-assistant-backend-error.log`

---

## 🔐 Security Layers

```
┌────────────────────────────────────────────┐
│  1. SSL/TLS (Let's Encrypt Certificate)   │
│     ↓ Encrypted HTTPS traffic             │
└────────────────────────────────────────────┘

┌────────────────────────────────────────────┐
│  2. Nginx Security Headers                 │
│     • X-Frame-Options: SAMEORIGIN          │
│     • X-Content-Type-Options: nosniff      │
│     • X-XSS-Protection: 1; mode=block      │
└────────────────────────────────────────────┘

┌────────────────────────────────────────────┐
│  3. CORS Configuration (Backend)           │
│     • Allowed origins from .env            │
│     • Credentials support                  │
└────────────────────────────────────────────┘

┌────────────────────────────────────────────┐
│  4. Environment Variables                  │
│     • API keys in .env (not in git)        │
│     • Secure file permissions (600)        │
└────────────────────────────────────────────┘

┌────────────────────────────────────────────┐
│  5. Firewall (UFW)                         │
│     • Only ports 22, 80, 443 open          │
│     • Rate limiting possible               │
└────────────────────────────────────────────┘

┌────────────────────────────────────────────┐
│  6. Non-Root User                          │
│     • Services run as 'deploy' user        │
│     • Minimal privileges                   │
└────────────────────────────────────────────┘
```

---

## 📊 Resource Usage

### Expected Resource Consumption:

**CPU**:
- Idle: 1-5%
- Processing request: 20-40%
- Peak: 60-80%

**Memory**:
- Backend: 200-400 MB
- Nginx: 20-50 MB
- System: 200-300 MB
- Total: ~600-800 MB (2GB recommended)

**Disk**:
- Application code: ~50 MB
- Dependencies: ~500 MB
- Database: 12 MB
- Vector store: ~50 MB
- Logs: Grows over time (10-100 MB)
- Total: ~1-2 GB (50GB droplet is plenty)

**Network**:
- Frontend initial load: 1-2 MB
- Chat message: <10 KB
- Response: 1-5 KB
- Bandwidth: Minimal (unless heavy traffic)

---

## 🔄 Data Flow Examples

### Example 1: User asks "Does ActivePieces have Slack?"

```
1. Frontend: User types and sends message
   ↓
2. POST request to /api/chat/stream
   ↓
3. Backend receives request
   ↓
4. Planning layer analyzes:
   - Query type: "piece_lookup"
   - Tool: "check_activepieces"
   - Max calls: 1
   ↓
5. Agent executes check_activepieces("slack")
   ↓
6. Database query: SELECT * FROM pieces WHERE name LIKE '%slack%'
   ↓
7. Result: Slack piece found with 30 actions, 5 triggers
   ↓
8. LLM formats response
   ↓
9. Response streamed to frontend via SSE
   ↓
10. Frontend displays response
    ↓
11. Session saved to JSON file
```

### Example 2: User asks "How do I filter data in a flow?"

```
1. Frontend sends message
   ↓
2. Planning layer detects "howto" query
   ↓
3. Agent uses search_activepieces_docs("filter data flow")
   ↓
4. Query embedded via OpenAI API (text-embedding-ada-002)
   ↓
5. FAISS searches vector store for similar embeddings
   ↓
6. Returns 6 most relevant document chunks
   ↓
7. LLM uses chunks as context
   ↓
8. Generates comprehensive answer
   ↓
9. Response streamed to frontend
```

### Example 3: User asks "What's the latest news about AI?"

```
1. Frontend sends message
   ↓
2. Planning layer detects external/current info needed
   ↓
3. Agent uses web_search("latest news about AI")
   ↓
4. Backend calls OpenAI Responses API with web_search tool
   ↓
5. OpenAI searches the web and synthesizes answer
   ↓
6. Response returned to agent
   ↓
7. Agent formats and streams to frontend
```

---

## 🎯 Key Design Decisions

### Why SQLite instead of PostgreSQL?
- ✅ No database server to manage
- ✅ Single file - easy backups
- ✅ Perfect for read-heavy workloads
- ✅ Simpler deployment
- ✅ Lower memory usage
- ✅ Fast for this data size (12MB)

### Why FAISS instead of Pinecone/Weaviate?
- ✅ No external service required
- ✅ No API limits or costs
- ✅ Local files - privacy and speed
- ✅ In-memory search is very fast
- ✅ Simple setup

### Why Nginx + Uvicorn?
- ✅ Nginx handles SSL, static files, and proxying
- ✅ Uvicorn handles Python async efficiently
- ✅ Best of both worlds
- ✅ Industry standard architecture

### Why Session Files instead of Redis?
- ✅ Simple JSON files - easy to debug
- ✅ No Redis server to manage
- ✅ Sufficient for moderate traffic
- ✅ Easy backups and migrations
- ✅ Human-readable format

### Why Systemd instead of Docker?
- ✅ Native Linux integration
- ✅ Better resource usage
- ✅ Simpler for single-app deployments
- ✅ Easier to debug
- ✅ No Docker daemon overhead

---

## 📈 Scaling Considerations

### Current Setup: Good for ~100 concurrent users

### To scale to 1,000+ users:

1. **Backend**:
   - Increase Uvicorn workers (--workers 4-8)
   - Upgrade droplet (4GB+ RAM)
   - Add load balancer

2. **Database**:
   - SQLite is fine for reads
   - Consider PostgreSQL if heavy writes
   - Add read replicas if needed

3. **Sessions**:
   - Move to Redis or PostgreSQL
   - Centralized session storage

4. **Vector Store**:
   - Consider Pinecone/Weaviate
   - Or keep FAISS with more resources

5. **Infrastructure**:
   - Multiple droplets behind load balancer
   - CDN for frontend (Cloudflare)
   - Separate database server

---

## 🛠️ Maintenance Tasks

### Daily:
- Monitor service status
- Check logs for errors
- Verify disk space

### Weekly:
- Review application logs
- Check for security updates
- Monitor resource usage

### Monthly:
- Backup database and sessions
- Update dependencies
- Review and clear old logs
- Test SSL renewal

### Quarterly:
- Full system update
- Performance review
- Security audit
- Backup verification

---

## 📚 Additional Resources

### File Locations Quick Reference:

```
Application:      /var/www/Flow_Assistant/
Backend Source:   /var/www/Flow_Assistant/src/
Frontend Source:  /var/www/Flow_Assistant/frontend/
Frontend Build:   /var/www/Flow_Assistant/frontend/dist/
Database:         /var/www/Flow_Assistant/data/activepieces.db
Vector Store:     /var/www/Flow_Assistant/data/ap_faiss_index/
Sessions:         /var/www/Flow_Assistant/data/chat_sessions/
Environment:      /var/www/Flow_Assistant/.env
Virtual Env:      /var/www/Flow_Assistant/venv/

Nginx Config:     /etc/nginx/sites-available/flow-assistant
Service File:     /etc/systemd/system/flow-assistant-backend.service

Logs:
  Backend:        /var/log/flow-assistant-backend.log
  Backend Errors: /var/log/flow-assistant-backend-error.log
  Nginx Access:   /var/log/nginx/access.log
  Nginx Error:    /var/log/nginx/error.log
  System Service: journalctl -u flow-assistant-backend
```

---

**🎯 You now understand the complete architecture!**

Use this as a reference while following the deployment guide.

