# Arbitrage Bot for Base Network

## Overview

A sophisticated arbitrage bot designed for the Base network that monitors Uniswap V3, SushiSwap, and Aerodrome DEXes for profitable trading opportunities. The bot features comprehensive safety checks, real-time execution capabilities, and fallback mechanisms for token handling.

## Features

### 🔍 **Multi-DEX Monitoring**
- **Uniswap V3**: Monitors all pools with real-time price data
- **SushiSwap**: Scans factory pairs for arbitrage opportunities  
- **Aerodrome**: Tracks concentrated liquidity pools
- Real-time price comparison across all three DEXes

### 🛡️ **Safety & Risk Management**
- **Safe Mode**: Restricts trading to small amounts ($5) and safe tokens
- **Position Size Limits**: Configurable position sizes (default: $5 for testing)
- **Profit Range Validation**: 1-20% profit thresholds for realistic opportunities
- **Liquidity Requirements**: Minimum $100k liquidity for safe execution
- **Token Validation**: Prevents invalid swaps (e.g., WETH-to-WETH)
- **Fallback Logic**: Handles inaccessible tokens gracefully

### ⚡ **Real-Time Execution**
- **Live Trading Mode**: Execute real transactions on Base network
- **Simulation Mode**: Safe testing without sending transactions
- **Token Approvals**: Automatic ERC20 approvals for DEX routers
- **Gas Optimization**: Base network optimized gas settings
- **Transaction Monitoring**: Real-time transaction status tracking

### 🔧 **Advanced Features**
- **Flash Loan Support**: Calculates flash loan arbitrage opportunities
- **MEV Protection**: Accounts for MEV bot costs in profit calculations
- **Slippage Protection**: Configurable slippage limits (default: 1%)
- **Error Handling**: Comprehensive error recovery and logging
- **Balance Checking**: Validates wallet balances before execution

## Configuration

### Environment Variables
Create a `.env` file with the following variables:

```env
# Web3 Provider
WEB3_PROVIDER=https://mainnet.base.org

# API Keys
UNISWAP_API_KEY=your_uniswap_api_key
UNISWAP_V3_SUBGRAPH=https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3
AERODROME_SUBGRAPH=https://api.thegraph.com/subgraphs/name/aerodrome-finance/exchange-v2

# Contract Addresses
SUSHI_FACTORY_ADDRESS=0x6B3595068778DD592e39A122f4f5a5cF09C90fE2

# Wallet (for live trading)
PRIVATE_KEY=your_private_key_here
```

### Safety Settings
```python
# Safe testing configuration
POSITION_SIZE_USD = 5          # $5 position size for testing
MIN_PROFIT_PCT = 1.0          # 1% minimum profit
MAX_PROFIT_PCT = 20.0         # 20% maximum profit
MIN_LIQUIDITY_USD = 100000    # $100k minimum liquidity
SAFE_MODE = True              # Enable safety restrictions
SIMULATION_MODE = False       # Set to True for simulation only
```

## Usage

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd Arbitrage-Bot

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration
```

### Running the Bot

#### Simulation Mode (Safe Testing)
```bash
# Edit script.py to set SIMULATION_MODE = True
python script.py
```

#### Live Trading Mode
```bash
# Edit script.py to set:
# - SIMULATION_MODE = False
# - EXECUTION_MODE = True
# - Add your PRIVATE_KEY to .env
python script.py
```

### Execution Modes

1. **Simulation Mode**: 
   - No real transactions sent
   - Safe for testing and learning
   - Shows what trades would be executed

2. **Live Mode**:
   - Real transactions on Base network
   - Requires funded wallet
   - Uses safe position sizes ($5 default)

## Safety Features

### 🛡️ **Built-in Protections**
- **Position Size Limits**: Maximum $10 for safe testing
- **Token Restrictions**: Only major tokens (WETH, USDC, etc.)
- **Profit Validation**: Realistic profit ranges only
- **Liquidity Checks**: Minimum liquidity requirements
- **Balance Validation**: Checks wallet balances before execution

### ⚠️ **Risk Warnings**
- **Educational Purpose**: This bot is for learning and testing
- **Small Amounts**: Designed for small position sizes
- **Base Network**: Optimized for Base network conditions
- **No Guarantees**: Cryptocurrency trading involves risk

## Supported Tokens

### Base Network Tokens
- **WETH**: 0x4200000000000000000000000000000000000006
- **USDC**: 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913
- **weETH**: 0xd9aa30E1B4c60CAe79FC379ff651abACE84F5AA9

### Fallback Logic
The bot handles token accessibility issues:
- Falls back to WETH if specific tokens are inaccessible
- Prevents invalid swaps (same token to same token)
- Validates token contracts before execution

## Monitoring & Logging

### Real-Time Output
```
🚀 Real-Time Arbitrage Bot - Safe Testing Mode
============================================================
📊 Found 150 Uniswap pools
📊 Found 89 SushiSwap pools  
📊 Found 67 Aerodrome pools

🔥 Found 3 executable arbitrage opportunities:
1. WETH/weETH (FLASH_LOAN)
   Buy on Uniswap @ 1.000123
   Sell on SushiSwap @ 1.000456
   Profit: 0.33%
   Net Profit: $1.23
```

### Balance Monitoring
```
🔍 Checking available tokens for 0x1234...
   ✅ WETH: 1000000000000000000 wei
   ✅ USDC: 5000000 wei
   ❌ weETH: 0 wei
```

## Project Status

### ✅ **Completed Features**
- [x] Multi-DEX price monitoring
- [x] Real-time arbitrage detection
- [x] Safe execution mode with $5 positions
- [x] Token approval and swap execution
- [x] Comprehensive error handling
- [x] Balance validation and fallback logic
- [x] Flash loan profit calculations
- [x] MEV protection cost estimation

### 🔄 **Current Status**
- **Active Development**: Bot is running live with safety features
- **Base Network Optimized**: Configured for Base network conditions
- **Safe Testing Mode**: Using small position sizes for validation
- **Real Execution**: Can execute actual trades (with safety limits)

### 🚧 **Future Enhancements**
- [ ] Additional DEX support (PancakeSwap, etc.)
- [ ] Advanced MEV protection strategies
- [ ] Automated position sizing based on liquidity
- [ ] Web dashboard for monitoring
- [ ] Telegram/Discord notifications

## Disclaimer

⚠️ **IMPORTANT**: This bot is for educational and research purposes only.

- **No Financial Advice**: This is not investment advice
- **Risk Warning**: Cryptocurrency trading involves substantial risk
- **Small Amounts**: Designed for small position sizes only
- **Testing Focus**: Use simulation mode for learning
- **No Guarantees**: Past performance doesn't guarantee future results

## License

This project is for educational purposes. Use at your own risk.

---

**Current Version**: v2.0 - Base Network Optimized with Safety Features
**Last Updated**: December 2024