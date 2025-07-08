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

## Flash Loan Arbitrage Flow

### 🔄 **Complete Flash Loan Execution Flow**

The bot now supports flash loan arbitrage for enhanced capital efficiency. Here's how the full flow works:

#### **1. Opportunity Detection & Analysis**
```
📊 Scanning DEXes → 🔍 Finding price differences → 📈 Calculating flash loan vs regular profit
```

#### **2. Strategy Selection**
- **Regular Arbitrage**: Uses your own capital (current $5 position size)
- **Flash Loan Arbitrage**: Borrows large amounts ($100k) for maximum profit

#### **3. Flash Loan Execution Flow**

**Step 1: Flash Loan Request**
```python
# Borrow $100k worth of tokens from Aave
flash_loan_amount = 100000  # USD
flash_loan_token = WETH_BASE  # Most liquid token
flash_loan_function = aave_lending_pool.borrow(
    flash_loan_token,
    flash_loan_amount_wei,
    2,  # Variable interest rate
    0,  # Referral code
    wallet_address
)
```

**Step 2: Arbitrage Execution**
```python
# Execute arbitrage with borrowed funds
1. Approve borrowed tokens for buy DEX
2. Buy token on cheaper DEX (e.g., Uniswap)
3. Approve received tokens for sell DEX  
4. Sell token on expensive DEX (e.g., SushiSwap)
5. Receive profit + original borrowed amount
```

**Step 3: Flash Loan Repayment**
```python
# Repay flash loan with fees
flash_loan_fee = 0.09%  # Aave flash loan fee
total_repay = borrowed_amount + flash_loan_fee
repay_function = aave_lending_pool.repay(
    flash_loan_token,
    total_repay_amount,
    2,  # Variable interest rate
    wallet_address
)
```

#### **4. Profit Calculation**

**Regular Arbitrage (Current):**
- Position Size: $5
- Profit: ~$0.25 (5% of $5)
- Capital Required: $5

**Flash Loan Arbitrage (Enhanced):**
- Position Size: $100,000
- Profit: ~$500 (0.5% of $100k)
- Capital Required: $0 (borrowed)
- Flash Loan Fee: $90 (0.09%)
- Net Profit: $410

#### **5. Safety & Risk Management**

**Flash Loan Safety Features:**
- **Minimum Profit Threshold**: $50 minimum profit to use flash loans
- **Maximum Position Size**: $100k flash loan limit
- **Fee Calculation**: 0.09% Aave flash loan fee
- **Gas Optimization**: Base network low gas costs
- **Error Handling**: Comprehensive failure recovery

**Risk Mitigation:**
- **Atomic Transactions**: All operations in single transaction
- **Slippage Protection**: 1% maximum slippage
- **Liquidity Checks**: Minimum $100k pool liquidity
- **Token Validation**: Only major tokens (WETH, USDC)

#### **6. Execution Modes**

**Safe Mode (Current):**
```python
SAFE_MODE = True
FLASH_LOAN_ENABLED = False  # Disabled for safety
# Uses regular arbitrage with $5 positions
```

**Flash Loan Mode (Advanced):**
```python
SAFE_MODE = False
FLASH_LOAN_ENABLED = True
# Uses flash loans for $100k positions
```

#### **7. Real-World Example**

**Scenario**: WETH/weETH arbitrage opportunity
```
📊 Price Difference Detected:
   Uniswap: 1.000123 WETH/weETH
   SushiSwap: 1.000456 WETH/weETH
   Profit: 0.33%

🚀 Flash Loan Execution:
   1. Borrow 40 WETH ($100k) from Aave
   2. Buy 40 weETH on Uniswap @ 1.000123
   3. Sell 40 weETH on SushiSwap @ 1.000456
   4. Receive 40.133 WETH (profit: 0.133 WETH)
   5. Repay 40 WETH + 0.036 WETH fee to Aave
   6. Keep 0.097 WETH profit (~$242)

💰 Net Result:
   Gross Profit: $330
   Flash Loan Fee: $90
   Gas Costs: $2
   Net Profit: $238
```

#### **8. Technical Implementation**

**Flash Loan Contract Integration:**
```python
# Aave V3 Lending Pool (Base Network)
AAVE_LENDING_POOL = "0xA238Dd80C259a72e81d7e4664a9801593F98d1c5"

# Flash Loan Settings
FLASH_LOAN_AMOUNT_USD = 100000  # $100k
FLASH_LOAN_FEE_PCT = 0.0009     # 0.09%
FLASH_LOAN_MIN_PROFIT_USD = 50  # $50 minimum
```

**Execution Methods:**
- `execute_flash_loan_arbitrage()`: Main flash loan execution
- `execute_flash_loan_operation()`: Flash loan request and repayment
- `execute_arbitrage_with_flash_loan()`: Arbitrage with borrowed funds
- `repay_flash_loan()`: Flash loan repayment with fees

#### **9. Monitoring & Logging**

**Flash Loan Execution Logs:**
```
🚀 Executing FLASH LOAN arbitrage: WETH/weETH
   Buy on Uniswap @ 1.000123
   Sell on SushiSwap @ 1.000456
   Expected profit: 0.33%
   Flash loan amount: $100,000

🔐 Initiating flash loan for 40000000000000000000 wei...
✅ Flash loan requested: 0x1234...
✅ Flash loan received!

🔄 Executing arbitrage with flash loaned funds...
✅ Arbitrage with flash loan completed!

💰 Repaying flash loan...
   Original amount: 40000000000000000000 wei
   Flash loan fee: 36000000000000000 wei
   Total to repay: 40036000000000000000 wei
✅ Flash loan repaid successfully!

✅ Flash loan arbitrage executed successfully!
```

#### **10. Advantages of Flash Loan Arbitrage**

**Capital Efficiency:**
- **No Capital Required**: Borrow instead of using own funds
- **Larger Positions**: $100k vs $5 positions
- **Higher Profits**: Scale with borrowed amount

**Risk Management:**
- **Atomic Execution**: All operations in single transaction
- **No Liquidation Risk**: Flash loans are repaid immediately
- **Predictable Costs**: Fixed flash loan fees

**Profit Optimization:**
- **MEV Protection**: Flash loans are harder to front-run
- **Gas Efficiency**: Single transaction vs multiple
- **Slippage Reduction**: Larger orders can get better prices

---

**Current Status**: Flash loan functionality is implemented and ready for testing. Currently disabled in safe mode for security.