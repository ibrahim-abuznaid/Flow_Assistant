# Complete Deployment Guide - DigitalOcean Droplet

## 🚀 Deploy ActivePieces AI Assistant from Scratch

This guide will walk you through deploying the complete application on a fresh DigitalOcean Ubuntu droplet. Everything will work - backend, frontend, database, vector store, RAG, and web search.

---

## 📋 What You'll Get

✅ **Backend**: FastAPI server with LangChain AI agent  
✅ **Frontend**: React UI with real-time chat  
✅ **Database**: SQLite with 433+ ActivePieces integrations  
✅ **Vector Store**: FAISS for semantic search (RAG)  
✅ **Web Search**: OpenAI or Perplexity integration  
✅ **Production Ready**: Nginx, SSL, systemd services  

---

## 🎯 Prerequisites

### Before You Start

1. **DigitalOcean Droplet**
   - Ubuntu 22.04 or 24.04 LTS
   - Minimum: 2GB RAM, 1 vCPU, 50GB SSD
   - Recommended: 4GB RAM, 2 vCPU, 80GB SSD

2. **API Keys** (Get these ready)
   - OpenAI API key (required) - [Get it here](https://platform.openai.com/api-keys)
   - Perplexity API key (optional) - [Get it here](https://www.perplexity.ai/)

3. **Domain Name** (Optional but recommended)
   - Point your domain's A record to your droplet's IP
   - Example: `assistant.yourdomain.com` → `your.droplet.ip`

4. **SSH Access**
   - Make sure you can SSH into your droplet
   - `ssh root@your_droplet_ip`

---

## 🚀 Step-by-Step Deployment

### Step 1: Initial Server Setup (5 minutes)

SSH into your droplet:

```bash
ssh root@your_droplet_ip
```

Update the system:

```bash
apt update && apt upgrade -y
```

### Step 2: Install System Dependencies (5 minutes)

Install all required packages:

```bash
# Install Python, Node.js, Nginx, and other essentials
apt install -y python3 python3-pip python3-venv nodejs npm nginx git curl ufw

# Install Node.js 20 (required for frontend)
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs

# Verify installations
python3 --version    # Should be 3.8+
node --version       # Should be 18+
npm --version
nginx -v
```

### Step 3: Clone the Repository (2 minutes)

```bash
# Create application directory
mkdir -p /opt/activepieces-assistant
cd /opt/activepieces-assistant

# Clone your repository
git clone https://github.com/yourusername/Flow_Assistant.git .

# If repository is private, use SSH or provide credentials
```

### Step 4: Setup Python Backend (5 minutes)

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
pip install -r requirements.txt

# Verify installation
python -c "import fastapi; import langchain; print('✓ Dependencies installed')"
```

### Step 5: Configure Environment Variables (3 minutes)

Create your `.env` file:

```bash
nano .env
```

Add the following configuration (replace with your actual keys):

```ini
# ============================================================================
# LLM Configuration
# ============================================================================
OPENAI_API_KEY=sk-your-actual-openai-key-here
MODEL_PROVIDER=openai
MODEL_NAME=gpt-4o

# Planning Layer Model (optional - uses gpt-4o if not set)
PLANNER_MODEL=gpt-4o-mini

# Flow Builder Model (optional - uses gpt-4o if not set)
FLOW_BUILDER_MODEL=gpt-4o-mini

# ============================================================================
# Web Search Configuration
# ============================================================================
# Search provider: openai (default) or perplexity
SEARCH_PROVIDER=openai

# Perplexity API Key (only needed if SEARCH_PROVIDER=perplexity)
# PERPLEXITY_API_KEY=pplx-your-key-here

# ============================================================================
# Database Configuration (SQLite - No setup needed!)
# ============================================================================
SQLITE_DB_FILE=data/activepieces.db

# ============================================================================
# Application Configuration
# ============================================================================
PORT=8000
ALLOWED_ORIGINS=http://your-domain.com,https://your-domain.com
```

**Important**: Replace:
- `sk-your-actual-openai-key-here` with your OpenAI API key
- `your-domain.com` with your actual domain (or use your droplet IP)

Save and exit: `Ctrl+X`, then `Y`, then `Enter`

### Step 6: Verify Database (1 minute)

The SQLite database is included in the repository. Let's verify it:

```bash
# Test database connection
python src/db_config.py
```

Expected output:
```
[OK] Database connected successfully! Found 433 pieces.
Database size: 2.32 MB
```

### Step 7: Prepare Vector Store (3 minutes)

Create the FAISS vector index for semantic search:

```bash
# Make sure you're in the virtual environment
source venv/bin/activate

# Run the preparation script
python scripts/migration/prepare_knowledge_base.py
```

Expected output:
```
Loading Pieces knowledge base...
Total pieces: 433
Total actions: 2681
Total triggers: 694

Creating documents...
Created 3808 documents

Creating vector store...
✓ Knowledge base preparation complete!
```

### Step 8: Build Frontend (5 minutes)

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create production environment file
cat > .env.production << 'EOF'
VITE_API_URL=http://your-domain.com
EOF

# Build for production
npm run build

# Go back to root
cd ..
```

**Note**: Replace `http://your-domain.com` with:
- Your domain: `https://yourdomain.com` (if using SSL)
- Or your IP: `http://your.droplet.ip`

### Step 9: Create Systemd Services (3 minutes)

#### Backend Service

```bash
cat > /etc/systemd/system/activepieces-backend.service << 'EOF'
[Unit]
Description=ActivePieces AI Assistant Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/activepieces-assistant
Environment="PATH=/opt/activepieces-assistant/venv/bin"
EnvironmentFile=/opt/activepieces-assistant/.env
ExecStart=/opt/activepieces-assistant/venv/bin/uvicorn src.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
```

#### Frontend Service

First, install `serve`:

```bash
npm install -g serve
```

Create frontend service:

```bash
cat > /etc/systemd/system/activepieces-frontend.service << 'EOF'
[Unit]
Description=ActivePieces AI Assistant Frontend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/activepieces-assistant/frontend
ExecStart=/usr/bin/serve -s dist -l 5173
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
```

#### Set Permissions

```bash
chown -R www-data:www-data /opt/activepieces-assistant
chmod -R 755 /opt/activepieces-assistant
```

### Step 10: Configure Nginx (3 minutes)

Create Nginx configuration:

```bash
cat > /etc/nginx/sites-available/activepieces-assistant << 'EOF'
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;  # Replace with your domain or droplet IP

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Frontend
    location / {
        proxy_pass http://localhost:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api/ {
        rewrite ^/api/(.*) /$1 break;
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Direct backend endpoints (health, stats, etc.)
    location ~ ^/(health|stats|chat|sessions|reset) {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Add CORS headers for chat endpoint
        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS, DELETE' always;
        add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range' always;
        
        if ($request_method = 'OPTIONS') {
            return 204;
        }
    }

    # Increase upload size for code generation
    client_max_body_size 10M;
}
EOF
```

**Important**: Replace `your-domain.com` with:
- Your actual domain name
- Or your droplet IP address

Enable the site:

```bash
# Remove default site
rm -f /etc/nginx/sites-enabled/default

# Enable your site
ln -sf /etc/nginx/sites-available/activepieces-assistant /etc/nginx/sites-enabled/

# Test configuration
nginx -t

# If test passes, restart Nginx
systemctl restart nginx
systemctl enable nginx
```

### Step 11: Configure Firewall (2 minutes)

```bash
# Enable firewall
ufw --force enable

# Allow SSH (IMPORTANT - do this first!)
ufw allow OpenSSH

# Allow HTTP and HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Check status
ufw status
```

Expected output:
```
Status: active

To                         Action      From
--                         ------      ----
OpenSSH                    ALLOW       Anywhere
80/tcp                     ALLOW       Anywhere
443/tcp                    ALLOW       Anywhere
```

### Step 12: Start Services (2 minutes)

```bash
# Reload systemd
systemctl daemon-reload

# Enable services (start on boot)
systemctl enable activepieces-backend
systemctl enable activepieces-frontend

# Start services
systemctl start activepieces-backend
systemctl start activepieces-frontend

# Check status
systemctl status activepieces-backend --no-pager
systemctl status activepieces-frontend --no-pager
```

Both services should show **active (running)** in green.

### Step 13: Verify Deployment (2 minutes)

#### Test Backend

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status":"healthy","message":"Service is operational"}
```

#### Test Frontend

Open your browser and go to:
- `http://your-domain.com` (if using domain)
- `http://your.droplet.ip` (if using IP)

You should see the AI Assistant interface!

### Step 14: Setup SSL with Let's Encrypt (Optional, 5 minutes)

**Only if you have a domain name:**

```bash
# Install Certbot
apt install -y certbot python3-certbot-nginx

# Obtain SSL certificate
certbot --nginx -d your-domain.com -d www.your-domain.com

# Follow the prompts:
# - Enter your email
# - Agree to terms
# - Choose whether to redirect HTTP to HTTPS (recommended: Yes)
```

Certbot will automatically:
- ✅ Obtain SSL certificate
- ✅ Update Nginx configuration
- ✅ Setup auto-renewal

Verify auto-renewal:

```bash
certbot renew --dry-run
```

---

## ✅ Post-Deployment Verification

### 1. Check All Services

```bash
# Backend
systemctl status activepieces-backend --no-pager

# Frontend
systemctl status activepieces-frontend --no-pager

# Nginx
systemctl status nginx --no-pager
```

All should show **active (running)**.

### 2. Test the Application

1. **Open your browser**: `https://your-domain.com` (or `http://your-ip`)
2. **Send a test message**: "Does ActivePieces have a Slack integration?"
3. **Verify response**: Should get detailed information about Slack integration

### 3. Test All Features

- ✅ **Chat**: Send messages and get responses
- ✅ **Database**: Ask about specific integrations
- ✅ **RAG**: Ask complex questions that need semantic search
- ✅ **Web Search**: Ask "What's the latest news about automation?"
- ✅ **Code Generation**: Ask "Create code to fetch user data from an API"
- ✅ **Build Flow**: Enable "Build Flow" mode and ask to create a workflow

---

## 📊 Application Management

### View Logs

```bash
# Backend logs (live)
journalctl -u activepieces-backend -f

# Frontend logs (live)
journalctl -u activepieces-frontend -f

# Nginx access logs
tail -f /var/log/nginx/access.log

# Nginx error logs
tail -f /var/log/nginx/error.log

# View last 50 lines of backend logs
journalctl -u activepieces-backend -n 50
```

### Restart Services

```bash
# Restart backend
systemctl restart activepieces-backend

# Restart frontend
systemctl restart activepieces-frontend

# Restart Nginx
systemctl restart nginx

# Restart all
systemctl restart activepieces-backend activepieces-frontend nginx
```

### Stop Services

```bash
systemctl stop activepieces-backend
systemctl stop activepieces-frontend
```

### Update Application

```bash
# Navigate to app directory
cd /opt/activepieces-assistant

# Pull latest changes
git pull origin main

# Update backend
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Update frontend
cd frontend
npm install
npm run build
cd ..

# Restart services
systemctl restart activepieces-backend
systemctl restart activepieces-frontend
```

### Backup Data

```bash
# Backup database
cp data/activepieces.db data/activepieces_backup_$(date +%Y%m%d).db

# Backup vector store
tar -czf data/faiss_backup_$(date +%Y%m%d).tar.gz data/ap_faiss_index/

# Backup chat sessions
tar -czf data/sessions_backup_$(date +%Y%m%d).tar.gz data/chat_sessions/

# Backup environment
cp .env .env.backup
```

---

## 🐛 Troubleshooting

### Backend Not Starting

**Check logs**:
```bash
journalctl -u activepieces-backend -n 50
```

**Common issues**:

1. **Import Error** - Missing dependencies
   ```bash
   cd /opt/activepieces-assistant
   source venv/bin/activate
   pip install -r requirements.txt
   systemctl restart activepieces-backend
   ```

2. **Port Already in Use**
   ```bash
   # Check what's using port 8000
   lsof -i :8000
   # Kill the process if needed
   kill -9 <PID>
   systemctl restart activepieces-backend
   ```

3. **Permission Issues**
   ```bash
   chown -R www-data:www-data /opt/activepieces-assistant
   chmod -R 755 /opt/activepieces-assistant
   systemctl restart activepieces-backend
   ```

4. **API Key Error**
   ```bash
   # Check .env file
   cat /opt/activepieces-assistant/.env | grep OPENAI_API_KEY
   # Should show: OPENAI_API_KEY=sk-xxxxx
   
   # Fix if needed
   nano /opt/activepieces-assistant/.env
   systemctl restart activepieces-backend
   ```

### Frontend Not Loading

**Check logs**:
```bash
journalctl -u activepieces-frontend -n 50
```

**Common issues**:

1. **Build Failed**
   ```bash
   cd /opt/activepieces-assistant/frontend
   npm install
   npm run build
   systemctl restart activepieces-frontend
   ```

2. **Wrong API URL**
   ```bash
   # Check frontend env
   cat /opt/activepieces-assistant/frontend/.env.production
   
   # Should match your domain/IP
   # Fix if needed and rebuild
   nano /opt/activepieces-assistant/frontend/.env.production
   npm run build
   systemctl restart activepieces-frontend
   ```

### Database Issues

**Check database**:
```bash
cd /opt/activepieces-assistant
source venv/bin/activate
python src/db_config.py
```

**If database is missing**:
```bash
# Database should be in the repository
ls -la data/activepieces.db

# If missing, check git
git status
git pull origin main
```

### Vector Store Issues

**Check vector store**:
```bash
ls -la data/ap_faiss_index/
# Should show: index.faiss and index.pkl
```

**Recreate if needed**:
```bash
cd /opt/activepieces-assistant
source venv/bin/activate
python scripts/migration/prepare_knowledge_base.py
systemctl restart activepieces-backend
```

### Nginx Issues

**Test configuration**:
```bash
nginx -t
```

**Check logs**:
```bash
tail -f /var/log/nginx/error.log
```

**Common issues**:

1. **Syntax Error**
   ```bash
   # Edit config
   nano /etc/nginx/sites-available/activepieces-assistant
   
   # Test and restart
   nginx -t
   systemctl restart nginx
   ```

2. **Port Conflicts**
   ```bash
   # Check if another process uses port 80
   lsof -i :80
   ```

### SSL Certificate Issues

**Check certificate**:
```bash
certbot certificates
```

**Renew manually**:
```bash
certbot renew
systemctl restart nginx
```

**Test renewal**:
```bash
certbot renew --dry-run
```

---

## 🚀 Performance Optimization

### Use Gunicorn for Better Performance

```bash
cd /opt/activepieces-assistant
source venv/bin/activate
pip install gunicorn

# Update backend service
nano /etc/systemd/system/activepieces-backend.service
```

Change `ExecStart` to:
```
ExecStart=/opt/activepieces-assistant/venv/bin/gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

Restart:
```bash
systemctl daemon-reload
systemctl restart activepieces-backend
```

### Enable Nginx Caching

Add to your Nginx config (in `server` block):

```nginx
# Gzip compression
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json;

# Browser caching for static files
location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

Test and restart:
```bash
nginx -t
systemctl restart nginx
```

### Monitor Resource Usage

```bash
# Check memory
free -h

# Check disk
df -h

# Check CPU and processes
htop

# Monitor specific service
htop -p $(pgrep -f uvicorn)
```

---

## 🔐 Security Best Practices

### 1. Secure SSH

```bash
# Change default SSH port (optional)
nano /etc/ssh/sshd_config
# Change: Port 22 to Port 2222
systemctl restart sshd

# Disable root login (after setting up sudo user)
# In sshd_config: PermitRootLogin no
```

### 2. Install Fail2Ban

```bash
apt install -y fail2ban

# Configure
cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
nano /etc/fail2ban/jail.local

# Start
systemctl enable fail2ban
systemctl start fail2ban
```

### 3. Enable Auto-Updates

```bash
apt install -y unattended-upgrades
dpkg-reconfigure -plow unattended-upgrades
```

### 4. Regular Backups

Create automated backup script:

```bash
cat > /opt/activepieces-assistant/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/activepieces-assistant/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
cp /opt/activepieces-assistant/data/activepieces.db $BACKUP_DIR/db_$DATE.db

# Backup vector store
tar -czf $BACKUP_DIR/faiss_$DATE.tar.gz /opt/activepieces-assistant/data/ap_faiss_index/

# Backup sessions
tar -czf $BACKUP_DIR/sessions_$DATE.tar.gz /opt/activepieces-assistant/data/chat_sessions/

# Keep only last 7 days
find $BACKUP_DIR -name "*.db" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

chmod +x /opt/activepieces-assistant/backup.sh
```

Add to crontab (daily at 2 AM):

```bash
crontab -e
# Add:
0 2 * * * /opt/activepieces-assistant/backup.sh >> /var/log/activepieces-backup.log 2>&1
```

### 5. Monitor Logs

Setup log rotation:

```bash
cat > /etc/logrotate.d/activepieces << 'EOF'
/var/log/activepieces/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
}
EOF
```

---

## 📈 Monitoring Setup (Optional)

### Basic Monitoring with htop

```bash
apt install -y htop
htop
```

### Setup Status Page

Create a simple status check script:

```bash
cat > /opt/activepieces-assistant/check_status.sh << 'EOF'
#!/bin/bash

echo "=== ActivePieces AI Assistant Status ==="
echo ""

# Check backend
if systemctl is-active --quiet activepieces-backend; then
    echo "✅ Backend: Running"
else
    echo "❌ Backend: Stopped"
fi

# Check frontend
if systemctl is-active --quiet activepieces-frontend; then
    echo "✅ Frontend: Running"
else
    echo "❌ Frontend: Stopped"
fi

# Check nginx
if systemctl is-active --quiet nginx; then
    echo "✅ Nginx: Running"
else
    echo "❌ Nginx: Stopped"
fi

# Check API health
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ API Health: OK"
else
    echo "❌ API Health: Failed (HTTP $HTTP_CODE)"
fi

# Resource usage
echo ""
echo "=== Resource Usage ==="
free -h | grep Mem
df -h / | grep -v Filesystem
echo ""
EOF

chmod +x /opt/activepieces-assistant/check_status.sh
```

Run it:
```bash
/opt/activepieces-assistant/check_status.sh
```

---

## 🎯 Quick Reference

### Service Commands

```bash
# Start
systemctl start activepieces-backend
systemctl start activepieces-frontend

# Stop
systemctl stop activepieces-backend
systemctl stop activepieces-frontend

# Restart
systemctl restart activepieces-backend
systemctl restart activepieces-frontend

# Status
systemctl status activepieces-backend
systemctl status activepieces-frontend

# Logs
journalctl -u activepieces-backend -f
journalctl -u activepieces-frontend -f
```

### File Locations

```
Application: /opt/activepieces-assistant/
Backend service: /etc/systemd/system/activepieces-backend.service
Frontend service: /etc/systemd/system/activepieces-frontend.service
Nginx config: /etc/nginx/sites-available/activepieces-assistant
Environment: /opt/activepieces-assistant/.env
Database: /opt/activepieces-assistant/data/activepieces.db
Vector store: /opt/activepieces-assistant/data/ap_faiss_index/
Logs: journalctl -u service-name
```

### Useful Commands

```bash
# Check ports
lsof -i :8000  # Backend
lsof -i :5173  # Frontend
lsof -i :80    # Nginx

# Test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/stats

# Monitor resources
htop
free -h
df -h

# Check logs
tail -f /var/log/nginx/error.log
journalctl -u activepieces-backend -n 100
```

---

## ✨ Success Checklist

- [ ] Droplet created and accessible via SSH
- [ ] System updated and dependencies installed
- [ ] Repository cloned
- [ ] Python virtual environment created
- [ ] Dependencies installed
- [ ] `.env` file configured with API keys
- [ ] Database verified
- [ ] Vector store created
- [ ] Frontend built
- [ ] Systemd services created and running
- [ ] Nginx configured and running
- [ ] Firewall configured
- [ ] SSL certificate installed (if using domain)
- [ ] Application accessible in browser
- [ ] Chat working
- [ ] Web search working
- [ ] Code generation working
- [ ] All features tested

---

## 🎉 You're Done!

Your AI Assistant is now fully deployed and running!

**Access your application**:
- 🌐 **URL**: `https://your-domain.com` (or `http://your-ip`)
- 🔧 **Backend API**: `https://your-domain.com/health`
- 📊 **Stats**: `https://your-domain.com/stats`

**Next Steps**:
1. Test all features thoroughly
2. Setup monitoring and alerts
3. Configure automated backups
4. Share with your team!

**Need Help?**
- Check the [Troubleshooting](#-troubleshooting) section
- Review logs: `journalctl -u activepieces-backend -f`
- Check GitHub Issues

---

## 📚 Additional Resources

- **GitHub**: Your repository URL
- **OpenAI Docs**: https://platform.openai.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Nginx Docs**: https://nginx.org/en/docs/
- **Let's Encrypt**: https://letsencrypt.org/

---

**Happy Deploying! 🚀**

*Last updated: 2024*

