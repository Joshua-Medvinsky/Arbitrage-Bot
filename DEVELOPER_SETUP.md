# Developer Setup Guide## Prerequisites

- **Node.js** 16+ ([Download](https://nodejs.org/))
- **Rust** latest stable ([Install](https://rustup.rs/))
- **Python** 3.8+ ([Download](https://python.org/))

## Platform-Specific Setup

### Windows
Choose your preferred option:

**PowerShell (Recommended):**
```powershell
.\setup-dev.ps1
```

**Command Prompt:**
```cmd
setup-dev.bat
```

### macOS/Linux  
Use the Bash script:
```bash
chmod +x setup-dev.sh
./setup-dev.sh
```

All scripts do the same thing:
- Check prerequisites
- Install Python dependencies
- Install Node.js dependencies  
- Create `.env` file template
- Verify Tauri CLI is available Quick Start

1. **Clone and setup:**
   ```bash
   git clone https://github.com/Joshua-Medvinsky/Arbitrage-Bot.git
   cd Arbitrage-Bot
   
   # Run automated setup (choose your platform):
   .\setup-dev.ps1     # Windows PowerShell
   ./setup-dev.sh      # macOS/Linux (run: chmod +x setup-dev.sh first)
   setup-dev.bat       # Windows Command Prompt
   ```

2. **Start development:**
   ```bash
   cd frontend
   npm run tauri dev
   ```

## Prerequisites

- **Node.js** 16+ ([Download](https://nodejs.org/))
- **Rust** latest stable ([Install](https://rustup.rs/))
- **Python** 3.8+ ([Download](https://python.org/))

## Manual Setup

### 1. Install Dependencies
```bash
# Python backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### 2. Environment Configuration
Create `.env` file in project root:
```env
PRIVATE_KEY=your_private_key_here
RPC_URL=https://mainnet.base.org
MIN_PROFIT_THRESHOLD_USD=0.50
FLASH_LOAN_AMOUNT_USD=100000
DISABLE_DEX_CALLS=true
```

### 3. Development Commands

| Command | Purpose |
|---------|---------|
| `npm run tauri dev` | Full app with hot reload |
| `npm run dev` | Frontend only |
| `npm run tauri build` | Production build |
| `python websocket_server.py` | Backend only |
| `python build_executable.py` | Build .exe |

## Project Structure

```
├── frontend/                 # React + Tauri app
│   ├── src/                 # React components  
│   ├── src-tauri/          # Rust backend
│   └── package.json
├── scripts/                # Python arbitrage logic
├── contracts/              # Smart contracts
├── websocket_server.py     # Python WebSocket server
└── requirements.txt        # Python dependencies
```

## Development Workflow

### Frontend Changes
- Edit files in `frontend/src/`
- Hot reload automatically updates the app
- TypeScript errors show in terminal and VS Code

### Backend (Rust) Changes  
- Edit files in `frontend/src-tauri/src/`
- App automatically recompiles on save
- Rust errors show in terminal

### Python Backend Changes
- Edit `websocket_server.py` or files in `scripts/`
- Restart the app to see changes
- Or run `python websocket_server.py` separately

## Troubleshooting

### TypeScript Errors
```bash
cd frontend
npm run check
```

### Rust Compilation Issues
```bash
rustup update
cd frontend  
npm run tauri build -- --debug
```

### WebSocket Connection Failed
- Ensure backend runs on `localhost:8000`
- Check firewall settings
- Verify port 8000 is available

### Python Module Errors
```bash
pip install -r requirements.txt
python -c "import web3, websockets, aiohttp"
```

## VS Code Setup

**Recommended Extensions:**
- Rust Analyzer
- Tauri
- Python
- ES7+ React/Redux/React-Native snippets

**Settings:**
```json
{
  "rust-analyzer.cargo.features": ["tauri/api"],
  "typescript.preferences.includePackageJsonAutoImports": "on"
}
```

## Git Workflow

**Don't commit:**
- `target/` directories (Rust build cache)
- `node_modules/`
- `.env` files with real keys
- `arbitrage-bot-server.exe` (regenerated on build)

**Do commit:**
- Source code changes
- Configuration file templates
- Documentation updates
- Build script improvements

## Need Help?

1. Check this README
2. Look at existing code for patterns
3. Check VS Code Problems panel for errors
4. Run `npm run check` for TypeScript issues
5. Ask in team chat/issues
