@echo off
REM Developer setup script for Arbitrage Bot (Windows Batch)

echo 🚀 Setting up Arbitrage Bot development environment...

REM Check prerequisites
echo 📋 Checking prerequisites...

REM Check Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js not found. Please install Node.js 16+
    echo    Download from: https://nodejs.org/
    pause
    exit /b 1
) else (
    for /f "tokens=*" %%i in ('node --version') do echo ✅ Node.js: %%i
)

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found. Please install Python 3.8+
    echo    Download from: https://python.org/
    pause
    exit /b 1
) else (
    for /f "tokens=*" %%i in ('python --version') do echo ✅ Python: %%i
)

REM Check Rust
rustc --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Rust not found. Please install Rust
    echo    Install from: https://rustup.rs/
    pause
    exit /b 1
) else (
    for /f "tokens=*" %%i in ('rustc --version') do echo ✅ Rust: %%i
)

REM Install Python dependencies
echo 📦 Installing Python dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Failed to install Python dependencies
    pause
    exit /b 1
)

REM Install frontend dependencies
echo 📦 Installing frontend dependencies...
cd frontend
npm install
if %errorlevel% neq 0 (
    echo ❌ Failed to install frontend dependencies
    pause
    exit /b 1
)
cd ..

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo 📝 Creating .env file...
    (
        echo # Arbitrage Bot Configuration
        echo PRIVATE_KEY=your_private_key_here
        echo RPC_URL=https://mainnet.base.org
        echo MIN_PROFIT_THRESHOLD_USD=0.50
        echo FLASH_LOAN_AMOUNT_USD=100000
        echo DISABLE_DEX_CALLS=true
    ) > .env
    echo ✅ Created .env file. Please update with your values.
)

echo.
echo 🎉 Setup complete! To start development:
echo    cd frontend ^&^& npm run tauri dev
echo.
echo 📚 Other useful commands:
echo    npm run dev          # Frontend only
echo    npm run tauri build  # Production build
echo    python websocket_server.py  # Backend only
pause
