# Repository Structure Guide

This document explains the organized structure of the Flow Assistant repository.

## 📂 Directory Structure

### `/src/` - Main Application Code
Contains all the core Python application code.

**Files:**
- `main.py` - FastAPI application with API endpoints
- `agent.py` - LLM agent configuration
- `flow_builder.py` - GPT-5 powered flow guide generator
- `tools.py` - Tool definitions (database search, semantic search, web search)
- `db_config.py` - Database connection and configuration
- `memory.py` - Conversation memory and session management
- `llm_config.py` - LLM initialization (supports OpenAI, Anthropic, Google)

**How to import:**
```python
from src.agent import get_agent
from src.tools import check_activepieces
from src.memory import log_interaction
```

---

### `/tests/` - Test Suite
All test files for validating functionality.

**Files:**
- `test_assistant.py` - Main test suite for the assistant
- `test_sessions.py` - Session management tests

**How to run:**
```bash
# Run main test suite
python tests/test_assistant.py

# Test from root using run.py
python run.py  # Select option 4
```

---

### `/docs/` - Documentation
All documentation organized by category.

#### `/docs/setup/` - Setup & Installation
- `INSTALLATION.md` - Complete installation guide
- `QUICKSTART.md` - Quick start guide
- `GET_STARTED.md` - Getting started tutorial
- `SETUP_SUMMARY.md` - Setup summary
- `GITHUB_SETUP.md` - GitHub repository setup

#### `/docs/deployment/` - Deployment Guides
- `DEPLOYMENT.md` - Full deployment documentation
- `DEPLOYMENT_CHECKLIST.md` - Pre-deployment checklist
- `DEPLOYMENT_GUIDE_INDEX.md` - Index of all deployment guides
- `EASY_DEPLOYMENT_GUIDE.md` - Simplified deployment guide
- `QUICK_START_PRODUCTION.md` - Quick production setup (15 min)

#### `/docs/troubleshooting/` - Fix & Troubleshooting
- `TROUBLESHOOTING.md` - General troubleshooting guide
- `FIX_DATABASE_CONNECTION.md` - Database connection fixes
- `FIX_MAX_ITERATIONS.md` - Agent iteration limit fixes
- `FIX_MODEL_ERROR.md` - LLM model error fixes
- `FAISS_LOADING_FIX.md` - Vector store loading fixes
- `PYTHON_3.13_FIX.md` - Python 3.13 compatibility fixes

#### `/docs/features/` - Feature Documentation
- `ai_assistant_build_guide.md` - Complete build guide
- `AGENT_CONNECTION_GUIDE.md` - Agent-database connection guide
- `BUILD_COMPLETE.md` - Build completion summary
- `COMPLETE_ENHANCEMENT_SUMMARY.md` - Enhancement summary
- `ENHANCED_AGENT_SUMMARY.md` - Enhanced agent features
- `GPT5_UPDATE_SUMMARY.md` - GPT-5 integration summary
- `REAL_TIME_STATUS_FEATURE.md` - Real-time status updates
- `STOP_FUNCTIONALITY_GUIDE.md` - Stop functionality guide
- `QUICK_TEST_IMPROVEMENTS.md` - Testing improvements

#### `/docs/migration/` - Migration Guides
- `MIGRATION_COMPLETE.md` - Migration completion summary
- `POSTGRES_MIGRATION.md` - PostgreSQL migration guide
- `SQLITE_MIGRATION_SUMMARY.md` - SQLite migration summary
- `REBUILD_FAISS_GUIDE.md` - FAISS rebuild guide

#### `/docs/` (root level)
- `PROJECT_OVERVIEW.md` - Complete project overview
- `PROJECT_SUMMARY.md` - Quick project summary

---

### `/scripts/` - Utility Scripts
Helper scripts for various tasks.

#### `/scripts/migration/` - Data Migration Scripts
- `migrate_to_sqlite.py` - PostgreSQL to SQLite migration
- `rebuild_faiss_enhanced.py` - Enhanced FAISS rebuild
- `rebuild_faiss_simple.py` - Simple FAISS rebuild
- `prepare_knowledge_base.py` - Knowledge base preparation
- `db_config_postgresql_backup.py` - PostgreSQL config backup

**How to run:**
```bash
# Prepare knowledge base
python scripts/migration/prepare_knowledge_base.py

# Rebuild FAISS index
python scripts/migration/rebuild_faiss_enhanced.py
```

#### `/scripts/deployment/` - Deployment Scripts
- `deploy_ubuntu.sh` - Ubuntu deployment script
- `fix_services.sh` - Service fix script
- `update_app.sh` - Application update script
- `setup.py` - Automated setup script

**How to run:**
```bash
# Run setup
python scripts/deployment/setup.py

# Deploy to Ubuntu
sudo bash scripts/deployment/deploy_ubuntu.sh
```

#### `/scripts/maintenance/` - Maintenance Scripts
(Reserved for future maintenance utilities)

---

### `/config/` - Configuration Files
Server and service configuration files.

**Files:**
- `nginx.conf.template` - Nginx reverse proxy configuration
- `/config/systemd/` - Systemd service files
  - `activepieces-backend.service` - Backend service
  - `activepieces-frontend.service` - Frontend service

**How to use:**
```bash
# Copy and configure nginx
sudo cp config/nginx.conf.template /etc/nginx/sites-available/activepieces

# Install systemd services
sudo cp config/systemd/*.service /etc/systemd/system/
```

---

### `/data/` - Data Files
All data files and databases (excluded from git).

**Contents:**
- `activepieces.db` - SQLite database
- `ap_faiss_index/` - FAISS vector store
  - `index.faiss` - FAISS index file
  - `index.pkl` - Document store
- `chat_sessions/` - Chat session storage
- `chat_history.json` - Legacy chat history
- `pieces_knowledge_base.json` - Knowledge base JSON
- `sessions_index.json` - Session index

**Note:** This folder is in `.gitignore` to prevent committing sensitive data.

---

### `/frontend/` - React Frontend
React application for the user interface.

**Structure:**
```
frontend/
├── src/
│   ├── App.jsx       # Main React component
│   ├── App.css       # Styles
│   ├── main.jsx      # Entry point
│   └── index.css     # Global styles
├── index.html        # HTML template
├── package.json      # Dependencies
├── vite.config.js    # Vite configuration
└── node_modules/     # Installed packages
```

**How to run:**
```bash
cd frontend
npm install
npm run dev
```

---

### Root Files

#### Application Files
- `run.py` - Main application launcher (use this to start the app)
- `demo_enhanced_agent.py` - Demo script showing enhanced features
- `requirements.txt` - Python dependencies

#### Configuration Files
- `.env.example` - Environment variables template
- `.env` - Your environment variables (not in git)
- `.gitignore` - Git ignore rules

#### Documentation Files
- `README.md` - Main project README
- `STRUCTURE.md` - This file
- `LICENSE` - MIT License

#### Package Files
- `package-lock.json` - NPM lock file (legacy)

---

## 🚀 Quick Navigation

### I want to...

**...start the application:**
```bash
python run.py
```

**...run tests:**
```bash
python tests/test_assistant.py
```

**...find setup documentation:**
- Look in `/docs/setup/`
- Start with `docs/setup/QUICKSTART.md`

**...deploy to production:**
- Look in `/docs/deployment/`
- Start with `docs/deployment/QUICK_START_PRODUCTION.md`

**...fix an issue:**
- Look in `/docs/troubleshooting/`
- Start with `docs/troubleshooting/TROUBLESHOOTING.md`

**...understand a feature:**
- Look in `/docs/features/`
- Start with `docs/features/ai_assistant_build_guide.md`

**...modify the code:**
- Main code is in `/src/`
- Start with `src/main.py` (API endpoints)
- Agent logic is in `src/agent.py`
- Tools are in `src/tools.py`

**...add a test:**
- Add tests in `/tests/`
- Follow patterns in `tests/test_assistant.py`

**...migrate data:**
- Scripts are in `/scripts/migration/`
- Run `python scripts/migration/prepare_knowledge_base.py`

---

## 📋 File Naming Conventions

- **Python files**: `snake_case.py`
- **Documentation**: `SCREAMING_SNAKE_CASE.md` or `snake_case.md`
- **Config files**: `lowercase.conf` or `service-name.service`
- **Scripts**: `snake_case.py` or `kebab-case.sh`

---

## 🔄 Import Path Changes

After reorganization, import paths have changed:

**Old (before reorganization):**
```python
from agent import get_agent
from tools import check_activepieces
from memory import log_interaction
```

**New (after reorganization):**
```python
from src.agent import get_agent
from src.tools import check_activepieces
from src.memory import log_interaction
```

**Running the application:**
```bash
# Old
uvicorn main:app --reload

# New
uvicorn src.main:app --reload
```

---

## 🎯 Benefits of This Structure

1. **Easy Navigation**: Find what you need quickly
2. **Clear Organization**: Code, tests, docs, scripts are separated
3. **Better Maintenance**: Related files are grouped together
4. **Scalability**: Easy to add new features/docs without clutter
5. **Professional**: Standard structure used in production projects

---

## 🤝 Contributing

When adding new files:

1. **Code files** → `/src/`
2. **Tests** → `/tests/`
3. **Documentation** → `/docs/` (in appropriate subfolder)
4. **Scripts** → `/scripts/` (in appropriate subfolder)
5. **Config** → `/config/`
6. **Data** → `/data/` (and add to `.gitignore` if sensitive)

---

## 📞 Need Help?

- Check `/docs/troubleshooting/TROUBLESHOOTING.md`
- Review `/docs/setup/QUICKSTART.md`
- See `/docs/features/ai_assistant_build_guide.md`
- Open an issue on GitHub

---

**Last Updated:** October 2024
**Version:** 2.0 (Reorganized Structure)

