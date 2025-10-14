# 🚀 START HERE - Deployment Guide

## Welcome! Ready to Deploy Your AI Assistant?

This guide will help you deploy the **ActivePieces AI Assistant** to a fresh DigitalOcean droplet in **30 minutes or less**!

---

## 📍 You Are Here

```
┌─────────────────────────────────────────────────────────────┐
│                                                               │
│              👋 WELCOME TO DEPLOYMENT GUIDE!                 │
│                                                               │
│    Everything you need to deploy is documented and ready     │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Choose Your Deployment Path

### Path 1: Lightning Fast ⚡ (5 minutes)
**Perfect for**: Those who trust automation

```bash
# One command does everything!
curl -fsSL https://raw.githubusercontent.com/yourusername/Flow_Assistant/main/scripts/deployment/deploy_digitalocean.sh | sudo bash
```

**What happens**:
- ✅ Installs all dependencies
- ✅ Configures everything
- ✅ Prompts for your API keys
- ✅ Sets up SSL (optional)
- ✅ Starts all services

**Time**: 5-10 minutes  
**Effort**: Minimal (just enter API keys)  
**Documentation**: [deploy_digitalocean.sh](scripts/deployment/deploy_digitalocean.sh)

---

### Path 2: Quick Manual 🏃 (30 minutes)
**Perfect for**: Those who want control but not too much reading

➜ **Follow**: [QUICK_DEPLOY.md](QUICK_DEPLOY.md)

**What you do**:
- Copy-paste commands
- Configure .env file
- Verify deployment

**Features**:
- Step-by-step commands
- No lengthy explanations
- Quick troubleshooting
- Essential commands only

**Time**: 30 minutes  
**Effort**: Moderate (copy-paste commands)

---

### Path 3: Complete Walkthrough 📚 (45 minutes)
**Perfect for**: First-time deployers, learning, production setup

➜ **Follow**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

**What you get**:
- Detailed explanations
- Understanding each step
- Comprehensive troubleshooting
- Security best practices
- Performance optimization
- Monitoring setup

**Time**: 45 minutes  
**Effort**: Higher (read and understand)

---

## 📊 What Gets Deployed?

```
Your Complete AI Assistant Stack:

┌────────────────────────────────────────┐
│           🌐 Nginx (Port 80/443)       │
│         Reverse Proxy + SSL/TLS        │
└──────────────┬─────────────────────────┘
               │
    ┌──────────┴──────────┐
    │                     │
┌───▼──────┐      ┌───────▼────┐
│ Frontend │      │  Backend   │
│  React   │      │  FastAPI   │
│ (5173)   │      │  (8000)    │
└──────────┘      └─────┬──────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
    ┌───▼────┐     ┌────▼───┐     ┌────▼────┐
    │ SQLite │     │ FAISS  │     │   Web   │
    │   DB   │     │ Vector │     │  Search │
    └────────┘     └────────┘     └─────────┘

Components:
✅ Backend: FastAPI + LangChain + OpenAI
✅ Frontend: React UI with real-time chat
✅ Database: SQLite (433+ integrations)
✅ Vector Store: FAISS (RAG system)
✅ Web Search: OpenAI or Perplexity
✅ Infrastructure: Nginx + SSL + Systemd
```

---

## 📋 What You Need

### Prerequisites Checklist

- [ ] **DigitalOcean Droplet**
  - Ubuntu 22.04 or 24.04 LTS
  - 2GB RAM minimum (4GB recommended)
  - 50GB SSD minimum

- [ ] **API Keys**
  - OpenAI API key (required) - [Get it here](https://platform.openai.com/api-keys)
  - Perplexity API key (optional) - [Get it here](https://www.perplexity.ai/)

- [ ] **Access**
  - SSH access to your droplet
  - `ssh root@your_droplet_ip`

- [ ] **Domain** (Optional but recommended)
  - For SSL certificate
  - Point A record to droplet IP

---

## 🚀 Quick Start (30 min)

### Step 1: Choose Your Path (1 min)
Pick one of the three paths above based on your preference.

### Step 2: Prepare (2 min)
- Have your OpenAI API key ready
- SSH into your droplet
- Note your domain/IP

### Step 3: Deploy (20 min)
Follow your chosen guide:
- **Fast**: Run automated script
- **Quick**: Follow [QUICK_DEPLOY.md](QUICK_DEPLOY.md)
- **Complete**: Follow [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

### Step 4: Verify (5 min)
```bash
# Check services
systemctl status activepieces-backend
systemctl status activepieces-frontend

# Test health
curl http://localhost:8000/health

# Expected: {"status":"healthy","message":"Service is operational"}
```

### Step 5: Access (2 min)
Open browser: `http://your-domain.com` or `http://your-ip`

**You're done! 🎉**

---

## 📚 All Documentation

### Main Guides
1. **[DEPLOYMENT_INDEX.md](DEPLOYMENT_INDEX.md)** - Navigation hub (all guides)
2. **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Complete walkthrough
3. **[QUICK_DEPLOY.md](QUICK_DEPLOY.md)** - Quick reference

### Support Docs
4. **[DEPLOYMENT_SUMMARY.md](DEPLOYMENT_SUMMARY.md)** - Architecture overview
5. **[DEPLOYMENT_COMPLETE.md](DEPLOYMENT_COMPLETE.md)** - What's new
6. **[DEPLOYMENT_CHANGELOG.md](DEPLOYMENT_CHANGELOG.md)** - Change log
7. **[DEPLOYMENT_FILES.md](DEPLOYMENT_FILES.md)** - File reference

### Scripts
8. **[deploy_digitalocean.sh](scripts/deployment/deploy_digitalocean.sh)** - Automated deployment

### Configuration
9. **[env.example](env.example)** - Environment template

---

## 🔧 After Deployment

### Verify Everything Works

```bash
# 1. Check services are running
systemctl status activepieces-backend --no-pager
systemctl status activepieces-frontend --no-pager

# 2. Test health endpoint
curl http://localhost:8000/health

# 3. Test stats endpoint
curl http://localhost:8000/stats

# 4. Open web interface
# http://your-domain.com
```

### Test Features

1. **Chat**: Send "Does ActivePieces have a Slack integration?"
2. **Web Search**: Send "What's the latest news about automation?"
3. **Code Generation**: Send "Create code to fetch user data from an API"
4. **Build Flow**: Enable toggle and send "Create a Slack notification workflow"

---

## 🆘 If Something Goes Wrong

### Quick Fixes

**Services not running?**
```bash
journalctl -u activepieces-backend -n 50
systemctl restart activepieces-backend
```

**Can't access website?**
```bash
systemctl status nginx
nginx -t
systemctl restart nginx
```

**Need detailed help?**
➜ See [DEPLOYMENT_GUIDE.md - Troubleshooting](DEPLOYMENT_GUIDE.md#-troubleshooting)

---

## ✅ Success Checklist

Your deployment is successful when:

- [ ] Both services show "active (running)"
- [ ] Health endpoint returns 200 OK
- [ ] Web interface loads
- [ ] Can send chat messages
- [ ] Database queries work
- [ ] Web search works
- [ ] Code generation works
- [ ] Build Flow mode works
- [ ] SSL configured (if using domain)
- [ ] Firewall properly set

---

## 🎯 Recommended Path

**For Most Users**:
1. Start with **[DEPLOYMENT_INDEX.md](DEPLOYMENT_INDEX.md)**
2. Review **[DEPLOYMENT_COMPLETE.md](DEPLOYMENT_COMPLETE.md)**
3. Choose deployment method (automated/quick/complete)
4. Deploy!
5. Verify all features work
6. Setup monitoring and backups

**Total Time**: 30-45 minutes  
**Result**: Production-ready AI Assistant! 🚀

---

## 📖 Documentation Map

```
START_HERE.md (You are here!)
    │
    ├─➜ DEPLOYMENT_INDEX.md (Choose your path)
    │       │
    │       ├─➜ Path 1: deploy_digitalocean.sh (Automated)
    │       ├─➜ Path 2: QUICK_DEPLOY.md (Quick Manual)
    │       └─➜ Path 3: DEPLOYMENT_GUIDE.md (Complete)
    │
    ├─➜ DEPLOYMENT_COMPLETE.md (What's new)
    ├─➜ DEPLOYMENT_SUMMARY.md (Architecture)
    ├─➜ DEPLOYMENT_FILES.md (File reference)
    └─➜ env.example (Configuration)
```

---

## 💡 Tips

### Before Deploying
- ✅ Have OpenAI API key ready
- ✅ Know your domain/IP
- ✅ Have 30-45 minutes available
- ✅ Read prerequisites

### During Deployment
- ✅ Follow ONE guide completely
- ✅ Don't skip steps
- ✅ Note any errors
- ✅ Check logs if issues

### After Deployment
- ✅ Test all features
- ✅ Setup SSL (if domain)
- ✅ Configure backups
- ✅ Monitor services
- ✅ Review security

---

## 🌟 What You'll Have

After successful deployment:

**Access**: `https://your-domain.com`

**Features**:
- 🤖 AI-powered chat assistant
- 💬 Real-time messaging
- 🔍 Semantic search (RAG)
- 🌐 Web search integration
- 💻 Code generation
- 🏗️ Flow building guides
- 🔒 Secure HTTPS
- ⚡ Production-ready

**Management**:
- Service auto-restart
- Health monitoring
- Log rotation
- Easy updates
- Backup procedures

---

## 🎉 Ready to Start?

### Next Steps:

1. **Read**: [DEPLOYMENT_INDEX.md](DEPLOYMENT_INDEX.md) (5 min)
2. **Choose**: Your deployment path
3. **Deploy**: Follow your chosen guide (30-45 min)
4. **Enjoy**: Your AI Assistant! 🚀

---

## 📞 Need Help?

- **Documentation**: Check [DEPLOYMENT_INDEX.md](DEPLOYMENT_INDEX.md)
- **Troubleshooting**: See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md#-troubleshooting)
- **Quick Fixes**: See [QUICK_DEPLOY.md](QUICK_DEPLOY.md#-troubleshooting)
- **Issues**: Open GitHub issue with error logs

---

**Let's Deploy! 🚀**

➜ **Next**: [DEPLOYMENT_INDEX.md](DEPLOYMENT_INDEX.md)

---

*Everything is documented. Everything is tested. Everything works.*  
*Your AI Assistant awaits! 🤖*

