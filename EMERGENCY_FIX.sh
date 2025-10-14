#!/bin/bash

# Emergency fix for wrong deployment script
# Run this on your droplet to fix the issues

set -e

echo "================================"
echo "Emergency Fix Script"
echo "================================"
echo ""

# Stop failing services
echo "→ Stopping failing services..."
systemctl stop activepieces-backend || true
systemctl stop activepieces-frontend || true
systemctl disable activepieces-backend || true
systemctl disable activepieces-frontend || true

# Clean up wrong deployment
echo "→ Cleaning up incorrect deployment..."
rm -rf /opt/activepieces-assistant

# Remove old services
rm -f /etc/systemd/system/activepieces-backend.service
rm -f /etc/systemd/system/activepieces-frontend.service
systemctl daemon-reload

echo "✓ Cleanup complete!"
echo ""
echo "Now run the CORRECT deployment script:"
echo ""
echo "  cd /opt/Flow_Assistant"
echo "  chmod +x scripts/deployment/deploy_ubuntu.sh"
echo "  sudo ./scripts/deployment/deploy_ubuntu.sh"
echo ""

