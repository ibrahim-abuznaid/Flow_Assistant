# Deployment Documentation Index

## 📚 Complete Guide to Deploying Your AI Assistant

This index helps you choose the right deployment guide for your needs.

---

## 🚀 Quick Start (Choose Your Path)

### Path 1: I Want It Fast (5 minutes)
**Best for**: Experienced users who trust automation

➜ **[Automated Deployment Script](scripts/deployment/deploy_digitalocean.sh)**
```bash
curl -fsSL https://raw.githubusercontent.com/yourusername/Flow_Assistant/main/scripts/deployment/deploy_digitalocean.sh | sudo bash
```

---

### Path 2: I Want Quick Manual Steps (30 minutes)
**Best for**: Users who want control but not too much detail

➜ **[QUICK_DEPLOY.md](QUICK_DEPLOY.md)** - TL;DR deployment guide
- Copy-paste ready commands
- Minimal explanations
- Quick troubleshooting
- Essential commands

---

### Path 3: I Want to Understand Everything (45 minutes)
**Best for**: First-time deployers, learning, production setup

➜ **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Complete step-by-step guide
- Detailed explanations
- All components covered
- Comprehensive troubleshooting
- Security best practices
- Performance optimization

---

## 📖 Documentation Structure

### Core Deployment Guides

| Document | Purpose | Time | Difficulty |
|----------|---------|------|------------|
| **[QUICK_DEPLOY.md](QUICK_DEPLOY.md)** | Fast deployment with minimal reading | 30 min | Easy |
| **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** | Complete guide with full details | 45 min | Easy-Medium |
| **[deploy_digitalocean.sh](scripts/deployment/deploy_digitalocean.sh)** | Automated deployment script | 5 min | Very Easy |

### Supporting Documentation

| Document | Purpose |
|----------|---------|
| **[DEPLOYMENT_SUMMARY.md](DEPLOYMENT_SUMMARY.md)** | Overview of deployment system |
| **[README.md](README.md)** | Project overview and features |
| **[env.example](env.example)** | Environment variables template |

### Setup Guides

| Document | Purpose |
|----------|---------|
| **[docs/setup/GITHUB_SETUP.md](docs/setup/GITHUB_SETUP.md)** | GitHub repository setup |
| **[docs/setup/SETUP_SUMMARY.md](docs/setup/SETUP_SUMMARY.md)** | Project setup overview |

---

## 🎯 What Gets Deployed

### Components

✅ **Backend**
- FastAPI web server
- LangChain AI agent
- OpenAI integration
- Port: 8000
- Service: `activepieces-backend`

✅ **Frontend**
- React 18 application
- Vite build system
- Modern UI with chat
- Port: 5173
- Service: `activepieces-frontend`

✅ **Database**
- SQLite (included)
- 433 pieces/integrations
- 2,681 actions
- 694 triggers
- File: `data/activepieces.db`

✅ **Vector Store**
- FAISS for RAG
- 3,808 documents
- Semantic search
- Directory: `data/ap_faiss_index/`

✅ **Web Search**
- OpenAI Responses API (default)
- Perplexity (alternative)
- Configurable via env

✅ **Infrastructure**
- Nginx reverse proxy
- SSL/TLS with Let's Encrypt
- UFW firewall
- Systemd services
- Auto-restart enabled

---

## 📋 Prerequisites

### Required
- Ubuntu 22.04 or 24.04 LTS
- 2GB RAM minimum (4GB recommended)
- 1 vCPU minimum (2 vCPU recommended)
- 50GB SSD minimum
- SSH access
- OpenAI API key

### Optional
- Domain name (for SSL)
- Perplexity API key (for alternative search)

---

## ⏱️ Deployment Timeline

### Automated (5-10 minutes)
```
1. Run script          (1 min)
2. Script execution    (3-5 min)
3. Enter API keys      (1 min)
4. SSL setup           (2-3 min, optional)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total: 5-10 minutes
```

### Quick Manual (30 minutes)
```
1. System setup        (5 min)
2. Clone & install     (5 min)
3. Configure           (2 min)
4. Database & vector   (3 min)
5. Build frontend      (5 min)
6. Create services     (3 min)
7. Configure Nginx     (3 min)
8. Firewall            (1 min)
9. Start services      (2 min)
10. Verify             (1 min)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total: 30 minutes
```

### Complete Manual (45 minutes)
```
Same as Quick Manual, plus:
- Reading explanations
- Understanding each step
- Optional optimizations
- Security hardening
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total: 45 minutes
```

---

## 🗂️ File Locations

### Application
```
/opt/activepieces-assistant/          # Application root
├── src/                              # Backend source
│   ├── main.py                       # FastAPI app
│   ├── agent.py                      # AI agent
│   ├── db_config.py                  # Database config
│   └── ...
├── frontend/                         # Frontend source
│   ├── dist/                         # Production build
│   └── ...
├── data/                             # Data files
│   ├── activepieces.db              # Database
│   ├── ap_faiss_index/              # Vector store
│   └── chat_sessions/               # Chat history
├── .env                             # Environment variables
└── venv/                            # Python virtual env
```

### System Configuration
```
/etc/systemd/system/
├── activepieces-backend.service      # Backend service
└── activepieces-frontend.service     # Frontend service

/etc/nginx/
└── sites-available/
    └── activepieces-assistant        # Nginx config
```

### Logs
```
journalctl -u activepieces-backend    # Backend logs
journalctl -u activepieces-frontend   # Frontend logs
/var/log/nginx/access.log             # Nginx access
/var/log/nginx/error.log              # Nginx errors
```

---

## ✅ Deployment Checklist

### Pre-Deployment
- [ ] DigitalOcean droplet created (Ubuntu 22.04/24.04)
- [ ] SSH access confirmed
- [ ] OpenAI API key obtained
- [ ] Domain DNS configured (optional)
- [ ] Repository URL ready

### During Deployment
- [ ] System updated
- [ ] Dependencies installed
- [ ] Repository cloned
- [ ] Python environment setup
- [ ] Environment configured
- [ ] Database verified
- [ ] Vector store created
- [ ] Frontend built
- [ ] Services created
- [ ] Nginx configured
- [ ] Firewall configured
- [ ] SSL configured (optional)

### Post-Deployment
- [ ] Backend service running
- [ ] Frontend service running
- [ ] Nginx running
- [ ] Health endpoint OK
- [ ] Web interface accessible
- [ ] Chat functionality working
- [ ] Web search working
- [ ] Code generation working
- [ ] Build Flow mode working
- [ ] Auto-restart enabled
- [ ] Backups configured

---

## 🔧 Quick Commands Reference

### Service Management
```bash
# Status
systemctl status activepieces-backend
systemctl status activepieces-frontend

# Restart
systemctl restart activepieces-backend
systemctl restart activepieces-frontend

# Logs
journalctl -u activepieces-backend -f
journalctl -u activepieces-frontend -f
```

### Testing
```bash
# Health check
curl http://localhost:8000/health

# Stats
curl http://localhost:8000/stats

# Web interface
http://your-domain.com
```

### Maintenance
```bash
# Update application
cd /opt/activepieces-assistant
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
cd frontend && npm install && npm run build && cd ..
systemctl restart activepieces-backend activepieces-frontend

# Backup
cp data/activepieces.db data/backup_$(date +%Y%m%d).db
```

---

## 🐛 Troubleshooting

### Quick Fixes

**Backend won't start?**
```bash
journalctl -u activepieces-backend -n 50
# Check API keys in .env
nano /opt/activepieces-assistant/.env
systemctl restart activepieces-backend
```

**Frontend not loading?**
```bash
cd /opt/activepieces-assistant/frontend
npm run build
systemctl restart activepieces-frontend
```

**Database issues?**
```bash
cd /opt/activepieces-assistant
source venv/bin/activate
python src/db_config.py
```

**Vector store missing?**
```bash
cd /opt/activepieces-assistant
source venv/bin/activate
python scripts/migration/prepare_knowledge_base.py
systemctl restart activepieces-backend
```

### Full Troubleshooting Guide
See **[DEPLOYMENT_GUIDE.md - Troubleshooting Section](DEPLOYMENT_GUIDE.md#-troubleshooting)**

---

## 🔐 Security Checklist

- [ ] UFW firewall enabled
- [ ] Only necessary ports open (22, 80, 443)
- [ ] SSL certificate installed
- [ ] Strong API keys used
- [ ] `.env` file not in git
- [ ] Auto-updates configured
- [ ] Fail2Ban installed (optional)
- [ ] Regular backups scheduled
- [ ] Logs monitored regularly

---

## 📊 Performance Optimization

### Quick Wins
- Use Gunicorn instead of Uvicorn
- Enable Nginx gzip compression
- Setup browser caching
- Monitor with htop

### Detailed Guide
See **[DEPLOYMENT_GUIDE.md - Performance Section](DEPLOYMENT_GUIDE.md#-performance-optimization)**

---

## 🆘 Getting Help

### If Something Goes Wrong

1. **Check Logs**
   ```bash
   journalctl -u activepieces-backend -n 100
   ```

2. **Review Troubleshooting**
   - [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md#-troubleshooting)
   - [QUICK_DEPLOY.md](QUICK_DEPLOY.md#-troubleshooting)

3. **Verify Configuration**
   ```bash
   cat /opt/activepieces-assistant/.env
   systemctl status activepieces-backend
   ```

4. **Test Components**
   ```bash
   # Test database
   python src/db_config.py
   
   # Test vector store
   ls -la data/ap_faiss_index/
   
   # Test health
   curl http://localhost:8000/health
   ```

5. **GitHub Issues**
   - Open issue with error logs
   - Include system info
   - Describe steps taken

---

## 📚 Additional Resources

### Documentation
- **[README.md](README.md)** - Project overview
- **[DEPLOYMENT_SUMMARY.md](DEPLOYMENT_SUMMARY.md)** - Deployment system overview
- **[env.example](env.example)** - Environment variables

### External Links
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [LangChain Documentation](https://langchain.com)
- [OpenAI API Docs](https://platform.openai.com/docs)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Let's Encrypt](https://letsencrypt.org/)

---

## 🎯 Next Steps After Deployment

1. **Test All Features**
   - Send test messages
   - Try web search
   - Test code generation
   - Enable Build Flow mode

2. **Configure Monitoring**
   - Setup status checks
   - Configure log rotation
   - Monitor resource usage

3. **Setup Backups**
   - Database backups
   - Session backups
   - Configuration backups

4. **Optimize Performance**
   - Switch to Gunicorn
   - Enable compression
   - Monitor and tune

5. **Share with Team**
   - Document access URLs
   - Share API endpoints
   - Train users

---

## ✨ Success!

Once deployed, you'll have:
- 🤖 AI-powered assistant for ActivePieces
- 💬 Real-time chat interface
- 🔍 Semantic search (RAG)
- 🌐 Web search integration
- 💻 Code generation
- 🏗️ Flow building guidance
- 🔒 Secure HTTPS connection
- ⚡ Production-ready setup

**Access your assistant**: `https://your-domain.com`

---

## 📝 Feedback & Contributions

Found an issue or have a suggestion?
- Open a GitHub issue
- Submit a pull request
- Improve documentation

---

*Last Updated: 2024*
*Deployment guides tested on Ubuntu 22.04 and 24.04 LTS*

---

**Happy Deploying! 🚀**

