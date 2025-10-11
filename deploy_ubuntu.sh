#!/bin/bash

# ============================================================================
# ActivePieces AI Assistant - Ubuntu Deployment Script
# ============================================================================
# This script automates the deployment of the AI Assistant on Ubuntu
# Tested on Ubuntu 22.04 and 24.04 LTS
# ============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "\n${BLUE}============================================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}============================================================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

check_root() {
    if [ "$EUID" -ne 0 ]; then 
        print_error "Please run as root or with sudo"
        exit 1
    fi
}

# ============================================================================
# Main Deployment
# ============================================================================

print_header "ActivePieces AI Assistant - Ubuntu Deployment"

# Check if running as root
check_root

# Get the actual user who called sudo
ACTUAL_USER=${SUDO_USER:-$USER}
APP_DIR="/opt/activepieces-assistant"

print_header "Step 1: System Update"
apt update && apt upgrade -y
print_success "System updated successfully"

print_header "Step 2: Installing Dependencies"
apt install -y python3 python3-pip python3-venv nodejs npm postgresql postgresql-contrib nginx git curl software-properties-common

print_success "Base dependencies installed"

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    print_warning "Node.js version is below 18, installing Node.js 20..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt-get install -y nodejs
    print_success "Node.js 20 installed"
fi

print_header "Step 3: PostgreSQL Configuration"

# Check if database exists
DB_EXISTS=$(sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='activepieces_pieces'" 2>/dev/null || echo "")

if [ "$DB_EXISTS" != "1" ]; then
    print_warning "Creating PostgreSQL database and user..."
    
    # Prompt for database password
    read -sp "Enter a secure password for PostgreSQL user 'activepieces_user': " DB_PASSWORD
    echo
    
    sudo -u postgres psql <<EOF
CREATE DATABASE activepieces_pieces;
CREATE USER activepieces_user WITH ENCRYPTED PASSWORD '$DB_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE activepieces_pieces TO activepieces_user;
EOF
    
    print_success "Database and user created successfully"
    print_warning "Database password: $DB_PASSWORD (save this!)"
else
    print_success "Database already exists"
fi

# Enable and start PostgreSQL
systemctl enable postgresql
systemctl start postgresql
print_success "PostgreSQL configured and running"

print_header "Step 4: Application Setup"

# Create application directory if it doesn't exist
if [ ! -d "$APP_DIR" ]; then
    mkdir -p "$APP_DIR"
    print_success "Created application directory: $APP_DIR"
fi

# If we're in the git repo, copy files
if [ -d ".git" ]; then
    print_warning "Copying files from current directory to $APP_DIR..."
    rsync -av --exclude '.git' --exclude 'venv' --exclude 'node_modules' --exclude '__pycache__' . "$APP_DIR/"
    print_success "Files copied successfully"
else
    print_error "Not in a git repository. Please run this script from the project root."
    exit 1
fi

cd "$APP_DIR"

print_header "Step 5: Python Environment Setup"

# Create virtual environment
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# Activate and install dependencies
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
print_success "Python dependencies installed"

print_header "Step 6: Environment Configuration"

if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_warning "Created .env file from .env.example"
        print_warning "IMPORTANT: Edit .env file and add your API keys!"
        print_warning "  nano $APP_DIR/.env"
    else
        print_error ".env.example not found. Cannot create .env file."
    fi
else
    print_success ".env file already exists"
fi

print_header "Step 7: Frontend Setup"

cd frontend

# Install dependencies
npm install
print_success "Frontend dependencies installed"

# Create production environment file
if [ ! -f ".env.production" ]; then
    echo "VITE_API_URL=http://localhost:8000" > .env.production
    print_success "Created .env.production for frontend"
fi

# Build frontend
npm run build
print_success "Frontend built successfully"

cd ..

print_header "Step 8: Systemd Service Setup"

# Create backend service
cat > /etc/systemd/system/activepieces-backend.service <<EOF
[Unit]
Description=ActivePieces AI Assistant Backend
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

print_success "Backend service created"

# Install serve for frontend
npm install -g serve

# Create frontend service
cat > /etc/systemd/system/activepieces-frontend.service <<EOF
[Unit]
Description=ActivePieces AI Assistant Frontend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=$APP_DIR/frontend
ExecStart=/usr/bin/serve -s dist -l 5173
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

print_success "Frontend service created"

# Set permissions
chown -R www-data:www-data "$APP_DIR"
print_success "Permissions set correctly"

# Reload systemd
systemctl daemon-reload

print_header "Step 9: Nginx Configuration"

# Prompt for domain or IP
read -p "Enter your domain name (or press Enter to use server IP): " DOMAIN
if [ -z "$DOMAIN" ]; then
    DOMAIN=$(curl -s ifconfig.me 2>/dev/null || echo "your-server-ip")
    print_warning "Using IP address: $DOMAIN"
fi

# Create Nginx config
cat > /etc/nginx/sites-available/activepieces-assistant <<EOF
server {
    listen 80;
    server_name $DOMAIN;

    # Frontend
    location / {
        proxy_pass http://localhost:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
    }

    # Backend API
    location /api/ {
        rewrite ^/api/(.*) /\$1 break;
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Direct backend access (for health checks, etc.)
    location ~ ^/(health|stats) {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
    }
}
EOF

# Enable site
ln -sf /etc/nginx/sites-available/activepieces-assistant /etc/nginx/sites-enabled/

# Test Nginx configuration
nginx -t
systemctl restart nginx
systemctl enable nginx
print_success "Nginx configured successfully"

print_header "Step 10: Firewall Configuration"

# Configure UFW
ufw --force enable
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
print_success "Firewall configured"

print_header "Step 11: Starting Services"

# Enable and start services
systemctl enable activepieces-backend
systemctl enable activepieces-frontend
systemctl start activepieces-backend
systemctl start activepieces-frontend

sleep 3

# Check service status
if systemctl is-active --quiet activepieces-backend; then
    print_success "Backend service is running"
else
    print_error "Backend service failed to start. Check logs with: journalctl -u activepieces-backend -n 50"
fi

if systemctl is-active --quiet activepieces-frontend; then
    print_success "Frontend service is running"
else
    print_error "Frontend service failed to start. Check logs with: journalctl -u activepieces-frontend -n 50"
fi

print_header "Deployment Summary"

echo -e "${GREEN}✓ Deployment completed successfully!${NC}\n"

echo -e "${BLUE}Next Steps:${NC}"
echo -e "1. Configure your API keys:"
echo -e "   ${YELLOW}nano $APP_DIR/.env${NC}"
echo -e ""
echo -e "2. Restart backend after configuring:"
echo -e "   ${YELLOW}sudo systemctl restart activepieces-backend${NC}"
echo -e ""
echo -e "3. Access your application:"
echo -e "   ${YELLOW}http://$DOMAIN${NC}"
echo -e ""
echo -e "4. Check service status:"
echo -e "   ${YELLOW}sudo systemctl status activepieces-backend${NC}"
echo -e "   ${YELLOW}sudo systemctl status activepieces-frontend${NC}"
echo -e ""
echo -e "5. View logs:"
echo -e "   ${YELLOW}sudo journalctl -u activepieces-backend -f${NC}"
echo -e ""
echo -e "6. (Optional) Setup SSL with Let's Encrypt:"
echo -e "   ${YELLOW}sudo apt install certbot python3-certbot-nginx${NC}"
echo -e "   ${YELLOW}sudo certbot --nginx -d $DOMAIN${NC}"
echo -e ""

print_header "Deployment Complete!"

echo -e "${BLUE}For detailed information, see DEPLOYMENT.md${NC}\n"

