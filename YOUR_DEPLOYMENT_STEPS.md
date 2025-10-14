# 🚀 Your Deployment Steps - Flow_Assistant

## Welcome! Here's How to Deploy Your Flow_Assistant from GitHub

You've pushed your repository to GitHub. Now let's deploy it to your DigitalOcean droplet!

---

## 📋 What You Need

1. **DigitalOcean Droplet**
   - Ubuntu 22.04 or 24.04 LTS
   - 2GB RAM minimum (4GB recommended)

2. **Your GitHub Repo**: `Flow_Assistant`

3. **OpenAI API Key** - Have it ready

4. **SSH Access** to your droplet

---

## 🎯 Choose Your Deployment Method

### ⭐ RECOMMENDED: Copy-Paste Deployment

**Best for**: Quick deployment with full control

➜ **Follow**: [DEPLOY_FROM_GITHUB.md](DEPLOY_FROM_GITHUB.md)

**What it is**:
- All commands are ready to copy-paste
- Just replace 2 things:
  1. `YOUR_GITHUB_USERNAME` → your GitHub username
  2. `YOUR_DROPLET_IP` → your droplet IP address
- Takes 30 minutes
- You understand each step

**Start here**: Open [DEPLOY_FROM_GITHUB.md](DEPLOY_FROM_GITHUB.md) and follow along! 👈

---

### Alternative: Detailed Guide

**For**: Understanding every detail

➜ **Follow**: [docs/deployment/DEPLOYMENT_GUIDE.md](docs/deployment/DEPLOYMENT_GUIDE.md)

**What it is**:
- Complete explanations
- Troubleshooting for every step
- Security best practices
- Performance optimization

---

## 🚀 Quick Overview (30 minutes total)

Here's what you'll do:

1. **SSH into droplet** (1 min)
   ```bash
   ssh root@your_droplet_ip
   ```

2. **Install dependencies** (5 min)
   - Python, Node.js, Nginx, etc.

3. **Clone your repo** (2 min)
   ```bash
   git clone https://github.com/YOUR_GITHUB_USERNAME/Flow_Assistant.git
   ```

4. **Setup Python** (5 min)
   - Create virtual environment
   - Install requirements

5. **Configure .env** (2 min)
   - Add your OpenAI API key

6. **Verify database** (1 min)
   - Already included in repo!

7. **Create vector store** (3 min)
   - For RAG/semantic search

8. **Build frontend** (5 min)
   - React production build

9. **Create services** (2 min)
   - Backend and frontend systemd services

10. **Configure Nginx** (2 min)
    - Reverse proxy

11. **Setup firewall** (1 min)
    - Secure your droplet

12. **Start everything** (1 min)
    - Services running!

13. **Test it** (2 min)
    - Access in browser!

---

## 📝 Quick Commands Reference

### Main Deployment Command (after SSH)

```bash
# 1. Update system
apt update && apt upgrade -y

# 2. Install dependencies
apt install -y python3 python3-pip python3-venv nodejs npm nginx git curl ufw
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs

# 3. Clone your repo (REPLACE YOUR_GITHUB_USERNAME!)
mkdir -p /opt/activepieces-assistant
cd /opt/activepieces-assistant
git clone https://github.com/YOUR_GITHUB_USERNAME/Flow_Assistant.git .

# 4. Continue with remaining steps from DEPLOY_FROM_GITHUB.md
```

---

## ✅ After Deployment

You'll have:

- ✅ **Backend**: Running on port 8000
- ✅ **Frontend**: Running on port 5173
- ✅ **Nginx**: Serving on port 80
- ✅ **Database**: SQLite with 433+ integrations
- ✅ **Vector Store**: FAISS for RAG
- ✅ **Web Search**: OpenAI integration
- ✅ **Services**: Auto-restart on failure

**Access**: `http://YOUR_DROPLET_IP`

---

## 🔧 After First Login

### Test All Features:

1. **Chat**: "Does ActivePieces have a Slack integration?"
2. **Web Search**: "What's the latest news about automation?"
3. **Code Generation**: "Create code to fetch user data from an API"
4. **Build Flow**: Enable toggle and ask to create a workflow

---

## 🆘 If Something Goes Wrong

### Check Logs
```bash
journalctl -u activepieces-backend -f
journalctl -u activepieces-frontend -f
```

### Restart Services
```bash
systemctl restart activepieces-backend
systemctl restart activepieces-frontend
```

### Get Help
- Check [DEPLOY_FROM_GITHUB.md](DEPLOY_FROM_GITHUB.md) troubleshooting section
- Check [docs/deployment/DEPLOYMENT_GUIDE.md](docs/deployment/DEPLOYMENT_GUIDE.md) detailed troubleshooting

---

## 🎯 Your Next Steps

### Step 1: Open This Guide
➜ **[DEPLOY_FROM_GITHUB.md](DEPLOY_FROM_GITHUB.md)**

### Step 2: Have These Ready
- [ ] Your GitHub username
- [ ] Your droplet IP address
- [ ] Your OpenAI API key
- [ ] SSH access to droplet

### Step 3: Start Deploying!
- Copy and paste commands
- Replace placeholders (YOUR_GITHUB_USERNAME, YOUR_DROPLET_IP)
- Follow the steps

### Step 4: Success!
- Access at `http://YOUR_DROPLET_IP`
- Start using your AI Assistant!

---

## 📚 All Deployment Documentation

If you want more details:

1. **[DEPLOY_FROM_GITHUB.md](DEPLOY_FROM_GITHUB.md)** ⭐ - Copy-paste deployment (START HERE!)
2. **[docs/deployment/GITHUB_CLONE_DEPLOY.md](docs/deployment/GITHUB_CLONE_DEPLOY.md)** - GitHub deployment with explanations
3. **[docs/deployment/DEPLOYMENT_GUIDE.md](docs/deployment/DEPLOYMENT_GUIDE.md)** - Complete guide with all details
4. **[docs/deployment/DEPLOYMENT_INDEX.md](docs/deployment/DEPLOYMENT_INDEX.md)** - Index of all deployment docs

---

## 💡 Pro Tips

1. **Use copy-paste**: Don't type commands manually
2. **Replace placeholders**: YOUR_GITHUB_USERNAME, YOUR_DROPLET_IP, sk-YOUR-KEY
3. **Save your droplet IP**: You'll need it multiple times
4. **Keep your .env secure**: Never commit it to GitHub
5. **Test each step**: Make sure services start before continuing

---

## 🔐 Security Notes

After deployment:
- [ ] Setup SSL if you have a domain (certbot --nginx)
- [ ] Change default SSH port (optional)
- [ ] Setup automated backups
- [ ] Monitor logs regularly

---

## 🎉 Ready to Deploy?

**Your deployment journey**:

1. Open **[DEPLOY_FROM_GITHUB.md](DEPLOY_FROM_GITHUB.md)** 👈 START HERE
2. Follow the steps (30 minutes)
3. Access your AI Assistant at `http://YOUR_DROPLET_IP`
4. Enjoy! 🚀

---

## ❓ Questions?

- **What if my repo is private?** See [DEPLOY_FROM_GITHUB.md](DEPLOY_FROM_GITHUB.md) Step 3 for authentication options
- **What if I get errors?** Check the troubleshooting section in each guide
- **Can I use a domain?** Yes! After deployment, run `certbot --nginx -d yourdomain.com`
- **How do I update?** `cd /opt/activepieces-assistant && git pull && [restart services]`

---

## 📞 Support

If you need help:
1. Check logs: `journalctl -u activepieces-backend -n 100`
2. Review troubleshooting in [DEPLOY_FROM_GITHUB.md](DEPLOY_FROM_GITHUB.md)
3. Check [docs/deployment/DEPLOYMENT_GUIDE.md](docs/deployment/DEPLOYMENT_GUIDE.md) for detailed help

---

**Let's deploy your AI Assistant! 🚀**

➜ **Next**: [DEPLOY_FROM_GITHUB.md](DEPLOY_FROM_GITHUB.md)

---

*Everything is documented. Everything is tested. Your AI Assistant awaits!* 🤖


