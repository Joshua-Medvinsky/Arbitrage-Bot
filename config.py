# Configuration for Flash Loan Arbitrage Bot
# Base Network - Uniswap V3, SushiSwap, Aerodrome

import os
from dotenv import load_dotenv

load_dotenv()

# Network Configuration
WEB3_PROVIDER = os.getenv("WEB3_PROVIDER", "https://mainnet.base.org")

# API Keys and Endpoints
UNISWAP_API_KEY = os.getenv("UNISWAP_API_KEY", "")
UNISWAP_V3_SUBGRAPH = os.getenv("UNISWAP_V3_SUBGRAPH", "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3")
AERODROME_SUBGRAPH = os.getenv("AERODROME_SUBGRAPH", "https://api.thegraph.com/subgraphs/name/aerodrome-finance/aerodrome-v2")

# Contract Addresses (Base Network)
SUSHI_FACTORY_ADDRESS = os.getenv("SUSHI_FACTORY_ADDRESS", "0x6B3595068778DD592e39A122f4f5a5cF09C90fE2")

# Token Addresses (Base Network)
WETH_ADDRESS = "0x4200000000000000000000000000000000000006"
USDC_ADDRESS = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
ZORA_ADDRESS = "0x4200000000000000000000000000000000000006"  # Using WETH as proxy

# Execution Settings
EXECUTION_MODE = os.getenv("EXECUTION_MODE", "True").lower() == "true"
SIMULATION_MODE = os.getenv("SIMULATION_MODE", "False").lower() == "true"
SAFE_MODE = os.getenv("SAFE_MODE", "True").lower() == "true"
FLASH_LOAN_ENABLED = os.getenv("FLASH_LOAN_ENABLED", "False").lower() == "true"

# Position Sizing
POSITION_SIZE_USD = float(os.getenv("POSITION_SIZE_USD", "5"))
MIN_PROFIT_PCT = float(os.getenv("MIN_PROFIT_PCT", "1.0"))
MAX_PROFIT_PCT = float(os.getenv("MAX_PROFIT_PCT", "20.0"))

# Risk Management
MIN_LIQUIDITY_USD = float(os.getenv("MIN_LIQUIDITY_USD", "100000"))
MAX_SLIPPAGE = float(os.getenv("MAX_SLIPPAGE", "0.01"))
DEFAULT_ETH_AMOUNT = float(os.getenv("DEFAULT_ETH_AMOUNT", "0.002"))
DEFAULT_GAS_ETH = float(os.getenv("DEFAULT_GAS_ETH", "0.001"))

# Gas Settings (Base Network)
BASE_GAS_PRICE_GWEI = int(os.getenv("BASE_GAS_PRICE_GWEI", "1000000"))
GAS_LIMIT_SWAP = int(os.getenv("GAS_LIMIT_SWAP", "300000"))
GAS_LIMIT_APPROVE = int(os.getenv("GAS_LIMIT_APPROVE", "100000"))

# Fee Settings
DEFAULT_SLIPPAGE_PCT = float(os.getenv("DEFAULT_SLIPPAGE_PCT", "0.01"))
TRANSACTION_FEE_PCT = float(os.getenv("TRANSACTION_FEE_PCT", "0.003"))
SLIPPAGE_PCT = float(os.getenv("SLIPPAGE_PCT", "0.01"))
MEV_PROTECTION_COST_USD = float(os.getenv("MEV_PROTECTION_COST_USD", "1.0"))
MIN_PROFIT_THRESHOLD_USD = float(os.getenv("MIN_PROFIT_THRESHOLD_USD", "0.50"))

# Flash Loan Settings
FLASH_LOAN_AMOUNT_USD = float(os.getenv("FLASH_LOAN_AMOUNT_USD", "100000"))
FLASH_LOAN_FEE_PCT = float(os.getenv("FLASH_LOAN_FEE_PCT", "0.0009"))
FLASH_LOAN_MIN_PROFIT_USD = float(os.getenv("FLASH_LOAN_MIN_PROFIT_USD", "50"))

# ABI Definitions
PAIR_ABI = [
    {"constant":True,"inputs":[],"name":"getReserves","outputs":[{"name":"_reserve0","type":"uint112"},{"name":"_reserve1","type":"uint112"},{"name":"_blockTimestampLast","type":"uint32"}],"type":"function"},
    {"constant":True,"inputs":[],"name":"token0","outputs":[{"name":"","type":"address"}],"type":"function"},
    {"constant":True,"inputs":[],"name":"token1","outputs":[{"name":"","type":"address"}],"type":"function"}
]

SUSHI_FACTORY_ABI = [
    {"constant":True,"inputs":[{"name":"","type":"uint256"}],"name":"allPairs","outputs":[{"name":"","type":"address"}],"type":"function"},
    {"constant":True,"inputs":[],"name":"allPairsLength","outputs":[{"name":"","type":"uint256"}],"type":"function"}
]

# Project Structure Paths
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
CONTRACTS_DIR = os.path.join(PROJECT_ROOT, "contracts")
SCRIPTS_DIR = os.path.join(PROJECT_ROOT, "scripts")
TESTS_DIR = os.path.join(PROJECT_ROOT, "tests")
DOCS_DIR = os.path.join(PROJECT_ROOT, "docs")
EXAMPLES_DIR = os.path.join(PROJECT_ROOT, "examples")

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = os.path.join(PROJECT_ROOT, "logs", "arbitrage_bot.log")

# Create logs directory if it doesn't exist
os.makedirs(os.path.join(PROJECT_ROOT, "logs"), exist_ok=True)

# Flash loan contract addresses (Aave V3 on Base)
AAVE_LENDING_POOL = "0xA238Dd80C259a72e81d7e4664a9801593F98d1c5"
AAVE_LENDING_POOL_ABI = [
    {"inputs":[{"internalType":"address","name":"asset","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"uint256","name":"interestRateMode","type":"uint256"},{"internalType":"uint16","name":"referralCode","type":"uint16"},{"internalType":"address","name":"onBehalfOf","type":"address"}],"name":"borrow","outputs":[],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[{"internalType":"address","name":"asset","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"uint256","name":"rateMode","type":"uint256"},{"internalType":"address","name":"onBehalfOf","type":"address"}],"name":"repay","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[{"internalType":"address","name":"asset","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"address","name":"onBehalfOf","type":"address"},{"internalType":"uint16","name":"referralCode","type":"uint16"}],"name":"supply","outputs":[],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[{"internalType":"address","name":"asset","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"address","name":"to","type":"address"}],"name":"withdraw","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[{"internalType":"address","name":"receiverAddress","type":"address"},{"internalType":"address[]","name":"assets","type":"address[]"},{"internalType":"uint256[]","name":"amounts","type":"uint256[]"},{"internalType":"uint256[]","name":"interestRateModes","type":"uint256[]"},{"internalType":"address","name":"onBehalfOf","type":"address"},{"internalType":"bytes","name":"params","type":"bytes"},{"internalType":"uint16","name":"referralCode","type":"uint16"}],"name":"flashLoan","outputs":[],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[{"internalType":"address","name":"receiverAddress","type":"address"},{"internalType":"address","name":"asset","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"bytes","name":"params","type":"bytes"},{"internalType":"uint16","name":"referralCode","type":"uint16"}],"name":"flashLoan","outputs":[],"stateMutability":"nonpayable","type":"function"}
]

# Flash loan receiver contract address (deploy this contract first)
FLASH_LOAN_RECEIVER_ADDRESS = "0x51795d44fB0E8633a24A9157CD0Ac5291A489D07"  # Deploy and set this address