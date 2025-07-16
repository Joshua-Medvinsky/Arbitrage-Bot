# Cross-Platform Development Starter for Arbitrage Bot
# This PowerShell script works on Windows, macOS, and Linux (with PowerShell Core)

Write-Host "🚀 Starting Arbitrage Bot Development Environment..." -ForegroundColor Green

# Check if we're in the right directory
if (-not (Test-Path "socketio_server.py")) {
    Write-Host "❌ socketio_server.py not found. Please run from the project root." -ForegroundColor Red
    exit 1
}

# Check if Python virtual environment exists
if (-not (Test-Path ".venv")) {
    Write-Host "❌ Virtual environment (.venv) not found. Please set up your Python environment first." -ForegroundColor Red
    exit 1
}

# Check if frontend directory exists
if (-not (Test-Path "frontend")) {
    Write-Host "❌ Frontend directory not found." -ForegroundColor Red
    exit 1
}

Write-Host "✅ All prerequisites found. Starting services..." -ForegroundColor Green

# Determine the correct Python executable path based on OS
if ($IsWindows -or $env:OS -eq "Windows_NT") {
    $pythonPath = ".\.venv\Scripts\python.exe"
} else {
    # macOS and Linux
    $pythonPath = "./.venv/bin/python"
}

Write-Host "🐍 Starting Python backend server..." -ForegroundColor Cyan
Write-Host "   Using Python: $pythonPath" -ForegroundColor Gray

# Start the backend server in a new process
$backendProcess = Start-Process -FilePath "pwsh" -ArgumentList "-Command", "$pythonPath socketio_server.py" -PassThru -WindowStyle Normal

# Give backend time to start
Write-Host "⏳ Waiting for backend to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

Write-Host "🌐 Starting React frontend..." -ForegroundColor Cyan
Set-Location "frontend"

try {
    # Check if node_modules exists, install if not
    if (-not (Test-Path "node_modules")) {
        Write-Host "📦 Installing frontend dependencies..." -ForegroundColor Yellow
        npm install
    }
    
    # Start the frontend
    npm run dev
} finally {
    # Cleanup: Stop the backend process when frontend exits
    Write-Host "`n🧹 Cleaning up..." -ForegroundColor Yellow
    if ($backendProcess -and !$backendProcess.HasExited) {
        Write-Host "🛑 Stopping backend server..." -ForegroundColor Red
        Stop-Process -Id $backendProcess.Id -Force -ErrorAction SilentlyContinue
    }
    Write-Host "✅ Cleanup complete. Development session ended." -ForegroundColor Green
}
