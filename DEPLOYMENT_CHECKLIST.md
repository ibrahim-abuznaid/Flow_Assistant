# Deployment Checklist ✅

Use this checklist to ensure your deployment is complete and secure.

## 📋 Pre-Deployment

### Code Preparation
- [ ] All code is committed to git
- [ ] `.env` file is NOT in git (check `.gitignore`)
- [ ] API keys are removed from code
- [ ] Database credentials are in environment variables
- [ ] All tests pass locally
- [ ] Documentation is up to date

### Environment Setup
- [ ] `.env.example` file exists and is complete
- [ ] All required environment variables are documented
- [ ] Frontend API URL is configurable
- [ ] Database connection string is correct

### GitHub
- [ ] Repository is created on GitHub
- [ ] Remote origin is configured
- [ ] Code is pushed to GitHub
- [ ] Repository description is set
- [ ] Topics/tags are added
- [ ] README.md is updated with correct URLs

## 🚀 Deployment to Ubuntu Server

### Server Preparation
- [ ] Ubuntu 22.04 or 24.04 LTS is running
- [ ] SSH access is configured
- [ ] Server has at least 2GB RAM
- [ ] Domain name is configured (if using)

### System Setup
- [ ] System packages are updated
- [ ] Python 3.8+ is installed
- [ ] Node.js 18+ is installed
- [ ] PostgreSQL is installed
- [ ] Nginx is installed

### Database Setup
- [ ] PostgreSQL is running
- [ ] Database is created
- [ ] Database user is created
- [ ] User has proper permissions
- [ ] Database credentials are secure
- [ ] Connection is tested

### Application Setup
- [ ] Code is cloned to `/opt/activepieces-assistant`
- [ ] Virtual environment is created
- [ ] Python dependencies are installed
- [ ] Frontend dependencies are installed
- [ ] Frontend is built for production
- [ ] `.env` file is created and configured
- [ ] FAISS index is generated (if needed)

### Service Configuration
- [ ] Backend systemd service is created
- [ ] Frontend systemd service is created
- [ ] Services are enabled
- [ ] Services are started
- [ ] Services are running correctly
- [ ] Logs show no errors

### Nginx Configuration
- [ ] Nginx config is created
- [ ] Config is enabled in sites-enabled
- [ ] Nginx configuration test passes
- [ ] Nginx is restarted
- [ ] Frontend is accessible
- [ ] Backend API is accessible

### Security
- [ ] Firewall (UFW) is enabled
- [ ] SSH port is allowed
- [ ] HTTP (80) is allowed
- [ ] HTTPS (443) is allowed
- [ ] Unnecessary ports are blocked
- [ ] Strong passwords are used
- [ ] API keys are not exposed

### SSL/HTTPS (Optional but Recommended)
- [ ] Certbot is installed
- [ ] SSL certificate is obtained
- [ ] Auto-renewal is configured
- [ ] HTTPS is working
- [ ] HTTP redirects to HTTPS

## ✅ Post-Deployment

### Testing
- [ ] Frontend loads successfully
- [ ] Can send chat messages
- [ ] Backend responds correctly
- [ ] Database queries work
- [ ] Error handling works
- [ ] Health endpoint responds: `/health`
- [ ] Stats endpoint works: `/stats`

### Performance
- [ ] Response times are acceptable
- [ ] Memory usage is normal
- [ ] CPU usage is normal
- [ ] Database performance is good

### Monitoring
- [ ] Application logs are accessible
- [ ] Nginx logs are accessible
- [ ] Database logs are accessible
- [ ] System resources are monitored
- [ ] Error tracking is set up (optional)

### Documentation
- [ ] Deployment is documented
- [ ] Environment variables are documented
- [ ] Troubleshooting guide is available
- [ ] Team members know how to access logs

### Maintenance
- [ ] Backup strategy is in place
- [ ] Update procedure is documented
- [ ] Log rotation is configured
- [ ] Database maintenance is scheduled

## 🔐 Security Checklist

### Application Security
- [ ] No API keys in code
- [ ] Environment variables are secure
- [ ] Database credentials are strong
- [ ] CORS is properly configured
- [ ] Input validation is in place
- [ ] Error messages don't leak sensitive info

### Server Security
- [ ] SSH is secured (keys, no root login)
- [ ] Firewall is properly configured
- [ ] Only necessary ports are open
- [ ] System is updated regularly
- [ ] Fail2ban is configured (optional)
- [ ] SSL/TLS is enabled
- [ ] Security headers are set

### Database Security
- [ ] Database user has minimal permissions
- [ ] Database is not publicly accessible
- [ ] Strong password is used
- [ ] Regular backups are configured
- [ ] Sensitive data is encrypted

## 📊 Monitoring Checklist

### Application Monitoring
- [ ] Backend service status: `systemctl status activepieces-backend`
- [ ] Frontend service status: `systemctl status activepieces-frontend`
- [ ] Backend logs: `journalctl -u activepieces-backend -f`
- [ ] Frontend logs: `journalctl -u activepieces-frontend -f`

### System Monitoring
- [ ] Disk usage: `df -h`
- [ ] Memory usage: `free -h`
- [ ] CPU usage: `top` or `htop`
- [ ] Network status: `netstat -tulpn`

### Nginx Monitoring
- [ ] Nginx status: `systemctl status nginx`
- [ ] Access logs: `/var/log/nginx/access.log`
- [ ] Error logs: `/var/log/nginx/error.log`

### Database Monitoring
- [ ] PostgreSQL status: `systemctl status postgresql`
- [ ] Database connections: Check connection count
- [ ] Database size: Monitor growth
- [ ] Query performance: Monitor slow queries

## 🔧 Quick Commands

### Service Management
```bash
# Restart services
sudo systemctl restart activepieces-backend
sudo systemctl restart activepieces-frontend
sudo systemctl restart nginx

# View logs
sudo journalctl -u activepieces-backend -f
sudo journalctl -u activepieces-frontend -f

# Check status
sudo systemctl status activepieces-backend
```

### Update Application
```bash
cd /opt/activepieces-assistant
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
cd frontend && npm install && npm run build
sudo systemctl restart activepieces-backend
sudo systemctl restart activepieces-frontend
```

### Database Backup
```bash
pg_dump -h localhost -U activepieces_user activepieces_pieces > backup_$(date +%Y%m%d).sql
```

## 🎯 Success Criteria

Deployment is successful when:

✅ Application is accessible via browser
✅ Chat messages work correctly
✅ No errors in logs
✅ All services are running
✅ HTTPS is enabled (if applicable)
✅ Performance is acceptable
✅ Monitoring is in place
✅ Backups are configured

## 📞 Troubleshooting

If anything fails, see:
- [DEPLOYMENT.md](DEPLOYMENT.md) - Full deployment guide
- [GITHUB_SETUP.md](GITHUB_SETUP.md) - GitHub configuration
- [README.md](README.md) - General documentation

## 🎉 Congratulations!

Once all items are checked, your deployment is complete!

For ongoing maintenance:
1. Monitor logs regularly
2. Update dependencies monthly
3. Backup database weekly
4. Review security quarterly
5. Update documentation as needed

