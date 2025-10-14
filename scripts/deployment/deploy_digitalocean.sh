#!/bin/bash

# ============================================================================
# ActivePieces AI Assistant - Complete DigitalOcean Deployment Script
# ============================================================================
# This script automates the complete deployment process on Ubuntu 22.04/24.04
# Includes: Backend, Frontend, Database, Vector Store, Nginx, SSL, and more
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
APP_DIR="/opt/activepieces-assistant"
APP_USER="www-data"

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

# ============================================================================
# Main Deployment Script
# ============================================================================

clear
print_header "ActivePieces AI Assistant - DigitalOcean Deployment"

# Check if running as root
check_root

# Get the actual user who called sudo (if applicable)
ACTUAL_USER=${SUDO_USER:-$USER}

echo -e "${CYAN}This script will:${NC}"
echo "  ✓ Install all system dependencies"
echo "  ✓ Setup Python backend with FastAPI"
echo "  ✓ Setup React frontend"
echo "  ✓ Configure SQLite database (included)"
echo "  ✓ Create FAISS vector store for RAG"
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
# Step 1: System Update
# ============================================================================

print_header "Step 1/14: System Update"
print_step "Updating system packages..."
apt update && apt upgrade -y
print_success "System updated successfully"

# ============================================================================
# Step 2: Install System Dependencies
# ============================================================================

print_header "Step 2/14: Installing System Dependencies"
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
    htop

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
# Step 3: Clone Repository
# ============================================================================

print_header "Step 3/14: Cloning Repository"

if [ -d "$APP_DIR" ]; then
    print_warning "Application directory already exists at $APP_DIR"
    read -p "Remove and re-clone? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$APP_DIR"
    else
        cd "$APP_DIR"
        print_step "Using existing directory, pulling latest changes..."
        git pull origin main || true
    fi
fi

if [ ! -d "$APP_DIR" ]; then
    print_step "Enter your GitHub repository URL:"
    read REPO_URL
    
    mkdir -p "$APP_DIR"
    git clone "$REPO_URL" "$APP_DIR"
    print_success "Repository cloned successfully"
fi

cd "$APP_DIR"

# ============================================================================
# Step 4: Setup Python Backend
# ============================================================================

print_header "Step 4/14: Setting Up Python Backend"

# Create virtual environment
if [ ! -d "venv" ]; then
    print_step "Creating Python virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# Activate and install dependencies
print_step "Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
print_success "Python dependencies installed"

# ============================================================================
# Step 5: Configure Environment Variables
# ============================================================================

print_header "Step 5/14: Configuring Environment Variables"

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
    read -p "Choose (1 or 2): " SEARCH_CHOICE
    
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
# Step 6: Verify Database
# ============================================================================

print_header "Step 6/14: Verifying Database"

if [ -f "data/activepieces.db" ]; then
    print_step "Testing database connection..."
    source venv/bin/activate
    python src/db_config.py
    print_success "Database verified"
else
    print_error "Database file not found at data/activepieces.db"
    print_warning "Make sure it's included in your repository"
fi

# ============================================================================
# Step 7: Prepare Vector Store
# ============================================================================

print_header "Step 7/14: Preparing Vector Store (FAISS)"

if [ ! -d "data/ap_faiss_index" ]; then
    print_step "Creating FAISS vector index..."
    source venv/bin/activate
    
    # Check if knowledge base exists
    if [ -f "data/pieces_knowledge_base.json" ]; then
        python scripts/migration/prepare_knowledge_base.py
        print_success "Vector store created successfully"
    else
        print_warning "Knowledge base JSON not found, vector store creation skipped"
        print_warning "RAG features may not work properly"
    fi
else
    print_success "Vector store already exists"
fi

# ============================================================================
# Step 8: Build Frontend
# ============================================================================

print_header "Step 8/14: Building Frontend"

cd frontend

# Install dependencies
print_step "Installing frontend dependencies..."
npm install
print_success "Frontend dependencies installed"

# Get domain/IP for frontend config
print_step "Configure frontend API URL"
read -p "Enter your domain or IP (e.g., example.com or 123.45.67.89): " DOMAIN

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
# Step 9: Create Systemd Services
# ============================================================================

print_header "Step 9/14: Creating Systemd Services"

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
print_success "Permissions set"

# ============================================================================
# Step 10: Configure Nginx
# ============================================================================

print_header "Step 10/14: Configuring Nginx"

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
# Step 11: Configure Firewall
# ============================================================================

print_header "Step 11/14: Configuring Firewall"

print_step "Setting up UFW firewall..."
ufw --force enable
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp

print_success "Firewall configured"
ufw status

# ============================================================================
# Step 12: Start Services
# ============================================================================

print_header "Step 12/14: Starting Services"

# Reload systemd
systemctl daemon-reload

# Enable services
systemctl enable activepieces-backend
systemctl enable activepieces-frontend

# Start services
print_step "Starting backend service..."
systemctl start activepieces-backend
sleep 2

print_step "Starting frontend service..."
systemctl start activepieces-frontend
sleep 2

# Check status
if systemctl is-active --quiet activepieces-backend; then
    print_success "Backend service is running"
else
    print_error "Backend service failed to start"
    journalctl -u activepieces-backend -n 20
fi

if systemctl is-active --quiet activepieces-frontend; then
    print_success "Frontend service is running"
else
    print_error "Frontend service failed to start"
    journalctl -u activepieces-frontend -n 20
fi

# ============================================================================
# Step 13: Verify Deployment
# ============================================================================

print_header "Step 13/14: Verifying Deployment"

print_step "Testing backend health..."
sleep 3
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)

if [ "$HTTP_CODE" = "200" ]; then
    print_success "Backend health check passed (HTTP $HTTP_CODE)"
else
    print_warning "Backend health check returned HTTP $HTTP_CODE"
fi

# ============================================================================
# Step 14: SSL Setup (Optional)
# ============================================================================

print_header "Step 14/14: SSL Certificate Setup (Optional)"

echo -e "${CYAN}Would you like to setup SSL with Let's Encrypt?${NC}"
echo "  - Requires: Valid domain name pointing to this server"
echo "  - Provides: Free HTTPS certificate"
echo ""
read -p "Setup SSL now? (y/n) " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_step "Installing Certbot..."
    apt install -y certbot python3-certbot-nginx
    
    print_step "Obtaining SSL certificate..."
    certbot --nginx -d $DOMAIN -d www.$DOMAIN
    
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
        cd ..
    else
        print_warning "SSL setup failed or was cancelled"
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
else
    echo -e "   ${GREEN}http://$DOMAIN${NC}"
fi

echo ""
echo -e "${BLUE}🔧 Service Management:${NC}"
echo -e "   View backend logs:  ${YELLOW}journalctl -u activepieces-backend -f${NC}"
echo -e "   View frontend logs: ${YELLOW}journalctl -u activepieces-frontend -f${NC}"
echo -e "   Restart backend:    ${YELLOW}systemctl restart activepieces-backend${NC}"
echo -e "   Check status:       ${YELLOW}systemctl status activepieces-backend${NC}"
echo ""
echo -e "${BLUE}📊 Useful Endpoints:${NC}"
echo -e "   Health Check:  ${GREEN}http://$DOMAIN/health${NC}"
echo -e "   Stats:         ${GREEN}http://$DOMAIN/stats${NC}"
echo ""
echo -e "${BLUE}📚 Documentation:${NC}"
echo -e "   Full Guide:    ${YELLOW}$APP_DIR/DEPLOYMENT_GUIDE.md${NC}"
echo -e "   README:        ${YELLOW}$APP_DIR/README.md${NC}"
echo ""
echo -e "${BLUE}🔐 Security Reminders:${NC}"
echo "   ✓ Firewall is enabled (UFW)"
echo "   ✓ Change default SSH port (optional)"
echo "   ✓ Setup regular backups"
echo "   ✓ Monitor logs regularly"
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${GREEN}Happy Deploying! 🚀${NC}"
echo ""

