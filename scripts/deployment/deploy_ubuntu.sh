#!/bin/bash

# ============================================================================
# ActivePieces AI Assistant - Ubuntu 25.04 Deployment Script
# ============================================================================
# Optimized deployment for Ubuntu 25.04 x64
# GitHub Repo: https://github.com/ibrahim-abuznaid/Flow_Assistant.git
# ============================================================================
# USAGE:
#   1. cd /opt
#   2. git clone https://github.com/ibrahim-abuznaid/Flow_Assistant.git
#   3. cd Flow_Assistant
#   4. chmod +x scripts/deployment/deploy_ubuntu.sh
#   5. sudo ./scripts/deployment/deploy_ubuntu.sh
# ============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
APP_DIR="/opt/Flow_Assistant"
APP_USER="www-data"
REPO_URL="https://github.com/ibrahim-abuznaid/Flow_Assistant.git"

# ============================================================================
# Helper Functions
# ============================================================================

print_header() {
    echo ""
    echo -e "${BLUE}============================================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}============================================================================${NC}"
    echo ""
}

print_step() {
    echo -e "${CYAN}➜ $1${NC}"
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

check_file() {
    if [ ! -f "$1" ]; then
        print_error "Required file not found: $1"
        exit 1
    fi
}

check_dir() {
    if [ ! -d "$1" ]; then
        print_error "Required directory not found: $1"
        exit 1
    fi
}

# ============================================================================
# Main Deployment Script
# ============================================================================

clear
print_header "ActivePieces AI Assistant - Ubuntu 25.04 Deployment"

# Check if running as root
check_root

echo -e "${CYAN}This script will:${NC}"
echo "  ✓ Install all system dependencies"
echo "  ✓ Setup Python backend with FastAPI"
echo "  ✓ Setup React frontend"
echo "  ✓ Use existing SQLite database (included in repo)"
echo "  ✓ Use existing FAISS vector store (included in repo)"
echo "  ✓ Setup Nginx reverse proxy"
echo "  ✓ Create systemd services"
echo "  ✓ Configure firewall"
echo "  ✓ (Optional) Setup SSL with Let's Encrypt"
echo ""
read -p "Continue with deployment? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_warning "Deployment cancelled"
    exit 0
fi

# ============================================================================
# Step 1: Verify We're in the Right Directory
# ============================================================================

print_header "Step 1/13: Verifying Installation Directory"

if [ "$PWD" != "$APP_DIR" ]; then
    print_error "This script must be run from $APP_DIR"
    print_warning "Current directory: $PWD"
    echo ""
    echo "Please run:"
    echo "  cd $APP_DIR"
    echo "  sudo ./scripts/deployment/deploy_ubuntu.sh"
    exit 1
fi

print_success "Working directory verified: $APP_DIR"

# ============================================================================
# Step 2: Verify Required Files Exist
# ============================================================================

print_header "Step 2/13: Verifying Repository Files"

print_step "Checking required files and directories..."

# Core directories
check_dir "src"
check_dir "frontend"
check_dir "scripts"
check_dir "data"

# Data files
check_file "data/activepieces.db"
check_file "data/pieces_knowledge_base.json"
check_dir "data/ap_faiss_index"
check_file "data/ap_faiss_index/index.faiss"
check_file "data/ap_faiss_index/index.pkl"

# Configuration files
check_file "requirements.txt"
check_file "env.example"
check_file "frontend/package.json"

print_success "All required files verified!"

# ============================================================================
# Step 3: System Update
# ============================================================================

print_header "Step 3/13: System Update"
print_step "Updating system packages..."
apt update && apt upgrade -y
print_success "System updated successfully"

# ============================================================================
# Step 4: Install System Dependencies
# ============================================================================

print_header "Step 4/13: Installing System Dependencies"
print_step "Installing Python, Node.js, Nginx, and other tools..."

apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    nodejs \
    npm \
    nginx \
    git \
    curl \
    ufw \
    software-properties-common \
    htop \
    certbot \
    python3-certbot-nginx

print_success "Base dependencies installed"

# Check and install Node.js 20 if needed
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    print_warning "Node.js version is below 18, installing Node.js 20..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt-get install -y nodejs
    print_success "Node.js 20 installed"
else
    print_success "Node.js $(node -v) is already installed"
fi

# ============================================================================
# Step 5: Setup Python Backend
# ============================================================================

print_header "Step 5/13: Setting Up Python Backend"

# Create virtual environment
if [ ! -d "venv" ]; then
    print_step "Creating Python virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_warning "Virtual environment already exists, skipping creation"
fi

# Activate and install dependencies
print_step "Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
print_success "Python dependencies installed"

# ============================================================================
# Step 6: Configure Environment Variables
# ============================================================================

print_header "Step 6/13: Configuring Environment Variables"

if [ ! -f ".env" ]; then
    print_step "Creating .env file..."
    
    # Prompt for API keys
    echo ""
    echo -e "${CYAN}Please provide your API keys:${NC}"
    echo ""
    read -p "OpenAI API Key (required): " OPENAI_KEY
    
    echo ""
    echo -e "${CYAN}Web Search Provider:${NC}"
    echo "  1. OpenAI (default, no extra key needed)"
    echo "  2. Perplexity (requires Perplexity API key)"
    read -p "Choose (1 or 2) [default: 1]: " SEARCH_CHOICE
    
    if [ "$SEARCH_CHOICE" = "2" ]; then
        read -p "Perplexity API Key: " PERPLEXITY_KEY
        SEARCH_PROVIDER="perplexity"
    else
        SEARCH_PROVIDER="openai"
        PERPLEXITY_KEY=""
    fi
    
    # Create .env file
    cat > .env << EOF
# ============================================================================
# LLM Configuration
# ============================================================================
OPENAI_API_KEY=$OPENAI_KEY
MODEL_PROVIDER=openai
MODEL_NAME=gpt-4o

# Planning Layer Model
PLANNER_MODEL=gpt-4o-mini

# Flow Builder Model
FLOW_BUILDER_MODEL=gpt-4o-mini

# ============================================================================
# Web Search Configuration
# ============================================================================
SEARCH_PROVIDER=$SEARCH_PROVIDER
EOF

    if [ ! -z "$PERPLEXITY_KEY" ]; then
        echo "PERPLEXITY_API_KEY=$PERPLEXITY_KEY" >> .env
    fi

    cat >> .env << EOF

# ============================================================================
# Database Configuration (SQLite - No setup needed!)
# ============================================================================
SQLITE_DB_FILE=data/activepieces.db

# ============================================================================
# Application Configuration
# ============================================================================
PORT=8000
EOF

    print_success ".env file created"
else
    print_success ".env file already exists"
fi

# ============================================================================
# Step 7: Verify Database
# ============================================================================

print_header "Step 7/13: Verifying Database"

print_step "Testing database connection..."
source venv/bin/activate
python3 -c "from src.db_config import test_connection; test_connection()"

if [ $? -eq 0 ]; then
    print_success "Database verified and working!"
else
    print_error "Database verification failed"
    exit 1
fi

# ============================================================================
# Step 8: Verify Vector Store
# ============================================================================

print_header "Step 8/13: Verifying FAISS Vector Store"

print_step "Checking vector store files..."
if [ -f "data/ap_faiss_index/index.faiss" ] && [ -f "data/ap_faiss_index/index.pkl" ]; then
    print_success "FAISS vector store verified!"
    
    # Test loading the vector store
    print_step "Testing vector store loading..."
    python3 -c "
import os
os.environ['OPENAI_API_KEY'] = '$(grep OPENAI_API_KEY .env | cut -d= -f2)'
from src.tools import get_vector_store
try:
    vs = get_vector_store()
    print('✓ Vector store loaded successfully')
except Exception as e:
    print(f'✗ Vector store loading failed: {e}')
    exit(1)
"
    print_success "Vector store is functional!"
else
    print_error "Vector store files missing"
    exit 1
fi

# ============================================================================
# Step 9: Build Frontend
# ============================================================================

print_header "Step 9/13: Building Frontend"

cd frontend

# Install dependencies
print_step "Installing frontend dependencies..."
npm install
print_success "Frontend dependencies installed"

# Get domain/IP for frontend config
print_step "Configure frontend API URL"
echo ""
echo -e "${CYAN}Enter your domain or IP address:${NC}"
echo "  Examples: example.com, www.example.com, or 123.45.67.89"
read -p "Domain/IP: " DOMAIN

# Create production environment
cat > .env.production << EOF
VITE_API_URL=http://$DOMAIN
EOF

# Build frontend
print_step "Building frontend for production..."
npm run build
print_success "Frontend built successfully"

cd ..

# ============================================================================
# Step 10: Create Systemd Services
# ============================================================================

print_header "Step 10/13: Creating Systemd Services"

# Backend service
print_step "Creating backend service..."
cat > /etc/systemd/system/activepieces-backend.service << EOF
[Unit]
Description=ActivePieces AI Assistant Backend
After=network.target

[Service]
Type=simple
User=$APP_USER
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
EnvironmentFile=$APP_DIR/.env
ExecStart=$APP_DIR/venv/bin/uvicorn src.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

print_success "Backend service created"

# Install serve for frontend
print_step "Installing serve for frontend..."
npm install -g serve > /dev/null 2>&1

# Frontend service
print_step "Creating frontend service..."
cat > /etc/systemd/system/activepieces-frontend.service << EOF
[Unit]
Description=ActivePieces AI Assistant Frontend
After=network.target

[Service]
Type=simple
User=$APP_USER
WorkingDirectory=$APP_DIR/frontend
ExecStart=/usr/bin/serve -s dist -l 5173
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

print_success "Frontend service created"

# Set permissions
print_step "Setting correct permissions..."
chown -R $APP_USER:$APP_USER "$APP_DIR"
chmod -R 755 "$APP_DIR"

# Ensure data directory is writable (for sessions)
chmod -R 775 "$APP_DIR/data"
print_success "Permissions set"

# ============================================================================
# Step 11: Configure Nginx
# ============================================================================

print_header "Step 11/13: Configuring Nginx"

print_step "Creating Nginx configuration..."

cat > /etc/nginx/sites-available/activepieces-assistant << EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Frontend
    location / {
        proxy_pass http://localhost:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
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

    # Direct backend endpoints
    location ~ ^/(health|stats|chat|sessions|reset) {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        
        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS, DELETE' always;
        add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range' always;
        
        if (\$request_method = 'OPTIONS') {
            return 204;
        }
    }

    client_max_body_size 10M;
}
EOF

# Remove default site and enable ours
rm -f /etc/nginx/sites-enabled/default
ln -sf /etc/nginx/sites-available/activepieces-assistant /etc/nginx/sites-enabled/

# Test configuration
print_step "Testing Nginx configuration..."
nginx -t

if [ $? -eq 0 ]; then
    print_success "Nginx configuration is valid"
systemctl restart nginx
systemctl enable nginx
    print_success "Nginx configured and started"
else
    print_error "Nginx configuration test failed"
    exit 1
fi

# ============================================================================
# Step 12: Configure Firewall
# ============================================================================

print_header "Step 12/13: Configuring Firewall"

print_step "Setting up UFW firewall..."
ufw --force enable
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp

print_success "Firewall configured"
ufw status

# ============================================================================
# Step 13: Start Services
# ============================================================================

print_header "Step 13/13: Starting Services"

# Reload systemd
systemctl daemon-reload

# Enable services
systemctl enable activepieces-backend
systemctl enable activepieces-frontend

# Start services
print_step "Starting backend service..."
systemctl start activepieces-backend
sleep 3

print_step "Starting frontend service..."
systemctl start activepieces-frontend
sleep 3

# Check status
if systemctl is-active --quiet activepieces-backend; then
    print_success "Backend service is running"
else
    print_error "Backend service failed to start"
    echo ""
    echo "Last 20 log lines:"
    journalctl -u activepieces-backend -n 20 --no-pager
    exit 1
fi

if systemctl is-active --quiet activepieces-frontend; then
    print_success "Frontend service is running"
else
    print_error "Frontend service failed to start"
    echo ""
    echo "Last 20 log lines:"
    journalctl -u activepieces-frontend -n 20 --no-pager
    exit 1
fi

# ============================================================================
# Verify Deployment
# ============================================================================

print_step "Testing backend health endpoint..."
sleep 3
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)

if [ "$HTTP_CODE" = "200" ]; then
    print_success "Backend health check passed (HTTP $HTTP_CODE)"
else
    print_warning "Backend health check returned HTTP $HTTP_CODE"
    echo "Checking backend logs..."
    journalctl -u activepieces-backend -n 10 --no-pager
fi

# ============================================================================
# SSL Setup (Optional)
# ============================================================================

print_header "SSL Certificate Setup (Optional)"

echo -e "${CYAN}Would you like to setup SSL with Let's Encrypt?${NC}"
echo "  - Requires: Valid domain name pointing to this server"
echo "  - Provides: Free HTTPS certificate"
echo ""
read -p "Setup SSL now? (y/n) " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_step "Obtaining SSL certificate..."
    certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --register-unsafely-without-email || certbot --nginx -d $DOMAIN --non-interactive --agree-tos --register-unsafely-without-email
    
    if [ $? -eq 0 ]; then
        print_success "SSL certificate installed successfully!"
        print_success "Auto-renewal is configured"
        
        # Update frontend .env.production to use HTTPS
        cat > $APP_DIR/frontend/.env.production << EOF
VITE_API_URL=https://$DOMAIN
EOF
        
        # Rebuild frontend
        cd $APP_DIR/frontend
        npm run build
        systemctl restart activepieces-frontend
        cd $APP_DIR
        
        print_success "Frontend updated to use HTTPS"
    else
        print_warning "SSL setup failed or was cancelled"
        print_warning "You can run this manually later: sudo certbot --nginx -d $DOMAIN"
    fi
else
    print_warning "SSL setup skipped"
fi

# ============================================================================
# Deployment Summary
# ============================================================================

clear
print_header "🎉 Deployment Complete!"

echo -e "${GREEN}✓ Your AI Assistant is now running!${NC}"
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}📍 Access Your Application:${NC}"

if systemctl is-active --quiet nginx && [ -d "/etc/letsencrypt/live/$DOMAIN" ] 2>/dev/null; then
    echo -e "   ${GREEN}https://$DOMAIN${NC}"
    echo -e "   ${GREEN}https://www.$DOMAIN${NC}"
else
    echo -e "   ${GREEN}http://$DOMAIN${NC}"
    if [ "$DOMAIN" != "localhost" ] && [[ ! "$DOMAIN" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        echo -e "   ${GREEN}http://www.$DOMAIN${NC}"
    fi
fi

echo ""
echo -e "${BLUE}🔧 Service Management:${NC}"
echo -e "   View backend logs:  ${YELLOW}journalctl -u activepieces-backend -f${NC}"
echo -e "   View frontend logs: ${YELLOW}journalctl -u activepieces-frontend -f${NC}"
echo -e "   Restart backend:    ${YELLOW}systemctl restart activepieces-backend${NC}"
echo -e "   Restart frontend:   ${YELLOW}systemctl restart activepieces-frontend${NC}"
echo -e "   Check status:       ${YELLOW}systemctl status activepieces-backend${NC}"
echo ""
echo -e "${BLUE}📊 Useful Endpoints:${NC}"
echo -e "   Health Check:  ${GREEN}http://$DOMAIN/health${NC}"
echo -e "   Stats:         ${GREEN}http://$DOMAIN/stats${NC}"
echo ""
echo -e "${BLUE}📂 Important Paths:${NC}"
echo -e "   Application:   ${YELLOW}$APP_DIR${NC}"
echo -e "   Database:      ${YELLOW}$APP_DIR/data/activepieces.db${NC}"
echo -e "   Vector Store:  ${YELLOW}$APP_DIR/data/ap_faiss_index/${NC}"
echo -e "   Environment:   ${YELLOW}$APP_DIR/.env${NC}"
echo ""
echo -e "${BLUE}🔐 Security Reminders:${NC}"
echo "   ✓ Firewall is enabled (UFW)"
echo "   ✓ Change default SSH port (optional but recommended)"
echo "   ✓ Setup regular backups of data/ directory"
echo "   ✓ Monitor logs regularly"
echo "   ✓ Keep system updated: apt update && apt upgrade"
echo ""
echo -e "${BLUE}🔄 Update Application:${NC}"
echo -e "   ${YELLOW}cd $APP_DIR${NC}"
echo -e "   ${YELLOW}git pull origin main${NC}"
echo -e "   ${YELLOW}source venv/bin/activate${NC}"
echo -e "   ${YELLOW}pip install -r requirements.txt${NC}"
echo -e "   ${YELLOW}cd frontend && npm install && npm run build && cd ..${NC}"
echo -e "   ${YELLOW}sudo systemctl restart activepieces-backend activepieces-frontend${NC}"
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${GREEN}Happy Deploying! 🚀${NC}"
echo ""
