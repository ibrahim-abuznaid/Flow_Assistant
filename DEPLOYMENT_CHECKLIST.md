# ✅ Ubuntu 25.04 Deployment Checklist

Use this checklist to deploy your ActivePieces AI Assistant step-by-step.

---

## 📋 Pre-Deployment (Local - Windows)

- [ ] **Review changes made**
  - [ ] Fixed `scripts/migration/prepare_knowledge_base.py` paths
  - [ ] Created `scripts/deployment/deploy_ubuntu.sh` (new script)
  - [ ] Updated `.gitignore` to ignore `.venv/`
  - [ ] Verified all data files are in repo

- [ ] **Commit and push changes**
  ```bash
  git status
  git add .
  git commit -m "Add Ubuntu 25.04 deployment script and fix paths"
  git push origin main
  ```

- [ ] **Verify GitHub repo**
  - Visit: https://github.com/ibrahim-abuznaid/Flow_Assistant
  - Confirm latest commit is there
  - Check that `scripts/deployment/deploy_ubuntu.sh` exists

- [ ] **Get API Key**
  - OpenAI API Key: https://platform.openai.com/api-keys
  - Save it somewhere safe for later

---

## 🌐 Server Setup (DigitalOcean Droplet)

- [ ] **Create Ubuntu 25.04 Droplet**
  - OS: Ubuntu 25.04 x64
  - Plan: Basic ($6/month or higher)
  - Region: Choose closest to you
  - Authentication: SSH key or password

- [ ] **Note your droplet IP**
  - IP Address: `___.___.___.___`

- [ ] **(Optional) Configure Domain**
  - Point A record to droplet IP
  - Point www A record to droplet IP
  - Wait 5-10 minutes for DNS propagation

---

## 🚀 Deployment Steps (On Droplet)

### Step 1: Connect to Droplet

- [ ] **SSH into server**
  ```bash
  ssh root@YOUR_DROPLET_IP
  ```
  
- [ ] **Verify OS version**
  ```bash
  lsb_release -a
  # Should show: Ubuntu 25.04
  ```

### Step 2: Clone Repository

- [ ] **Navigate to /opt**
  ```bash
  cd /opt
  ```

- [ ] **Clone your repository**
  ```bash
  git clone https://github.com/ibrahim-abuznaid/Flow_Assistant.git
  ```

- [ ] **Enter directory**
  ```bash
  cd Flow_Assistant
  ```

- [ ] **Verify files exist**
  ```bash
  ls -la data/
  # Should see: activepieces.db, ap_faiss_index/, pieces_knowledge_base.json
  ```

### Step 3: Prepare Deployment Script

- [ ] **Make script executable**
  ```bash
  chmod +x scripts/deployment/deploy_ubuntu.sh
  ```

- [ ] **Verify script exists**
  ```bash
  ls -lh scripts/deployment/deploy_ubuntu.sh
  # Should show the file with execute permissions
  ```

### Step 4: Run Deployment

- [ ] **Execute deployment script**
  ```bash
  sudo ./scripts/deployment/deploy_ubuntu.sh
  ```

- [ ] **Confirm deployment** when prompted
  - Type: `y` and press Enter

### Step 5: Provide Configuration

- [ ] **Enter OpenAI API Key**
  - Paste your API key
  - Press Enter

- [ ] **Choose Web Search Provider**
  - Enter `1` for OpenAI (recommended)
  - Or `2` for Perplexity

- [ ] **Enter Domain/IP**
  - Your domain: `example.com`
  - Or your IP: `123.45.67.89`
  - Press Enter

### Step 6: Wait for Installation

- [ ] **Monitor progress**
  - Watch for green checkmarks ✓
  - Look for any red X errors
  - Script runs for ~10-15 minutes

### Step 7: SSL Setup (Optional)

- [ ] **SSL Certificate**
  - Type `y` if you have a domain name
  - Type `n` if using IP address
  - Press Enter

---

## ✅ Post-Deployment Verification

### Check Services

- [ ] **Backend service running**
  ```bash
  systemctl status activepieces-backend
  # Should show: active (running) in green
  ```

- [ ] **Frontend service running**
  ```bash
  systemctl status activepieces-frontend
  # Should show: active (running) in green
  ```

- [ ] **Nginx running**
  ```bash
  systemctl status nginx
  # Should show: active (running) in green
  ```

### Test Endpoints

- [ ] **Health check**
  ```bash
  curl http://localhost:8000/health
  # Should return: {"status":"healthy"}
  ```

- [ ] **Stats endpoint**
  ```bash
  curl http://localhost:8000/stats
  # Should return JSON with database stats
  ```

### Test in Browser

- [ ] **Open in browser**
  - Visit: `http://YOUR_DOMAIN` or `http://YOUR_IP`
  - Should see the chat interface

- [ ] **Test chat functionality**
  - Type: "What integrations are available?"
  - Should get a response
  - Try: "Show me Slack actions"

---

## 🎯 Final Checks

### Security

- [ ] **Firewall enabled**
  ```bash
  ufw status
  # Should show: active
  ```

- [ ] **Only necessary ports open**
  ```bash
  ufw status numbered
  # Should show: 22/tcp (SSH), 80/tcp (HTTP), 443/tcp (HTTPS)
  ```

### Resources

- [ ] **Check disk space**
  ```bash
  df -h
  # Should have plenty free
  ```

- [ ] **Check memory**
  ```bash
  free -h
  # Should have some free memory
  ```

### Logs

- [ ] **Check backend logs**
  ```bash
  journalctl -u activepieces-backend -n 20
  # Should show successful startup
  ```

- [ ] **Check frontend logs**
  ```bash
  journalctl -u activepieces-frontend -n 20
  # Should show: Serving! on port 5173
  ```

---

## 📝 Document Your Setup

Record these details for future reference:

- **Droplet IP:** `___.___.___.___`
- **Domain (if used):** `_________________`
- **Application URL:** `http://_______________`
- **SSL Enabled:** Yes / No
- **Deployment Date:** `_________________`
- **OpenAI API Key Location:** `_________________`

---

## 🔄 Maintenance Tasks

### Regular Tasks (Weekly)

- [ ] **Check logs for errors**
  ```bash
  journalctl -u activepieces-backend -n 100 | grep -i error
  ```

- [ ] **Monitor disk space**
  ```bash
  df -h
  ```

- [ ] **Check service status**
  ```bash
  systemctl status activepieces-backend activepieces-frontend
  ```

### Monthly Tasks

- [ ] **Update system packages**
  ```bash
  apt update && apt upgrade -y
  ```

- [ ] **Backup data directory**
  ```bash
  tar -czf ~/backup-$(date +%Y%m%d).tar.gz /opt/Flow_Assistant/data/
  ```

- [ ] **Review SSL certificate expiry**
  ```bash
  certbot certificates
  ```

---

## 🆘 Troubleshooting Quick Reference

### Backend Won't Start

```bash
# View logs
journalctl -u activepieces-backend -n 50

# Check .env file
cat /opt/Flow_Assistant/.env

# Restart service
systemctl restart activepieces-backend
```

### Frontend Won't Start

```bash
# View logs
journalctl -u activepieces-frontend -n 50

# Rebuild
cd /opt/Flow_Assistant/frontend
npm run build
systemctl restart activepieces-frontend
```

### Can't Access Website

```bash
# Check Nginx
nginx -t
systemctl restart nginx

# Check firewall
ufw status

# Check all services
systemctl status activepieces-backend activepieces-frontend nginx
```

---

## 📚 Documentation Reference

- **Quick Commands:** [QUICK_DEPLOY_COMMANDS.md](QUICK_DEPLOY_COMMANDS.md)
- **Full Guide:** [DEPLOY_UBUNTU_25.md](DEPLOY_UBUNTU_25.md)
- **Fixes Summary:** [DEPLOYMENT_FIXES_SUMMARY.md](DEPLOYMENT_FIXES_SUMMARY.md)

---

## ✨ Success!

When all items are checked:

🎉 **Your AI Assistant is live!**

Test it by asking:
- "Does ActivePieces have a Slack integration?"
- "How do I send an email?"
- "What actions are available for Google Sheets?"

---

*Deployment Script Version: 1.0*
*Target OS: Ubuntu 25.04 x64*
*Last Updated: October 14, 2025*

