# 🚀 Deploy Your Flow_Assistant from GitHub

## Copy-Paste Deployment Commands

Run these commands on your DigitalOcean droplet to deploy your Flow_Assistant.

---

## 🎯 Your Setup

- **GitHub Repo**: `Flow_Assistant`
- **GitHub Username**: Replace `YOUR_GITHUB_USERNAME` below
- **OpenAI API Key**: Have it ready

---

## 📋 Deployment Steps

### 1. SSH into Your Droplet

```bash
ssh root@YOUR_DROPLET_IP
```

### 2. Install Everything (One Command)

```bash
apt update && apt upgrade -y && \
apt install -y python3 python3-pip python3-venv nodejs npm nginx git curl ufw && \
curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
apt-get install -y nodejs
```

### 3. Clone Your Repository

```bash
mkdir -p /opt/activepieces-assistant && \
cd /opt/activepieces-assistant && \
git clone https://github.com/YOUR_GITHUB_USERNAME/Flow_Assistant.git .
```

**⚠️ Replace `YOUR_GITHUB_USERNAME` with your actual GitHub username!**

**If your repo is private**, use one of these instead:

```bash
# Option A: Personal Access Token
git clone https://YOUR_TOKEN@github.com/YOUR_GITHUB_USERNAME/Flow_Assistant.git .

# Option B: SSH (if you have SSH keys)
git clone git@github.com:YOUR_GITHUB_USERNAME/Flow_Assistant.git .
```

### 4. Setup Python

```bash
python3 -m venv venv && \
source venv/bin/activate && \
pip install --upgrade pip && \
pip install -r requirements.txt
```

### 5. Create .env File

```bash
nano .env
```

**Paste this** (replace `sk-YOUR-KEY` with your actual OpenAI API key):

```ini
OPENAI_API_KEY=sk-YOUR-ACTUAL-KEY-HERE
MODEL_PROVIDER=openai
MODEL_NAME=gpt-4o
SEARCH_PROVIDER=openai
SQLITE_DB_FILE=data/activepieces.db
PORT=8000
```

**Save**: Press `Ctrl+X`, then `Y`, then `Enter`

### 6. Verify Database

```bash
python src/db_config.py
```

**Should show**: `[OK] Database connected successfully! Found 433 pieces.`

### 7. Create Vector Store

```bash
source venv/bin/activate && \
python scripts/migration/prepare_knowledge_base.py
```

**Takes 2-3 minutes**. Should show: `✓ Knowledge base preparation complete!`

### 8. Build Frontend

```bash
cd frontend && \
npm install && \
echo "VITE_API_URL=http://YOUR_DROPLET_IP" > .env.production && \
npm run build && \
cd ..
```

**⚠️ Replace `YOUR_DROPLET_IP` with your actual droplet IP address!**

### 9. Create Services

```bash
# Backend service
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

# Install serve for frontend
npm install -g serve

# Frontend service
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

# Set permissions
chown -R www-data:www-data /opt/activepieces-assistant && \
chmod -R 755 /opt/activepieces-assistant
```

### 10. Configure Nginx

```bash
cat > /etc/nginx/sites-available/activepieces-assistant << 'EOF'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://localhost:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api/ {
        rewrite ^/api/(.*) /$1 break;
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
    }

    location ~ ^/(health|stats|chat|sessions|reset) {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        add_header 'Access-Control-Allow-Origin' '*' always;
    }

    client_max_body_size 10M;
}
EOF

# Enable site
rm -f /etc/nginx/sites-enabled/default && \
ln -sf /etc/nginx/sites-available/activepieces-assistant /etc/nginx/sites-enabled/ && \
nginx -t && \
systemctl restart nginx && \
systemctl enable nginx
```

### 11. Configure Firewall

```bash
ufw --force enable && \
ufw allow OpenSSH && \
ufw allow 80/tcp && \
ufw allow 443/tcp
```

### 12. Start Everything

```bash
systemctl daemon-reload && \
systemctl enable activepieces-backend activepieces-frontend && \
systemctl start activepieces-backend activepieces-frontend
```

### 13. Check Status

```bash
systemctl status activepieces-backend --no-pager && \
systemctl status activepieces-frontend --no-pager
```

**Both should show "active (running)" in green!**

### 14. Test It

```bash
curl http://localhost:8000/health
```

**Expected**: `{"status":"healthy","message":"Service is operational"}`

---

## 🎉 SUCCESS!

Your AI Assistant is now running!

**Access it**: Open your browser and go to:

```
http://YOUR_DROPLET_IP
```

**Test it**: Send a message like:
- "Does ActivePieces have a Slack integration?"
- "Create code to fetch user data from an API"
- "What's the latest news about automation?"

---

## 🔧 Useful Commands

### View Logs
```bash
# Backend logs (live)
journalctl -u activepieces-backend -f

# Frontend logs (live)
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

### Services not running?
```bash
# Check logs
journalctl -u activepieces-backend -n 50

# Usually fix with:
cd /opt/activepieces-assistant
source venv/bin/activate
pip install -r requirements.txt
systemctl restart activepieces-backend
```

### Can't access website?
```bash
# Check Nginx
systemctl status nginx
nginx -t

# Restart if needed
systemctl restart nginx
```

### Need to recreate vector store?
```bash
cd /opt/activepieces-assistant
source venv/bin/activate
python scripts/migration/prepare_knowledge_base.py
systemctl restart activepieces-backend
```

---

## 🔐 Optional: Add SSL (if you have a domain)

```bash
# Install certbot
apt install -y certbot python3-certbot-nginx

# Get certificate (replace your-domain.com)
certbot --nginx -d your-domain.com

# Update frontend to use HTTPS
cd /opt/activepieces-assistant/frontend
echo "VITE_API_URL=https://your-domain.com" > .env.production
npm run build
systemctl restart activepieces-frontend
```

---

## 📚 More Help

- **[GitHub Clone Deploy Guide](docs/deployment/GITHUB_CLONE_DEPLOY.md)** - Detailed version
- **[Complete Deployment Guide](docs/deployment/DEPLOYMENT_GUIDE.md)** - All features explained
- **[Deployment Index](docs/deployment/DEPLOYMENT_INDEX.md)** - All deployment docs

---

## ✅ What You Have Now

- ✅ Backend: FastAPI + LangChain + OpenAI
- ✅ Frontend: React UI with real-time chat
- ✅ Database: 433+ ActivePieces integrations
- ✅ Vector Store: FAISS for RAG/semantic search
- ✅ Web Search: OpenAI integration
- ✅ Services: Auto-restart on failure
- ✅ Firewall: Properly configured
- ✅ Production: Ready to use!

**Enjoy your AI Assistant! 🤖**

---

**Need help?** Check the logs: `journalctl -u activepieces-backend -f`


