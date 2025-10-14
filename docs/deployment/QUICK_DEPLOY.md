# Quick Deploy - TL;DR

## 🚀 Deploy in 3 Commands

### Prerequisites
- Ubuntu 22.04/24.04 droplet
- OpenAI API key
- SSH access

### Deploy Now

```bash
# 1. SSH into your droplet
ssh root@your_droplet_ip

# 2. Run automated deployment
curl -fsSL https://raw.githubusercontent.com/yourusername/Flow_Assistant/main/scripts/deployment/deploy_digitalocean.sh | sudo bash

# 3. Access your app
# http://your_droplet_ip
```

---

## 📝 Manual Deployment (30 min)

If you prefer manual control, follow these steps:

### 1. System Setup (5 min)
```bash
ssh root@your_droplet_ip
apt update && apt upgrade -y
apt install -y python3 python3-pip python3-venv nodejs npm nginx git curl ufw
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs
```

### 2. Clone & Setup (5 min)
```bash
cd /opt
git clone https://github.com/yourusername/Flow_Assistant.git activepieces-assistant
cd activepieces-assistant
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure (2 min)
```bash
cat > .env << 'EOF'
OPENAI_API_KEY=sk-your-key-here
MODEL_PROVIDER=openai
MODEL_NAME=gpt-4o
SEARCH_PROVIDER=openai
SQLITE_DB_FILE=data/activepieces.db
PORT=8000
EOF
```

### 4. Database & Vector Store (3 min)
```bash
python src/db_config.py
python scripts/migration/prepare_knowledge_base.py
```

### 5. Build Frontend (5 min)
```bash
cd frontend
npm install
echo "VITE_API_URL=http://your_domain.com" > .env.production
npm run build
cd ..
```

### 6. Create Services (3 min)
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

# Frontend service
npm install -g serve
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
chown -R www-data:www-data /opt/activepieces-assistant
```

### 7. Configure Nginx (3 min)
```bash
cat > /etc/nginx/sites-available/activepieces-assistant << 'EOF'
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://localhost:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location ~ ^/(api/|health|stats|chat|sessions|reset) {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    client_max_body_size 10M;
}
EOF

rm -f /etc/nginx/sites-enabled/default
ln -sf /etc/nginx/sites-available/activepieces-assistant /etc/nginx/sites-enabled/
nginx -t && systemctl restart nginx
```

### 8. Firewall (1 min)
```bash
ufw --force enable
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
```

### 9. Start Everything (2 min)
```bash
systemctl daemon-reload
systemctl enable activepieces-backend activepieces-frontend
systemctl start activepieces-backend activepieces-frontend
```

### 10. Verify (1 min)
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy","message":"Service is operational"}
```

---

## 🔐 SSL Setup (Optional, 5 min)

```bash
apt install -y certbot python3-certbot-nginx
certbot --nginx -d your_domain.com -d www.your_domain.com
```

---

## ✅ Quick Checks

### Is everything running?
```bash
systemctl status activepieces-backend --no-pager
systemctl status activepieces-frontend --no-pager
systemctl status nginx --no-pager
curl http://localhost:8000/health
```

### View logs
```bash
# Live logs
journalctl -u activepieces-backend -f

# Last 50 lines
journalctl -u activepieces-backend -n 50
```

### Restart services
```bash
systemctl restart activepieces-backend
systemctl restart activepieces-frontend
```

---

## 🆘 Troubleshooting

### Backend won't start?
```bash
journalctl -u activepieces-backend -n 50
# Check for missing dependencies or API key issues
```

### Frontend not loading?
```bash
cd /opt/activepieces-assistant/frontend
npm run build
systemctl restart activepieces-frontend
```

### Database errors?
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

## 📚 Full Documentation

For detailed information, see:
- **[Complete Deployment Guide](DEPLOYMENT_GUIDE.md)** - Full step-by-step guide
- **[README](README.md)** - Project overview and features
- **[Troubleshooting](DEPLOYMENT_GUIDE.md#-troubleshooting)** - Common issues

---

## 🎯 What You Get

✅ **Backend**: FastAPI + LangChain AI agent  
✅ **Frontend**: React UI with real-time chat  
✅ **Database**: SQLite with 433+ integrations  
✅ **Vector Store**: FAISS for RAG  
✅ **Web Search**: OpenAI or Perplexity  
✅ **Production Ready**: Nginx + SSL + systemd  

---

**Need Help?** See the [Full Deployment Guide](DEPLOYMENT_GUIDE.md) or check the logs!

