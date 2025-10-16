# 🚀 Start Here - Manual Deployment Guide

Welcome! You're about to manually deploy Flow Assistant to a DigitalOcean droplet.

---

## 📚 Documentation Overview

I've created **3 comprehensive documents** to guide you through the deployment:

### 1. 📖 **ARCHITECTURE_OVERVIEW.md** (Read This First!)
**Purpose**: Understand what you're deploying

**What's inside**:
- System architecture diagram
- All components explained (Frontend, Backend, Database, Vector Store, etc.)
- How requests flow through the system
- Technology stack details
- Design decisions explained
- Resource usage expectations

**Why read it**: You'll understand exactly what each piece does and why it's needed. This makes troubleshooting much easier!

**Time needed**: 15-20 minutes

---

### 2. 📋 **MANUAL_DEPLOYMENT_GUIDE.md** (The Main Guide)
**Purpose**: Step-by-step deployment instructions

**What's inside**:
- 10 phases with detailed steps
- Commands to copy and paste
- Verification steps after each phase
- Troubleshooting section
- Update procedures
- Security checklist

**Phases**:
1. Server Setup (Ubuntu droplet, SSH)
2. Install Dependencies (Python, Node.js, Nginx)
3. Deploy Database (SQLite setup)
4. Deploy Vector Store (FAISS)
5. Deploy Backend (FastAPI/Python)
6. Deploy Frontend (React build)
7. Configure Nginx (Reverse proxy)
8. Setup SSL (HTTPS with Let's Encrypt)
9. Setup Systemd Services (Auto-start)
10. Final Testing (Verify everything works)

**Why follow it**: Every command is tested and explained. You'll know exactly what's happening at each step.

**Time needed**: 2-3 hours (for first-time deployment)

---

### 3. ✅ **DEPLOYMENT_CHECKLIST.md** (Print This!)
**Purpose**: Quick reference while deploying

**What's inside**:
- Checkbox list for each step
- Quick verification commands
- Troubleshooting quick reference
- Service management commands
- Post-deployment checklist

**Why use it**: Print it out or keep it on a second screen. Check off each item as you complete it.

**Time needed**: Use alongside the main guide

---

## 🎯 How to Use These Documents

### Recommended Approach:

**Step 1**: Read ARCHITECTURE_OVERVIEW.md (20 min)
- Get familiar with all the components
- Understand the big picture
- Know what you're deploying and why

**Step 2**: Prepare Your Prerequisites
- [ ] Create DigitalOcean account
- [ ] Create a droplet (Ubuntu 22.04/24.04, 2GB RAM)
- [ ] Get your OpenAI API key
- [ ] (Optional) Point your domain to droplet IP
- [ ] Set up SSH access

**Step 3**: Follow MANUAL_DEPLOYMENT_GUIDE.md
- Open it in one window
- Open DEPLOYMENT_CHECKLIST.md in another
- Open SSH terminal in a third
- Work through each phase
- Check off items in the checklist
- Verify each component before moving on

**Step 4**: Test Everything
- Complete Phase 10 testing
- Verify all checkboxes are marked
- Bookmark your deployment

---

## 🔧 What You're Deploying

### Quick Overview:

```
Your Deployment:
├── Frontend (React App)
│   └── Served by Nginx at https://yourdomain.com
│
├── Backend (Python/FastAPI)
│   └── Running on port 8000 with systemd
│
├── Database (SQLite)
│   └── 12MB file with 433 pieces, 2681 actions
│
├── Vector Store (FAISS)
│   └── For semantic search and RAG
│
└── Session Storage (JSON files)
    └── For chat history
```

**All running on a single DigitalOcean droplet!**

---

## ⚙️ Prerequisites Checklist

Before you start, make sure you have:

- [ ] **DigitalOcean Account** (or sign up at digitalocean.com)
- [ ] **$12/month budget** (for 2GB droplet - can upgrade later)
- [ ] **OpenAI API Key** (get from platform.openai.com)
- [ ] **Basic terminal knowledge** (copy/paste commands, read output)
- [ ] **Domain name** (optional - can use IP address initially)
- [ ] **2-3 hours** (for first deployment)

---

## 🎬 Quick Start

Ready to deploy? Follow these steps:

### 1. Create Your Droplet

```bash
1. Log into DigitalOcean
2. Click "Create" → "Droplets"
3. Choose:
   - Ubuntu 22.04 LTS
   - Basic plan: $12/month (2GB RAM, 1 vCPU)
   - Datacenter: Closest to you
   - SSH keys or password
4. Create and wait for IP address
```

### 2. Connect via SSH

```bash
ssh root@YOUR_DROPLET_IP
```

### 3. Open the Main Guide

Open **MANUAL_DEPLOYMENT_GUIDE.md** and start with **Phase 1: Server Setup**

### 4. Work Through Each Phase

Follow the guide step-by-step:
- ✅ Phase 1: Server Setup
- ✅ Phase 2: Install Dependencies
- ✅ Phase 3: Deploy Database
- ✅ Phase 4: Deploy Vector Store
- ✅ Phase 5: Deploy Backend
- ✅ Phase 6: Deploy Frontend
- ✅ Phase 7: Configure Nginx
- ✅ Phase 8: Setup SSL (if using domain)
- ✅ Phase 9: Setup Systemd Services
- ✅ Phase 10: Final Testing

### 5. Verify Everything Works

Visit `https://yourdomain.com` (or `http://YOUR_IP`) and test:
- Chat functionality
- Build Flow mode
- Statistics display
- Session management

---

## 📊 Project Components at a Glance

| Component | Technology | Purpose | Size |
|-----------|------------|---------|------|
| **Frontend** | React + Vite | User interface | ~2 MB built |
| **Backend** | FastAPI + Python | API server | ~500 MB with deps |
| **Database** | SQLite | ActivePieces data | 12 MB |
| **Vector Store** | FAISS | Semantic search | ~50 MB |
| **Sessions** | JSON files | Chat history | Grows over time |
| **Web Server** | Nginx | Reverse proxy + SSL | ~20 MB |

**Total disk usage**: ~2 GB (50 GB droplet has plenty of space)

**Memory usage**: ~600-800 MB (2 GB droplet is sufficient)

---

## 🆘 Need Help?

### During Deployment:

1. **Check the verification steps** after each phase
2. **Look at DEPLOYMENT_CHECKLIST.md** for quick fixes
3. **Review MANUAL_DEPLOYMENT_GUIDE.md troubleshooting section**
4. **Check logs**: 
   ```bash
   tail -f /var/log/flow-assistant-backend.log
   sudo journalctl -u flow-assistant-backend -n 50
   ```

### Common Issues:

| Issue | Solution |
|-------|----------|
| Backend won't start | Check logs, verify .env file, test manually |
| Frontend not loading | Verify dist/ exists, check nginx config |
| 502 Bad Gateway | Backend not running - restart service |
| Database errors | Check file exists and has correct permissions |
| SSL issues | Verify domain points to IP, run certbot |

---

## 📝 Important Notes

### About SSL/HTTPS:
- If you **have a domain**: Follow Phase 8 for SSL setup
- If you **don't have a domain yet**: Skip Phase 8, use HTTP initially
- You can add SSL later when you get a domain

### About API Keys:
- **Required**: OpenAI API key (for LLM and embeddings)
- **Optional**: Perplexity API key (for alternative web search)

### About Git Repository:
- The guide assumes you've pushed your code to GitHub
- If not, you can also upload via SCP or rsync
- Make sure `.env` is NOT in your git repository!

### Time Estimates:
- **First deployment**: 2-3 hours (reading + setup)
- **Subsequent deployments**: 30-45 minutes
- **Updates only**: 5-10 minutes

---

## 🎯 Success Criteria

Your deployment is successful when:

✅ You can access the website at your domain/IP  
✅ Statistics show: 433 pieces, 2681 actions, 694 triggers  
✅ You can send a chat message and get a response  
✅ Build Flow mode generates flow guides  
✅ Sessions are saved and loadable  
✅ Backend service is running and auto-starts  
✅ SSL is active (if using domain)  
✅ Nginx is serving frontend and proxying API  

---

## 🗺️ Deployment Roadmap

```
START
  │
  ├─→ [Read Architecture Overview] (15-20 min)
  │     └─→ Understand what you're deploying
  │
  ├─→ [Prepare Prerequisites] (10-30 min)
  │     ├─→ Create DigitalOcean account
  │     ├─→ Create droplet
  │     └─→ Get API keys
  │
  ├─→ [Follow Manual Guide] (2-3 hours)
  │     ├─→ Phase 1: Server Setup
  │     ├─→ Phase 2: Dependencies
  │     ├─→ Phase 3: Database
  │     ├─→ Phase 4: Vector Store
  │     ├─→ Phase 5: Backend
  │     ├─→ Phase 6: Frontend
  │     ├─→ Phase 7: Nginx
  │     ├─→ Phase 8: SSL (optional)
  │     ├─→ Phase 9: Systemd
  │     └─→ Phase 10: Testing
  │
  └─→ [DEPLOYED!] 🎉
        └─→ Your app is live!
```

---

## 📖 Next Steps

**Right now**: Open **ARCHITECTURE_OVERVIEW.md** and read it

**After reading**: Open **MANUAL_DEPLOYMENT_GUIDE.md** and start Phase 1

**While deploying**: Use **DEPLOYMENT_CHECKLIST.md** to track progress

---

## 💬 Final Words

This deployment is designed to be:

- ✅ **Manual**: You control every step
- ✅ **Educational**: You understand what's happening
- ✅ **Reliable**: Every step is tested
- ✅ **Production-ready**: Built with best practices

**Don't rush!** Take your time with each phase. Verify each component works before moving to the next. This will save you debugging time later.

---

**🚀 Ready? Let's deploy!**

Open **ARCHITECTURE_OVERVIEW.md** to begin.

---

## 📄 Document Quick Access

1. **ARCHITECTURE_OVERVIEW.md** - Understanding the system
2. **MANUAL_DEPLOYMENT_GUIDE.md** - Step-by-step instructions
3. **DEPLOYMENT_CHECKLIST.md** - Progress tracking

All three documents work together to ensure a successful deployment!

**Good luck! 🍀**

