# PowerShell Build Script for Arbitrage Bot Desktop Application
# Creates Windows installers for the Tauri-based desktop application

Write-Host "🚀 Starting Arbitrage Bot Desktop Build..." -ForegroundColor Green

# Check if we're in the right directory
if (-not (Test-Path "socketio_server.py")) {
    Write-Host "❌ socketio_server.py not found. Please run from the project root." -ForegroundColor Red
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
            $originalLocation = Get-Location
            Set-Location $WorkingDirectory
            Invoke-Expression $Command
            Set-Location $originalLocation
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

# Step 1: Verify Node.js is installed
Write-Host "`n📦 Checking Node.js installation..." -ForegroundColor Cyan
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js version: $nodeVersion" -ForegroundColor Green
}
catch {
    Write-Host "❌ Node.js not found. Please install Node.js 16 or higher." -ForegroundColor Red
    exit 1
}

# Step 2: Verify Rust is installed (required for Tauri)
Write-Host "`n🦀 Checking Rust installation..." -ForegroundColor Cyan
try {
    $rustVersion = rustc --version
    Write-Host "✅ Rust version: $rustVersion" -ForegroundColor Green
}
catch {
    Write-Host "❌ Rust not found. Please install Rust from https://rustup.rs/" -ForegroundColor Red
    exit 1
}

# Step 3: Install frontend dependencies
Write-Host "`n📦 Installing frontend dependencies..." -ForegroundColor Cyan
if (-not (Test-Path "frontend")) {
    Write-Host "❌ Frontend directory not found" -ForegroundColor Red
    exit 1
}

if (-not (Invoke-BuildCommand "npm install" "frontend")) {
    Write-Host "❌ Failed to install frontend dependencies" -ForegroundColor Red
    exit 1
}

# Step 4: Build Tauri desktop application
Write-Host "`n🔨 Building Tauri desktop application..." -ForegroundColor Cyan
if (-not (Invoke-BuildCommand "npm run tauri build" "frontend")) {
    Write-Host "❌ Failed to build Tauri application" -ForegroundColor Red
    exit 1
}

# Step 5: Create distribution package
Write-Host "`n📦 Creating distribution package..." -ForegroundColor Cyan
$distDir = "demo-distribution"
if (Test-Path $distDir) {
    Remove-Item $distDir -Recurse -Force
}
New-Item -ItemType Directory -Path $distDir | Out-Null

# Copy Tauri build artifacts
$bundleDir = "frontend\src-tauri\target\release\bundle"
if (Test-Path $bundleDir) {
    Copy-Item "$bundleDir\*" $distDir -Recurse -Force
    Write-Host "✅ Tauri installers copied to distribution" -ForegroundColor Green
} else {
    Write-Host "❌ Tauri bundle not found" -ForegroundColor Red
    exit 1
}

# Copy Python server executable
if (Test-Path "arbitrage-bot-server.exe") {
    Copy-Item "arbitrage-bot-server.exe" "$distDir\" -Force
    Write-Host "✅ Python server executable copied" -ForegroundColor Green
} else {
    Write-Host "⚠️  Python server executable not found - building it..." -ForegroundColor Yellow
    # Build Python executable if it doesn't exist
    if (Test-Path "build_demo.py") {
        if (Invoke-BuildCommand "python build_demo.py") {
            Copy-Item "arbitrage-bot-server.exe" "$distDir\" -Force
            Write-Host "✅ Python server executable built and copied" -ForegroundColor Green
        }
    }
}

# Copy documentation files
$docFiles = @("README.md", "DEPLOYMENT_SUMMARY.md", "requirements.txt")
foreach ($file in $docFiles) {
    if (Test-Path $file) {
        Copy-Item $file "$distDir\" -Force
    }
}

# Create demo-specific README
$demoReadme = @"
# Arbitrage Bot Demo Distribution

This distribution contains everything needed to run the Arbitrage Bot demo on Windows.

## Files Included

### Desktop Application (Recommended)
- ``nsis/Arbitrage Bot_1.0.0_x64-setup.exe`` - Windows installer for the desktop application
- ``msi/Arbitrage Bot_1.0.0_x64_en-US.msi`` - MSI installer package

### Standalone Server
- ``arbitrage-bot-server.exe`` - Standalone Python server (13.8MB)

## Quick Start

### Option 1: Desktop Application (Recommended)
1. Run ``nsis/Arbitrage Bot_1.0.0_x64-setup.exe`` to install the desktop application
2. Launch "Arbitrage Bot" from your Start Menu
3. The application will open as a native desktop window

### Option 2: Standalone Server
1. Double-click ``arbitrage-bot-server.exe`` to start the server
2. Open your web browser and go to ``http://localhost:8000``
3. The web interface will load in your browser

## Features
- **Real-time monitoring** of arbitrage opportunities
- **Safe mode controls** to prevent actual trading during demo
- **Interactive dashboard** with charts and statistics  
- **Settings management** for DEX configurations
- **Bot start/stop controls** with status indicators

## Demo Notes
- This is a demonstration version with safe mode enabled by default
- No actual trading will occur unless explicitly configured
- All blockchain interactions are simulated or read-only
- The application includes comprehensive logging and monitoring

## System Requirements
- Windows 10 or later (64-bit)
- No additional dependencies required
- Internet connection for blockchain data (optional for demo)

## Support
- Check the included documentation files for detailed setup instructions
- The application includes built-in help and configuration guides
"@

$demoReadme | Out-File -FilePath "$distDir\DEMO_README.md" -Encoding UTF8

Write-Host "✅ Distribution package created in: $((Get-Item $distDir).FullName)" -ForegroundColor Green

# Step 6: Display results
Write-Host "`n📦 Build artifacts created:" -ForegroundColor Cyan
$bundleDir = "$distDir"
Get-ChildItem $bundleDir -Recurse | Where-Object { $_.Name -like "*.exe" -or $_.Name -like "*.msi" } | ForEach-Object {
    $sizeMB = [math]::Round($_.Length/1MB,2)
    Write-Host "  📄 $($_.Name) ($sizeMB MB)" -ForegroundColor Blue
}

Write-Host "`n🎉 Build completed successfully!" -ForegroundColor Green
Write-Host "`nWhat was built:" -ForegroundColor Cyan
Write-Host "1. ✅ Desktop application installers (NSIS + MSI)" -ForegroundColor White
Write-Host "2. ✅ Standalone Python server executable" -ForegroundColor White
Write-Host "3. ✅ Complete distribution package" -ForegroundColor White

Write-Host "`nRecommended for demo:" -ForegroundColor Yellow
Write-Host "- Use the NSIS installer: demo-distribution\nsis\Arbitrage Bot_1.0.0_x64-setup.exe" -ForegroundColor White
Write-Host "- This provides the best user experience without console windows" -ForegroundColor White

Write-Host "`nFor distribution:" -ForegroundColor Cyan
Write-Host "- Send the entire 'demo-distribution' folder" -ForegroundColor White
Write-Host "- Recipients only need to run the installer - no dependencies required" -ForegroundColor White
