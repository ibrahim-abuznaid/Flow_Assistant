# Ubuntu Deployment Guide - DigitalOcean Droplet

This guide will walk you through deploying the ActivePieces AI Assistant on an Ubuntu server (DigitalOcean Droplet).

## 📋 Prerequisites

- **DigitalOcean Droplet** running Ubuntu 22.04 or 24.04 LTS
- Minimum specs: 2GB RAM, 1 vCPU (4GB RAM recommended for better performance)
- Domain name (optional, but recommended for production)
- API Keys: OpenAI (required), Perplexity (optional)

## 🚀 Quick Deployment (Automated)

1. **SSH into your droplet:**
   ```bash
   ssh root@your_server_ip
   ```

2. **Clone the repository:**
   ```bash
   cd /opt
   git clone https://github.com/yourusername/Flow_Assistant.git
   cd Flow_Assistant
   ```

3. **Run the deployment script:**
   ```bash
   chmod +x deploy_ubuntu.sh
   sudo ./deploy_ubuntu.sh
   ```

4. **Configure environment variables:**
   ```bash
   nano .env
   # Add your API keys and database credentials
   ```

5. **Start services:**
   ```bash
   sudo systemctl start activepieces-backend
   sudo systemctl start activepieces-frontend
   sudo systemctl enable activepieces-backend
   sudo systemctl enable activepieces-frontend
   ```

---

## 📝 Manual Deployment (Step-by-Step)

### Step 1: Initial Server Setup

#### 1.1 Update System Packages
```bash
sudo apt update && sudo apt upgrade -y
```

#### 1.2 Install Required System Dependencies
```bash
sudo apt install -y python3 python3-pip python3-venv nodejs npm postgresql postgresql-contrib nginx git curl
```

#### 1.3 Verify Node.js Version (needs 18+)
```bash
node --version
```

If version is below 18, install Node.js 20:
```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### Step 2: PostgreSQL Database Setup

#### 2.1 Configure PostgreSQL
```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user (in psql prompt)
CREATE DATABASE activepieces_pieces;
CREATE USER activepieces_user WITH ENCRYPTED PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE activepieces_pieces TO activepieces_user;
\q
```

#### 2.2 Configure PostgreSQL to Accept Connections
```bash
# Edit PostgreSQL configuration
sudo nano /etc/postgresql/*/main/postgresql.conf

# Find and update:
listen_addresses = 'localhost'
port = 5432
```

#### 2.3 Restart PostgreSQL
```bash
sudo systemctl restart postgresql
sudo systemctl enable postgresql
```

### Step 3: Clone and Setup Application

#### 3.1 Create Application Directory
```bash
sudo mkdir -p /opt/activepieces-assistant
sudo chown $USER:$USER /opt/activepieces-assistant
cd /opt/activepieces-assistant
```

#### 3.2 Clone Repository
```bash
git clone https://github.com/yourusername/Flow_Assistant.git .
```

#### 3.3 Setup Python Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

#### 4.1 Create .env File
```bash
cp .env.example .env
nano .env
```

#### 4.2 Update .env with Your Values
```ini
# AI Configuration
OPENAI_API_KEY=sk-your-actual-openai-key
PERPLEXITY_API_KEY=pplx-your-actual-key  # Optional

# LLM Settings
MODEL_PROVIDER=openai
MODEL_NAME=gpt-4-turbo-preview

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=activepieces_pieces
DB_USER=activepieces_user
DB_PASSWORD=your_secure_password

# Application
PORT=8000
```

### Step 5: Import Database Data

#### 5.1 Import ActivePieces Data
If you have a SQL dump or need to populate the database:
```bash
# If you have a database dump:
psql -h localhost -U activepieces_user -d activepieces_pieces < database_dump.sql

# Or run your preparation script:
source venv/bin/activate
python prepare_knowledge_base.py
```

#### 5.2 Test Database Connection
```bash
python db_config.py
```

### Step 6: Build Frontend

#### 6.1 Install Frontend Dependencies
```bash
cd frontend
npm install
```

#### 6.2 Update Frontend API Configuration
```bash
# Create production environment file
nano .env.production

# Add:
VITE_API_URL=http://your_server_ip:8000
```

#### 6.3 Build Frontend for Production
```bash
npm run build
```

### Step 7: Setup Systemd Services

#### 7.1 Create Backend Service
```bash
sudo nano /etc/systemd/system/activepieces-backend.service
```

Add this content:
```ini
[Unit]
Description=ActivePieces AI Assistant Backend
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/activepieces-assistant
Environment="PATH=/opt/activepieces-assistant/venv/bin"
ExecStart=/opt/activepieces-assistant/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 7.2 Create Frontend Service (using serve)
First, install serve globally:
```bash
sudo npm install -g serve
```

Then create the service:
```bash
sudo nano /etc/systemd/system/activepieces-frontend.service
```

Add this content:
```ini
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
```

#### 7.3 Set Correct Permissions
```bash
sudo chown -R www-data:www-data /opt/activepieces-assistant
```

#### 7.4 Enable and Start Services
```bash
sudo systemctl daemon-reload
sudo systemctl enable activepieces-backend
sudo systemctl enable activepieces-frontend
sudo systemctl start activepieces-backend
sudo systemctl start activepieces-frontend
```

#### 7.5 Check Service Status
```bash
sudo systemctl status activepieces-backend
sudo systemctl status activepieces-frontend
```

### Step 8: Configure Nginx as Reverse Proxy

#### 8.1 Create Nginx Configuration
```bash
sudo nano /etc/nginx/sites-available/activepieces-assistant
```

Add this configuration:
```nginx
server {
    listen 80;
    server_name your_domain.com;  # Replace with your domain or server IP

    # Frontend
    location / {
        proxy_pass http://localhost:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api/ {
        rewrite ^/api/(.*) /$1 break;
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check endpoint (optional)
    location /health {
        proxy_pass http://localhost:8000/health;
        proxy_http_version 1.1;
    }
}
```

#### 8.2 Enable Site and Restart Nginx
```bash
sudo ln -s /etc/nginx/sites-available/activepieces-assistant /etc/nginx/sites-enabled/
sudo nginx -t  # Test configuration
sudo systemctl restart nginx
sudo systemctl enable nginx
```

### Step 9: Configure Firewall (UFW)

```bash
# Allow SSH (IMPORTANT: Do this first!)
sudo ufw allow OpenSSH

# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable
sudo ufw status
```

### Step 10: Setup SSL with Let's Encrypt (Optional but Recommended)

#### 10.1 Install Certbot
```bash
sudo apt install certbot python3-certbot-nginx -y
```

#### 10.2 Obtain SSL Certificate
```bash
sudo certbot --nginx -d your_domain.com -d www.your_domain.com
```

#### 10.3 Auto-renewal Setup (Certbot usually does this automatically)
```bash
sudo systemctl status certbot.timer
```

---

## 🔧 Application Management

### View Logs
```bash
# Backend logs
sudo journalctl -u activepieces-backend -f

# Frontend logs
sudo journalctl -u activepieces-frontend -f

# Nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### Restart Services
```bash
# Restart backend
sudo systemctl restart activepieces-backend

# Restart frontend
sudo systemctl restart activepieces-frontend

# Restart nginx
sudo systemctl restart nginx
```

### Stop Services
```bash
sudo systemctl stop activepieces-backend
sudo systemctl stop activepieces-frontend
```

### Update Application
```bash
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

## 🔍 Troubleshooting

### Backend Not Starting
```bash
# Check logs
sudo journalctl -u activepieces-backend -n 50

# Check if port is in use
sudo netstat -tulpn | grep 8000

# Manually test backend
cd /opt/activepieces-assistant
source venv/bin/activate
python main.py
```

### Database Connection Issues
```bash
# Test PostgreSQL connection
psql -h localhost -U activepieces_user -d activepieces_pieces

# Check PostgreSQL status
sudo systemctl status postgresql

# View PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-*-main.log
```

### Nginx Issues
```bash
# Test Nginx configuration
sudo nginx -t

# Check Nginx status
sudo systemctl status nginx

# View Nginx error logs
sudo tail -f /var/log/nginx/error.log
```

### Frontend Not Loading
```bash
# Check if frontend service is running
sudo systemctl status activepieces-frontend

# Rebuild frontend
cd /opt/activepieces-assistant/frontend
npm run build
sudo systemctl restart activepieces-frontend
```

### Permission Issues
```bash
# Fix ownership
sudo chown -R www-data:www-data /opt/activepieces-assistant

# Fix FAISS index permissions
sudo chmod -R 755 /opt/activepieces-assistant/ap_faiss_index
```

---

## 📊 Monitoring and Maintenance

### Setup Log Rotation
Create log rotation for application logs:
```bash
sudo nano /etc/logrotate.d/activepieces-assistant
```

Add:
```
/var/log/activepieces/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
}
```

### Monitor Resource Usage
```bash
# Check memory usage
free -h

# Check disk usage
df -h

# Check CPU usage
top

# Monitor specific process
htop -p $(pgrep -f uvicorn)
```

### Database Maintenance
```bash
# Backup database
pg_dump -h localhost -U activepieces_user activepieces_pieces > backup_$(date +%Y%m%d).sql

# Vacuum database (optimize)
sudo -u postgres psql -d activepieces_pieces -c "VACUUM ANALYZE;"
```

---

## 🔒 Security Best Practices

1. **Change default passwords** - Update all default database passwords
2. **Keep system updated** - Run `sudo apt update && sudo apt upgrade` regularly
3. **Use strong API keys** - Never commit API keys to version control
4. **Enable firewall** - Use UFW to restrict access
5. **Use HTTPS** - Always use SSL certificates in production
6. **Regular backups** - Backup your database and configuration files
7. **Monitor logs** - Regularly check application and system logs
8. **Limit SSH access** - Use SSH keys instead of passwords
9. **Update dependencies** - Keep Python packages and npm packages updated

---

## 🎯 Performance Optimization

### Optimize PostgreSQL
```bash
# Edit PostgreSQL config
sudo nano /etc/postgresql/*/main/postgresql.conf

# Recommended settings for 4GB RAM:
shared_buffers = 1GB
effective_cache_size = 3GB
maintenance_work_mem = 256MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 10MB
min_wal_size = 1GB
max_wal_size = 4GB
```

### Optimize Python Backend
Consider using Gunicorn for better performance:
```bash
pip install gunicorn

# Update backend service to use:
ExecStart=/opt/activepieces-assistant/venv/bin/gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Enable Gzip Compression in Nginx
```nginx
# Add to nginx config
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json;
```

---

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review application logs: `sudo journalctl -u activepieces-backend -f`
3. Check GitHub issues: https://github.com/yourusername/Flow_Assistant/issues
4. Review the main README.md and other documentation files

---

## 🎉 Success!

Your AI Assistant should now be running at:
- **HTTP**: http://your_server_ip or http://your_domain.com
- **HTTPS** (if configured): https://your_domain.com

Test the deployment:
```bash
curl http://localhost:8000/health
```

You should see: `{"status":"healthy","message":"Service is operational"}`

