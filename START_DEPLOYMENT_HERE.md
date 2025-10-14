# 🚀 START HERE - Deploy to Ubuntu 25.04

## ✅ All Fixed & Ready!

Your repository is now fully configured for deployment to Ubuntu 25.04. All database path issues have been resolved.

---

## 📦 Changes Made

### 1. Fixed Database Paths ✓
**File:** `scripts/migration/prepare_knowledge_base.py`
- ✅ Changed: `pieces_knowledge_base.json` → `data/pieces_knowledge_base.json`
- ✅ Changed: `ap_faiss_index` → `data/ap_faiss_index`

### 2. Created New Deployment Script ✓
**File:** `scripts/deployment/deploy_ubuntu.sh`
- ✅ Optimized for Ubuntu 25.04 x64
- ✅ Uses existing database (no rebuild)
- ✅ Uses existing FAISS index (no rebuild)
- ✅ Comprehensive error checking
- ✅ Validates all files before deployment

### 3. Updated .gitignore ✓
- ✅ Added `.venv/` to ignore list
- ✅ Ensured data files are NOT ignored
- ✅ Database, FAISS index, and knowledge base will be in repo

### 4. Created Documentation ✓
- ✅ `DEPLOY_UBUNTU_25.md` - Full deployment guide
- ✅ `QUICK_DEPLOY_COMMANDS.md` - Copy-paste commands
- ✅ `DEPLOYMENT_CHECKLIST.md` - Step-by-step checklist
- ✅ `DEPLOYMENT_FIXES_SUMMARY.md` - What was fixed
- ✅ `START_DEPLOYMENT_HERE.md` - This file!

---

## 🎯 Next Steps

### Step 1: Commit Changes to GitHub

Open your terminal (PowerShell/Command Prompt) and run:

```bash
cd "C:\AP work\Flow_Assistant"

# Check what changed
git status

# Add all changes
git add .

# Commit
git commit -m "Fix database paths and add Ubuntu 25.04 deployment script"

# Push to GitHub
git push origin main
```

### Step 2: Verify on GitHub

Visit your repository and confirm the files are there:
- https://github.com/ibrahim-abuznaid/Flow_Assistant

Check that you see:
- ✅ `scripts/deployment/deploy_ubuntu.sh`
- ✅ `DEPLOY_UBUNTU_25.md`
- ✅ `QUICK_DEPLOY_COMMANDS.md`
- ✅ Latest commit shows your changes

### Step 3: Prepare Your Droplet

You'll need:
- [ ] Ubuntu 25.04 x64 droplet (DigitalOcean, AWS, etc.)
- [ ] Root/sudo access
- [ ] Droplet IP address
- [ ] OpenAI API Key: https://platform.openai.com/api-keys
- [ ] (Optional) Domain name pointing to droplet

### Step 4: Deploy! 🚀

**SSH into your droplet:**
```bash
ssh root@YOUR_DROPLET_IP
```

**Run these commands:**
```bash
cd /opt
git clone https://github.com/ibrahim-abuznaid/Flow_Assistant.git
cd Flow_Assistant
chmod +x scripts/deployment/deploy_ubuntu.sh
sudo ./scripts/deployment/deploy_ubuntu.sh
```

**When prompted, enter:**
1. OpenAI API Key
2. Web Search provider (choose 1 for OpenAI)
3. Your domain or IP address
4. SSL setup (y/n)

**Wait ~10-15 minutes** for automatic installation!

---

## 📖 Helpful Commands Reference

### On Your Droplet (After Deployment)

**Check if everything is running:**
```bash
systemctl status activepieces-backend
systemctl status activepieces-frontend
systemctl status nginx
```

**View live logs:**
```bash
journalctl -u activepieces-backend -f
```

**Restart services:**
```bash
systemctl restart activepieces-backend
systemctl restart activepieces-frontend
```

**Test health:**
```bash
curl http://localhost:8000/health
```

---

## 📚 Full Documentation

Choose your guide:

1. **🚀 QUICK_DEPLOY_COMMANDS.md** ⭐
   - Copy-paste commands
   - Quick troubleshooting
   - Best for experienced users

2. **📖 DEPLOY_UBUNTU_25.md**
   - Complete step-by-step guide
   - Detailed explanations
   - Troubleshooting section
   - Best for beginners

3. **✅ DEPLOYMENT_CHECKLIST.md**
   - Interactive checklist
   - Track your progress
   - Nothing gets missed

4. **🔧 DEPLOYMENT_FIXES_SUMMARY.md**
   - Technical details
   - What was changed
   - Why it was changed

---

## 🎯 Quick Access URLs

After deployment, access your app at:

- **HTTP:** `http://YOUR_DOMAIN` or `http://YOUR_IP`
- **HTTPS:** `https://YOUR_DOMAIN` (if SSL configured)
- **Health:** `http://YOUR_DOMAIN/health`
- **Stats:** `http://YOUR_DOMAIN/stats`

---

## 🐛 If Something Goes Wrong

### Backend won't start?
```bash
journalctl -u activepieces-backend -n 50
```

### Frontend won't start?
```bash
journalctl -u activepieces-frontend -n 50
```

### Can't access website?
```bash
nginx -t
systemctl status nginx
ufw status
```

### Need to check files?
```bash
ls -la /opt/Flow_Assistant/data/
cat /opt/Flow_Assistant/.env
```

---

## ✨ What Makes This Deployment Different

| Feature | Status |
|---------|--------|
| Database included in repo | ✅ Yes (no setup needed) |
| FAISS index included | ✅ Yes (no rebuild needed) |
| Single script deployment | ✅ Yes (one command) |
| Error checking | ✅ Comprehensive |
| File validation | ✅ Pre-deployment checks |
| Auto-restart on crash | ✅ systemd services |
| SSL/HTTPS support | ✅ Optional Let's Encrypt |
| Firewall configured | ✅ UFW automatic setup |
| Nginx proxy | ✅ Automatic configuration |

---

## 📞 Support

- **GitHub Issues:** https://github.com/ibrahim-abuznaid/Flow_Assistant/issues
- **Documentation:** See files listed above
- **Logs:** `journalctl -u activepieces-backend -f`

---

## 🎉 You're Ready!

Everything is fixed and ready to deploy. Just:

1. ✅ Commit and push changes to GitHub
2. ✅ SSH into your Ubuntu 25.04 droplet
3. ✅ Run the 4 commands from Step 4
4. ✅ Access your app at your domain/IP

**Estimated deployment time:** 10-15 minutes
**Difficulty level:** Easy - Just follow the prompts!

---

**Last Updated:** October 14, 2025  
**Repository:** https://github.com/ibrahim-abuznaid/Flow_Assistant.git  
**Script:** `scripts/deployment/deploy_ubuntu.sh`  
**Target OS:** Ubuntu 25.04 x64

