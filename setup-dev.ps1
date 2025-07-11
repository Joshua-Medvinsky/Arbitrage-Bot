#!/usr/bin/env pwsh
# Developer setup script for Arbitrage Bot

Write-Host "🚀 Setting up Arbitrage Bot development environment..." -ForegroundColor Green

# Check prerequisites
Write-Host "📋 Checking prerequisites..." -ForegroundColor Yellow

# Check Node.js
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found. Please install Node.js 16+" -ForegroundColor Red
    exit 1
}

# Check Python
try {
    $pythonVersion = python --version
    Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

# Check Rust
try {
    $rustVersion = rustc --version
    Write-Host "✅ Rust: $rustVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Rust not found. Please install Rust" -ForegroundColor Red
    exit 1
}

# Install Python dependencies
Write-Host "📦 Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Install frontend dependencies
Write-Host "📦 Installing frontend dependencies..." -ForegroundColor Yellow
Set-Location frontend
npm install

# Install Tauri CLI if not present
Write-Host "📦 Checking Tauri CLI..." -ForegroundColor Yellow
try {
    npx @tauri-apps/cli --version | Out-Null
    Write-Host "✅ Tauri CLI available" -ForegroundColor Green
} catch {
    Write-Host "📦 Installing Tauri CLI..." -ForegroundColor Yellow
    npm install -g @tauri-apps/cli
}

# Create .env file if it doesn't exist
if (!(Test-Path "../.env")) {
    Write-Host "📝 Creating .env file..." -ForegroundColor Yellow
    @"
# Arbitrage Bot Configuration
PRIVATE_KEY=your_private_key_here
RPC_URL=https://mainnet.base.org
MIN_PROFIT_THRESHOLD_USD=0.50
FLASH_LOAN_AMOUNT_USD=100000
DISABLE_DEX_CALLS=true
"@ | Out-File -FilePath "../.env" -Encoding UTF8
    Write-Host "✅ Created .env file. Please update with your values." -ForegroundColor Green
}

Write-Host "" -ForegroundColor White
Write-Host "🎉 Setup complete! To start development:" -ForegroundColor Green
Write-Host "   npm run tauri dev" -ForegroundColor Cyan
Write-Host "" -ForegroundColor White
Write-Host "📚 Other useful commands:" -ForegroundColor Yellow
Write-Host "   npm run dev          # Frontend only" -ForegroundColor Gray
Write-Host "   npm run tauri build  # Production build" -ForegroundColor Gray
Write-Host "   python websocket_server.py  # Backend only" -ForegroundColor Gray
