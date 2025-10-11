# 📚 Deployment & Setup Documentation Index

Welcome! This index will guide you through all the documentation needed to deploy your ActivePieces AI Assistant.

## 🎯 Quick Navigation

### For First-Time Setup
1. **[QUICK_START_PRODUCTION.md](QUICK_START_PRODUCTION.md)** ⭐ START HERE
   - Fastest way to deploy (15 minutes)
   - One-command deployment
   - Common troubleshooting

### For GitHub Upload
2. **[GITHUB_SETUP.md](GITHUB_SETUP.md)** 
   - Prepare project for GitHub
   - Security best practices
   - Repository configuration

### For Detailed Deployment
3. **[DEPLOYMENT.md](DEPLOYMENT.md)**
   - Complete step-by-step guide
   - Manual deployment instructions
   - Advanced configuration

### For Tracking Progress
4. **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)**
   - Complete deployment checklist
   - Verification steps
   - Success criteria

## 📋 Documentation Overview

### Essential Files

| File | Purpose | When to Use |
|------|---------|-------------|
| **[QUICK_START_PRODUCTION.md](QUICK_START_PRODUCTION.md)** | Rapid deployment guide | First deployment, need it fast |
| **[DEPLOYMENT.md](DEPLOYMENT.md)** | Comprehensive deployment | Detailed setup, troubleshooting |
| **[GITHUB_SETUP.md](GITHUB_SETUP.md)** | GitHub configuration | Before pushing to GitHub |
| **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** | Deployment checklist | During deployment for tracking |
| **[README.md](README.md)** | Project overview | Understanding the project |

### Configuration Files

| File | Purpose |
|------|---------|
| `.env.example` | Environment variables template |
| `frontend/.env.production.example` | Frontend production config |
| `nginx.conf.template` | Nginx configuration template |
| `systemd/activepieces-backend.service` | Backend service file |
| `systemd/activepieces-frontend.service` | Frontend service file |

### Deployment Scripts

| File | Purpose |
|------|---------|
| `deploy_ubuntu.sh` | Automated deployment script |

## 🚀 Deployment Workflows

### Workflow 1: Quick Deploy (Recommended)
Perfect for: Getting started fast, testing deployment

```
1. [GITHUB_SETUP.md] - Upload to GitHub
   ↓
2. [QUICK_START_PRODUCTION.md] - Deploy in 15 minutes
   ↓
3. [DEPLOYMENT_CHECKLIST.md] - Verify deployment
```

### Workflow 2: Detailed Deploy
Perfect for: Production setup, custom configuration

```
1. [GITHUB_SETUP.md] - Upload to GitHub
   ↓
2. [DEPLOYMENT.md] - Follow detailed guide
   ↓
3. [DEPLOYMENT_CHECKLIST.md] - Complete checklist
```

### Workflow 3: Manual Deploy
Perfect for: Learning, customization, specific requirements

```
1. [README.md] - Understand the project
   ↓
2. [DEPLOYMENT.md] - Manual setup section
   ↓
3. Configure systemd services manually
   ↓
4. [DEPLOYMENT_CHECKLIST.md] - Verify
```

## 📖 Step-by-Step Guide

### Phase 1: Preparation (Before Deployment)

1. **Review the Project**
   - Read [README.md](README.md)
   - Understand features and requirements

2. **Prepare for GitHub**
   - Follow [GITHUB_SETUP.md](GITHUB_SETUP.md)
   - Ensure no secrets in code
   - Configure `.gitignore`

3. **Get Required Credentials**
   - OpenAI API key (required)
   - Perplexity API key (optional)
   - Domain name (optional)

### Phase 2: GitHub Upload

1. **Initialize Repository**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. **Push to GitHub**
   - Create repository on GitHub
   - Add remote and push
   - See [GITHUB_SETUP.md](GITHUB_SETUP.md) for details

### Phase 3: Server Setup

Choose your deployment method:

**Option A: Quick Deploy** (15 minutes)
- Follow [QUICK_START_PRODUCTION.md](QUICK_START_PRODUCTION.md)
- Run automated script
- Configure `.env`
- Done!

**Option B: Detailed Deploy** (1 hour)
- Follow [DEPLOYMENT.md](DEPLOYMENT.md)
- Manual step-by-step setup
- Full control and understanding

### Phase 4: Verification

1. **Use the Checklist**
   - Open [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
   - Check off each item
   - Verify all services

2. **Test the Application**
   - Visit http://your_server_ip
   - Send test messages
   - Check logs

### Phase 5: Secure & Optimize

1. **Enable HTTPS**
   ```bash
   sudo certbot --nginx -d your_domain.com
   ```

2. **Optimize Performance**
   - See [DEPLOYMENT.md](DEPLOYMENT.md) - Performance section
   - Configure PostgreSQL
   - Use Gunicorn

3. **Setup Monitoring**
   - Configure log rotation
   - Setup backup scripts
   - Monitor resources

## 🛠️ Common Tasks

### Updating the Application
```bash
cd /opt/activepieces-assistant
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
cd frontend && npm install && npm run build
sudo systemctl restart activepieces-backend
sudo systemctl restart activepieces-frontend
```

See: [QUICK_START_PRODUCTION.md](QUICK_START_PRODUCTION.md#updating-the-application)

### Viewing Logs
```bash
sudo journalctl -u activepieces-backend -f
```

See: [DEPLOYMENT.md](DEPLOYMENT.md#application-management)

### Backup Database
```bash
pg_dump -h localhost -U activepieces_user activepieces_pieces > backup.sql
```

See: [DEPLOYMENT.md](DEPLOYMENT.md#database-maintenance)

## 🔧 Configuration Reference

### Environment Variables

All environment variables are documented in:
- `.env.example` - Main configuration
- `frontend/.env.production.example` - Frontend config

Key variables:
- `OPENAI_API_KEY` - Required for LLM
- `DB_PASSWORD` - Database password
- `ALLOWED_ORIGINS` - CORS configuration
- `VITE_API_URL` - Frontend API endpoint

### Service Files

Located in `systemd/` directory:
- `activepieces-backend.service` - Backend service
- `activepieces-frontend.service` - Frontend service

### Nginx Configuration

Template: `nginx.conf.template`
- HTTP/HTTPS configuration
- Reverse proxy setup
- SSL settings (commented)

## 📊 Architecture Overview

```
┌─────────────────────────────────────────────┐
│              Nginx (Port 80/443)            │
│          (Reverse Proxy + SSL)              │
└─────────────────┬───────────────────────────┘
                  │
        ┌─────────┴──────────┐
        │                    │
        ▼                    ▼
┌───────────────┐    ┌──────────────────┐
│   Frontend    │    │     Backend      │
│  (Port 5173)  │    │   (Port 8000)    │
│  React + Vite │    │  FastAPI + LLM   │
└───────────────┘    └────────┬─────────┘
                              │
                              ▼
                     ┌────────────────┐
                     │   PostgreSQL   │
                     │  (Port 5432)   │
                     └────────────────┘
```

## 🆘 Troubleshooting Guide

### Quick Links

| Issue | Solution Location |
|-------|-------------------|
| Backend won't start | [QUICK_START_PRODUCTION.md](QUICK_START_PRODUCTION.md#backend-not-starting) |
| Database connection fails | [DEPLOYMENT.md](DEPLOYMENT.md#database-connection-issues) |
| Frontend not loading | [QUICK_START_PRODUCTION.md](QUICK_START_PRODUCTION.md#frontend-not-loading) |
| Nginx errors | [DEPLOYMENT.md](DEPLOYMENT.md#nginx-issues) |
| SSL/HTTPS setup | [DEPLOYMENT.md](DEPLOYMENT.md#step-10-setup-ssl-with-lets-encrypt-optional-but-recommended) |
| Permission errors | [DEPLOYMENT.md](DEPLOYMENT.md#permission-issues) |

### Getting Help

1. Check relevant documentation above
2. Review logs: `sudo journalctl -u activepieces-backend -f`
3. Verify checklist: [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
4. Check GitHub issues
5. Review [DEPLOYMENT.md](DEPLOYMENT.md) troubleshooting section

## 📝 Checklist Summary

Before deployment:
- [ ] Read [GITHUB_SETUP.md](GITHUB_SETUP.md)
- [ ] Upload to GitHub
- [ ] Have API keys ready

During deployment:
- [ ] Follow [QUICK_START_PRODUCTION.md](QUICK_START_PRODUCTION.md) or [DEPLOYMENT.md](DEPLOYMENT.md)
- [ ] Use [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
- [ ] Configure `.env` file

After deployment:
- [ ] Test application
- [ ] Enable HTTPS
- [ ] Setup backups
- [ ] Configure monitoring

## 🎯 Recommended Path

**For most users, we recommend:**

1. **Start**: [GITHUB_SETUP.md](GITHUB_SETUP.md)
   - Get your code on GitHub safely

2. **Deploy**: [QUICK_START_PRODUCTION.md](QUICK_START_PRODUCTION.md)
   - Fast, automated deployment

3. **Verify**: [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
   - Ensure everything works

4. **Reference**: Keep [DEPLOYMENT.md](DEPLOYMENT.md) handy
   - For detailed troubleshooting

## 📚 Additional Resources

### Project Documentation
- [README.md](README.md) - Project overview
- [QUICKSTART.md](QUICKSTART.md) - Local development setup
- [AGENT_CONNECTION_GUIDE.md](AGENT_CONNECTION_GUIDE.md) - Database connection details

### Technical Guides
- [POSTGRES_MIGRATION.md](POSTGRES_MIGRATION.md) - Database migration info
- [BUILD_COMPLETE.md](BUILD_COMPLETE.md) - Build information

## 🚀 Ready to Deploy?

Choose your path:

1. **🏃 Fast Track (15 min)**
   → [QUICK_START_PRODUCTION.md](QUICK_START_PRODUCTION.md)

2. **📖 Detailed Guide (1 hour)**
   → [DEPLOYMENT.md](DEPLOYMENT.md)

3. **📋 Use Checklist**
   → [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)

---

**Good luck with your deployment! 🎉**

For questions or issues, please check the troubleshooting sections in the guides above.

