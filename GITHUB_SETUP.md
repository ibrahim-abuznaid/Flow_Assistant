# GitHub Setup Guide

This guide will help you prepare your ActivePieces AI Assistant project for GitHub and configure it for production deployment.

## 📋 Pre-Deployment Checklist

Before uploading to GitHub, ensure:

- [ ] All sensitive data is in `.env` (not committed)
- [ ] `.gitignore` is properly configured
- [ ] README.md is updated with your information
- [ ] Database credentials are not hardcoded
- [ ] API keys are stored in environment variables
- [ ] Documentation is complete

## 🚀 Step 1: Initialize Git Repository

If you haven't already initialized git:

```bash
cd /path/to/Flow_Assistant
git init
```

## 📝 Step 2: Review .gitignore

Ensure your `.gitignore` includes:

```gitignore
# Environment variables
.env
.env.local
.env.*.local

# Secrets
*.key
*.pem
secrets/

# Database
*.db
*.sqlite

# Logs
*.log
logs/

# FAISS index (regenerate on deployment)
ap_faiss_index/

# Node modules
node_modules/
frontend/node_modules/

# Build directories
frontend/dist/
frontend/build/
```

**Verify no sensitive files will be committed:**
```bash
git status
```

## 🔑 Step 3: Configure Environment Variables

### 3.1 Create .env.example (Already included)

This file serves as a template for other developers. It should contain:
- All required environment variable names
- Example/placeholder values (NOT real API keys)
- Comments explaining each variable

### 3.2 Ensure .env is Ignored

```bash
# Verify .env is in .gitignore
cat .gitignore | grep .env

# Remove .env from git if accidentally tracked
git rm --cached .env
```

## 🌐 Step 4: Create GitHub Repository

### 4.1 On GitHub:
1. Go to https://github.com/new
2. Create a new repository named `Flow_Assistant` (or your preferred name)
3. Choose **Public** or **Private**
4. **DO NOT** initialize with README (you already have one)
5. Click "Create repository"

### 4.2 Link Local Repo to GitHub:

```bash
# Add remote origin (replace with your username)
git remote add origin https://github.com/yourusername/Flow_Assistant.git

# Verify remote is added
git remote -v
```

## 📤 Step 5: First Commit and Push

```bash
# Stage all files
git add .

# Check what will be committed (verify no .env file!)
git status

# Commit
git commit -m "Initial commit: ActivePieces AI Assistant

- FastAPI backend with LangChain integration
- React frontend with modern UI
- PostgreSQL knowledge base
- FAISS vector search
- Deployment scripts for Ubuntu/DigitalOcean
- Comprehensive documentation"

# Push to GitHub
git push -u origin main
```

If you get an error about 'main' branch, try:
```bash
git branch -M main
git push -u origin main
```

## 🔐 Step 6: Secure Your Repository

### 6.1 Add GitHub Secrets (for CI/CD)

If you plan to use GitHub Actions:

1. Go to your repository on GitHub
2. Settings → Secrets and variables → Actions
3. Add repository secrets:
   - `OPENAI_API_KEY`
   - `PERPLEXITY_API_KEY`
   - `DB_PASSWORD`
   - etc.

### 6.2 Enable Security Features

1. **Dependabot**: Settings → Security → Dependabot
   - Enable "Dependabot alerts"
   - Enable "Dependabot security updates"

2. **Code Scanning**: Settings → Security → Code scanning
   - Set up CodeQL analysis (optional)

## 📚 Step 7: Update Repository Information

### 7.1 Add Repository Description

On GitHub repository page:
- Click "Edit" next to About
- Add description: "AI-powered assistant for ActivePieces workflow automation platform"
- Add topics: `ai`, `langchain`, `fastapi`, `react`, `activepieces`, `chatbot`
- Add website URL (if deployed)

### 7.2 Update README.md Links

Replace placeholder URLs in README.md:

```markdown
# Replace 'yourusername' with your actual GitHub username
https://github.com/yourusername/Flow_Assistant

# Update the clone command
git clone https://github.com/yourusername/Flow_Assistant.git
```

## 🚢 Step 8: Deployment from GitHub

### On Your Ubuntu Server (DigitalOcean):

```bash
# 1. SSH into your server
ssh root@your_server_ip

# 2. Clone your repository
cd /opt
git clone https://github.com/yourusername/Flow_Assistant.git
cd Flow_Assistant

# 3. Copy environment template
cp .env.example .env

# 4. Edit .env with your actual credentials
nano .env

# 5. Run deployment script
chmod +x deploy_ubuntu.sh
sudo ./deploy_ubuntu.sh
```

Or follow the manual deployment guide in [DEPLOYMENT.md](DEPLOYMENT.md)

## 🔄 Step 9: Update Workflow

When you make changes:

```bash
# 1. Pull latest changes (if working on multiple machines)
git pull

# 2. Make your changes
# ... edit files ...

# 3. Check status
git status

# 4. Stage changes
git add .

# 5. Commit
git commit -m "Description of changes"

# 6. Push
git push
```

### Update Deployment:

```bash
# On your server
cd /opt/Flow_Assistant
git pull origin main

# Restart services
sudo systemctl restart activepieces-backend
sudo systemctl restart activepieces-frontend
```

## 📋 Step 10: Create GitHub Releases

For version management:

```bash
# Tag a version
git tag -a v1.0.0 -m "Initial release"
git push origin v1.0.0
```

Then on GitHub:
1. Go to Releases
2. Click "Draft a new release"
3. Select the tag
4. Add release notes
5. Publish release

## 🛡️ Security Best Practices

### What to NEVER Commit:

❌ `.env` files
❌ API keys or tokens
❌ Database passwords
❌ SSL certificates (`.pem`, `.key`, `.crt`)
❌ Private keys
❌ Production credentials
❌ User data or logs

### What to ALWAYS Commit:

✅ `.env.example` (with placeholder values)
✅ Source code
✅ Documentation
✅ Configuration templates
✅ Deployment scripts
✅ Requirements/dependencies files

### If You Accidentally Commit Secrets:

1. **Immediately rotate the exposed credentials**
2. **Remove from git history:**
   ```bash
   # Use BFG Repo-Cleaner or git filter-branch
   # This is complex - consider creating a new repo if critical
   ```
3. **Force push** (be careful with this):
   ```bash
   git push --force origin main
   ```

## 📊 Step 11: Set Up Project Board (Optional)

For task management:

1. Go to Projects tab on GitHub
2. Create a new project
3. Add columns: To Do, In Progress, Done
4. Create issues for features/bugs
5. Link issues to project board

## 🤝 Step 12: Collaboration Setup

### For Team Projects:

1. **Add collaborators:**
   - Settings → Collaborators and teams
   - Add team members

2. **Set up branch protection:**
   - Settings → Branches
   - Add rule for `main` branch
   - Require pull request reviews

3. **Create CONTRIBUTING.md:**
   - Add contribution guidelines
   - Code style requirements
   - PR process

## 📞 Support and Issues

### Enable GitHub Issues:
- Settings → Features → Issues ✓
- Create issue templates for:
  - Bug reports
  - Feature requests
  - Questions

### Enable GitHub Discussions:
- Settings → Features → Discussions ✓
- Create categories for:
  - General
  - Ideas
  - Q&A

## ✅ Final Checklist

Before making your repository public:

- [ ] All sensitive data is removed and in `.env`
- [ ] `.gitignore` is properly configured
- [ ] README.md is complete and updated
- [ ] LICENSE file is added
- [ ] Documentation is complete
- [ ] Example environment variables are provided
- [ ] Deployment guide is tested
- [ ] No credentials in commit history
- [ ] Repository description and topics are set
- [ ] Security features are enabled

## 🎉 You're Ready!

Your project is now:
- ✅ Secure and production-ready
- ✅ Well-documented
- ✅ Easy to deploy
- ✅ Ready for collaboration

For deployment to Ubuntu server, see: [DEPLOYMENT.md](DEPLOYMENT.md)

