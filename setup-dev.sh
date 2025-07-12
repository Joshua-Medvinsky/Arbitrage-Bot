#!/bin/bash
# Developer setup script for Arbitrage Bot (macOS/Linux)

echo "🚀 Setting up Arbitrage Bot development environment..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
GRAY='\033[0;37m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "${YELLOW}📋 Checking prerequisites...${NC}"

# Check Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✅ Node.js: $NODE_VERSION${NC}"
else
    echo -e "${RED}❌ Node.js not found. Please install Node.js 16+${NC}"
    echo -e "${CYAN}   Download from: https://nodejs.org/${NC}"
    exit 1
fi

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✅ Python: $PYTHON_VERSION${NC}"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version)
    echo -e "${GREEN}✅ Python: $PYTHON_VERSION${NC}"
    PYTHON_CMD="python"
else
    echo -e "${RED}❌ Python not found. Please install Python 3.8+${NC}"
    echo -e "${CYAN}   Download from: https://python.org/${NC}"
    exit 1
fi

# Check pip
if command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
elif command -v pip &> /dev/null; then
    PIP_CMD="pip"
else
    echo -e "${RED}❌ pip not found. Please install pip${NC}"
    exit 1
fi

# Check Rust
if command -v rustc &> /dev/null; then
    RUST_VERSION=$(rustc --version)
    echo -e "${GREEN}✅ Rust: $RUST_VERSION${NC}"
else
    echo -e "${RED}❌ Rust not found. Please install Rust${NC}"
    echo -e "${CYAN}   Install from: https://rustup.rs/${NC}"
    exit 1
fi

# Install Python dependencies
echo -e "${YELLOW}📦 Installing Python dependencies...${NC}"
$PIP_CMD install -r requirements.txt

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to install Python dependencies${NC}"
    exit 1
fi

# Install frontend dependencies
echo -e "${YELLOW}📦 Installing frontend dependencies...${NC}"
cd frontend
npm install

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to install frontend dependencies${NC}"
    exit 1
fi

# Check Tauri CLI
echo -e "${YELLOW}📦 Checking Tauri CLI...${NC}"
if npx @tauri-apps/cli --version &> /dev/null; then
    echo -e "${GREEN}✅ Tauri CLI available${NC}"
else
    echo -e "${YELLOW}📦 Installing Tauri CLI...${NC}"
    npm install -g @tauri-apps/cli
fi

# Create .env file if it doesn't exist
cd ..
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}📝 Creating .env file...${NC}"
    cat > .env << 'EOF'
# Arbitrage Bot Configuration
PRIVATE_KEY=your_private_key_here
RPC_URL=https://mainnet.base.org
MIN_PROFIT_THRESHOLD_USD=0.50
FLASH_LOAN_AMOUNT_USD=100000
DISABLE_DEX_CALLS=true
EOF
    echo -e "${GREEN}✅ Created .env file. Please update with your values.${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Setup complete! To start development:${NC}"
echo -e "${CYAN}   cd frontend && npm run tauri dev${NC}"
echo ""
echo -e "${YELLOW}📚 Other useful commands:${NC}"
echo -e "${GRAY}   npm run dev          # Frontend only${NC}"
echo -e "${GRAY}   npm run tauri build  # Production build${NC}"
echo -e "${GRAY}   $PYTHON_CMD websocket_server.py  # Backend only${NC}"
