# Troubleshooting Guide

## Frontend Service Error: 203/EXEC

**Error**: `Process: ExecStart=/usr/bin/serve (code=exited, status=203/EXEC)`

This means `serve` is not installed or not at the expected location.

### Solution:

```bash
# 1. Check if serve is installed
which serve

# 2. Install serve globally
sudo npm install -g serve

# 3. Find where serve is installed
which serve
# Usually: /usr/local/bin/serve or /usr/bin/serve

# 4. Update the service file with correct path
sudo nano /etc/systemd/system/activepieces-frontend.service

# 5. Change ExecStart line to use the correct path
# ExecStart=/usr/local/bin/serve -s dist -l 5173

# 6. Reload systemd and restart
sudo systemctl daemon-reload
sudo systemctl restart activepieces-frontend
sudo systemctl status activepieces-frontend
```

