# ============================================================================
# Frontend Update Deployment Script for Windows
# ============================================================================
# This PowerShell script automates deploying frontend changes to your server
# ============================================================================

param(
    [Parameter(Mandatory=$false)]
    [string]$ServerUser = "",
    
    [Parameter(Mandatory=$false)]
    [string]$ServerIP = "",
    
    [Parameter(Mandatory=$false)]
    [string]$ProjectPath = "/var/www/Flow_Assistant"
)

# Colors for output
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

function Write-Header($Message) {
    Write-Host ""
    Write-ColorOutput Cyan "============================================================================"
    Write-ColorOutput Cyan $Message
    Write-ColorOutput Cyan "============================================================================"
    Write-Host ""
}

function Write-Step($Message) {
    Write-ColorOutput Yellow "➜ $Message"
}

function Write-Success($Message) {
    Write-ColorOutput Green "✓ $Message"
}

function Write-Error($Message) {
    Write-ColorOutput Red "✗ $Message"
}

# ============================================================================
# Main Script
# ============================================================================

Clear-Host
Write-Header "Frontend Update Deployment"

# Get server details if not provided
if (-not $ServerUser) {
    $ServerUser = Read-Host "Enter your server username (e.g., deploy, root)"
}

if (-not $ServerIP) {
    $ServerIP = Read-Host "Enter your server IP or domain"
}

$ServerAddress = "$ServerUser@$ServerIP"

Write-Host ""
Write-ColorOutput Cyan "Configuration:"
Write-Host "  Server: $ServerAddress"
Write-Host "  Project Path: $ProjectPath"
Write-Host ""

$confirm = Read-Host "Proceed with deployment? (y/n)"
if ($confirm -ne 'y' -and $confirm -ne 'Y') {
    Write-Warning "Deployment cancelled"
    exit
}

# ============================================================================
# Step 1: Commit and Push Local Changes
# ============================================================================

Write-Header "Step 1: Committing and Pushing Changes"

Write-Step "Checking for uncommitted changes..."
$gitStatus = git status --porcelain

if ($gitStatus) {
    Write-Step "Found uncommitted changes. Committing..."
    
    git add frontend/src/App.jsx
    git add frontend/src/App.css
    
    $commitMessage = Read-Host "Enter commit message (or press Enter for default)"
    if (-not $commitMessage) {
        $commitMessage = "Update frontend: Fix long message display and improve UI"
    }
    
    git commit -m $commitMessage
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Changes committed"
    } else {
        Write-Error "Failed to commit changes"
        exit 1
    }
    
    Write-Step "Pushing to repository..."
    git push origin main
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Changes pushed to repository"
    } else {
        Write-Error "Failed to push changes"
        exit 1
    }
} else {
    Write-Success "No uncommitted changes found"
    
    Write-Step "Pushing any pending commits..."
    git push origin main
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Repository is up to date"
    }
}

# ============================================================================
# Step 2: Deploy to Server
# ============================================================================

Write-Header "Step 2: Deploying to Server"

Write-Step "Connecting to server and updating..."

# Create deployment command
$deployCommand = @"
cd $ProjectPath && \
echo '📥 Pulling latest changes...' && \
git pull origin main && \
echo '📦 Installing dependencies...' && \
cd frontend && \
npm install && \
echo '🏗️  Building frontend...' && \
npm run build && \
echo '🔄 Restarting service...' && \
sudo systemctl restart activepieces-frontend && \
echo '✅ Checking service status...' && \
sudo systemctl status activepieces-frontend --no-pager -l && \
echo '' && \
echo '✨ Deployment complete!'
"@

# Execute deployment
Write-Step "Running deployment commands on server..."
ssh $ServerAddress $deployCommand

if ($LASTEXITCODE -eq 0) {
    Write-Success "Deployment completed successfully!"
} else {
    Write-Error "Deployment failed. Check the error messages above."
    
    Write-Host ""
    Write-ColorOutput Yellow "Troubleshooting tips:"
    Write-Host "1. Check service logs: ssh $ServerAddress 'sudo journalctl -u activepieces-frontend -n 50'"
    Write-Host "2. Verify build output: ssh $ServerAddress 'ls -la $ProjectPath/frontend/dist/'"
    Write-Host "3. Check permissions: ssh $ServerAddress 'ls -la $ProjectPath/frontend/'"
    
    exit 1
}

# ============================================================================
# Step 3: Verification
# ============================================================================

Write-Header "Step 3: Verification"

Write-Step "Testing server connectivity..."

# Determine if using HTTP or HTTPS
if ($ServerIP -match "^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$") {
    $url = "http://$ServerIP/health"
} else {
    $url = "https://$ServerIP/health"
}

try {
    $response = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Success "Server is responding (HTTP $($response.StatusCode))"
    }
} catch {
    Write-Warning "Could not reach $url"
    Write-Host "Please verify manually by visiting your website"
}

# ============================================================================
# Deployment Summary
# ============================================================================

Write-Header "🎉 Deployment Complete!"

Write-ColorOutput Green "✓ Frontend has been updated on the server!"
Write-Host ""
Write-ColorOutput Cyan "Next Steps:"
Write-Host "  1. Visit your website: " -NoNewline
Write-ColorOutput Green "http://$ServerIP"
Write-Host "  2. Hard refresh your browser: Ctrl + Shift + R"
Write-Host "  3. Test long responses to verify the fix"
Write-Host ""
Write-ColorOutput Cyan "Verification Checklist:"
Write-Host "  □ Long messages display correctly"
Write-Host "  □ 'Show More' button appears for long content"
Write-Host "  □ Code blocks are scrollable"
Write-Host "  □ No layout breaking with long URLs"
Write-Host "  □ Mobile responsive design works"
Write-Host ""
Write-ColorOutput Yellow "View Logs:"
Write-Host "  ssh $ServerAddress 'sudo journalctl -u activepieces-frontend -f'"
Write-Host ""
Write-ColorOutput Green "Happy deploying! 🚀"
Write-Host ""

