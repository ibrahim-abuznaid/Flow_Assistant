# 🚀 Quick Deployment Guide - Ubuntu 25.04

Deploy your ActivePieces AI Assistant to Ubuntu 25.04 in under 15 minutes!

## ✨ What's Included

- ✅ **All data files in repo** (SQLite DB + FAISS vector store)
- ✅ **No rebuilding needed** - just clone and deploy
- ✅ **Automatic setup** - one script does everything
- ✅ **SSL support** - optional HTTPS with Let's Encrypt
- ✅ **Production ready** - systemd services, Nginx, firewall

## 📋 Prerequisites

1. **Ubuntu 25.04 x64** server (DigitalOcean, AWS, etc.)
2. **Root access** (sudo)
3. **Domain name** (optional but recommended for SSL)
4. **OpenAI API Key** ([Get one here](https://platform.openai.com/api-keys))

## 🎯 Deployment Steps

### Step 1: SSH into Your Server

```bash
ssh root@your-server-ip
```

### Step 2: Clone Repository to /opt

```bash
cd /opt
git clone https://github.com/ibrahim-abuznaid/Flow_Assistant.git
cd Flow_Assistant
```

### Step 3: Make Script Executable

```bash
chmod +x scripts/deployment/deploy_ubuntu.sh
```

### Step 4: Run Deployment Script

```bash
sudo ./scripts/deployment/deploy_ubuntu.sh
```

### Step 5: Follow the Prompts

The script will ask you for:
1. **OpenAI API Key** (required)
2. **Web Search Provider** (OpenAI or Perplexity)
3. **Domain or IP address** (for Nginx configuration)
4. **SSL setup** (optional)

That's it! 🎉

## 📊 What the Script Does

The deployment script automatically:

1. ✅ Updates system packages
2. ✅ Installs Python 3, Node.js 20, Nginx
3. ✅ Creates Python virtual environment
4. ✅ Installs all Python dependencies
5. ✅ Verifies database (SQLite) is working
6. ✅ Verifies FAISS vector store is working
7. ✅ Builds React frontend for production
8. ✅ Creates systemd services (auto-restart)
9. ✅ Configures Nginx reverse proxy
10. ✅ Sets up UFW firewall
11. ✅ Starts all services
12. ✅ (Optional) Configures SSL/HTTPS

## 🔧 After Deployment

### Access Your Application

- **HTTP:** `http://your-domain.com`
- **HTTPS:** `https://your-domain.com` (if SSL was configured)

### Manage Services

```bash
# View logs
journalctl -u activepieces-backend -f
journalctl -u activepieces-frontend -f

# Restart services
systemctl restart activepieces-backend
systemctl restart activepieces-frontend

# Check status
systemctl status activepieces-backend
systemctl status activepieces-frontend
```

### Test Endpoints

```bash
# Health check
curl http://your-domain.com/health

# Stats
curl http://your-domain.com/stats
```

## 🔄 Update Your Application

To update after making changes:

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

## 🐛 Troubleshooting

### Backend Won't Start

```bash
# Check logs
journalctl -u activepieces-backend -n 50

# Check if port 8000 is in use
netstat -tlnp | grep 8000

# Verify .env file
cat /opt/Flow_Assistant/.env
```

### Frontend Won't Start

```bash
# Check logs
journalctl -u activepieces-frontend -n 50

# Check if port 5173 is in use
netstat -tlnp | grep 5173

# Verify build
ls -la /opt/Flow_Assistant/frontend/dist/
```

### Database Issues

```bash
# Test database
cd /opt/Flow_Assistant
source venv/bin/activate
python3 -c "from src.db_config import test_connection; test_connection()"
```

### Vector Store Issues

```bash
# Verify files exist
ls -la /opt/Flow_Assistant/data/ap_faiss_index/

# Test loading
cd /opt/Flow_Assistant
source venv/bin/activate
python3 -c "from src.tools import get_vector_store; vs = get_vector_store(); print('OK')"
```

### Nginx Issues

```bash
# Test configuration
nginx -t

# Check status
systemctl status nginx

# View error logs
tail -f /var/log/nginx/error.log
```

## 🔐 Security Best Practices

1. **Change SSH Port** (optional but recommended)
   ```bash
   # Edit SSH config
   nano /etc/ssh/sshd_config
   # Change Port 22 to something else
   # Restart SSH
   systemctl restart sshd
   ```

2. **Setup Regular Backups**
   ```bash
   # Backup data directory
   tar -czf backup-$(date +%Y%m%d).tar.gz /opt/Flow_Assistant/data/
   ```

3. **Monitor Logs**
   ```bash
   # Setup logrotate
   nano /etc/logrotate.d/activepieces
   ```

4. **Keep System Updated**
   ```bash
   apt update && apt upgrade -y
   ```

## 📁 Important Files & Directories

| Path | Description |
|------|-------------|
| `/opt/Flow_Assistant/` | Application root |
| `/opt/Flow_Assistant/.env` | Environment variables (API keys) |
| `/opt/Flow_Assistant/data/` | Database & vector store |
| `/opt/Flow_Assistant/data/activepieces.db` | SQLite database |
| `/opt/Flow_Assistant/data/ap_faiss_index/` | FAISS vector store |
| `/etc/systemd/system/activepieces-backend.service` | Backend service |
| `/etc/systemd/system/activepieces-frontend.service` | Frontend service |
| `/etc/nginx/sites-available/activepieces-assistant` | Nginx config |

## 💡 Tips

1. **Use a domain name** instead of IP for SSL support
2. **Point domain to server** before running SSL setup
3. **Backup data/ directory** regularly
4. **Monitor disk space** - logs can grow large
5. **Set up monitoring** - use tools like Uptime Robot

## 🆘 Need Help?

- Check logs: `journalctl -u activepieces-backend -f`
- Test database: `python3 src/db_config.py`
- Verify files: All data files should be in `data/` directory
- Check permissions: `ls -la data/`

## 🎉 Success!

Your AI Assistant should now be running at your domain/IP!

Try asking it:
- "What integrations are available?"
- "How do I send an email?"
- "Show me Slack actions"

---

**Repository:** https://github.com/ibrahim-abuznaid/Flow_Assistant.git
**License:** MIT

