# PowerShell Build Script for Arbitrage Bot
# ⚠️  WARNING: This build script is OUTDATED and references old websocket_server.py
# ⚠️  It needs to be updated to use socketio_server.py before use
# ⚠️  TODO: Update all references from websocket_server.py to socketio_server.py
# This script builds a complete standalone Tauri application
# The result is a Windows installer that contains everything needed to run the bot

Write-Host "🚀 Starting Arbitrage Bot build process..." -ForegroundColor Green

# Check if we're in the right directory
if (-not (Test-Path "websocket_server.py")) {
    Write-Host "❌ websocket_server.py not found. Please run from the project root." -ForegroundColor Red
    exit 1
}

# Function to run commands with error checking
function Invoke-BuildCommand {
    param(
        [string]$Command,
        [string]$WorkingDirectory = $null
    )
    
    Write-Host "Running: $Command" -ForegroundColor Yellow
    if ($WorkingDirectory) {
        Write-Host "In directory: $WorkingDirectory" -ForegroundColor Gray
    }
    
    try {
        if ($WorkingDirectory) {
            Invoke-Expression "cd '$WorkingDirectory'; $Command"
        } else {
            Invoke-Expression $Command
        }
        Write-Host "✅ Success" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "❌ Error: $_" -ForegroundColor Red
        return $false
    }
}

# Step 1: Install PyInstaller if needed
Write-Host "`n🔨 Setting up PyInstaller..." -ForegroundColor Cyan
try {
    python -c "import PyInstaller" 2>$null
    Write-Host "✅ PyInstaller already installed" -ForegroundColor Green
}
catch {
    Write-Host "Installing PyInstaller..." -ForegroundColor Yellow
    if (-not (Invoke-BuildCommand "pip install pyinstaller")) {
        Write-Host "❌ Failed to install PyInstaller" -ForegroundColor Red
        exit 1
    }
}

# Step 2: Build Python executable
Write-Host "`n🔨 Building Python executable..." -ForegroundColor Cyan
if (-not (Invoke-BuildCommand "python complete_build.py")) {
    Write-Host "❌ Failed to build. Trying alternative method..." -ForegroundColor Yellow
    
    # Alternative: Use the build_executable.py script
    if (Test-Path "build_executable.py") {
        if (-not (Invoke-BuildCommand "python build_executable.py")) {
            Write-Host "❌ Failed to build Python executable" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "❌ No build script found" -ForegroundColor Red
        exit 1
    }
}

# Step 3: Build frontend
Write-Host "`n🔨 Building React frontend..." -ForegroundColor Cyan
if (Test-Path "frontend") {
    if (-not (Invoke-BuildCommand "npm install" "frontend")) {
        Write-Host "❌ Failed to install frontend dependencies" -ForegroundColor Red
        exit 1
    }
    
    if (-not (Invoke-BuildCommand "npm run build" "frontend")) {
        Write-Host "❌ Failed to build frontend" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "❌ Frontend directory not found" -ForegroundColor Red
    exit 1
}

# Step 4: Build Tauri application
Write-Host "`n🔨 Building Tauri application..." -ForegroundColor Cyan
if (-not (Invoke-BuildCommand "npm run tauri build" "frontend")) {
    Write-Host "❌ Failed to build Tauri application" -ForegroundColor Red
    exit 1
}

# Step 5: Check build artifacts
Write-Host "`n📦 Checking build artifacts..." -ForegroundColor Cyan
$bundleDir = "frontend\src-tauri\target\release\bundle"
if (Test-Path $bundleDir) {
    Write-Host "✅ Build artifacts found in: $bundleDir" -ForegroundColor Green
    Get-ChildItem $bundleDir -Recurse | Where-Object { $_.Name -like "*.exe" -or $_.Name -like "*.msi" } | ForEach-Object {
        Write-Host "  📄 $($_.FullName)" -ForegroundColor Blue
    }
} else {
    Write-Host "⚠️  Build artifacts not found in expected location" -ForegroundColor Yellow
}

Write-Host "`n🎉 Build completed successfully!" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Find your installer in the frontend\src-tauri\target\release\bundle directory" -ForegroundColor White
Write-Host "2. Test the application" -ForegroundColor White
Write-Host "3. Distribute the installer - users won't need Python or Node.js!" -ForegroundColor White
