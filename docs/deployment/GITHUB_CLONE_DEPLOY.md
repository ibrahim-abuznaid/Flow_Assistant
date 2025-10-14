# Deploy Flow_Assistant from GitHub

## 🚀 Quick Steps to Clone and Deploy

Follow these steps to clone your Flow_Assistant repository from GitHub and deploy it on your DigitalOcean droplet.

---

## 📋 Prerequisites

- DigitalOcean droplet (Ubuntu 22.04/24.04)
- Your GitHub repository: `Flow_Assistant`
- OpenAI API key
- SSH access to your droplet

---

## ⚡ Quick Deployment (30 minutes)

### Step 1: SSH into Your Droplet

```bash
ssh root@your_droplet_ip
```

### Step 2: Update System

```bash
apt update && apt upgrade -y
```

### Step 3: Install Dependencies

```bash
# Install all required packages
apt install -y python3 python3-pip python3-venv nodejs npm nginx git curl ufw

# Install Node.js 20
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs
```

### Step 4: Clone Repository from GitHub

```bash
# Create app directory
mkdir -p /opt/activepieces-assistant
cd /opt/activepieces-assistant

# Clone your repository (replace YOUR_GITHUB_USERNAME)
git clone https://github.com/YOUR_GITHUB_USERNAME/Flow_Assistant.git .
```

**Note**: The `.` at the end clones into the current directory.

#### If Repository is Private:

**Option A: Use Personal Access Token**
```bash
git clone https://YOUR_TOKEN@github.com/YOUR_GITHUB_USERNAME/Flow_Assistant.git .
```

**Option B: Use SSH** (if you have SSH keys set up)
```bash
git clone git@github.com:YOUR_GITHUB_USERNAME/Flow_Assistant.git .
```

### Step 5: Setup Python Backend

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 6: Configure Environment

```bash
# Create .env file
nano .env
```

Add this configuration (replace with your actual keys):

```ini
# AI Configuration
OPENAI_API_KEY=sk-your-actual-openai-key-here
MODEL_PROVIDER=openai
MODEL_NAME=gpt-4o

# Web Search
SEARCH_PROVIDER=openai

# Database (SQLite - already included!)
SQLITE_DB_FILE=data/activepieces.db

# Application
PORT=8000
```

Save: `Ctrl+X`, `Y`, `Enter`

### Step 7: Verify Database

```bash
python src/db_config.py
```

Expected: `[OK] Database connected successfully! Found 433 pieces.`

### Step 8: Create Vector Store

```bash
source venv/bin/activate
python scripts/migration/prepare_knowledge_base.py
```

This takes 2-3 minutes. Expected: `✓ Knowledge base preparation complete!`

### Step 9: Build Frontend

```bash
cd frontend
npm install

# Create production config (replace with your domain or IP)
echo "VITE_API_URL=http://your_droplet_ip" > .env.production

# Build
npm run build
cd ..
```

### Step 10: Create Backend Service

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

### Step 11: Create Frontend Service

```bash
# Install serve
npm install -g serve

# Create service
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

### Step 12: Set Permissions

```bash
chown -R www-data:www-data /opt/activepieces-assistant
chmod -R 755 /opt/activepieces-assistant
```

### Step 13: Configure Nginx

```bash
cat > /etc/nginx/sites-available/activepieces-assistant << 'EOF'
server {
    listen 80;
    server_name your_droplet_ip;  # Replace with your IP or domain

    # Frontend
    location / {
        proxy_pass http://localhost:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api/ {
        rewrite ^/api/(.*) /$1 break;
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }

    # Direct backend endpoints
    location ~ ^/(health|stats|chat|sessions|reset) {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        add_header 'Access-Control-Allow-Origin' '*' always;
    }

    client_max_body_size 10M;
}
EOF

# Enable site
rm -f /etc/nginx/sites-enabled/default
ln -sf /etc/nginx/sites-available/activepieces-assistant /etc/nginx/sites-enabled/

# Test and restart
nginx -t
systemctl restart nginx
systemctl enable nginx
```

### Step 14: Configure Firewall

```bash
ufw --force enable
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
```

### Step 15: Start Services

```bash
# Reload systemd
systemctl daemon-reload

# Enable and start
systemctl enable activepieces-backend activepieces-frontend
systemctl start activepieces-backend activepieces-frontend

# Check status
systemctl status activepieces-backend --no-pager
systemctl status activepieces-frontend --no-pager
```

### Step 16: Verify Everything Works

```bash
# Test backend
curl http://localhost:8000/health
# Expected: {"status":"healthy","message":"Service is operational"}

# Test in browser
# Go to: http://your_droplet_ip
```

---

## ✅ Success!

Your AI Assistant is now running!

**Access**: `http://your_droplet_ip`

### Test It:
1. Send message: "Does ActivePieces have a Slack integration?"
2. Should get detailed response about Slack

---

## 🔧 Quick Commands

### View Logs
```bash
journalctl -u activepieces-backend -f
journalctl -u activepieces-frontend -f
```

### Restart Services
```bash
systemctl restart activepieces-backend
systemctl restart activepieces-frontend
```

### Update from GitHub
```bash
cd /opt/activepieces-assistant
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
cd frontend && npm install && npm run build && cd ..
systemctl restart activepieces-backend activepieces-frontend
```

---

## 🆘 Troubleshooting

### Backend won't start?
```bash
journalctl -u activepieces-backend -n 50
# Check for errors

# Usually fix with:
cd /opt/activepieces-assistant
source venv/bin/activate
pip install -r requirements.txt
systemctl restart activepieces-backend
```

### Frontend not loading?
```bash
cd /opt/activepieces-assistant/frontend
npm run build
systemctl restart activepieces-frontend
```

### Database issues?
```bash
cd /opt/activepieces-assistant
source venv/bin/activate
python src/db_config.py
```

### Vector store missing?
```bash
cd /opt/activepieces-assistant
source venv/bin/activate
python scripts/migration/prepare_knowledge_base.py
systemctl restart activepieces-backend
```

---

## 🔐 Optional: Add SSL

If you have a domain name:

```bash
# Install certbot
apt install -y certbot python3-certbot-nginx

# Get certificate (replace your-domain.com)
certbot --nginx -d your-domain.com

# Follow prompts - it will configure everything automatically!
```

---

## 📚 Full Documentation

For more detailed information:
- **[Complete Deployment Guide](DEPLOYMENT_GUIDE.md)** - Full walkthrough
- **[Quick Deploy](QUICK_DEPLOY.md)** - Quick reference

---

## 🎉 You're Done!

Your Flow_Assistant is deployed and running from GitHub!

**What you have now**:
- ✅ Backend (FastAPI + LangChain)
- ✅ Frontend (React UI)
- ✅ Database (433+ integrations)
- ✅ Vector Store (RAG/semantic search)
- ✅ Web Search (OpenAI or Perplexity)
- ✅ Auto-restart services
- ✅ Firewall configured

**Next steps**:
1. Test all features
2. Setup SSL (if you have a domain)
3. Configure regular backups
4. Share with your team!

---

**Happy Coding! 🚀**


