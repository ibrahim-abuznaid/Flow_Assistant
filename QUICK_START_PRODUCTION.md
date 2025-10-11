# Quick Start - Production Deployment 🚀

Get your AI Assistant running in production in under 15 minutes!

## Prerequisites

- ✅ Ubuntu 22.04/24.04 droplet on DigitalOcean
- ✅ Your OpenAI API key
- ✅ SSH access to server
- ✅ (Optional) Domain name pointing to your server

## One-Command Deployment

### Step 1: SSH into Your Server
```bash
ssh root@your_server_ip
```

### Step 2: Clone and Deploy
```bash
cd /opt && \
git clone https://github.com/yourusername/Flow_Assistant.git && \
cd Flow_Assistant && \
chmod +x deploy_ubuntu.sh && \
sudo ./deploy_ubuntu.sh
```

The script will:
1. ✅ Update system packages
2. ✅ Install dependencies (Python, Node.js, PostgreSQL, Nginx)
3. ✅ Create database and user
4. ✅ Setup application
5. ✅ Configure services
6. ✅ Setup Nginx
7. ✅ Configure firewall

### Step 3: Configure Environment
```bash
nano /opt/activepieces-assistant/.env
```

Add your API keys:
```ini
OPENAI_API_KEY=sk-your-actual-key-here
PERPLEXITY_API_KEY=pplx-your-key-here  # Optional
MODEL_PROVIDER=openai
MODEL_NAME=gpt-4-turbo-preview
```

Save and exit (Ctrl+X, Y, Enter)

### Step 4: Restart Services
```bash
sudo systemctl restart activepieces-backend
```

### Step 5: Access Your Application
```
http://your_server_ip
```

## 🎉 That's It!

Your AI Assistant is now running in production!

---

## Optional: Enable HTTPS

### Install Certbot
```bash
sudo apt install certbot python3-certbot-nginx -y
```

### Get SSL Certificate
```bash
sudo certbot --nginx -d your_domain.com
```

Follow the prompts and certbot will:
- ✅ Obtain SSL certificate
- ✅ Configure Nginx for HTTPS
- ✅ Setup auto-renewal

---

## Manual Deployment (Step-by-Step)

If you prefer manual setup, follow these steps:

### 1. Update System
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Install Dependencies
```bash
sudo apt install -y python3 python3-pip python3-venv nodejs npm postgresql nginx git curl
```

### 3. Install Node.js 20
```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### 4. Setup PostgreSQL
```bash
sudo -u postgres psql <<EOF
CREATE DATABASE activepieces_pieces;
CREATE USER activepieces_user WITH ENCRYPTED PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE activepieces_pieces TO activepieces_user;
\q
EOF
```

### 5. Clone Repository
```bash
cd /opt
git clone https://github.com/yourusername/Flow_Assistant.git
cd Flow_Assistant
```

### 6. Setup Python Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 7. Configure Environment
```bash
cp .env.example .env
nano .env
# Add your API keys and database credentials
```

### 8. Build Frontend
```bash
cd frontend
npm install
npm run build
cd ..
```

### 9. Create Backend Service
```bash
sudo cp systemd/activepieces-backend.service /etc/systemd/system/
sudo systemctl enable activepieces-backend
sudo systemctl start activepieces-backend
```

### 10. Create Frontend Service
```bash
sudo npm install -g serve
sudo cp systemd/activepieces-frontend.service /etc/systemd/system/
sudo systemctl enable activepieces-frontend
sudo systemctl start activepieces-frontend
```

### 11. Configure Nginx
```bash
sudo cp nginx.conf.template /etc/nginx/sites-available/activepieces-assistant
# Edit the file to replace 'your_domain.com' with your actual domain/IP
sudo ln -s /etc/nginx/sites-available/activepieces-assistant /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 12. Configure Firewall
```bash
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

---

## Verification

### Check Services
```bash
sudo systemctl status activepieces-backend
sudo systemctl status activepieces-frontend
sudo systemctl status nginx
```

### Test API
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy","message":"Service is operational"}
```

### View Logs
```bash
sudo journalctl -u activepieces-backend -f
```

---

## Common Issues & Solutions

### Backend Not Starting
```bash
# Check logs
sudo journalctl -u activepieces-backend -n 50

# Common fix: Check .env file
nano /opt/activepieces-assistant/.env

# Restart
sudo systemctl restart activepieces-backend
```

### Database Connection Error
```bash
# Test PostgreSQL
sudo -u postgres psql -c "SELECT version();"

# Check database exists
sudo -u postgres psql -c "\l"

# Update .env with correct credentials
nano /opt/activepieces-assistant/.env
```

### Frontend Not Loading
```bash
# Check frontend service
sudo systemctl status activepieces-frontend

# Rebuild frontend
cd /opt/activepieces-assistant/frontend
npm run build
sudo systemctl restart activepieces-frontend
```

### Nginx Error
```bash
# Test configuration
sudo nginx -t

# Check logs
sudo tail -f /var/log/nginx/error.log

# Restart Nginx
sudo systemctl restart nginx
```

---

## Updating the Application

```bash
# Pull latest changes
cd /opt/activepieces-assistant
git pull origin main

# Update backend
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart activepieces-backend

# Update frontend
cd frontend
npm install
npm run build
sudo systemctl restart activepieces-frontend
```

---

## Useful Commands

### Service Management
```bash
# Start
sudo systemctl start activepieces-backend

# Stop
sudo systemctl stop activepieces-backend

# Restart
sudo systemctl restart activepieces-backend

# Check status
sudo systemctl status activepieces-backend
```

### View Logs
```bash
# Backend logs (live)
sudo journalctl -u activepieces-backend -f

# Frontend logs (live)
sudo journalctl -u activepieces-frontend -f

# Nginx access logs
sudo tail -f /var/log/nginx/access.log

# Nginx error logs
sudo tail -f /var/log/nginx/error.log
```

### Database Operations
```bash
# Backup database
pg_dump -h localhost -U activepieces_user activepieces_pieces > backup.sql

# Restore database
psql -h localhost -U activepieces_user activepieces_pieces < backup.sql

# Connect to database
psql -h localhost -U activepieces_user -d activepieces_pieces
```

---

## Performance Optimization

### Use Gunicorn (Better Performance)
```bash
source venv/bin/activate
pip install gunicorn

# Update backend service
sudo nano /etc/systemd/system/activepieces-backend.service

# Change ExecStart to:
# ExecStart=/opt/activepieces-assistant/venv/bin/gunicorn main:app \
#     -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

sudo systemctl daemon-reload
sudo systemctl restart activepieces-backend
```

### Optimize PostgreSQL
```bash
sudo nano /etc/postgresql/*/main/postgresql.conf

# For 4GB RAM server:
# shared_buffers = 1GB
# effective_cache_size = 3GB
# maintenance_work_mem = 256MB

sudo systemctl restart postgresql
```

---

## Security Hardening

### 1. Change Default SSH Port
```bash
sudo nano /etc/ssh/sshd_config
# Change: Port 22 to Port 2222
sudo systemctl restart sshd
```

### 2. Install Fail2Ban
```bash
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 3. Setup Auto-Updates
```bash
sudo apt install unattended-upgrades -y
sudo dpkg-reconfigure -plow unattended-upgrades
```

---

## Monitoring

### Setup Basic Monitoring
```bash
# Install htop for better process monitoring
sudo apt install htop -y

# Monitor resources
htop

# Monitor disk usage
df -h

# Monitor memory
free -h
```

---

## Next Steps

1. ✅ [Setup SSL with Let's Encrypt](#optional-enable-https)
2. ✅ Configure domain name
3. ✅ Setup regular backups
4. ✅ Configure monitoring/alerting
5. ✅ Review security settings
6. ✅ Setup CI/CD (optional)

---

## Documentation

For more detailed information:
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Complete deployment guide
- **[GITHUB_SETUP.md](GITHUB_SETUP.md)** - GitHub configuration
- **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** - Deployment checklist
- **[README.md](README.md)** - Main documentation

---

## Support

If you need help:
1. Check the [Troubleshooting](#common-issues--solutions) section
2. Review logs: `sudo journalctl -u activepieces-backend -f`
3. See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed guides
4. Open an issue on GitHub

---

**Happy Deploying! 🚀**

