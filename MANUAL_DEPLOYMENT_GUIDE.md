# 🚀 Manual Deployment Guide for DigitalOcean

A comprehensive step-by-step guide to manually deploy Flow Assistant on a DigitalOcean droplet.

---

## 📋 Table of Contents

1. [Project Components Overview](#project-components-overview)
2. [Prerequisites](#prerequisites)
3. [Phase 1: Server Setup](#phase-1-server-setup)
4. [Phase 2: Install Dependencies](#phase-2-install-dependencies)
5. [Phase 3: Deploy Database](#phase-3-deploy-database)
6. [Phase 4: Deploy Vector Store](#phase-4-deploy-vector-store)
7. [Phase 5: Deploy Backend](#phase-5-deploy-backend)
8. [Phase 6: Deploy Frontend](#phase-6-deploy-frontend)
9. [Phase 7: Configure Nginx](#phase-7-configure-nginx)
10. [Phase 8: Setup SSL](#phase-8-setup-ssl)
11. [Phase 9: Setup Systemd Services](#phase-9-setup-systemd-services)
12. [Phase 10: Final Testing](#phase-10-final-testing)
13. [Troubleshooting](#troubleshooting)

---

## 📊 Project Components Overview

Before we begin, let's understand what we're deploying:

### **1. Backend (Python/FastAPI)**
- **Location**: `src/` directory
- **Entry Point**: `src/main.py`
- **Port**: 8000
- **Dependencies**: Listed in `requirements.txt`
- **Key Components**:
  - FastAPI web server
  - LangChain agent with planning layer
  - Tool system (database queries, RAG, web search)
  - Session-based memory system

### **2. Frontend (React/Vite)**
- **Location**: `frontend/` directory
- **Entry Point**: `frontend/src/App.jsx`
- **Development Port**: 5173
- **Production**: Static files served by Nginx
- **Dependencies**: Listed in `frontend/package.json`

### **3. SQLite Database**
- **File**: `data/activepieces.db` (12MB)
- **Also**: `activepieces-pieces-db/activepieces-pieces.db` (backup)
- **Content**: 
  - 433 pieces (integrations)
  - 2,681 actions
  - 694 triggers
  - 10,118 input properties
- **No server required** - file-based database

### **4. Vector Store (FAISS)**
- **Location**: `data/ap_faiss_index/`
- **Files**:
  - `index.faiss` - FAISS index file
  - `index.pkl` - Document store and mappings
- **Purpose**: Semantic search for RAG
- **Model**: OpenAI text-embedding-ada-002

### **5. Session Storage**
- **Location**: `data/chat_sessions/`
- **Files**: JSON files per session
- **Index**: `data/sessions_index.json`

---

## 🔧 Prerequisites

### What You Need:

1. **DigitalOcean Account**
   - Create a droplet (Ubuntu 22.04 or 24.04 LTS)
   - Recommended: **2 GB RAM / 1 vCPU** or higher
   - $12/month droplet is sufficient for light use

2. **Domain Name** (optional but recommended)
   - Point your domain to your droplet's IP
   - Example: `flowassistant.yourdomain.com`

3. **API Keys**:
   - **OpenAI API Key** (required)
   - Perplexity API Key (optional, for web search)

4. **SSH Access**:
   - SSH key set up with DigitalOcean
   - Basic terminal knowledge

---

## Phase 1: Server Setup

### Step 1.1: Create Droplet

1. **Log into DigitalOcean** → Click "Create" → "Droplets"

2. **Choose Configuration**:
   - **Image**: Ubuntu 22.04 LTS x64
   - **Plan**: Basic (Regular) - $12/month (2GB RAM, 1 vCPU, 50GB SSD)
   - **Datacenter**: Choose closest to your users
   - **Authentication**: SSH keys (recommended) or Password
   - **Hostname**: `flow-assistant` or your choice

3. **Click "Create Droplet"**

4. **Wait for droplet to be created** (1-2 minutes)

5. **Note the IP address** (e.g., `143.198.123.45`)

### Step 1.2: Connect to Droplet

```bash
# On your local machine
ssh root@YOUR_DROPLET_IP

# Example:
ssh root@143.198.123.45
```

✅ **VERIFY**: You should see a terminal prompt like `root@flow-assistant:~#`

### Step 1.3: Update System

```bash
# Update package list
apt update

# Upgrade installed packages
apt upgrade -y
```

✅ **VERIFY**: Command completes without errors

### Step 1.4: Create Non-Root User (Security Best Practice)

```bash
# Create user
adduser deploy

# Add to sudo group
usermod -aG sudo deploy

# Copy SSH keys to new user
rsync --archive --chown=deploy:deploy ~/.ssh /home/deploy

# Switch to new user
su - deploy
```

✅ **VERIFY**: Prompt changes to `deploy@flow-assistant:~$`

---

## Phase 2: Install Dependencies

### Step 2.1: Install Python 3.11+

```bash
# Check current Python version
python3 --version

# If Python < 3.11, install Python 3.11
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev -y

# Set Python 3.11 as default
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
```

✅ **VERIFY**: Run `python3 --version` → Should show `Python 3.11.x` or higher

### Step 2.2: Install pip

```bash
sudo apt install python3-pip -y
```

✅ **VERIFY**: Run `pip3 --version` → Should show version info

### Step 2.3: Install Node.js and npm

```bash
# Install Node.js 20.x (LTS)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Verify installation
node --version
npm --version
```

✅ **VERIFY**: 
- `node --version` → Should show `v20.x.x`
- `npm --version` → Should show `10.x.x` or similar

### Step 2.4: Install Nginx

```bash
sudo apt install nginx -y

# Start and enable Nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

✅ **VERIFY**: 
- Visit `http://YOUR_DROPLET_IP` in browser
- Should see "Welcome to nginx!" page

### Step 2.5: Install Git

```bash
sudo apt install git -y
```

✅ **VERIFY**: Run `git --version` → Should show version info

---

## Phase 3: Deploy Database

### Step 3.1: Clone Repository

```bash
# Create app directory
sudo mkdir -p /var/www
sudo chown deploy:deploy /var/www

# Clone your repository
cd /var/www
git clone https://github.com/YOUR_USERNAME/Flow_Assistant.git
cd Flow_Assistant
```

✅ **VERIFY**: 
- Run `ls -la` 
- Should see project files (src/, frontend/, data/, etc.)

### Step 3.2: Verify Database Files

```bash
# Check if database exists
ls -lh data/activepieces.db
ls -lh activepieces-pieces-db/activepieces-pieces.db

# Check database size
du -h data/activepieces.db
```

✅ **VERIFY**: 
- Both files exist
- Size should be around 12MB

### Step 3.3: Test Database Connection

```bash
# Install sqlite3 for testing
sudo apt install sqlite3 -y

# Test database
sqlite3 data/activepieces.db "SELECT COUNT(*) as pieces FROM pieces;"
sqlite3 data/activepieces.db "SELECT COUNT(*) as actions FROM actions;"
sqlite3 data/activepieces.db "SELECT COUNT(*) as triggers FROM triggers;"
```

✅ **VERIFY**: 
- Should return: 433 pieces
- Should return: 2681 actions
- Should return: 694 triggers

### Step 3.4: Set Permissions

```bash
# Set proper permissions for data directory
chmod 755 data/
chmod 644 data/activepieces.db
chmod 755 data/chat_sessions/
```

✅ **VERIFY**: Run `ls -la data/` → Files should be readable

---

## Phase 4: Deploy Vector Store

### Step 4.1: Verify Vector Store Files

```bash
# Check FAISS index files
ls -lh data/ap_faiss_index/

# Should see:
# - index.faiss (the vector index)
# - index.pkl (document store)
```

✅ **VERIFY**: Both files exist

### Step 4.2: Check Vector Store Size

```bash
du -h data/ap_faiss_index/
```

✅ **VERIFY**: Directory should contain files (size varies)

**⚠️ IMPORTANT**: If vector store files don't exist, you'll need to generate them:

```bash
# After setting up Python environment (next phase), run:
python scripts/migration/prepare_knowledge_base.py
```

---

## Phase 5: Deploy Backend

### Step 5.1: Create Python Virtual Environment

```bash
cd /var/www/Flow_Assistant

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Your prompt should change to show (venv)
```

✅ **VERIFY**: Prompt shows `(venv)` prefix

### Step 5.2: Install Python Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# This will take 2-5 minutes
```

✅ **VERIFY**: 
- Run `pip list` 
- Should see packages like fastapi, langchain, openai, etc.

### Step 5.3: Configure Environment Variables

```bash
# Create .env file
nano .env
```

**Add the following content** (replace with your actual values):

```ini
# ============================================================================
# LLM Configuration
# ============================================================================
MODEL_PROVIDER=openai
MODEL_NAME=gpt-4o

# OpenAI API Key (REQUIRED)
OPENAI_API_KEY=sk-your-actual-openai-key-here

# Planning Layer Model
PLANNER_MODEL=gpt-5-mini

# Flow Builder Model
FLOW_BUILDER_MODEL=gpt-5-mini

# ============================================================================
# Web Search Configuration
# ============================================================================
SEARCH_PROVIDER=openai

# Perplexity API Key (only if using perplexity)
# PERPLEXITY_API_KEY=pplx-your-key-here

# ============================================================================
# Server Configuration
# ============================================================================
# For production, set allowed origins to your domain
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# ============================================================================
# Database Configuration
# ============================================================================
# SQLite path (default is correct)
SQLITE_DB_FILE=data/activepieces.db
```

**Save**: Press `Ctrl+X`, then `Y`, then `Enter`

✅ **VERIFY**: Run `cat .env` → Should show your configuration

### Step 5.4: Test Backend

```bash
# Make sure you're in project directory with venv activated
cd /var/www/Flow_Assistant
source venv/bin/activate

# Test database connection
python -c "from src.db_config import test_connection; test_connection()"

# Start backend (test mode)
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

**In a new SSH session** (keep the first one running):

```bash
# Test health endpoint
curl http://localhost:8000/health

# Should return: {"status":"healthy","message":"Service is operational"}

# Test stats endpoint
curl http://localhost:8000/stats

# Should return JSON with piece counts
```

✅ **VERIFY**: 
- Health check returns success
- Stats show correct counts (433 pieces, etc.)

**Stop the test server**: Go back to first SSH session and press `Ctrl+C`

---

## Phase 6: Deploy Frontend

### Step 6.1: Install Frontend Dependencies

```bash
cd /var/www/Flow_Assistant/frontend

# Install npm packages
npm install

# This will take 2-5 minutes
```

✅ **VERIFY**: 
- Run `ls node_modules/` 
- Should see many packages installed

### Step 6.2: Configure Frontend Environment

```bash
# Create production environment file
nano .env.production
```

**Add this content** (replace with your domain or droplet IP):

```ini
# Production API URL
VITE_API_URL=https://yourdomain.com/api

# OR if not using domain yet:
# VITE_API_URL=http://YOUR_DROPLET_IP/api
```

**Save**: `Ctrl+X`, `Y`, `Enter`

### Step 6.3: Build Frontend for Production

```bash
# Still in frontend directory
npm run build

# This creates optimized static files in frontend/dist/
```

✅ **VERIFY**: 
- Run `ls dist/` 
- Should see `index.html`, `assets/` directory, etc.

### Step 6.4: Check Build Size

```bash
du -h dist/
```

✅ **VERIFY**: Build should be a few MB

---

## Phase 7: Configure Nginx

### Step 7.1: Create Nginx Configuration

```bash
# Create nginx config file
sudo nano /etc/nginx/sites-available/flow-assistant
```

**Add this configuration**:

```nginx
# Upstream for backend API
upstream backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;  # Replace with your domain or droplet IP

    # Frontend - serve static files
    root /var/www/Flow_Assistant/frontend/dist;
    index index.html;

    # Frontend routes
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API proxy to backend
    location /api/ {
        proxy_pass http://backend/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Timeouts for long-running requests
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
    }

    # SSE (Server-Sent Events) for streaming
    location /api/chat/stream {
        proxy_pass http://backend/chat/stream;
        proxy_http_version 1.1;
        proxy_set_header Connection '';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # SSE specific settings
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 300;
        chunked_transfer_encoding off;
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1000;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json;

    # Client max body size (for file uploads if needed)
    client_max_body_size 10M;
}
```

**Save**: `Ctrl+X`, `Y`, `Enter`

### Step 7.2: Enable Site Configuration

```bash
# Create symbolic link to enable site
sudo ln -s /etc/nginx/sites-available/flow-assistant /etc/nginx/sites-enabled/

# Remove default site (optional)
sudo rm /etc/nginx/sites-enabled/default

# Test nginx configuration
sudo nginx -t
```

✅ **VERIFY**: Should say "syntax is ok" and "test is successful"

### Step 7.3: Restart Nginx

```bash
sudo systemctl restart nginx
sudo systemctl status nginx
```

✅ **VERIFY**: Status should show "active (running)"

---

## Phase 8: Setup SSL (HTTPS)

### Step 8.1: Install Certbot

```bash
sudo apt install certbot python3-certbot-nginx -y
```

### Step 8.2: Obtain SSL Certificate

**⚠️ IMPORTANT**: Make sure your domain is pointing to your droplet's IP first!

```bash
# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Follow the prompts:
# 1. Enter your email address
# 2. Agree to terms (Y)
# 3. Choose whether to redirect HTTP to HTTPS (recommended: 2 for redirect)
```

✅ **VERIFY**: 
- Certbot should say "Successfully enabled https://yourdomain.com"
- Visit `https://yourdomain.com` - should show lock icon

### Step 8.3: Test Auto-Renewal

```bash
# Test renewal process (doesn't actually renew)
sudo certbot renew --dry-run
```

✅ **VERIFY**: Should say "The dry run was successful"

---

## Phase 9: Setup Systemd Services

Now we'll create systemd services so the backend runs automatically and restarts if it crashes.

### Step 9.1: Create Backend Service

```bash
sudo nano /etc/systemd/system/flow-assistant-backend.service
```

**Add this content**:

```ini
[Unit]
Description=Flow Assistant Backend (FastAPI)
After=network.target

[Service]
Type=simple
User=deploy
Group=deploy
WorkingDirectory=/var/www/Flow_Assistant
Environment="PATH=/var/www/Flow_Assistant/venv/bin"
ExecStart=/var/www/Flow_Assistant/venv/bin/uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 2

# Restart policy
Restart=always
RestartSec=10

# Logging
StandardOutput=append:/var/log/flow-assistant-backend.log
StandardError=append:/var/log/flow-assistant-backend-error.log

[Install]
WantedBy=multi-user.target
```

**Save**: `Ctrl+X`, `Y`, `Enter`

### Step 9.2: Create Log Files

```bash
sudo touch /var/log/flow-assistant-backend.log
sudo touch /var/log/flow-assistant-backend-error.log
sudo chown deploy:deploy /var/log/flow-assistant-backend*.log
```

### Step 9.3: Enable and Start Service

```bash
# Reload systemd to recognize new service
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable flow-assistant-backend.service

# Start service
sudo systemctl start flow-assistant-backend.service

# Check status
sudo systemctl status flow-assistant-backend.service
```

✅ **VERIFY**: 
- Status should show "active (running)"
- Should see green dot next to "active"

### Step 9.4: Test Service

```bash
# Check if backend is responding
curl http://localhost:8000/health

# Check logs
tail -f /var/log/flow-assistant-backend.log

# Press Ctrl+C to stop watching logs
```

✅ **VERIFY**: Health check returns success

---

## Phase 10: Final Testing

### Step 10.1: Test Full Stack

**On your local machine**, open your browser and visit:

1. **Frontend**: `https://yourdomain.com`
   - Should load the chat interface
   - Should show "ActivePieces AI Assistant" header
   - Should display statistics (433 pieces, etc.)

2. **Test Chat**:
   - Type: "Does ActivePieces have a Slack integration?"
   - Click Send
   - Should get a response about Slack

3. **Test Build Flow Mode**:
   - Toggle "Build Flow" mode
   - Type: "Create a flow that sends an email when I receive a Slack message"
   - Should get a detailed flow guide

✅ **VERIFY**: All features work correctly

### Step 10.2: Test Each Component

```bash
# On the server, test each component

# 1. Database
sqlite3 /var/www/Flow_Assistant/data/activepieces.db "SELECT display_name FROM pieces LIMIT 5;"

# 2. Backend
curl http://localhost:8000/stats

# 3. Frontend (check if files are being served)
curl http://localhost/

# 4. API through Nginx
curl http://localhost/api/health
```

✅ **VERIFY**: All commands return expected results

### Step 10.3: Check System Resources

```bash
# Check memory usage
free -h

# Check disk usage
df -h

# Check running processes
ps aux | grep uvicorn

# Check open ports
sudo netstat -tlnp | grep -E '(80|443|8000)'
```

✅ **VERIFY**: 
- Memory usage is reasonable (< 80%)
- Disk has plenty of space
- Ports 80, 443, and 8000 are listening

---

## 🎉 Deployment Complete!

Your Flow Assistant is now deployed and running on DigitalOcean!

### Quick Reference URLs:

- **Frontend**: `https://yourdomain.com`
- **API Health**: `https://yourdomain.com/api/health`
- **API Stats**: `https://yourdomain.com/api/stats`

### Service Management Commands:

```bash
# Backend service
sudo systemctl status flow-assistant-backend    # Check status
sudo systemctl restart flow-assistant-backend   # Restart
sudo systemctl stop flow-assistant-backend      # Stop
sudo systemctl start flow-assistant-backend     # Start

# Nginx
sudo systemctl status nginx
sudo systemctl restart nginx
sudo nginx -t  # Test configuration

# View logs
tail -f /var/log/flow-assistant-backend.log
tail -f /var/log/flow-assistant-backend-error.log
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

---

## 🔧 Troubleshooting

### Issue: Backend Not Starting

```bash
# Check logs
sudo journalctl -u flow-assistant-backend.service -n 50 --no-pager

# Check if port is already in use
sudo lsof -i :8000

# Try starting manually
cd /var/www/Flow_Assistant
source venv/bin/activate
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### Issue: Frontend Not Loading

```bash
# Check if files exist
ls -la /var/www/Flow_Assistant/frontend/dist/

# Check nginx error logs
sudo tail -f /var/log/nginx/error.log

# Test nginx config
sudo nginx -t

# Rebuild frontend if needed
cd /var/www/Flow_Assistant/frontend
npm run build
```

### Issue: Database Connection Errors

```bash
# Check database file
ls -lh /var/www/Flow_Assistant/data/activepieces.db

# Test database
sqlite3 /var/www/Flow_Assistant/data/activepieces.db "SELECT COUNT(*) FROM pieces;"

# Check permissions
chmod 644 /var/www/Flow_Assistant/data/activepieces.db
```

### Issue: SSL Certificate Not Working

```bash
# Check certificate status
sudo certbot certificates

# Renew certificate
sudo certbot renew

# Check nginx SSL config
sudo nano /etc/nginx/sites-available/flow-assistant
```

### Issue: 502 Bad Gateway

This usually means the backend isn't running or Nginx can't reach it.

```bash
# Check backend status
sudo systemctl status flow-assistant-backend

# Check if backend is listening
curl http://localhost:8000/health

# Restart backend
sudo systemctl restart flow-assistant-backend

# Restart nginx
sudo systemctl restart nginx
```

### Issue: Out of Memory

```bash
# Check memory
free -h

# If low memory, consider:
# 1. Reduce uvicorn workers in service file (change --workers 2 to --workers 1)
# 2. Upgrade droplet to more RAM
# 3. Add swap space

# Add swap space (temporary fix):
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## 🔄 Updating Your Deployment

When you make changes to your code:

```bash
# SSH into server
ssh deploy@YOUR_DROPLET_IP

# Navigate to project
cd /var/www/Flow_Assistant

# Pull latest changes
git pull origin main

# If backend changes:
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart flow-assistant-backend

# If frontend changes:
cd frontend
npm install  # If dependencies changed
npm run build
sudo systemctl restart nginx

# Check everything is working
curl http://localhost:8000/health
```

---

## 📊 Monitoring

### Check Service Health

```bash
# Backend health
curl http://localhost:8000/health

# System resources
htop  # Install: sudo apt install htop

# Disk space
df -h

# Memory
free -h

# Service status
sudo systemctl status flow-assistant-backend
sudo systemctl status nginx
```

### View Logs

```bash
# Backend logs (live)
tail -f /var/log/flow-assistant-backend.log

# Backend errors
tail -f /var/log/flow-assistant-backend-error.log

# Nginx access logs
sudo tail -f /var/log/nginx/access.log

# Nginx error logs
sudo tail -f /var/log/nginx/error.log

# System logs for service
sudo journalctl -u flow-assistant-backend.service -f
```

---

## 🔒 Security Checklist

- ✅ SSH keys used instead of passwords
- ✅ Non-root user created (deploy)
- ✅ Firewall configured (ufw)
- ✅ SSL certificate installed (HTTPS)
- ✅ Nginx security headers configured
- ✅ API keys in .env file (not committed to git)
- ✅ Regular system updates (`sudo apt update && sudo apt upgrade`)

### Setup Firewall (Optional but Recommended)

```bash
# Enable firewall
sudo ufw enable

# Allow SSH
sudo ufw allow OpenSSH

# Allow HTTP and HTTPS
sudo ufw allow 'Nginx Full'

# Check status
sudo ufw status
```

---

## 📝 Notes

### Component Checklist

After deployment, verify each component:

- ✅ **SQLite Database**: 12MB file with 433 pieces, 2681 actions, 694 triggers
- ✅ **Vector Store**: FAISS index with embeddings for semantic search
- ✅ **Backend**: FastAPI server on port 8000 with LangChain agent
- ✅ **Frontend**: React app built and served by Nginx
- ✅ **Session Storage**: JSON files for chat history
- ✅ **Nginx**: Reverse proxy with SSL
- ✅ **Systemd**: Auto-restart services

### Key Files and Locations

```
/var/www/Flow_Assistant/                    # Main application
├── src/                                     # Backend source
│   ├── main.py                             # FastAPI app
│   ├── agent.py                            # LangChain agent
│   ├── tools.py                            # Agent tools
│   └── db_config.py                        # Database config
├── frontend/                                # Frontend source
│   ├── dist/                               # Built static files (served by Nginx)
│   └── src/                                # React source
├── data/                                    # Data directory
│   ├── activepieces.db                     # SQLite database (12MB)
│   ├── ap_faiss_index/                     # Vector store
│   └── chat_sessions/                      # Session storage
├── venv/                                    # Python virtual environment
└── .env                                     # Environment variables (API keys)

/etc/nginx/sites-available/flow-assistant   # Nginx config
/etc/systemd/system/flow-assistant-backend.service  # Systemd service
/var/log/flow-assistant-*.log               # Application logs
```

---

**🎊 Congratulations! Your Flow Assistant is now deployed and production-ready!**

For questions or issues, check the troubleshooting section above.

