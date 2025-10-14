# Deployment Files Reference

Quick reference for all deployment-related files in the project.

---

## 📑 Main Deployment Documentation

### Start Here! 👇

**[DEPLOYMENT_INDEX.md](DEPLOYMENT_INDEX.md)** 📑
- Navigation hub for all deployment docs
- Helps you choose the right deployment path
- Quick reference tables and commands
- Checklists and troubleshooting links

---

## 📚 Deployment Guides

### Primary Guides

1. **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** 📖
   - **Time**: 30-45 minutes
   - **Type**: Complete step-by-step guide
   - **Coverage**: ALL components (Backend, Frontend, DB, Vector Store, RAG, Search, Nginx, SSL, etc.)
   - **Best for**: First-time deployers, production setup
   - **Includes**: Troubleshooting, security, performance optimization

2. **[QUICK_DEPLOY.md](QUICK_DEPLOY.md)** 🚀
   - **Time**: 5-30 minutes
   - **Type**: TL;DR quick reference
   - **Coverage**: Essential steps only
   - **Best for**: Experienced users, quick deployments
   - **Includes**: Copy-paste commands, quick troubleshooting

3. **[DEPLOYMENT_SUMMARY.md](DEPLOYMENT_SUMMARY.md)** 📋
   - **Type**: System overview
   - **Coverage**: Architecture, components, configuration
   - **Best for**: Understanding the system
   - **Includes**: Diagrams, checklists, management commands

### Supporting Documentation

4. **[DEPLOYMENT_COMPLETE.md](DEPLOYMENT_COMPLETE.md)** ✅
   - **Type**: Overhaul summary
   - **Coverage**: What was done, how to use new docs
   - **Best for**: Understanding the changes
   - **Includes**: Before/after comparison, quick start

5. **[DEPLOYMENT_CHANGELOG.md](DEPLOYMENT_CHANGELOG.md)** 📝
   - **Type**: Change log
   - **Coverage**: What changed and why
   - **Best for**: Migration from old docs
   - **Includes**: Breaking changes, migration guide

6. **[DEPLOYMENT_FILES.md](DEPLOYMENT_FILES.md)** 📄
   - **Type**: File reference (this document)
   - **Coverage**: All deployment files explained
   - **Best for**: Quick file lookup

---

## 🤖 Deployment Scripts

### Automated Deployment

**[scripts/deployment/deploy_digitalocean.sh](scripts/deployment/deploy_digitalocean.sh)**
- Fully automated deployment
- Interactive prompts for configuration
- Handles all setup steps
- Color-coded output
- Post-deployment verification
- SSL setup included

**Usage**:
```bash
# On your DigitalOcean droplet
curl -fsSL https://raw.githubusercontent.com/yourusername/Flow_Assistant/main/scripts/deployment/deploy_digitalocean.sh | sudo bash
```

### Legacy Script (Still Works)

**[scripts/deployment/deploy_ubuntu.sh](scripts/deployment/deploy_ubuntu.sh)**
- Original deployment script
- PostgreSQL-focused
- Still functional but not recommended
- Use new script instead

---

## 📋 Configuration Files

### Environment Configuration

**[env.example](env.example)**
- Template for environment variables
- All required and optional variables
- Comments explaining each setting
- Copy to `.env` and fill in your values

**Key variables**:
```ini
OPENAI_API_KEY=your-key-here          # Required
MODEL_PROVIDER=openai                  # openai, anthropic, google
SEARCH_PROVIDER=openai                 # openai or perplexity
SQLITE_DB_FILE=data/activepieces.db   # Database location
```

### Nginx Configuration

Template is included in **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md#step-10-configure-nginx-3-minutes)**
- Reverse proxy setup
- SSL/TLS configuration
- Security headers
- CORS configuration
- Static file caching

### Systemd Services

Templates in **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md#step-9-create-systemd-services-3-minutes)**

1. **activepieces-backend.service**
   - FastAPI backend service
   - Auto-restart enabled
   - Environment file loaded

2. **activepieces-frontend.service**
   - React frontend service
   - Serves production build
   - Auto-restart enabled

---

## 📁 File Locations After Deployment

### Application Files
```
/opt/activepieces-assistant/
├── src/                              # Backend source
│   ├── main.py                       # FastAPI app
│   ├── agent.py                      # AI agent
│   ├── db_config.py                  # Database config
│   ├── tools.py                      # Agent tools
│   ├── memory.py                     # Session memory
│   ├── planner.py                    # Query planner
│   ├── llm_config.py                 # LLM setup
│   └── flow_builder.py              # Flow builder
│
├── frontend/                         # Frontend source
│   ├── src/                          # React source
│   ├── dist/                         # Production build
│   └── package.json                  # Dependencies
│
├── data/                             # Data files
│   ├── activepieces.db              # SQLite database
│   ├── ap_faiss_index/              # Vector store
│   │   ├── index.faiss
│   │   └── index.pkl
│   ├── chat_sessions/               # Chat history
│   └── pieces_knowledge_base.json   # Knowledge base
│
├── scripts/                          # Utility scripts
│   ├── deployment/                   # Deployment scripts
│   └── migration/                    # Migration scripts
│
├── .env                             # Environment variables (create this)
├── venv/                            # Python virtual environment
└── requirements.txt                 # Python dependencies
```

### System Configuration Files
```
/etc/systemd/system/
├── activepieces-backend.service      # Backend service
└── activepieces-frontend.service     # Frontend service

/etc/nginx/
└── sites-available/
    └── activepieces-assistant        # Nginx config

/var/log/nginx/
├── access.log                        # Nginx access logs
└── error.log                         # Nginx error logs
```

---

## 🔍 Quick File Lookup

### When You Need...

**To understand deployment**:
- Start: [DEPLOYMENT_INDEX.md](DEPLOYMENT_INDEX.md)
- Overview: [DEPLOYMENT_COMPLETE.md](DEPLOYMENT_COMPLETE.md)

**To deploy quickly**:
- Automated: [deploy_digitalocean.sh](scripts/deployment/deploy_digitalocean.sh)
- Manual: [QUICK_DEPLOY.md](QUICK_DEPLOY.md)

**To deploy with full details**:
- Guide: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

**To understand the system**:
- Architecture: [DEPLOYMENT_SUMMARY.md](DEPLOYMENT_SUMMARY.md)
- Changes: [DEPLOYMENT_CHANGELOG.md](DEPLOYMENT_CHANGELOG.md)

**To configure**:
- Template: [env.example](env.example)
- Services: See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

**To troubleshoot**:
- Quick fixes: [QUICK_DEPLOY.md](QUICK_DEPLOY.md#-troubleshooting)
- Detailed: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md#-troubleshooting)

---

## 📊 File Summary Table

| File | Type | Purpose | When to Use |
|------|------|---------|-------------|
| [DEPLOYMENT_INDEX.md](DEPLOYMENT_INDEX.md) | Navigation | Choose deployment path | **Start here** |
| [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) | Guide | Complete walkthrough | Need full details |
| [QUICK_DEPLOY.md](QUICK_DEPLOY.md) | Guide | Fast deployment | Want speed |
| [DEPLOYMENT_SUMMARY.md](DEPLOYMENT_SUMMARY.md) | Overview | System architecture | Understand system |
| [DEPLOYMENT_COMPLETE.md](DEPLOYMENT_COMPLETE.md) | Summary | What's new | See changes |
| [DEPLOYMENT_CHANGELOG.md](DEPLOYMENT_CHANGELOG.md) | Changelog | Migration info | Upgrading docs |
| [DEPLOYMENT_FILES.md](DEPLOYMENT_FILES.md) | Reference | File index | Find specific file |
| [deploy_digitalocean.sh](scripts/deployment/deploy_digitalocean.sh) | Script | Automated deploy | Fastest deployment |
| [env.example](env.example) | Config | Environment template | Configure app |

---

## ✅ Deployment Checklist

Use these files in this order:

### Planning Phase
1. Read [DEPLOYMENT_INDEX.md](DEPLOYMENT_INDEX.md) - Choose your path
2. Read [DEPLOYMENT_COMPLETE.md](DEPLOYMENT_COMPLETE.md) - Understand what you'll get
3. Review [DEPLOYMENT_SUMMARY.md](DEPLOYMENT_SUMMARY.md) - See architecture

### Deployment Phase
Choose ONE:
- **Fast**: Run [deploy_digitalocean.sh](scripts/deployment/deploy_digitalocean.sh)
- **Quick**: Follow [QUICK_DEPLOY.md](QUICK_DEPLOY.md)
- **Complete**: Follow [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

### Configuration Phase
1. Copy [env.example](env.example) to `.env`
2. Add your API keys
3. Configure search provider

### Verification Phase
1. Check services are running
2. Test health endpoint
3. Verify all features work
4. Review troubleshooting if needed

---

## 🆘 Troubleshooting

### Can't find the right guide?
➜ Start with [DEPLOYMENT_INDEX.md](DEPLOYMENT_INDEX.md)

### Deployment failed?
➜ Check [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md#-troubleshooting)

### Quick fix needed?
➜ See [QUICK_DEPLOY.md](QUICK_DEPLOY.md#-troubleshooting)

### Want to understand why something changed?
➜ Read [DEPLOYMENT_CHANGELOG.md](DEPLOYMENT_CHANGELOG.md)

### Need to see all files?
➜ You're reading it! (this file)

---

## 📚 External Resources

### Referenced in Documentation
- [FastAPI Docs](https://fastapi.tiangolo.com) - Web framework
- [LangChain Docs](https://langchain.com) - LLM orchestration
- [OpenAI API](https://platform.openai.com/docs) - AI provider
- [Nginx Docs](https://nginx.org/en/docs/) - Web server
- [Let's Encrypt](https://letsencrypt.org/) - Free SSL
- [Ubuntu Docs](https://ubuntu.com/server/docs) - Server OS

---

## 🎯 Summary

**All deployment files in one place!**

**Start**: [DEPLOYMENT_INDEX.md](DEPLOYMENT_INDEX.md)  
**Deploy**: Choose your path from index  
**Configure**: [env.example](env.example)  
**Troubleshoot**: See guides above  

Everything you need to deploy is documented and ready to use! 🚀

---

*Last Updated: 2024*

