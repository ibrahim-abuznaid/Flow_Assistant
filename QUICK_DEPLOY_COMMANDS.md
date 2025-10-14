# 🚀 Quick Deploy Commands - Copy & Paste

## Step-by-Step Deployment on Ubuntu 25.04

### 1️⃣ SSH into Your Droplet

```bash
ssh root@YOUR_DROPLET_IP
```

### 2️⃣ Clone Repository

```bash
cd /opt
git clone https://github.com/ibrahim-abuznaid/Flow_Assistant.git
cd Flow_Assistant
```

### 3️⃣ Make Script Executable

```bash
chmod +x scripts/deployment/deploy_ubuntu.sh
```

### 4️⃣ Run Deployment

```bash
sudo ./scripts/deployment/deploy_ubuntu.sh
```

### 5️⃣ When Prompted, Provide:

1. **OpenAI API Key** - Get from: https://platform.openai.com/api-keys
2. **Web Search** - Choose 1 (OpenAI) or 2 (Perplexity)
3. **Domain/IP** - Your droplet IP or domain name
4. **SSL** - Choose y or n (requires domain name)

---

## 📊 After Deployment

### Check Services

```bash
systemctl status activepieces-backend
systemctl status activepieces-frontend
systemctl status nginx
```

### View Logs

```bash
# Backend logs (live)
journalctl -u activepieces-backend -f

# Frontend logs (live)
journalctl -u activepieces-frontend -f

# Last 50 lines
journalctl -u activepieces-backend -n 50
```

### Restart Services

```bash
systemctl restart activepieces-backend
systemctl restart activepieces-frontend
```

### Test Endpoints

```bash
# Health check
curl http://YOUR_DOMAIN/health

# Stats
curl http://YOUR_DOMAIN/stats
```

---

## 🔄 Update Application (After Git Push)

```bash
cd /opt/Flow_Assistant
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
cd frontend
npm install
npm run build
cd ..
sudo systemctl restart activepieces-backend activepieces-frontend
```

---

## 🐛 Troubleshooting

### Backend Not Starting

```bash
# View detailed logs
journalctl -u activepieces-backend -n 100 --no-pager

# Check .env file
cat /opt/Flow_Assistant/.env

# Test database
cd /opt/Flow_Assistant
source venv/bin/activate
python3 src/db_config.py
```

### Frontend Not Starting

```bash
# View logs
journalctl -u activepieces-frontend -n 100 --no-pager

# Check build
ls -la /opt/Flow_Assistant/frontend/dist/

# Rebuild
cd /opt/Flow_Assistant/frontend
npm run build
sudo systemctl restart activepieces-frontend
```

### Nginx Issues

```bash
# Test config
nginx -t

# View error log
tail -f /var/log/nginx/error.log

# Restart nginx
systemctl restart nginx
```

### Check All Ports

```bash
# Check what's running on ports
netstat -tlnp | grep -E '(8000|5173|80|443)'

# Check firewall
ufw status
```

---

## 🔐 Important File Locations

| File/Directory | Path |
|----------------|------|
| Application | `/opt/Flow_Assistant/` |
| Environment | `/opt/Flow_Assistant/.env` |
| Database | `/opt/Flow_Assistant/data/activepieces.db` |
| Vector Store | `/opt/Flow_Assistant/data/ap_faiss_index/` |
| Backend Service | `/etc/systemd/system/activepieces-backend.service` |
| Frontend Service | `/etc/systemd/system/activepieces-frontend.service` |
| Nginx Config | `/etc/nginx/sites-available/activepieces-assistant` |

---

## 📝 Common Tasks

### View Environment Variables

```bash
cat /opt/Flow_Assistant/.env
```

### Edit Environment

```bash
nano /opt/Flow_Assistant/.env
# After editing, restart services:
sudo systemctl restart activepieces-backend
```

### Backup Data

```bash
tar -czf /root/backup-$(date +%Y%m%d).tar.gz /opt/Flow_Assistant/data/
```

### Check Disk Space

```bash
df -h
```

### Check Memory

```bash
free -h
```

### Monitor Resources

```bash
htop
```

---

## 🎯 SSL Setup (If Skipped During Install)

```bash
# Install certbot (already installed if you ran the script)
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d YOUR_DOMAIN -d www.YOUR_DOMAIN

# Update frontend to use HTTPS
cat > /opt/Flow_Assistant/frontend/.env.production << EOF
VITE_API_URL=https://YOUR_DOMAIN
EOF

# Rebuild frontend
cd /opt/Flow_Assistant/frontend
npm run build
sudo systemctl restart activepieces-frontend
```

---

## ✅ Health Checks

### All-in-One Health Check

```bash
echo "=== Services ===" && \
systemctl is-active activepieces-backend && \
systemctl is-active activepieces-frontend && \
systemctl is-active nginx && \
echo "=== Health ===" && \
curl -s http://localhost:8000/health && \
echo "" && \
echo "=== All Good! ==="
```

---

**Need More Help?**
- Full Guide: [DEPLOY_UBUNTU_25.md](DEPLOY_UBUNTU_25.md)
- GitHub: https://github.com/ibrahim-abuznaid/Flow_Assistant

