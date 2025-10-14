#!/bin/bash

# Fix ActivePieces Services Script
# This script updates the systemd service files with correct paths

echo "=========================================="
echo "Fixing ActivePieces Services"
echo "=========================================="

# Update backend service
echo "Creating backend service file..."
sudo tee /etc/systemd/system/activepieces-backend.service > /dev/null << 'EOF'
[Unit]
Description=ActivePieces AI Assistant Backend
After=network.target postgresql.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/activepieces-assistant/Flow_Assistant
Environment="PATH=/opt/activepieces-assistant/Flow_Assistant/venv/bin"
ExecStart=/opt/activepieces-assistant/Flow_Assistant/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

echo "✓ Backend service file created"

# Update frontend service
echo "Creating frontend service file..."
sudo tee /etc/systemd/system/activepieces-frontend.service > /dev/null << 'EOF'
[Unit]
Description=ActivePieces AI Assistant Frontend
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/activepieces-assistant/Flow_Assistant/frontend
ExecStart=/usr/local/bin/serve -s dist -l 5173
Restart=always

[Install]
WantedBy=multi-user.target
EOF

echo "✓ Frontend service file created"

# Reload and restart
echo ""
echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

echo "Starting backend service..."
sudo systemctl start activepieces-backend

echo "Starting frontend service..."
sudo systemctl start activepieces-frontend

echo ""
echo "=========================================="
echo "Service Status"
echo "=========================================="

# Check status
echo ""
echo "Backend Status:"
sudo systemctl status activepieces-backend --no-pager

echo ""
echo "=========================================="
echo ""
echo "Frontend Status:"
sudo systemctl status activepieces-frontend --no-pager

echo ""
echo "=========================================="
echo "Testing Endpoints"
echo "=========================================="

sleep 2

echo ""
echo "Testing backend health:"
curl http://127.0.0.1:8000/health
echo ""

echo ""
echo "Testing through Nginx:"
curl http://104.131.82.1/health
echo ""

echo ""
echo "=========================================="
echo "Done!"
echo "=========================================="

