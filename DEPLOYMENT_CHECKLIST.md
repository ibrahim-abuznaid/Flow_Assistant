# ✅ Deployment Checklist

Quick reference checklist for manual deployment. Check off each item as you complete it.

---

## 🔐 Prerequisites

- [ ] DigitalOcean account created
- [ ] Droplet created (Ubuntu 22.04/24.04, 2GB RAM minimum)
- [ ] SSH access configured
- [ ] Domain name pointed to droplet IP (optional)
- [ ] OpenAI API key ready
- [ ] Perplexity API key ready (optional)

**Droplet IP**: `___________________`  
**Domain**: `___________________`

---

## Phase 1: Server Setup

- [ ] Connected to droplet via SSH
- [ ] Updated system (`apt update && apt upgrade`)
- [ ] Created non-root user (`adduser deploy`)
- [ ] Added user to sudo group
- [ ] Copied SSH keys to new user
- [ ] Switched to deploy user

---

## Phase 2: Install Dependencies

- [ ] Python 3.11+ installed and verified
- [ ] pip installed
- [ ] Node.js 20.x installed
- [ ] npm installed
- [ ] Nginx installed and running
- [ ] Git installed
- [ ] sqlite3 installed

**Verification Commands**:
```bash
python3 --version  # 3.11+
node --version     # v20.x
npm --version      # 10.x
nginx -v           # nginx/1.x
git --version      # git/2.x
```

---

## Phase 3: Deploy Database

- [ ] Repository cloned to `/var/www/Flow_Assistant`
- [ ] Database file exists (`data/activepieces.db`)
- [ ] Database verified: 433 pieces
- [ ] Database verified: 2681 actions
- [ ] Database verified: 694 triggers
- [ ] Permissions set correctly

**Test Commands**:
```bash
sqlite3 data/activepieces.db "SELECT COUNT(*) FROM pieces;"    # 433
sqlite3 data/activepieces.db "SELECT COUNT(*) FROM actions;"   # 2681
sqlite3 data/activepieces.db "SELECT COUNT(*) FROM triggers;"  # 694
```

---

## Phase 4: Deploy Vector Store

- [ ] Vector store directory exists (`data/ap_faiss_index/`)
- [ ] `index.faiss` file present
- [ ] `index.pkl` file present
- [ ] If missing, plan to run `prepare_knowledge_base.py` later

---

## Phase 5: Deploy Backend

- [ ] Virtual environment created
- [ ] Virtual environment activated
- [ ] Python dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created
- [ ] `.env` file configured with API keys
- [ ] ALLOWED_ORIGINS set to your domain
- [ ] Database connection tested
- [ ] Backend test run successful (`uvicorn src.main:app --host 0.0.0.0 --port 8000`)
- [ ] Health endpoint returns success (`curl http://localhost:8000/health`)
- [ ] Stats endpoint returns data (`curl http://localhost:8000/stats`)

**Environment Variables Configured**:
- [ ] `OPENAI_API_KEY`
- [ ] `MODEL_PROVIDER` (openai)
- [ ] `MODEL_NAME` (gpt-4o)
- [ ] `PLANNER_MODEL` (gpt-5-mini)
- [ ] `FLOW_BUILDER_MODEL` (gpt-5-mini)
- [ ] `SEARCH_PROVIDER` (openai or perplexity)
- [ ] `ALLOWED_ORIGINS` (your domain)
- [ ] `SQLITE_DB_FILE` (data/activepieces.db)

---

## Phase 6: Deploy Frontend

- [ ] npm dependencies installed (`npm install` in frontend/)
- [ ] `.env.production` file created
- [ ] `VITE_API_URL` configured
- [ ] Production build created (`npm run build`)
- [ ] `dist/` directory exists with files
- [ ] Build size checked (should be a few MB)

---

## Phase 7: Configure Nginx

- [ ] Nginx config file created (`/etc/nginx/sites-available/flow-assistant`)
- [ ] server_name set to your domain
- [ ] Backend upstream configured (port 8000)
- [ ] Frontend root path set (`/var/www/Flow_Assistant/frontend/dist`)
- [ ] API proxy configured (`/api/`)
- [ ] SSE endpoint configured (`/api/chat/stream`)
- [ ] Config symlinked to sites-enabled
- [ ] Nginx config tested (`sudo nginx -t`)
- [ ] Nginx restarted
- [ ] Nginx status is active

---

## Phase 8: Setup SSL

- [ ] Certbot installed
- [ ] SSL certificate obtained for domain
- [ ] Auto-renewal tested
- [ ] HTTPS working (lock icon in browser)
- [ ] HTTP redirects to HTTPS

**Skip this phase if**:
- You don't have a domain yet (use HTTP for now)
- Testing with IP address only

---

## Phase 9: Setup Systemd Services

- [ ] Backend service file created (`/etc/systemd/system/flow-assistant-backend.service`)
- [ ] Log files created
- [ ] Service enabled (`systemctl enable`)
- [ ] Service started (`systemctl start`)
- [ ] Service status is active and running
- [ ] Backend responds to health check

**Service Management**:
```bash
sudo systemctl status flow-assistant-backend   # Check status
sudo systemctl restart flow-assistant-backend  # Restart
tail -f /var/log/flow-assistant-backend.log   # View logs
```

---

## Phase 10: Final Testing

### Frontend Tests

- [ ] Website loads at `https://yourdomain.com`
- [ ] Header shows "ActivePieces AI Assistant"
- [ ] Statistics displayed (433 pieces, 2681 actions, 694 triggers)
- [ ] Chat interface visible
- [ ] Send message button works

### Chat Tests

- [ ] Send test message: "Does ActivePieces have a Slack integration?"
- [ ] Response received successfully
- [ ] Response is relevant and accurate
- [ ] Status indicators show during processing

### Build Flow Mode Tests

- [ ] Toggle "Build Flow" mode on
- [ ] Send test: "Create a flow that sends email when I receive a Slack message"
- [ ] Detailed flow guide received
- [ ] Guide includes steps, pieces, and actions

### Backend Tests

```bash
# All should return success
curl http://localhost:8000/health
curl http://localhost:8000/stats
curl http://localhost:8000/sessions
```

### Component Tests

- [ ] Database queries work
- [ ] Vector search works (if available)
- [ ] Web search works
- [ ] Session storage works

### System Resource Tests

```bash
free -h        # Memory usage < 80%
df -h          # Disk space adequate
ps aux | grep uvicorn  # Backend process running
sudo netstat -tlnp | grep -E '(80|443|8000)'  # Ports listening
```

---

## 🎉 Post-Deployment

### Security

- [ ] Firewall configured (ufw)
- [ ] Only necessary ports open (22, 80, 443)
- [ ] Non-root user in use
- [ ] SSH keys used (not passwords)
- [ ] .env file not in git
- [ ] SSL certificate valid and auto-renewing

### Monitoring

- [ ] Backend logs accessible
- [ ] Nginx logs accessible
- [ ] System resource monitoring set up
- [ ] Health check endpoint bookmarked

### Documentation

- [ ] Server IP and credentials saved securely
- [ ] Domain configuration documented
- [ ] API keys backed up securely
- [ ] Deployment date noted

### Backup Plan

- [ ] Database backup strategy planned
- [ ] Session data backup considered
- [ ] .env file backed up securely (not in git!)

---

## 📊 Final Verification

Run all these commands and verify success:

```bash
# 1. Backend Health
curl https://yourdomain.com/api/health
# Expected: {"status":"healthy","message":"Service is operational"}

# 2. Backend Stats
curl https://yourdomain.com/api/stats
# Expected: JSON with 433 pieces, 2681 actions, 694 triggers

# 3. Service Status
sudo systemctl status flow-assistant-backend
# Expected: Active (running) in green

# 4. Nginx Status
sudo systemctl status nginx
# Expected: Active (running) in green

# 5. Disk Space
df -h
# Expected: Plenty of free space

# 6. Memory Usage
free -h
# Expected: Available memory > 20%

# 7. Process Check
ps aux | grep uvicorn
# Expected: uvicorn process running

# 8. Port Check
sudo netstat -tlnp | grep -E '(80|443|8000)'
# Expected: All three ports LISTEN
```

---

## 🔄 Common Update Tasks

### Update Code

```bash
cd /var/www/Flow_Assistant
git pull origin main

# Backend changes:
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart flow-assistant-backend

# Frontend changes:
cd frontend
npm install
npm run build
sudo systemctl restart nginx
```

### View Logs

```bash
# Backend
tail -f /var/log/flow-assistant-backend.log

# Errors
tail -f /var/log/flow-assistant-backend-error.log

# Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Restart Services

```bash
# Backend
sudo systemctl restart flow-assistant-backend

# Nginx
sudo systemctl restart nginx

# Both
sudo systemctl restart flow-assistant-backend nginx
```

---

## ⚠️ Troubleshooting Quick Reference

| Issue | Quick Fix |
|-------|-----------|
| 502 Bad Gateway | `sudo systemctl restart flow-assistant-backend` |
| Frontend not loading | Check `dist/` exists, restart nginx |
| Database errors | Check file exists, verify permissions |
| Backend won't start | Check logs: `sudo journalctl -u flow-assistant-backend -n 50` |
| Out of memory | Reduce workers or upgrade droplet |
| SSL expired | `sudo certbot renew` |
| Can't connect via SSH | Check firewall allows port 22 |

---

## 📝 Deployment Info

**Date Deployed**: `___________________`

**Droplet Details**:
- IP: `___________________`
- Size: `___________________`
- Region: `___________________`

**Domain**: `___________________`

**Services**:
- Backend: ✅ Running
- Frontend: ✅ Running  
- Nginx: ✅ Running
- SSL: ✅ Enabled

**API Keys**:
- OpenAI: ✅ Configured
- Perplexity: ☐ Configured

---

**🎊 Deployment Complete!**

Keep this checklist for reference and future updates.

