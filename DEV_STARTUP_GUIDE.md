# Development Startup Guide

This project now has **cross-platform** development startup options that automatically connect your frontend and backend.

## ✨ New Features

- 🌍 **Cross-platform compatibility** (Windows, macOS, Linux)
- 🔗 **Automatic frontend-backend connection**
- 🌐 **Internet connectivity status** (instead of local server status)
- 🚀 **One-command startup**

## 🚀 Quick Start Options

### Option 1: npm scripts (Recommended)
```bash
cd frontend
npm run dev:full
```

### Option 2: PowerShell script (Cross-platform)
```bash
# From project root
./start-dev.ps1
```

## 📡 Connection Status Changes

The status indicator now shows:
- **🟢 "Online - Ready for Live Trading"** - Internet connected, can perform live trades
- **🔴 "Offline - Simulation Only"** - No internet, limited to simulation mode

This assumes your local server (socketio_server.py) is running and connecting frontend/backend automatically.

## 🛠 How It Works

### npm scripts approach:
- Uses `concurrently` to run both frontend and backend simultaneously
- Automatically handles process lifecycle (kills both when you Ctrl+C)
- Cross-platform by design (works identically on all operating systems)

### PowerShell script approach:
- Checks prerequisites (Python venv, socketio_server.py, frontend directory)
- Auto-detects OS and uses correct Python path
- Starts backend in separate process, then frontend
- Automatically cleans up backend when frontend exits

## 📋 Prerequisites

1. **Python virtual environment** set up in `.venv/`
2. **Node.js and npm** installed
3. **Frontend dependencies** installed (`cd frontend && npm install`)

## 🔧 Troubleshooting

### "socketio_server.py not found"
- Make sure you're running from the project root directory
- Verify the file exists and is named correctly

### "Virtual environment not found"
- Create your Python virtual environment: `python -m venv .venv`
- Activate it and install dependencies: `pip install -r requirements.txt`

### Frontend won't start
- Install dependencies: `cd frontend && npm install`
- Make sure you have Node.js 16+ installed

## 🎯 Next Steps

1. **Test the setup**: Try `cd frontend && npm run dev:full`
2. **Verify connectivity**: Check that the status shows your internet connection
3. **Start developing**: Both frontend and backend are now running automatically!
