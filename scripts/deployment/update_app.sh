#!/bin/bash

# ============================================================================
# ActivePieces AI Assistant - Update Script
# ============================================================================
# This script updates the application after code changes
# Usage: sudo ./update_app.sh
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

# ============================================================================
# Main Update Process
# ============================================================================

print_header "ActivePieces AI Assistant - Update Script"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    print_error "Please run as root or with sudo"
    exit 1
fi

APP_DIR="/opt/activepieces-assistant/Flow_Assistant"

# Check if directory exists
if [ ! -d "$APP_DIR" ]; then
    print_error "Application directory not found: $APP_DIR"
    exit 1
fi

cd "$APP_DIR"

# ============================================================================
print_header "Step 1: Pulling Latest Changes from Git"

if [ -d ".git" ]; then
    print_warning "Pulling from Git..."
    git pull origin main || git pull origin master || print_warning "Git pull failed or not needed"
    print_success "Git pull completed"
else
    print_warning "Not a git repository, skipping git pull"
fi

# ============================================================================
print_header "Step 2: Updating Backend"

if [ -f "requirements.txt" ]; then
    print_warning "Installing Python dependencies..."
    source venv/bin/activate
    pip install -r requirements.txt --quiet
    print_success "Python dependencies updated"
else
    print_warning "requirements.txt not found, skipping"
fi

print_warning "Restarting backend service..."
systemctl restart activepieces-backend
sleep 3
print_success "Backend service restarted"

# ============================================================================
print_header "Step 3: Updating Frontend"

if [ -d "frontend" ]; then
    cd frontend
    
    if [ -f "package.json" ]; then
        print_warning "Installing frontend dependencies..."
        npm install --silent
        print_success "Frontend dependencies updated"
        
        print_warning "Building frontend..."
        npm run build
        print_success "Frontend built successfully"
    else
        print_warning "package.json not found, skipping"
    fi
    
    cd ..
    
    print_warning "Restarting frontend service..."
    systemctl restart activepieces-frontend
    sleep 3
    print_success "Frontend service restarted"
else
    print_warning "Frontend directory not found, skipping"
fi

# ============================================================================
print_header "Step 4: Restarting Nginx"

systemctl restart nginx
print_success "Nginx restarted"

# ============================================================================
print_header "Step 5: Checking Service Status"

echo ""
echo -e "${BLUE}Backend Status:${NC}"
systemctl status activepieces-backend --no-pager | head -15

echo ""
echo -e "${BLUE}Frontend Status:${NC}"
systemctl status activepieces-frontend --no-pager | head -15

echo ""
echo -e "${BLUE}Nginx Status:${NC}"
systemctl status nginx --no-pager | head -15

# ============================================================================
print_header "Step 6: Testing Application"

echo ""
print_warning "Testing backend health..."
if curl -s http://127.0.0.1:8000/health | grep -q "healthy"; then
    print_success "Backend is responding correctly"
else
    print_error "Backend health check failed"
fi

echo ""
print_warning "Testing through Nginx..."
if curl -s http://127.0.0.1/health | grep -q "healthy"; then
    print_success "Nginx proxy is working correctly"
else
    print_error "Nginx proxy check failed"
fi

# ============================================================================
print_header "Update Complete!"

echo ""
print_success "Application has been updated successfully!"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo "1. Check the service statuses above"
echo "2. View backend logs: ${YELLOW}sudo journalctl -u activepieces-backend -f${NC}"
echo "3. View frontend logs: ${YELLOW}sudo journalctl -u activepieces-frontend -f${NC}"
echo "4. Test in browser: ${YELLOW}http://104.131.82.1${NC}"
echo ""
echo -e "${BLUE}If there are any errors:${NC}"
echo "  Backend logs: ${YELLOW}sudo journalctl -u activepieces-backend -n 100${NC}"
echo "  Frontend logs: ${YELLOW}sudo journalctl -u activepieces-frontend -n 100${NC}"
echo ""

print_header "Done!"

