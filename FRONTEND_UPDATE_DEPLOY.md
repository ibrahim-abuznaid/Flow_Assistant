# 🚀 Deploy Frontend Updates to Cloud

This guide shows how to deploy your updated frontend (with long message fixes) to your DigitalOcean server.

---

## 📋 Prerequisites

Before starting, make sure you have:
- ✅ SSH access to your cloud server
- ✅ The frontend changes committed to your Git repository (or files ready to upload)
- ✅ Your server IP or domain name

---

## 🔄 Method 1: Deploy via Git (Recommended)

This is the cleanest method if your code is in a Git repository.

### Step 1: Commit and Push Your Changes

On your **local machine**:

```bash
# Make sure you're in the project root
cd "C:\AP work\Flow_Assistant"

# Stage the frontend changes
git add frontend/src/App.jsx
git add frontend/src/App.css

# Commit the changes
git commit -m "Fix long message display and improve UI"

# Push to your repository
git push origin main
```

### Step 2: SSH into Your Server

```bash
ssh your-user@your-server-ip
# Example: ssh deploy@123.45.67.89
```

### Step 3: Update the Code on Server

```bash
# Navigate to your project directory
cd /var/www/Flow_Assistant
# Or: cd /opt/activepieces-assistant

# Pull the latest changes
git pull origin main

# Navigate to frontend directory
cd frontend
```

### Step 4: Rebuild the Frontend

```bash
# Install any new dependencies (if any)
npm install

# Rebuild for production
npm run build
```

### Step 5: Restart the Frontend Service

```bash
# Restart the frontend service
sudo systemctl restart activepieces-frontend

# Or if using a different service name:
# sudo systemctl restart flow-assistant-frontend

# Check status
sudo systemctl status activepieces-frontend
```

### Step 6: Verify Changes

Visit your website and test:
- Long responses should now display properly
- Check the new expand/collapse button for messages > 3000 characters
- Verify the improved styling and shadows

---

## 📁 Method 2: Direct File Upload (If Not Using Git)

If you don't have Git set up, you can manually upload the files.

### Step 1: Upload Files via SCP

On your **local machine** (PowerShell):

```powershell
# Upload App.jsx
scp "C:\AP work\Flow_Assistant\frontend\src\App.jsx" your-user@your-server-ip:/var/www/Flow_Assistant/frontend/src/

# Upload App.css
scp "C:\AP work\Flow_Assistant\frontend\src\App.css" your-user@your-server-ip:/var/www/Flow_Assistant/frontend/src/
```

### Step 2: SSH and Rebuild

```bash
# SSH into server
ssh your-user@your-server-ip

# Navigate to frontend directory
cd /var/www/Flow_Assistant/frontend

# Rebuild
npm run build

# Restart service
sudo systemctl restart activepieces-frontend
```

---

## 🔍 Method 3: Using Nginx to Serve Static Files (Alternative)

If you're serving the frontend directly with Nginx instead of the Node service:

### Step 1-2: Same as Method 1 (pull code or upload files)

### Step 3: Rebuild Frontend

```bash
cd /var/www/Flow_Assistant/frontend
npm run build
```

### Step 4: Copy Built Files to Nginx Directory

```bash
# Copy the built files to Nginx web root
sudo cp -r dist/* /var/www/html/

# Or if using a specific directory:
# sudo cp -r dist/* /var/www/Flow_Assistant/frontend/dist/

# Set proper permissions
sudo chown -R www-data:www-data /var/www/html/
```

### Step 5: Reload Nginx

```bash
# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

---

## 🛠️ Quick Update Script

Create this script on your server for easy future updates:

```bash
# Create the script
sudo nano /usr/local/bin/update-frontend.sh
```

Add this content:

```bash
#!/bin/bash

echo "🔄 Updating Frontend..."

# Navigate to project
cd /var/www/Flow_Assistant

# Pull latest code
echo "📥 Pulling latest changes..."
git pull origin main

# Navigate to frontend
cd frontend

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Build frontend
echo "🏗️  Building frontend..."
npm run build

# Restart service
echo "🔄 Restarting frontend service..."
sudo systemctl restart activepieces-frontend

# Check status
echo "✅ Checking status..."
sudo systemctl status activepieces-frontend --no-pager

echo "✨ Frontend update complete!"
```

Make it executable:

```bash
sudo chmod +x /usr/local/bin/update-frontend.sh
```

**Usage**:
```bash
sudo /usr/local/bin/update-frontend.sh
```

---

## 🐛 Troubleshooting

### Frontend Not Updating?

1. **Clear Browser Cache**
   - Hard refresh: `Ctrl + Shift + R` (Windows) or `Cmd + Shift + R` (Mac)
   - Or open DevTools (F12) and right-click the refresh button → "Empty Cache and Hard Reload"

2. **Check Service Status**
   ```bash
   sudo systemctl status activepieces-frontend
   
   # View logs
   sudo journalctl -u activepieces-frontend -n 50
   ```

3. **Verify Build Output**
   ```bash
   ls -la /var/www/Flow_Assistant/frontend/dist/
   
   # Should see files like index.html, assets/, etc.
   ```

4. **Check Nginx Configuration**
   ```bash
   sudo nginx -t
   sudo systemctl reload nginx
   ```

5. **Verify File Permissions**
   ```bash
   sudo chown -R www-data:www-data /var/www/Flow_Assistant/frontend/dist/
   sudo chmod -R 755 /var/www/Flow_Assistant/frontend/dist/
   ```

### Service Won't Restart?

```bash
# Stop the service
sudo systemctl stop activepieces-frontend

# Kill any remaining processes
sudo pkill -f "serve -s dist"

# Start service again
sudo systemctl start activepieces-frontend

# Check status
sudo systemctl status activepieces-frontend
```

### Still Not Working?

```bash
# Check if port 5173 is in use
sudo netstat -tulpn | grep 5173

# Check Nginx logs
sudo tail -f /var/log/nginx/error.log

# Check system logs
sudo journalctl -xe
```

---

## 🎯 Quick Command Reference

```bash
# Pull latest code
cd /var/www/Flow_Assistant && git pull

# Rebuild frontend
cd frontend && npm run build

# Restart service
sudo systemctl restart activepieces-frontend

# Check status
sudo systemctl status activepieces-frontend

# View logs
sudo journalctl -u activepieces-frontend -f

# Hard restart (if needed)
sudo systemctl stop activepieces-frontend && sudo systemctl start activepieces-frontend
```

---

## ✅ Verification Checklist

After deployment, verify:

- [ ] Website loads without errors
- [ ] Long AI responses display correctly
- [ ] "Show More" / "Show Less" button appears for long messages
- [ ] Code blocks are scrollable and properly formatted
- [ ] Links break properly without overflowing
- [ ] Mobile responsive design works
- [ ] No console errors in browser DevTools (F12)
- [ ] All existing features still work

---

## 📝 Notes

- **Build Time**: The `npm run build` command typically takes 10-30 seconds
- **Zero Downtime**: The restart is very quick (< 2 seconds)
- **Cache**: Users may need to hard refresh to see changes immediately
- **Rollback**: If something goes wrong, run `git checkout HEAD~1` to revert

---

## 🚀 One-Line Deploy Command

For quick updates (after first setup):

```bash
cd /var/www/Flow_Assistant && git pull && cd frontend && npm run build && sudo systemctl restart activepieces-frontend && echo "✅ Deploy complete!"
```

---

**Need Help?** Check the logs:
```bash
sudo journalctl -u activepieces-frontend -f
```

