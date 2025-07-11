import asyncio
import os
import aiohttp
from web3 import Web3
from dotenv import load_dotenv
import sys
import time

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config import PAIR_ABI, SUSHI_FACTORY_ABI, DEFAULT_ETH_AMOUNT, DEFAULT_GAS_ETH, DEFAULT_SLIPPAGE_PCT, USDC_ADDRESS, WETH_ADDRESS, ZORA_ADDRESS, SUSHI_FACTORY_ADDRESS, BASE_GAS_PRICE_GWEI, GAS_LIMIT_SWAP, GAS_LIMIT_APPROVE, TRANSACTION_FEE_PCT, SLIPPAGE_PCT, MEV_PROTECTION_COST_USD, MIN_PROFIT_THRESHOLD_USD, SAFE_MODE, POSITION_SIZE_USD, FLASH_LOAN_ENABLED
from scripts.monitoring.token_addresses import TOKEN_ADDRESSES, WETH_BASE, USDC_BASE, weETH_BASE

load_dotenv()

WEB3_PROVIDER = os.getenv("WEB3_PROVIDER")
UNISWAP_V3_SUBGRAPH = os.getenv("UNISWAP_V3_SUBGRAPH")
AERODROME_SUBGRAPH = os.getenv("AERODROME_SUBGRAPH")
BALANCER_V2_SUBGRAPH = os.getenv("BALANCER_V2_SUBGRAPH")
UNISWAP_API_KEY = os.getenv("UNISWAP_API_KEY")

# Real-time execution settings
EXECUTION_MODE = False  # DISABLED - Set to False for safety
SIMULATION_MODE = True   # ENABLED - Set to True for simulation only
PRIVATE_KEY = os.getenv("PRIVATE_KEY")  # Your wallet private key
MIN_LIQUIDITY_USD = 100000  # Increased to $100k liquidity for safety
MAX_PROFIT_PCT = 300.0  # Reduced to 20% max profit for realistic opportunities
MIN_PROFIT_PCT = 5  # Lowered to 0.1% minimum for better opportunities
MAX_SLIPPAGE = 0.02  # Increased to 2% slippage for testing

w3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER))

# Convert addresses to checksum format
USDC = Web3.to_checksum_address(USDC_ADDRESS)
WETH = Web3.to_checksum_address(WETH_ADDRESS)

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
FLASH_LOAN_RECEIVER_ADDRESS = "0x95DD361C6e75A93C610f359bcAb5412050976ddb"

# Flash loan receiver contract ABI
FLASH_LOAN_RECEIVER_ABI = [
    {"inputs":[{"internalType":"address","name":"asset","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"address","name":"tokenIn","type":"address"},{"internalType":"address","name":"tokenOut","type":"address"},{"internalType":"string","name":"buyDex","type":"string"},{"internalType":"string","name":"sellDex","type":"string"},{"internalType":"uint256","name":"buyAmount","type":"uint256"},{"internalType":"uint256","name":"sellAmount","type":"uint256"},{"internalType":"uint24","name":"buyFee","type":"uint24"},{"internalType":"uint24","name":"sellFee","type":"uint24"}],"name":"requestFlashLoan","outputs":[],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"withdrawToken","outputs":[],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[],"name":"withdrawETH","outputs":[],"stateMutability":"nonpayable","type":"function"}
]

# Flash loan settings
FLASH_LOAN_ENABLED = False  # Disable flash loans for now, focus on regular arbitrage
FLASH_LOAN_AMOUNT_USD = 1  # Reduced to $1 for testing
FLASH_LOAN_FEE_PCT = 0.0009  # 0.09% flash loan fee
FLASH_LOAN_MIN_PROFIT_USD = 0.1  # Reduced minimum profit for testing

# Direct flash loan approach (no contract deployment needed)
DIRECT_FLASH_LOAN = True  # Set to True for simpler approach

# MEV Bot detection
MEV_BOT_ADDRESSES = [
    "0x0000000000000000000000000000000000000000",  # Placeholder - real MEV bots
]

# Uniswap V3 Router for execution (Base network)
UNISWAP_V3_ROUTER = Web3.to_checksum_address("0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45")
UNISWAP_V3_ROUTER_ABI = [
    {"inputs":[{"components":[{"internalType":"address","name":"tokenIn","type":"address"},{"internalType":"address","name":"tokenOut","type":"address"},{"internalType":"uint24","name":"fee","type":"uint24"},{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMinimum","type":"uint256"},{"internalType":"uint160","name":"sqrtPriceLimitX96","type":"uint160"}],"internalType":"struct IV3SwapRouter.ExactInputSingleParams","name":"params","type":"tuple"}],"name":"exactInputSingle","outputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"}],"stateMutability":"payable","type":"function"},
    {"inputs":[{"components":[{"internalType":"address","name":"tokenIn","type":"address"},{"internalType":"address","name":"tokenOut","type":"address"},{"internalType":"uint24","name":"fee","type":"uint24"},{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"amountInMaximum","type":"uint256"},{"internalType":"uint160","name":"sqrtPriceLimitX96","type":"uint160"}],"internalType":"struct IV3SwapRouter.ExactOutputSingleParams","name":"params","type":"tuple"}],"name":"exactOutputSingle","outputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"}],"stateMutability":"payable","type":"function"},
    {"inputs":[{"components":[{"internalType":"bytes","name":"path","type":"bytes"},{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMinimum","type":"uint256"}],"internalType":"struct IV3SwapRouter.ExactInputParams","name":"params","type":"tuple"}],"name":"exactInput","outputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"}],"stateMutability":"payable","type":"function"},
    {"inputs":[{"components":[{"internalType":"bytes","name":"path","type":"bytes"},{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"amountInMaximum","type":"uint256"}],"internalType":"struct IV3SwapRouter.ExactOutputParams","name":"params","type":"tuple"}],"name":"exactOutput","outputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"}],"stateMutability":"payable","type":"function"},
    {"inputs":[{"internalType":"bytes[]","name":"data","type":"bytes[]"}],"name":"multicall","outputs":[{"internalType":"bytes[]","name":"results","type":"bytes[]"}],"stateMutability":"payable","type":"function"}
]

# SushiSwap router address and ABI
SUSHISWAP_ROUTER = '0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F'
SUSHISWAP_ROUTER_ABI = [
    {"inputs":[{"internalType":"address","name":"_factory","type":"address"},{"internalType":"address","name":"_WETH","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},
    {"inputs":[],"name":"WETH","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},
    {"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint256","name":"amountADesired","type":"uint256"},{"internalType":"uint256","name":"amountBDesired","type":"uint256"},{"internalType":"uint256","name":"amountAMin","type":"uint256"},{"internalType":"uint256","name":"amountBMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"addLiquidity","outputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"amountB","type":"uint256"},{"internalType":"uint256","name":"liquidity","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"amountTokenDesired","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"addLiquidityETH","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"},{"internalType":"uint256","name":"liquidity","type":"uint256"}],"stateMutability":"payable","type":"function"},
    {"inputs":[],"name":"factory","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},
    {"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"reserveIn","type":"uint256"},{"internalType":"uint256","name":"reserveOut","type":"uint256"}],"name":"getAmountIn","outputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"}],"stateMutability":"pure","type":"function"},
    {"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"reserveIn","type":"uint256"},{"internalType":"uint256","name":"reserveOut","type":"uint256"}],"name":"getAmountOut","outputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"}],"stateMutability":"pure","type":"function"},
    {"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"}],"name":"getAmountsIn","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"view","type":"function"},
    {"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"}],"name":"getAmountsOut","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"view","type":"function"},
    {"inputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"reserveA","type":"uint256"},{"internalType":"uint256","name":"reserveB","type":"uint256"}],"name":"quote","outputs":[{"internalType":"uint256","name":"amountB","type":"uint256"}],"stateMutability":"pure","type":"function"},
    {"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountAMin","type":"uint256"},{"internalType":"uint256","name":"amountBMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"removeLiquidity","outputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"amountB","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"removeLiquidityETH","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"bool","name":"approveMax","type":"bool"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"removeLiquidityETHWithPermit","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"bool","name":"approveMax","type":"bool"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"removeLiquidityETHWithPermitSupportingFeeOnTransferTokens","outputs":[{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountAMin","type":"uint256"},{"internalType":"uint256","name":"amountBMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"bool","name":"approveMax","type":"bool"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"removeLiquidityWithPermit","outputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"amountB","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapETHForExactTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"payable","type":"function"},
    {"inputs":[{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactETHForTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"payable","type":"function"},
    {"inputs":[{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactETHForTokensSupportingFeeOnTransferTokens","outputs":[],"stateMutability":"payable","type":"function"},
    {"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForETH","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForETHSupportingFeeOnTransferTokens","outputs":[],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForTokensSupportingFeeOnTransferTokens","outputs":[],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"amountInMax","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapTokensForExactETH","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"amountInMax","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapTokensForExactTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},
    {"stateMutability":"payable","type":"receive"}
]

# ERC20 Token ABI for approvals
ERC20_ABI = [
    {"constant":True,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"type":"function"},
    {"constant":False,"inputs":[{"name":"_spender","type":"address"},{"name":"_value","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"type":"function"},
    {"constant":True,"inputs":[{"name":"_owner","type":"address"},{"name":"_spender","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"type":"function"},
    {"constant":True,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"type":"function"},
    {"constant":True,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"type":"function"}
]

# Uniswap V3 Factory for pool verification
UNISWAP_V3_FACTORY = Web3.to_checksum_address("0x33128a8fC17869897dcE68Ed026d694621f6FDfD")
UNISWAP_V3_FACTORY_ABI = [
    {"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint24","name":"fee","type":"uint24"}],"name":"getPool","outputs":[{"internalType":"address","name":"pool","type":"address"}],"stateMutability":"view","type":"function"}
]

# Aerodrome Router for execution (Base network)
AERODROME_ROUTER = Web3.to_checksum_address("0xcF77a3Ba9A5CA399B7c97c74d54e5b1Beb874E43")
AERODROME_ROUTER_ABI = [
    {"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"components":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"bool","name":"stable","type":"bool"},{"internalType":"address","name":"factory","type":"address"}],"internalType":"struct IRouter.Route[]","name":"routes","type":"tuple[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"}
]

# Balancer V2 Vault for execution (Base network)
BALANCER_V2_VAULT = Web3.to_checksum_address("0xBA12222222228d8Ba445958a75a0704d566BF2C8")
BALANCER_V2_VAULT_ABI = [
    {"inputs":[{"components":[{"internalType":"bytes32","name":"poolId","type":"bytes32"},{"internalType":"enum IVault.SwapKind","name":"kind","type":"uint8"},{"internalType":"contract IAsset","name":"assetIn","type":"address"},{"internalType":"contract IAsset","name":"assetOut","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"bytes","name":"userData","type":"bytes"}],"internalType":"struct IVault.SingleSwap","name":"singleSwap","type":"tuple"},{"components":[{"internalType":"address","name":"sender","type":"address"},{"internalType":"bool","name":"fromInternalBalance","type":"bool"},{"internalType":"address payable","name":"recipient","type":"address"},{"internalType":"bool","name":"toInternalBalance","type":"bool"}],"internalType":"struct IVault.FundManagement","name":"funds","type":"tuple"},{"internalType":"uint256","name":"limit","type":"uint256"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swap","outputs":[{"internalType":"uint256","name":"amountCalculated","type":"uint256"}],"stateMutability":"payable","type":"function"}
]

class ArbitrageExecutor:
    def __init__(self, private_key=None):
        self.w3 = w3
        self.account = None
        if private_key:
            self.account = self.w3.eth.account.from_key(private_key)
            print(f"🔐 Loaded wallet: {self.account.address}")
        else:
            print("⚠️  No private key provided - running in simulation mode")
        
        # Initialize contracts
        self.uniswap_router = w3.eth.contract(address=UNISWAP_V3_ROUTER, abi=UNISWAP_V3_ROUTER_ABI)
        self.aerodrome_router = w3.eth.contract(address=AERODROME_ROUTER, abi=AERODROME_ROUTER_ABI)
        self.balancer_vault = w3.eth.contract(address=BALANCER_V2_VAULT, abi=BALANCER_V2_VAULT_ABI)
        
        # Initialize flash loan contracts
        self.aave_lending_pool = w3.eth.contract(address=Web3.to_checksum_address(AAVE_LENDING_POOL), abi=AAVE_LENDING_POOL_ABI)
        
        # Initialize flash loan receiver contract
        if FLASH_LOAN_RECEIVER_ADDRESS != "0x0000000000000000000000000000000000000000":
            self.flash_loan_receiver = w3.eth.contract(
                address=Web3.to_checksum_address(FLASH_LOAN_RECEIVER_ADDRESS), 
                abi=FLASH_LOAN_RECEIVER_ABI
            )
            print(f"🔐 Flash loan receiver contract: {FLASH_LOAN_RECEIVER_ADDRESS}")
        else:
            self.flash_loan_receiver = None
            print("⚠️  Flash loan receiver contract not deployed - flash loans disabled")
            print("   Deploy flash_loan_receiver.sol first and set FLASH_LOAN_RECEIVER_ADDRESS")
        
    def validate_opportunity(self, opportunity):
        """Validate if an opportunity is realistic and executable"""
        profit_pct = opportunity['profit_pct']
        # Allow any opportunity with profit_pct > 20%
        if profit_pct > 20:
            return True, "Profit percentage above 20%, running regardless of expected net profit."
        # SAFETY CHECKS FOR TESTING
        if SAFE_MODE:
            # Only allow very small amounts for testing
            if POSITION_SIZE_USD > 10:
                return False, f"Position size ${POSITION_SIZE_USD} too large for testing mode"
            # Only allow profit up to MAX_PROFIT_PCT for safety
            if profit_pct > MAX_PROFIT_PCT:
                return False, f"Profit {profit_pct:.2f}% too high for safe testing (max {MAX_PROFIT_PCT}%)"
            # Only allow major tokens for safety
            safe_tokens = ['WETH', 'USDC', 'USDT', 'cbBTC', 'cbETH', 'wstETH']
            pair_tokens = opportunity['pair'].split('/')
            if not any(token in safe_tokens for token in pair_tokens):
                return False, f"Pair {opportunity['pair']} contains non-safe tokens"
        # Check if profit is within realistic bounds
        if profit_pct < MIN_PROFIT_PCT or profit_pct > MAX_PROFIT_PCT:
            return False, f"Profit {profit_pct:.2f}% outside realistic bounds ({MIN_PROFIT_PCT}%-{MAX_PROFIT_PCT}%)"
        # Check liquidity (if available)
        if 'tvl' in opportunity.get('profit_analysis', {}):
            tvl = opportunity['profit_analysis']['tvl']
            if tvl < MIN_LIQUIDITY_USD:
                return False, f"Insufficient liquidity: ${tvl:,.0f} < ${MIN_LIQUIDITY_USD:,.0f}"
        return True, "Opportunity validated"
    
    def get_token_contract(self, token_address):
        """Get ERC20 token contract"""
        return self.w3.eth.contract(address=Web3.to_checksum_address(token_address), abi=ERC20_ABI)
    
    def check_token_balance(self, token_address):
        """Check token balance for the wallet"""
        if not self.account:
            raise ValueError("No account loaded")
            
        try:
            token_contract = self.get_token_contract(token_address)
            
            # Test if contract is accessible
            try:
                symbol = token_contract.functions.symbol().call()
                print(f"   Contract symbol: {symbol}")
            except Exception as e:
                print(f"   Warning: Could not get symbol for {token_address}: {e}")
            
            balance = token_contract.functions.balanceOf(self.account.address).call()
            return balance
            
        except Exception as e:
            print(f"   Error accessing contract {token_address}: {e}")
            # Return 0 if contract is not accessible
            return 0
    
    def check_uniswap_pool_exists(self, token0, token1, fee):
        """Check if a Uniswap V3 pool exists for the given tokens and fee"""
        try:
            factory_contract = self.w3.eth.contract(address=UNISWAP_V3_FACTORY, abi=UNISWAP_V3_FACTORY_ABI)
            pool_address = factory_contract.functions.getPool(token0, token1, fee).call()
            if pool_address == "0x0000000000000000000000000000000000000000":
                return False, None
            return True, pool_address
        except Exception as e:
            print(f"[DEBUG] Error checking pool existence: {e}")
            return False, None
    
    def approve_token(self, token_address, spender_address, amount):
        """Approve token spending"""
        if not self.account:
            raise ValueError("No account loaded")
            
        token_contract = self.get_token_contract(token_address)
        
        # Check current allowance
        current_allowance = token_contract.functions.allowance(self.account.address, spender_address).call()
        
        if current_allowance < amount:
            # Build approval transaction
            approve_function = token_contract.functions.approve(spender_address, amount)
            
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            gas_price = self.w3.eth.gas_price
            
            tx = approve_function.build_transaction({
                'from': self.account.address,
                'gas': 100000,
                'gasPrice': gas_price,
                'nonce': nonce
            })
            
            if not SIMULATION_MODE:
                # Sign and send approval
                signed_tx = self.account.sign_transaction(tx)
                tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
                print(f"✅ Approval sent: {tx_hash.hex()}")
                
                # Wait for confirmation
                receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
                if receipt["status"] == 1:
                    print(f"✅ Approval confirmed!")
                    return True
                else:
                    print("❌ Approval failed")
                    return False
            else:
                print(f"📊 Simulation: Would approve {amount} tokens")
                return True
        
        return True  # Already approved
    
    def execute_uniswap_swap(self, token_in, token_out, amount_in, amount_out_min, fee):
        """Execute swap on Uniswap V3"""
        if not self.account:
            raise ValueError("No account loaded")
        
        # Ensure fee is uint24
        fee_uint24 = int(fee) & 0xFFFFFF

        # --- DEBUG: Print decimals and swap params ---
        try:
            token_in_contract = self.get_token_contract(token_in)
            token_out_contract = self.get_token_contract(token_out)
            decimals_in = token_in_contract.functions.decimals().call()
            decimals_out = token_out_contract.functions.decimals().call()
            print(f"[DEBUG] Uniswap swap params BEFORE DECIMAL FIX:")
            print(f"   tokenIn: {token_in} (decimals: {decimals_in})")
            print(f"   tokenOut: {token_out} (decimals: {decimals_out})")
            print(f"   amountIn: {amount_in}")
            print(f"   amountOutMin: {amount_out_min}")
            print(f"   fee: {fee_uint24}")

            # Fix amount_in and amount_out_min to correct decimals
            # If amount_in is for USDC (6 decimals), convert from 18 to 6 if too large
            if decimals_in == 6 and amount_in > 1e12:
                amount_in = int(amount_in / 1e12)
                print(f"[DEBUG] Adjusted amountIn for USDC decimals: {amount_in}")
            # If amount_out_min is for USDC (6 decimals), convert from 18 to 6 if too large
            if decimals_out == 6 and amount_out_min > 1e12:
                amount_out_min = int(amount_out_min / 1e12)
                print(f"[DEBUG] Adjusted amountOutMin for USDC decimals: {amount_out_min}")
            # If amount_in is for WETH (18 decimals), convert from 6 to 18 if too small
            if decimals_in == 18 and amount_in < 1e12:
                amount_in = int(amount_in * 1e12)
                print(f"[DEBUG] Adjusted amountIn for WETH decimals: {amount_in}")
            # If amount_out_min is for WETH (18 decimals), convert from 6 to 18 if too small
            if decimals_out == 18 and amount_out_min < 1e12:
                amount_out_min = int(amount_out_min * 1e12)
                print(f"[DEBUG] Adjusted amountOutMin for WETH decimals: {amount_out_min}")
            print(f"[DEBUG] Uniswap swap params AFTER DECIMAL FIX:")
            print(f"   amountIn: {amount_in}")
            print(f"   amountOutMin: {amount_out_min}")
        except Exception as e:
            print(f"[DEBUG] Could not fetch token decimals: {e}")

        params = {
            'tokenIn': Web3.to_checksum_address(token_in),
            'tokenOut': Web3.to_checksum_address(token_out),
            'fee': fee_uint24,
            'recipient': self.account.address,
            'amountIn': amount_in,
            'amountOutMinimum': amount_out_min,
            'sqrtPriceLimitX96': 0
        }
        
        # Check if the pool exists for the given fee tier
        token_in_checksum = Web3.to_checksum_address(token_in)
        token_out_checksum = Web3.to_checksum_address(token_out)
        pool_exists, pool_address = self.check_uniswap_pool_exists(token_in_checksum, token_out_checksum, fee_uint24)
        if not pool_exists:
            print(f"❌ Uniswap V3 pool does not exist for tokens {token_in}/{token_out} with fee {fee_uint24}")
            return False
        print(f"[DEBUG] Pool exists: {pool_address}")
        
        # Build transaction
        swap_function = self.uniswap_router.functions.exactInputSingle(params)
        
        nonce = self.w3.eth.get_transaction_count(self.account.address)
        gas_price = self.w3.eth.gas_price
        
        tx = swap_function.build_transaction({
            'from': self.account.address,
            'gas': 300000,
            'gasPrice': gas_price,
            'nonce': nonce
        })
        
        if not SIMULATION_MODE:
            # Sign and send swap
            signed_tx = self.account.sign_transaction(tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            print(f"✅ Uniswap swap sent: {tx_hash.hex()}")
            
            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            if receipt["status"] == 1:
                print(f"✅ Uniswap swap confirmed!")
                return True
            else:
                print("❌ Uniswap swap failed")
                # Try to get more details about the failure
                try:
                    # Get the transaction to see if there's an error
                    tx_data = self.w3.eth.get_transaction(tx_hash)
                    print(f"   Transaction data: {tx_data}")
                    
                    # Try to call the function with call() to see if it would succeed
                    try:
                        result = swap_function.call()
                        print(f"   Call simulation result: {result}")
                    except Exception as call_error:
                        print(f"   Call simulation failed: {call_error}")
                        
                        # Try to decode the revert reason
                        try:
                            # Try to get the revert reason from the transaction
                            tx_receipt = self.w3.eth.get_transaction_receipt(tx_hash)
                            if 'logs' in tx_receipt:
                                print(f"   Transaction logs: {tx_receipt['logs']}")
                        except Exception as log_error:
                            print(f"   Could not get transaction logs: {log_error}")
                except Exception as e:
                    print(f"   Could not get transaction details: {e}")
                return False
        else:
            print(f"📊 Simulation: Would swap {amount_in} tokens on Uniswap")
            return True
    
    def execute_flash_loan_arbitrage(self, opportunity):
        """Execute arbitrage using flash loans for capital efficiency"""
        if not self.account:
            print("❌ Cannot execute flash loan - no wallet loaded")
            return False
        
        try:
            print(f"🚀 Executing FLASH LOAN arbitrage: {opportunity['pair']}")
            print(f"   Buy on {opportunity['buy_dex']} @ {opportunity['buy_price']:.6f}")
            print(f"   Sell on {opportunity['sell_dex']} @ {opportunity['sell_price']:.6f}")
            print(f"   Expected profit: {opportunity['profit_pct']:.2f}%")
            print(f"   Flash loan amount: ${FLASH_LOAN_AMOUNT_USD:,.0f}")
            
            # Parse token addresses
            pair_tokens = opportunity['pair'].split('/')
            token0_symbol, token1_symbol = pair_tokens[0], pair_tokens[1]
            
            # Get token addresses
            token_addresses = {
                'WETH': WETH_BASE,
                'USDC': USDC_BASE,
                'weETH': weETH_BASE,
                'USDT': USDC_BASE,
                'cbBTC': WETH_BASE,
                'cbETH': WETH_BASE,
                'wstETH': WETH_BASE
            }
            
            token0_address = token_addresses.get(token0_symbol, WETH_BASE)
            token1_address = token_addresses.get(token1_symbol, WETH_BASE)
            
            # Determine which token to flash loan (usually the more liquid one)
            flash_loan_token = token0_address if token0_symbol == 'WETH' else token1_address
            flash_loan_symbol = token0_symbol if token0_symbol == 'WETH' else token1_symbol
            
            # Calculate flash loan amount in wei
            eth_price_usd = 2500
            flash_loan_amount_eth = FLASH_LOAN_AMOUNT_USD / eth_price_usd
            flash_loan_amount_wei = int(flash_loan_amount_eth * 1e18)
            
            print(f"   Flash loan token: {flash_loan_symbol} ({flash_loan_token})")
            print(f"   Flash loan amount: {flash_loan_amount_wei} wei (${FLASH_LOAN_AMOUNT_USD:,.0f})")
            
            # Execute flash loan arbitrage
            success = self.execute_flash_loan_operation(
                flash_loan_token,
                flash_loan_amount_wei,
                opportunity['buy_dex'],
                opportunity['sell_dex'],
                token0_address,
                token1_address,
                opportunity
            )
            
            if success:
                print("✅ Flash loan arbitrage executed successfully!")
                return True
            else:
                print("❌ Flash loan arbitrage failed")
                return False
                
        except Exception as e:
            print(f"❌ Flash loan execution failed: {e}")
            return False
    
    def execute_flash_loan_operation(self, flash_loan_token, flash_loan_amount, buy_dex, sell_dex, token0, token1, opportunity=None):
        """Execute the flash loan operation with arbitrage"""
        if not self.account:
            print("❌ Cannot execute flash loan - no wallet loaded")
            return False
        if not self.flash_loan_receiver:
            print("❌ Flash loan receiver contract not deployed")
            print("   Deploy flash_loan_receiver.sol first and set FLASH_LOAN_RECEIVER_ADDRESS")
            return False
        try:
            print(f"🔐 Initiating flash loan for {flash_loan_amount} wei...")
            print(f"   Using contract-based flash loan (atomic execution)")
            # Step 1: Request flash loan through the receiver contract
            if not SIMULATION_MODE:
                # Determine buyFee and sellFee (uint24)
                if opportunity:
                    print(f"[DEBUG] Opportunity fee tiers: uniswap_fee_tier={opportunity.get('uniswap_fee_tier')}, aerodrome_fee_tier={opportunity.get('aerodrome_fee_tier')}")
                    print(f"[DEBUG] buy_dex={buy_dex}, sell_dex={sell_dex}")
                    if buy_dex == 'Uniswap':
                        buyFee = opportunity.get('uniswap_fee_tier')
                        print(f"[DEBUG] buyFee (Uniswap) = {buyFee}")
                        if buyFee is None:
                            print(f"❌ No Uniswap fee tier for buy side of {opportunity['pair']}, skipping opportunity.")
                            return False
                        buyFee = int(buyFee)
                    elif buy_dex == 'Aerodrome':
                        buyFee = opportunity.get('aerodrome_fee_tier', 0)
                        print(f"[DEBUG] buyFee (Aerodrome) = {buyFee}")
                        buyFee = int(buyFee)
                    else:
                        print(f"❌ Unknown buy DEX: {buy_dex}, skipping opportunity.")
                        return False
                    if sell_dex == 'Uniswap':
                        sellFee = opportunity.get('uniswap_fee_tier')
                        print(f"[DEBUG] sellFee (Uniswap) = {sellFee}")
                        if sellFee is None:
                            print(f"❌ No Uniswap fee tier for sell side of {opportunity['pair']}, skipping opportunity.")
                            return False
                        sellFee = int(sellFee)
                    elif sell_dex == 'Aerodrome':
                        sellFee = opportunity.get('aerodrome_fee_tier', 0)
                        print(f"[DEBUG] sellFee (Aerodrome) = {sellFee}")
                        sellFee = int(sellFee)
                    else:
                        print(f"❌ Unknown sell DEX: {sell_dex}, skipping opportunity.")
                        return False
                # Build flash loan request transaction
                flash_loan_function = self.flash_loan_receiver.functions.requestFlashLoan(
                    flash_loan_token,      # asset to flash loan
                    flash_loan_amount,     # amount to borrow
                    token0,                # tokenIn for arbitrage
                    token1,                # tokenOut for arbitrage
                    buy_dex,               # buyDex
                    sell_dex,              # sellDex
                    flash_loan_amount,     # buyAmount
                    flash_loan_amount,     # sellAmount
                    buyFee,                # buyFee (uint24)
                    sellFee                # sellFee (uint24)
                )
                nonce = self.w3.eth.get_transaction_count(self.account.address)
                gas_price = self.w3.eth.gas_price
                tx = flash_loan_function.build_transaction({
                    'from': self.account.address,
                    'gas': 1000000,  # Higher gas for flash loan
                    'gasPrice': gas_price,
                    'nonce': nonce
                })
                # Sign and send flash loan
                signed_tx = self.account.sign_transaction(tx)
                tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
                print(f"✅ Flash loan requested: {tx_hash.hex()}")
                # Wait for flash loan confirmation
                receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
                if receipt["status"] != 1:
                    print("❌ Flash loan failed")
                    print("   This might be because:")
                    print("   - Flash loan receiver contract not deployed")
                    print("   - Insufficient liquidity in Aave pool")
                    print("   - Flash loan not supported for this token")
                    print("   - Arbitrage execution failed in contract")
                    return False
                print("✅ Flash loan executed successfully!")
                # Step 2: Check if we have profit in the receiver contract
                try:
                    # Check token balance in receiver contract
                    token_contract = self.get_token_contract(flash_loan_token)
                    receiver_balance = token_contract.functions.balanceOf(FLASH_LOAN_RECEIVER_ADDRESS).call()
                    if receiver_balance > 0:
                        print(f"💰 Profit detected in receiver contract: {receiver_balance} wei")
                        # Withdraw profit from receiver contract
                        withdraw_function = self.flash_loan_receiver.functions.withdrawToken(
                            flash_loan_token,
                            receiver_balance
                        )
                        nonce = self.w3.eth.get_transaction_count(self.account.address)
                        gas_price = self.w3.eth.gas_price
                        tx = withdraw_function.build_transaction({
                            'from': self.account.address,
                            'gas': 100000,
                            'gasPrice': gas_price,
                            'nonce': nonce
                        })
                        signed_tx = self.account.sign_transaction(tx)
                        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
                        print(f"✅ Profit withdrawal sent: {tx_hash.hex()}")
                        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
                        if receipt["status"] == 1:
                            print("✅ Profit withdrawn successfully!")
                        else:
                            print("❌ Profit withdrawal failed")
                    else:
                        print("⚠️  No profit detected in receiver contract")
                except Exception as e:
                    print(f"⚠️  Could not check/withdraw profit: {e}")
                return True
            else:
                print(f"📊 Simulation: Would execute flash loan for {flash_loan_amount} wei")
                print(f"   Would buy on {buy_dex}")
                print(f"   Would sell on {sell_dex}")
                print(f"   Would repay flash loan automatically")
                return True
        except Exception as e:
            print(f"❌ Flash loan operation failed: {e}")
            print("   Note: Flash loans require a deployed receiver contract")
            print("   with executeOperation() callback implementation")
            return False
    
    def execute_arbitrage(self, opportunity):
        """Execute the arbitrage trade with live price checking and gas estimation"""
        if not self.account:
            print("❌ Cannot execute - no wallet loaded")
            return False
        try:
            # Validate opportunity
            is_valid, message = self.validate_opportunity(opportunity)
            if not is_valid:
                print(f"❌ {message}")
                return False
            print(f"🚀 Executing arbitrage: {opportunity['pair']}")
            print(f"   Buy on {opportunity['buy_dex']} @ {opportunity['buy_price']:.6f}")
            print(f"   Sell on {opportunity['sell_dex']} @ {opportunity['sell_price']:.6f}")
            print(f"   Expected profit: {opportunity['profit_pct']:.2f}%")
            print(f"   Position size: ${POSITION_SIZE_USD}")
            print(f"   Mode: {'SIMULATION' if SIMULATION_MODE else 'LIVE'}")
            # SAFETY CHECK: Confirm execution
            if SAFE_MODE:
                print(f"⚠️  SAFE MODE: This is a test trade with ${POSITION_SIZE_USD}")
                print(f"   Max potential loss: ${POSITION_SIZE_USD * 0.05:.2f} (5% slippage)")
            # Parse token addresses from opportunity
            pair_tokens = opportunity['pair'].split('/')
            token0_symbol, token1_symbol = pair_tokens[0], pair_tokens[1]
            # Calculate amounts first
            eth_amount = POSITION_SIZE_USD / 2500  # Convert USD to ETH
            token_amount = int(eth_amount * 1e18)  # Convert to wei
            # Use actual token addresses from the opportunity
            token0_address = opportunity.get('token0_address', WETH_BASE)
            token1_address = opportunity.get('token1_address', WETH_BASE)
            print(f"   Token0: {token0_symbol} ({token0_address})")
            print(f"   Token1: {token1_symbol} ({token1_address})")
            print(f"   Required amount: {token_amount} wei (${POSITION_SIZE_USD})")
            # Determine input and output tokens based on arbitrage direction
            if opportunity['buy_dex'] == 'Uniswap' and opportunity['sell_dex'] == 'Aerodrome':
                input_token_symbol = token0_symbol
                input_token_address = token0_address
                output_token_symbol = token1_symbol
                output_token_address = token1_address
            else:
                input_token_symbol = token0_symbol
                input_token_address = token0_address
                output_token_symbol = token1_symbol
                output_token_address = token1_address
            print(f"   Input token: {input_token_symbol} ({input_token_address})")
            print(f"   Output token: {output_token_symbol} ({output_token_address})")
            # Validate that we're not trying to swap the same token
            if input_token_address == output_token_address:
                print(f"❌ Invalid swap: Cannot swap {input_token_symbol} for {output_token_symbol}")
                print(f"   Both tokens have the same address: {input_token_address}")
                return False
            # Check live prices before executing
            print(f"🔍 Checking live prices before execution...")
            # Get live price for buy DEX
            live_buy_price = None
            if opportunity['buy_dex'] == 'Uniswap':
                pool_address = opportunity.get('uniswap_pool_address')
                if pool_address:
                    live_buy_price = get_live_uniswap_price(
                        pool_address, 
                        input_token_address, 
                        output_token_address, 
                        opportunity.get('uniswap_fee_tier', 3000)
                    )
            elif opportunity['buy_dex'] == 'Aerodrome':
                pair_address = opportunity.get('aerodrome_pool_address')
                if pair_address:
                    live_buy_price = get_live_aerodrome_price(pair_address)
            if live_buy_price:
                print(f"   Live {opportunity['buy_dex']} price: {live_buy_price:.6f}")
                print(f"   Subgraph {opportunity['buy_dex']} price: {opportunity['buy_price']:.6f}")
                price_diff = abs(live_buy_price - opportunity['buy_price']) / opportunity['buy_price'] * 100
                print(f"   Price difference: {price_diff:.2f}%")
                if price_diff > 5:  # If price differs by more than 5%, skip
                    print(f"   ⚠️  Price difference too large, skipping opportunity")
                    return False
            # Check if we have the input tokens, convert ETH if needed
            if not check_and_convert_eth_if_needed(self, input_token_address, input_token_symbol, token_amount):
                print(f"❌ Cannot proceed without sufficient {input_token_symbol}")
                return False
            # Calculate amounts with slippage
            amount_out_min = int(token_amount * (1 - MAX_SLIPPAGE))
            print(f"   Amount: {token_amount} wei")
            print(f"   Min out: {amount_out_min} wei")
            # --- GAS ESTIMATION AND PROFIT CHECK ---
            expected_profit_usd = opportunity['profit_analysis']['net_profit_usd']
            gas_eth, gas_usd, gas_details = self.estimate_gas_for_arbitrage(opportunity, token_amount, amount_out_min)
            print(f"   Estimated total gas: {gas_eth:.6f} ETH (${gas_usd:.2f})")
            print(f"   Gas breakdown: {gas_details}")
            print(f"   Expected net profit (before gas): ${expected_profit_usd:.4f}")
            print(f"   Expected net profit (after gas): ${expected_profit_usd - gas_usd:.4f}")
            if expected_profit_usd - gas_usd <= 0:
                print(f"❌ Skipping trade: expected profit does not cover gas cost.")
                return False
            # Execute arbitrage
            success = self.execute_arbitrage_swaps(
                opportunity['buy_dex'], 
                opportunity['sell_dex'],
                input_token_address,
                output_token_address,
                token_amount,
                amount_out_min,
                opportunity=opportunity
            )
            if success:
                print("✅ Arbitrage executed successfully!")
                # Analyze realized profit after trade
                print("\n[Post-Trade Analysis]")
                # Get balances after trade
                weth_balance_after = self.check_token_balance(WETH_BASE)
                usdc_balance_after = self.check_token_balance(USDC_BASE)
                # If you want to track before/after, you need to snapshot before trade as well
                # For now, just print after-trade balances
                print(f"   WETH balance after: {weth_balance_after / 1e18:.6f} WETH")
                print(f"   USDC balance after: {usdc_balance_after / 1e6:.2f} USDC")
                # Optionally, estimate total USD value
                eth_price_usd = 2500
                total_usd = (weth_balance_after / 1e18) * eth_price_usd + (usdc_balance_after / 1e6)
                print(f"   Estimated total wallet value: ${total_usd:,.2f} (using WETH=${eth_price_usd})")
                # Auto-convert any non-WETH tokens back to WETH if detected
                self.auto_convert_non_weth_to_weth(min_swap_usd=5.0)
                # Print all token balances after conversion
                self.print_balances()
                return True
            else:
                print("❌ Arbitrage execution failed")
                return False
        except Exception as e:
            print(f"❌ Execution failed: {e}")
            return False
    
    def execute_arbitrage_swaps(self, buy_dex, sell_dex, token0, token1, amount, amount_out_min, opportunity=None):
        try:
            # Step 1: Approve tokens for buy DEX
            print(f"🔐 Approving tokens for {buy_dex}...")
            if buy_dex == 'Uniswap':
                if not self.approve_token(token0, UNISWAP_V3_ROUTER, amount):
                    return False
            elif buy_dex == 'Aerodrome':
                # Add approval logic if needed for Aerodrome
                pass
            elif buy_dex == 'Balancer V2':
                if not self.approve_token(token0, BALANCER_V2_VAULT, amount):
                    return False
            else:
                print(f"❌ Unsupported DEX: {buy_dex}")
                return False
            
            # Step 2: Execute buy swap
            print(f"🔄 Executing buy on {buy_dex}...")
            expected_usdc_out = None
            try:
                if buy_dex == 'Uniswap':
                    fee = opportunity['uniswap_fee_tier'] if opportunity and 'uniswap_fee_tier' in opportunity else 3000
                    if not self.execute_uniswap_swap(token0, token1, amount, amount_out_min, fee):
                        return False
                elif buy_dex == 'Aerodrome':
                    fee = opportunity['aerodrome_fee_tier'] if opportunity and 'aerodrome_fee_tier' in opportunity else None
                    buy_price = opportunity['buy_price'] if opportunity else None
                    if not self.execute_aerodrome_swap(token0, token1, amount, amount_out_min, fee, buy_price=buy_price):
                        return False
                    # For Aerodrome, estimate USDC out: amount (WETH) * buy_price (USDC/WETH)
                    decimals_in = 18  # WETH
                    decimals_out = 6  # USDC
                    amount_in_float = amount / (10 ** decimals_in)
                    expected_usdc_out = int(amount_in_float * buy_price * (10 ** decimals_out))
                    print(f"[DEBUG] Estimated USDC out from Aerodrome buy: {expected_usdc_out}")
                elif buy_dex == 'Balancer V2':
                    pool_address = opportunity.get('balancer_pool_address') if opportunity else None
                    if not self.execute_balancer_v2_swap(token0, token1, amount, amount_out_min, pool_address):
                        return False
                    # For Balancer V2, estimate USDC out: amount (WETH) * buy_price (USDC/WETH)
                    buy_price = opportunity['buy_price'] if opportunity else 2532.5
                    decimals_in = 18  # WETH
                    decimals_out = 6  # USDC
                    amount_in_float = amount / (10 ** decimals_in)
                    expected_usdc_out = int(amount_in_float * buy_price * (10 ** decimals_out))
                    print(f"[DEBUG] Estimated USDC out from Balancer V2 buy: {expected_usdc_out}")
            except Exception as e:
                print(f"❌ Buy swap failed on {buy_dex}: {e}")
                return False
            
            # Step 3: Approve tokens for sell DEX and calculate min_out
            print(f"🔐 Approving tokens for {sell_dex}...")
            min_out = amount_out_min
            sell_amount = expected_usdc_out if expected_usdc_out is not None else amount
            if sell_dex == 'Uniswap':
                # Calculate expected output and min out for sell swap
                sell_price = opportunity['sell_price'] if opportunity else 1
                token_in_contract = self.get_token_contract(token1)
                token_out_contract = self.get_token_contract(token0)
                decimals_in = token_in_contract.functions.decimals().call()
                decimals_out = token_out_contract.functions.decimals().call()
                amount_in_float = sell_amount / (10 ** decimals_in)
                print(f"[DEBUG] amount_in_float (USDC): {amount_in_float}")
                print(f"[DEBUG] sell_price: {sell_price}")
                expected_output = amount_in_float / sell_price
                print(f"[DEBUG] expected_output (WETH): {expected_output}")
                min_out_float = expected_output * (1 - MAX_SLIPPAGE)
                print(f"[DEBUG] min_out_float (WETH): {min_out_float}")
                min_out = int(min_out_float * (10 ** decimals_out))
                print(f"[DEBUG] min_out (WETH, int): {min_out}")
                
                # For testing, try with 0 min out to see if the issue is slippage
                min_out = 0
                print(f"[DEBUG] Using min_out = 0 for testing")
                if not self.approve_token(token1, UNISWAP_V3_ROUTER, sell_amount):
                    return False
            elif sell_dex == 'Balancer V2':
                if not self.approve_token(token1, BALANCER_V2_VAULT, sell_amount):
                    return False
            
            # Step 4: Execute sell swap
            print(f"🔄 Executing sell on {sell_dex}...")
            try:
                if sell_dex == 'Uniswap':
                    fee = opportunity['uniswap_fee_tier'] if opportunity and 'uniswap_fee_tier' in opportunity else 3000
                    
                    # Check live price before executing Uniswap swap
                    if opportunity and 'uniswap_pool_address' in opportunity:
                        live_price = get_live_uniswap_price(
                            opportunity['uniswap_pool_address'],
                            token0,  # WETH (token0)
                            token1,  # USDC (token1)
                            fee
                        )
                        if live_price:
                            print(f"[DEBUG] Live Uniswap price: {live_price}")
                            print(f"[DEBUG] Expected price: {sell_price}")
                            # Convert live price to USDC per WETH for comparison
                            live_price_usdc_per_weth = 1 / live_price if live_price > 0 else 0
                            print(f"[DEBUG] Live price (USDC per WETH): {live_price_usdc_per_weth}")
                            price_diff = abs(live_price_usdc_per_weth - sell_price) / sell_price * 100
                            print(f"[DEBUG] Price difference: {price_diff:.2f}%")
                            if price_diff > 5:
                                print(f"⚠️  Live price differs by {price_diff:.2f}%, but proceeding anyway")
                    
                    print(f"[DEBUG] Uniswap sell parameters:")
                    print(f"   tokenIn: {token1} (USDC)")
                    print(f"   tokenOut: {token0} (WETH)")
                    print(f"   amountIn: {sell_amount} (USDC)")
                    print(f"   amountOutMin: {min_out} (WETH)")
                    print(f"   fee: {fee}")
                    print(f"   pool_address: {opportunity.get('uniswap_pool_address', 'N/A') if opportunity else 'N/A'}")
                    
                    # Check if we have enough USDC for the swap
                    usdc_balance = self.check_token_balance(token1)
                    print(f"[DEBUG] USDC balance: {usdc_balance}")
                    print(f"[DEBUG] Required USDC: {sell_amount}")
                    if usdc_balance < sell_amount:
                        print(f"❌ Insufficient USDC balance for swap")
                        return False
                    
                    if not self.execute_uniswap_swap(token1, token0, sell_amount, min_out, fee):
                        return False
                elif sell_dex == 'Aerodrome':
                    fee = opportunity['aerodrome_fee_tier'] if opportunity and 'aerodrome_fee_tier' in opportunity else None
                    if not self.execute_aerodrome_swap(token1, token0, amount, min_out, fee):
                        return False
                elif sell_dex == 'Balancer V2':
                    pool_address = opportunity.get('balancer_pool_address') if opportunity else None
                    if not self.execute_balancer_v2_swap(token1, token0, sell_amount, min_out, pool_address):
                        return False
            except Exception as e:
                print(f"❌ Sell swap failed on {sell_dex}: {e}")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Swap execution failed: {e}")
            return False
    
    def check_available_tokens(self):
        """Check what tokens are available in the wallet"""
        if not self.account:
            print("❌ No account loaded")
            return
        
        print(f"🔍 Checking available tokens for {self.account.address}...")
        
        # Common tokens to check
        tokens_to_check = {
            'WETH': WETH_BASE,
            'USDC': USDC_BASE,
            'weETH': weETH_BASE
        }
        
        for symbol, address in tokens_to_check.items():
            try:
                balance = self.check_token_balance(address)
                if balance > 0:
                    print(f"   ✅ {symbol}: {balance} wei")
                else:
                    print(f"   ❌ {symbol}: 0 wei")
            except Exception as e:
                print(f"   ❌ {symbol}: Error - {e}")

    def execute_aerodrome_swap(self, token_in, token_out, amount_in, amount_out_min, fee=None, buy_price=None):
        """Execute swap on Aerodrome"""
        if not self.account:
            raise ValueError("No account loaded")
        # Approve token if needed
        if not self.approve_token(token_in, AERODROME_ROUTER, amount_in):
            print(f"❌ Approval failed for Aerodrome swap")
            return False
        # Build route (single hop)
        # For Aerodrome, stable = False for WETH/USDC
        route = [{
            'from': Web3.to_checksum_address(token_in),
            'to': Web3.to_checksum_address(token_out),
            'stable': False,
            'factory': Web3.to_checksum_address('0x420DD381b31aEf6683db6B902084cB0FFECe40Da')  # Aerodrome default factory (Base)
        }]
        # Deadline: 5 minutes from now
        latest_block = self.w3.eth.get_block('latest')
        deadline = latest_block.get('timestamp', 0) + 300
        # --- FIX: Calculate amount_out_min in output token decimals (USDC, 6) ---
        try:
            token_in_contract = self.get_token_contract(token_in)
            token_out_contract = self.get_token_contract(token_out)
            decimals_in = token_in_contract.functions.decimals().call()
            decimals_out = token_out_contract.functions.decimals().call()
            # Estimate expected output using buy_price if provided
            price = buy_price if buy_price else 2532.5  # fallback to rough price
            amount_in_float = amount_in / (10 ** decimals_in)
            expected_out = amount_in_float * price
            min_out = int(expected_out * (1 - MAX_SLIPPAGE) * (10 ** decimals_out))
            print(f"[DEBUG] Aerodrome swap: amount_in={amount_in}, price={price}, expected_out={expected_out}, min_out={min_out}")
            amount_out_min = min_out
        except Exception as e:
            print(f"[DEBUG] Could not calculate min_out for Aerodrome swap: {e}")
        # Build transaction
        swap_function = self.aerodrome_router.functions.swapExactTokensForTokens(
            amount_in,
            amount_out_min,
            route,
            self.account.address,
            deadline
        )
        nonce = self.w3.eth.get_transaction_count(self.account.address)
        gas_price = self.w3.eth.gas_price
        tx = swap_function.build_transaction({
            'from': self.account.address,
            'gas': 300000,
            'gasPrice': gas_price,
            'nonce': nonce
        })
        if not SIMULATION_MODE:
            signed_tx = self.account.sign_transaction(tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            print(f"✅ Aerodrome swap sent: {tx_hash.hex()}")
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            if receipt["status"] == 1:
                print(f"✅ Aerodrome swap confirmed!")
                return True
            else:
                print("❌ Aerodrome swap failed")
                return False
        else:
            print(f"📊 Simulation: Would swap {amount_in} tokens on Aerodrome")
            return True

    def convert_eth_to_weth(self, amount_wei):
        """Convert ETH to WETH using the WETH contract"""
        if not self.account:
            raise ValueError("No account loaded")
            
        # WETH contract address on Base
        weth_address = Web3.to_checksum_address("0x4200000000000000000000000000000000000006")
        
        # WETH contract ABI (minimal for deposit)
        weth_abi = [
            {"inputs":[],"name":"deposit","outputs":[],"stateMutability":"payable","type":"function"},
            {"inputs":[{"internalType":"uint256","name":"wad","type":"uint256"}],"name":"withdraw","outputs":[],"stateMutability":"nonpayable","type":"function"}
        ]
        
        weth_contract = self.w3.eth.contract(address=weth_address, abi=weth_abi)
        
        # Check ETH balance
        eth_balance = self.w3.eth.get_balance(self.account.address)
        if eth_balance < amount_wei:
            raise ValueError(f"Insufficient ETH balance: {eth_balance} < {amount_wei}")
        
        print(f"🔄 Converting {amount_wei / 1e18:.6f} ETH to WETH...")
        
        # Build deposit transaction
        deposit_function = weth_contract.functions.deposit()
        
        nonce = self.w3.eth.get_transaction_count(self.account.address)
        gas_price = self.w3.eth.gas_price
        
        tx = deposit_function.build_transaction({
            'from': self.account.address,
            'value': amount_wei,  # Send ETH with the transaction
            'gas': 100000,
            'gasPrice': gas_price,
            'nonce': nonce
        })
        
        if not SIMULATION_MODE:
            # Sign and send conversion
            signed_tx = self.account.sign_transaction(tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            print(f"✅ ETH→WETH conversion sent: {tx_hash.hex()}")
            
            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            if receipt["status"] == 1:
                print(f"✅ ETH→WETH conversion confirmed!")
                return True
            else:
                print("❌ ETH→WETH conversion failed")
                return False
        else:
            print(f"📊 Simulation: Would convert {amount_wei / 1e18:.6f} ETH to WETH")
            return True

    def ensure_sufficient_weth(self, required_amount_wei):
        """Ensure we have sufficient WETH, convert ETH if needed"""
        try:
            # Check current WETH balance
            weth_balance = self.check_token_balance(WETH_BASE)
            
            if weth_balance >= required_amount_wei:
                print(f"✅ Sufficient WETH balance: {weth_balance / 1e18:.6f} WETH")
                return True
            
            # Calculate how much ETH we need to convert
            eth_needed = required_amount_wei - weth_balance
            if eth_needed <= 0:
                return True  # We have enough WETH
                
            print(f"❌ Insufficient WETH: {weth_balance / 1e18:.6f} WETH")
            print(f"   Need: {required_amount_wei / 1e18:.6f} WETH")
            print(f"   Converting: {eth_needed / 1e18:.6f} ETH to WETH")
            
            # Convert ETH to WETH
            return self.convert_eth_to_weth(eth_needed)
            
        except Exception as e:
            print(f"❌ Error ensuring sufficient WETH: {e}")
            return False

    def estimate_gas_for_arbitrage(self, opportunity, amount, amount_out_min):
        """Estimate total gas cost (in ETH and USD) for the arbitrage (approvals + swaps)"""
        gas_price = self.w3.eth.gas_price
        total_gas = 0
        gas_details = {}
        buy_dex = opportunity['buy_dex']
        sell_dex = opportunity['sell_dex']
        token0 = opportunity['token0_address']
        token1 = opportunity['token1_address']
        if not self.account:
            return 0, 0, {}
        account = self.account.address
        # Approval for buy DEX
        if buy_dex == 'Uniswap':
            approve_func = self.get_token_contract(token0).functions.approve(UNISWAP_V3_ROUTER, amount)
            try:
                gas = approve_func.estimate_gas({'from': str(account)})
                gas_details['approve_buy'] = gas
                total_gas += gas
            except Exception as e:
                gas_details['approve_buy'] = 0
        elif buy_dex == 'Aerodrome':
            approve_func = self.get_token_contract(token0).functions.approve(AERODROME_ROUTER, amount)
            try:
                gas = approve_func.estimate_gas({'from': str(account)})
                gas_details['approve_buy'] = gas
                total_gas += gas
            except Exception as e:
                gas_details['approve_buy'] = 0
        elif buy_dex == 'Balancer V2':
            approve_func = self.get_token_contract(token0).functions.approve(BALANCER_V2_VAULT, amount)
            try:
                gas = approve_func.estimate_gas({'from': str(account)})
                gas_details['approve_buy'] = gas
                total_gas += gas
            except Exception as e:
                gas_details['approve_buy'] = 0
        # Buy swap
        if buy_dex == 'Uniswap':
            fee = opportunity['uniswap_fee_tier'] if 'uniswap_fee_tier' in opportunity else 3000
            params = {
                'tokenIn': Web3.to_checksum_address(token0),
                'tokenOut': Web3.to_checksum_address(token1),
                'fee': int(fee) & 0xFFFFFF,
                'recipient': account,
                'amountIn': amount,
                'amountOutMinimum': amount_out_min,
                'sqrtPriceLimitX96': 0
            }
            swap_func = self.uniswap_router.functions.exactInputSingle(params)
            try:
                gas = swap_func.estimate_gas({'from': str(account)})
                gas_details['buy_swap'] = gas
                total_gas += gas
            except Exception as e:
                gas_details['buy_swap'] = 0
        elif buy_dex == 'Aerodrome':
            route = [{
                'from': Web3.to_checksum_address(token0),
                'to': Web3.to_checksum_address(token1),
                'stable': False,
                'factory': Web3.to_checksum_address('0x420DD381b31aEf6683db6B902084cB0FFECe40Da')
            }]
            latest_block = self.w3.eth.get_block('latest')
            deadline = latest_block.get('timestamp', 0) + 300
            swap_func = self.aerodrome_router.functions.swapExactTokensForTokens(amount, amount_out_min, route, account, deadline)
            try:
                gas = swap_func.estimate_gas({'from': str(account)})
                gas_details['buy_swap'] = gas
                total_gas += gas
            except Exception as e:
                gas_details['buy_swap'] = 0
        elif buy_dex == 'Balancer V2':
            # Build single swap parameters for gas estimation
            single_swap = {
                'sender': account,
                'recipient': account,
                'request': 0,
                'tokenIn': Web3.to_checksum_address(token0),
                'tokenOut': Web3.to_checksum_address(token1),
                'amountIn': amount,
                'amountOut': amount_out_min,
                'userData': 0
            }
            funds = {
                'sender': account,
                'fromInternalBalance': False,
                'recipient': account,
                'toInternalBalance': False
            }
            latest_block = self.w3.eth.get_block('latest')
            deadline = latest_block.get('timestamp', 0) + 300
            swap_func = self.balancer_vault.functions.swap(single_swap, funds, amount_out_min, deadline)
            try:
                gas = swap_func.estimate_gas({'from': str(account)})
                gas_details['buy_swap'] = gas
                total_gas += gas
            except Exception as e:
                gas_details['buy_swap'] = 0
        # Approval for sell DEX
        if sell_dex == 'Uniswap':
            approve_func = self.get_token_contract(token1).functions.approve(UNISWAP_V3_ROUTER, amount)
            try:
                gas = approve_func.estimate_gas({'from': str(account)})
                gas_details['approve_sell'] = gas
                total_gas += gas
            except Exception as e:
                gas_details['approve_sell'] = 0
        elif sell_dex == 'Aerodrome':
            approve_func = self.get_token_contract(token1).functions.approve(AERODROME_ROUTER, amount)
            try:
                gas = approve_func.estimate_gas({'from': str(account)})
                gas_details['approve_sell'] = gas
                total_gas += gas
            except Exception as e:
                gas_details['approve_sell'] = 0
        elif sell_dex == 'Balancer V2':
            approve_func = self.get_token_contract(token1).functions.approve(BALANCER_V2_VAULT, amount)
            try:
                gas = approve_func.estimate_gas({'from': str(account)})
                gas_details['approve_sell'] = gas
                total_gas += gas
            except Exception as e:
                gas_details['approve_sell'] = 0
        # Sell swap
        if sell_dex == 'Uniswap':
            fee = opportunity['uniswap_fee_tier'] if 'uniswap_fee_tier' in opportunity else 3000
            params = {
                'tokenIn': Web3.to_checksum_address(token1),
                'tokenOut': Web3.to_checksum_address(token0),
                'fee': int(fee) & 0xFFFFFF,
                'recipient': account,
                'amountIn': amount,
                'amountOutMinimum': 0,
                'sqrtPriceLimitX96': 0
            }
            swap_func = self.uniswap_router.functions.exactInputSingle(params)
            try:
                gas = swap_func.estimate_gas({'from': str(account)})
                gas_details['sell_swap'] = gas
                total_gas += gas
            except Exception as e:
                gas_details['sell_swap'] = 0
        elif sell_dex == 'Aerodrome':
            route = [{
                'from': Web3.to_checksum_address(token1),
                'to': Web3.to_checksum_address(token0),
                'stable': False,
                'factory': Web3.to_checksum_address('0x420DD381b31aEf6683db6B902084cB0FFECe40Da')
            }]
            latest_block = self.w3.eth.get_block('latest')
            deadline = latest_block.get('timestamp', 0) + 300
            swap_func = self.aerodrome_router.functions.swapExactTokensForTokens(amount, 0, route, account, deadline)
            try:
                gas = swap_func.estimate_gas({'from': str(account)})
                gas_details['sell_swap'] = gas
                total_gas += gas
            except Exception as e:
                gas_details['sell_swap'] = 0
        elif sell_dex == 'Balancer V2':
            # Build single swap parameters for gas estimation
            single_swap = {
                'sender': account,
                'recipient': account,
                'request': 0,
                'tokenIn': Web3.to_checksum_address(token1),
                'tokenOut': Web3.to_checksum_address(token0),
                'amountIn': amount,
                'amountOut': 0,
                'userData': 0
            }
            funds = {
                'sender': account,
                'fromInternalBalance': False,
                'recipient': account,
                'toInternalBalance': False
            }
            latest_block = self.w3.eth.get_block('latest')
            deadline = latest_block.get('timestamp', 0) + 300
            swap_func = self.balancer_vault.functions.swap(single_swap, funds, 0, deadline)
            try:
                gas = swap_func.estimate_gas({'from': str(account)})
                gas_details['sell_swap'] = gas
                total_gas += gas
            except Exception as e:
                gas_details['sell_swap'] = 0
        gas_eth = total_gas * gas_price / 1e18
        eth_price_usd = 2500
        gas_usd = gas_eth * eth_price_usd
        return gas_eth, gas_usd, gas_details

    def auto_convert_non_weth_to_weth(self, min_swap_usd=1.0):
        """Auto-convert any non-WETH token balances (USDC, etc.) back to WETH if balance > min_swap_usd"""
        eth_price_usd = 2500
        print("\n[Auto-Convert] Wallet balances BEFORE conversion:")
        self.print_balances()
        # Loop over all tokens except WETH
        for symbol, token_address in TOKEN_ADDRESSES.items():
            if symbol == 'WETH' or not token_address:
                continue
            if token_address == WETH_BASE:
                continue  # Don't try to convert WETH to itself
            try:
                balance = self.check_token_balance(token_address)
                if symbol == 'USDC':
                    decimals = 6
                    price_usd = 1
                else:
                    decimals = 18
                    price_usd = eth_price_usd
                balance_float = balance / (10 ** decimals)
                balance_usd = balance_float * price_usd
                print(f"[DEBUG] {symbol} balance before conversion: {balance_float:.8f} ({balance_usd:.2f} USD)")
                if balance_usd >= min_swap_usd and balance > 0:
                    print(f"🔄 Auto-converting {balance_float:.6f} {symbol} (${balance_usd:.2f}) to WETH...")
                    approve_success = self.approve_token(token_address, self.uniswap_router.address, balance)
                    if not approve_success:
                        print(f"❌ Approval failed for {symbol}, skipping conversion.")
                        continue
                    # Try Uniswap first, fallback to Aerodrome if Uniswap fails
                    tx_hash = self.execute_uniswap_swap(token_address, WETH_BASE, balance, 0, 3000)
                    if not tx_hash:
                        print(f"⚠️  Uniswap swap failed, trying Aerodrome...")
                        approve_success = self.approve_token(token_address, self.aerodrome_router.address, balance)
                        if not approve_success:
                            print(f"❌ Approval failed for {symbol} on Aerodrome, skipping conversion.")
                            continue
                        tx_hash = self.execute_aerodrome_swap(token_address, WETH_BASE, balance, 0)
                    if tx_hash:
                        print(f"✅ Swap sent: {tx_hash}")
                        new_balance = self.check_token_balance(token_address)
                        new_balance_float = new_balance / (10 ** decimals)
                        print(f"[DEBUG] {symbol} balance after conversion: {new_balance_float:.8f}")
                        if new_balance < 1:
                            print(f"✅ Auto-converted all {symbol} to WETH!")
                        else:
                            print(f"⚠️  {symbol} balance remains after swap: {new_balance_float:.8f}")
                    else:
                        print(f"❌ Swap failed for {symbol}")
            except Exception as e:
                print(f"❌ Error converting {symbol} to WETH: {e}")
        print("\n[Auto-Convert] Wallet balances AFTER conversion:")
        self.print_balances()

    def print_balances(self):
        """Print all token balances in the wallet for tracked tokens"""
        print("\n📊 Wallet Balances:")
        for symbol, address in TOKEN_ADDRESSES.items():
            try:
                balance = self.check_token_balance(address)
                if symbol == 'USDC':
                    decimals = 6
                else:
                    decimals = 18
                balance_float = balance / (10 ** decimals)
                print(f"   {symbol}: {balance_float:.6f}")
            except Exception as e:
                print(f"   {symbol}: Error - {e}")

    def execute_balancer_v2_swap(self, token_in, token_out, amount_in, amount_out_min, pool_address=None):
        """Execute swap on Balancer V2"""
        if not self.account:
            raise ValueError("No account loaded")
        
        # Approve token if needed
        if not self.approve_token(token_in, BALANCER_V2_VAULT, amount_in):
            print(f"❌ Approval failed for Balancer V2 swap")
            return False
        
        # Build single swap parameters
        single_swap = {
            'sender': self.account.address,
            'recipient': self.account.address,
            'request': 0,  # Single swap
            'tokenIn': Web3.to_checksum_address(token_in),
            'tokenOut': Web3.to_checksum_address(token_out),
            'amountIn': amount_in,
            'amountOut': amount_out_min,
            'userData': 0
        }
        
        # Build fund management parameters
        funds = {
            'sender': self.account.address,
            'fromInternalBalance': False,
            'recipient': self.account.address,
            'toInternalBalance': False
        }
        
        # Deadline: 5 minutes from now
        latest_block = self.w3.eth.get_block('latest')
        deadline = latest_block.get('timestamp', 0) + 300
        
        # Build transaction
        swap_function = self.balancer_vault.functions.swap(
            single_swap,
            funds,
            amount_out_min,  # limit
            deadline
        )
        
        nonce = self.w3.eth.get_transaction_count(self.account.address)
        gas_price = self.w3.eth.gas_price
        
        tx = swap_function.build_transaction({
            'from': self.account.address,
            'gas': 300000,
            'gasPrice': gas_price,
            'nonce': nonce
        })
        
        if not SIMULATION_MODE:
            signed_tx = self.account.sign_transaction(tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            print(f"✅ Balancer V2 swap sent: {tx_hash.hex()}")
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            if receipt["status"] == 1:
                print(f"✅ Balancer V2 swap confirmed!")
                return True
            else:
                print("❌ Balancer V2 swap failed")
                return False
        else:
            print(f"📊 Simulation: Would swap {amount_in} tokens on Balancer V2")
            return True

async def get_aerodrome_prices():
    """Get all Aerodrome pool prices with enhanced monitoring"""
    if not AERODROME_SUBGRAPH:
        print("AERODROME_SUBGRAPH not configured")
        return {}
    
    query = {
        "query": """
        {
          pools(first: 1000, orderBy: totalValueLockedUSD, orderDirection: desc) {
            id
            token0 { id symbol }
            token1 { id symbol }
            token0Price
            token1Price
            totalValueLockedUSD
            volumeUSD
          }
        }
        """
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(AERODROME_SUBGRAPH, json=query) as resp:
                result = await resp.json()
                
                print(f"Aerodrome subgraph response status: {resp.status}")
                if resp.status != 200:
                    print(f"Aerodrome subgraph error: {result}")
                    return {}
                
                if result is None:
                    print("Aerodrome subgraph returned None")
                    return {}
                
                pairs = result.get("data", {}).get("pools", [])
                print(f"Found {len(pairs)} Aerodrome pools")
                
                prices = {}
                processed_count = 0
                for i, pair in enumerate(pairs):
                    if i % 100 == 0:
                        print(f"Processing Aerodrome pool {i}/{len(pairs)}...")
                    
                    try:
                        t0 = pair["token0"]
                        t1 = pair["token1"]
                        pair_key = f"{t0['symbol']}/{t1['symbol']}"
                        
                        price = 1.0
                        if 'token1Price' in pair and pair['token1Price']:
                            price = float(pair['token1Price'])
                        elif 'token0Price' in pair and pair['token0Price']:
                            price = float(pair['token0Price'])
                        
                        tvl = float(pair.get("totalValueLockedUSD", 0))
                        volume = float(pair.get("volumeUSD", 0))
                        
                        # More aggressive filtering
                        if 0.0001 < price < 1000000 and tvl > MIN_LIQUIDITY_USD and volume > 1000:
                            prices[pair_key] = {
                                'price': price,
                                'tvl': tvl,
                                'volume': volume,
                                'pool_id': pair['id'],
                                'token0': t0['id'],
                                'token1': t1['id'],
                                'fee_tier': None  # Aerodrome does not use fee tiers, but keep for consistency
                            }
                            processed_count += 1
                    except Exception as e:
                        continue
                
                print(f"Processed {processed_count} Aerodrome pools")
                return prices
                
    except Exception as e:
        print(f"Error fetching Aerodrome prices: {e}")
        return {}

async def get_balancer_v2_prices():
    """Get all Balancer V2 pool prices with enhanced monitoring"""
    if not BALANCER_V2_SUBGRAPH:
        print("BALANCER_V2_SUBGRAPH not configured")
        return {}
    
    try:
        async with aiohttp.ClientSession() as session:
            # Step 1: Get all pool IDs from balancers
            print("🔍 Step 1: Fetching Balancer V2 pool IDs...")
            pool_ids_query = {
                "query": """
                {
                  balancers {
                    id
                    poolCount
                    pools {
                      id
                    }
                  }
                }
                """
            }
            
            async with session.post(BALANCER_V2_SUBGRAPH, json=pool_ids_query) as resp:
                result = await resp.json()
                
                print(f"Balancer V2 subgraph response status: {resp.status}")
                if resp.status != 200:
                    print(f"Balancer V2 subgraph error: {result}")
                    return {}
                
                if result is None:
                    print("Balancer V2 subgraph returned None")
                    return {}
                
                # Extract pool IDs from balancers
                pool_ids = []
                balancers = result.get("data", {}).get("balancers", [])
                for balancer in balancers:
                    pools = balancer.get("pools", [])
                    for pool in pools:
                        pool_ids.append(pool["id"])
                
                print(f"Found {len(pool_ids)} Balancer V2 pool IDs")
                
                if not pool_ids:
                    print("No pool IDs found")
                    return {}
                
                # Step 2: Query each pool for details (limit to first 100 for performance)
                print("🔍 Step 2: Fetching pool details...")
                prices = {}
                processed_count = 0
                
                # Limit to first 100 pools for performance
                pool_ids_to_query = pool_ids[:100]
                
                for i, pool_id in enumerate(pool_ids_to_query):
                    if i % 10 == 0:
                        print(f"Processing Balancer V2 pool {i}/{len(pool_ids_to_query)}...")
                    
                    try:
                        # Query individual pool details
                        pool_query = {
                            "query": f"""
                            {{
                              pool(id: "{pool_id}") {{
                                id
                                address
                                poolType
                                poolTypeVersion
                                tokens {{
                                  id
                                  symbol
                                  decimals
                                  balance
                                  weight
                                }}
                                swaps(first: 1, orderBy: timestamp, orderDirection: desc) {{
                                  tokenAmountIn
                                  tokenAmountOut
                                  tokenIn
                                  tokenOut
                                }}
                                totalLiquidity
                                totalShares
                              }}
                            }}
                            """
                        }
                        
                        async with session.post(BALANCER_V2_SUBGRAPH, json=pool_query) as pool_resp:
                            pool_result = await pool_resp.json()
                            
                            if pool_resp.status != 200:
                                continue
                            
                            pool_data = pool_result.get("data", {}).get("pool")
                            if not pool_data:
                                continue
                            
                            tokens = pool_data.get("tokens", [])
                            if len(tokens) < 2:
                                continue
                            
                            # Get the first two tokens for price calculation
                            token0 = tokens[0]
                            token1 = tokens[1]
                            
                            # Calculate price based on token balances and weights
                            balance0 = float(token0.get("balance", 0))
                            balance1 = float(token1.get("balance", 0))
                            weight0 = float(token0.get("weight", 0))
                            weight1 = float(token1.get("weight", 0))
                            
                            if balance0 == 0 or balance1 == 0:
                                continue
                            
                            # Calculate price (token1/token0)
                            price = balance1 / balance0
                            
                            # Get total liquidity
                            total_liquidity = float(pool_data.get("totalLiquidity", 0))
                            
                            # Estimate TVL (rough calculation)
                            tvl = total_liquidity * 2  # Rough estimate
                            
                            pair_key = f"{token0['symbol']}/{token1['symbol']}"
                            
                            # Filter for liquid pools
                            if 0.0001 < price < 1000000 and tvl > MIN_LIQUIDITY_USD:
                                prices[pair_key] = {
                                    'price': price,
                                    'tvl': tvl,
                                    'volume': 0,  # Balancer V2 doesn't provide volume in this query
                                    'pool_id': pool_data['id'],
                                    'pool_address': pool_data['address'],
                                    'token0': token0['id'],
                                    'token1': token1['id'],
                                    'fee_tier': None  # Balancer V2 uses dynamic fees
                                }
                                processed_count += 1
                                
                    except Exception as e:
                        print(f"Error processing pool {pool_id}: {e}")
                        continue
                
                print(f"Processed {processed_count} Balancer V2 pools")
                return prices
                
    except Exception as e:
        print(f"Error fetching Balancer V2 prices: {e}")
        return {}

# Add live price checking functions
def get_live_uniswap_price(pool_address, token0_address, token1_address, fee_tier):
    """Get live price from Uniswap V3 pool contract"""
    try:
        # Uniswap V3 Pool ABI (minimal for price checking)
        pool_abi = [
            {"inputs":[],"name":"slot0","outputs":[{"internalType":"uint160","name":"sqrtPriceX96","type":"uint160"},{"internalType":"int24","name":"tick","type":"int24"},{"internalType":"uint16","name":"observationIndex","type":"uint16"},{"internalType":"uint16","name":"observationCardinality","type":"uint16"},{"internalType":"uint16","name":"observationCardinalityNext","type":"uint16"},{"internalType":"uint8","name":"feeProtocol","type":"uint8"},{"internalType":"bool","name":"unlocked","type":"bool"}],"stateMutability":"view","type":"function"},
            {"inputs":[],"name":"token0","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},
            {"inputs":[],"name":"token1","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"}
        ]
        
        pool_contract = w3.eth.contract(address=Web3.to_checksum_address(pool_address), abi=pool_abi)
        
        # Get slot0 data (contains current sqrt price)
        slot0 = pool_contract.functions.slot0().call()
        sqrt_price_x96 = slot0[0]
        
        if sqrt_price_x96 == 0:
            return None
        
        # Calculate price from sqrt price using proper Uniswap V3 formula
        # price = (sqrt_price_x96 / 2^96)^2
        # But we need to handle the Q64.96 format correctly
        sqrt_price_float = sqrt_price_x96 / (2**96)
        price = sqrt_price_float ** 2
        
        # Determine which token is token0 vs token1 to get correct price direction
        pool_token0 = pool_contract.functions.token0().call()
        pool_token1 = pool_contract.functions.token1().call()
        
        print(f"[DEBUG] Live price calculation:")
        print(f"   sqrt_price_x96: {sqrt_price_x96}")
        print(f"   sqrt_price_float: {sqrt_price_float}")
        print(f"   calculated_price: {price}")
        print(f"   pool_token0: {pool_token0}")
        print(f"   pool_token1: {pool_token1}")
        print(f"   input_token0: {token0_address}")
        print(f"   input_token1: {token1_address}")
        
        # For USDC→WETH swap, we want WETH per USDC price
        # The sqrt price represents token1/token0, so if token0 is USDC and token1 is WETH,
        # the price is WETH per USDC
        if token0_address.lower() == pool_token0.lower() and token1_address.lower() == pool_token1.lower():
            # Our input token is pool's token0, output is pool's token1
            # Price is token1/token0, which is what we want
            final_price = price
            print(f"   Using price as-is (token0→token1): {final_price}")
        elif token0_address.lower() == pool_token1.lower() and token1_address.lower() == pool_token0.lower():
            # Our input token is pool's token1, output is pool's token0
            # Need to invert: 1/price
            final_price = 1 / price if price > 0 else None
            print(f"   Using inverted price (token1→token0): {final_price}")
        else:
            # Fallback: assume we want token1/token0 price
            final_price = price
            print(f"   Using fallback price: {final_price}")
        
        return final_price
            
    except Exception as e:
        print(f"Error getting live Uniswap price for {pool_address}: {e}")
        return None

def get_live_aerodrome_price(pair_address):
    """Get live price from Aerodrome pair contract"""
    try:
        # Aerodrome Pair ABI (minimal for price checking)
        pair_abi = [
            {"constant":True,"inputs":[],"name":"getReserves","outputs":[{"internalType":"uint112","name":"_reserve0","type":"uint112"},{"internalType":"uint112","name":"_reserve1","type":"uint112"},{"internalType":"uint32","name":"_blockTimestampLast","type":"uint32"}],"payable":False,"stateMutability":"view","type":"function"},
            {"constant":True,"inputs":[],"name":"token0","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":False,"stateMutability":"view","type":"function"},
            {"constant":True,"inputs":[],"name":"token1","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":False,"stateMutability":"view","type":"function"}
        ]
        
        pair_contract = w3.eth.contract(address=Web3.to_checksum_address(pair_address), abi=pair_abi)
        
        # Get reserves
        reserves = pair_contract.functions.getReserves().call()
        reserve0, reserve1 = reserves[0], reserves[1]
        
        if reserve0 == 0 or reserve1 == 0:
            return None
        
        # Get token addresses
        token0 = pair_contract.functions.token0().call()
        token1 = pair_contract.functions.token1().call()
        
        # Calculate price (reserve1 / reserve0)
        price = reserve1 / reserve0
        
        return price
        
    except Exception as e:
        print(f"Error getting live Aerodrome price for {pair_address}: {e}")
        return None

def check_and_convert_eth_if_needed(executor, input_token_address, input_token_symbol, required_amount):
    """Check if we have the input token, if not try to convert ETH"""
    try:
        # Check current balance
        current_balance = executor.check_token_balance(input_token_address)
        print(f"   Current {input_token_symbol} balance: {current_balance} wei")
        
        if current_balance >= required_amount:
            print(f"   ✅ Sufficient {input_token_symbol} balance")
            return True
        
        # If we don't have enough, try to convert ETH
        print(f"   ❌ Insufficient {input_token_symbol} balance, attempting ETH conversion...")
        
        # Check ETH balance
        eth_balance = executor.w3.eth.get_balance(executor.account.address)
        eth_balance_usd = (eth_balance / 1e18) * 2500  # Rough USD conversion
        print(f"   ETH balance: {eth_balance} wei (${eth_balance_usd:.2f})")
        
        if eth_balance < required_amount:
            print(f"   ❌ Insufficient ETH balance for conversion")
            return False
        
        # For WETH, use the new conversion method
        if input_token_symbol == 'WETH':
            print(f"   Converting ETH to WETH...")
            return executor.ensure_sufficient_weth(required_amount)
        else:
            print(f"   Need to implement ETH→{input_token_symbol} conversion")
            return False
            
    except Exception as e:
        print(f"   ❌ Error checking/converting token: {e}")
        return False

def find_arbitrage_opportunities(uniswap_prices, aerodrome_prices, balancer_v2_prices, executor=None):
    """Find arbitrage opportunities with enhanced analysis"""
    opportunities = []
    all_prices = {
        'Uniswap': uniswap_prices,
        'Aerodrome': aerodrome_prices,
        'Balancer V2': balancer_v2_prices
    }
    all_pairs = set()
    for dex_prices in all_prices.values():
        all_pairs.update(dex_prices.keys())
    for pair in all_pairs:
        prices = {dex: all_prices[dex][pair] for dex in all_prices if pair in all_prices[dex]}
        if not isinstance(prices, dict) or len(prices) < 2:
            print(f"[SKIP] {pair}: not enough DEXes ({list(prices.keys())})")
            continue
        pair_prices = {}
        for dex_name, dex_prices in all_prices.items():
            if pair in dex_prices:
                price = dex_prices[pair]['price']
                pair_prices[dex_name] = price
        if len(pair_prices) >= 2:
            prices_list = list(pair_prices.values())
            min_price = min(prices_list)
            max_price = max(prices_list)
            profit_pct = ((max_price - min_price) / min_price) * 100 if min_price > 0 else 0
            print(f"[PAIR] {pair}: min={min_price}, max={max_price}, profit={profit_pct:.2f}%")
            # For each buy/sell DEX combination
            for buy_dex in pair_prices:
                for sell_dex in pair_prices:
                    if buy_dex == sell_dex:
                        continue
                    buy_price = pair_prices[buy_dex]
                    sell_price = pair_prices[sell_dex]
                    if sell_price <= buy_price:
                        continue
                    # Build opportunity dict
                    # Get token addresses and fee tiers if available
                    buy_info = all_prices[buy_dex][pair]
                    sell_info = all_prices[sell_dex][pair]
                    token0 = buy_info.get('token0')
                    token1 = buy_info.get('token1')
                    fee_tier_buy = buy_info.get('fee_tier')
                    fee_tier_sell = sell_info.get('fee_tier')
                    tvl = min(buy_info.get('tvl', 0), sell_info.get('tvl', 0))
                    # Estimate profit
                    profit_analysis = estimate_profit(buy_price, sell_price)
                    opportunity = {
                        'pair': pair,
                        'buy_dex': buy_dex,
                        'sell_dex': sell_dex,
                        'buy_price': buy_price,
                        'sell_price': sell_price,
                        'profit_pct': profit_pct,
                        'profit_analysis': profit_analysis,
                        'token0_address': token0,
                        'token1_address': token1,
                        'uniswap_fee_tier': fee_tier_buy if buy_dex == 'Uniswap' else fee_tier_sell if sell_dex == 'Uniswap' else None,
                        'aerodrome_fee_tier': fee_tier_buy if buy_dex == 'Aerodrome' else fee_tier_sell if sell_dex == 'Aerodrome' else None,
                        'uniswap_pool_address': buy_info.get('pool_id') if buy_dex == 'Uniswap' else sell_info.get('pool_id') if sell_dex == 'Uniswap' else None,
                        'aerodrome_pool_address': buy_info.get('pool_id') if buy_dex == 'Aerodrome' else sell_info.get('pool_id') if sell_dex == 'Aerodrome' else None,
                    }
                    # Use executor.validate_opportunity for filtering if provided
                    if executor is not None:
                        is_valid, reason = executor.validate_opportunity(opportunity)
                        if is_valid:
                            opportunities.append(opportunity)
                        else:
                            print(f"[FILTERED] {pair} ({buy_dex}->{sell_dex}): {reason}")
                    else:
                        if profit_analysis['net_profit_usd'] > 0 and tvl > MIN_LIQUIDITY_USD:
                            opportunities.append(opportunity)
    return opportunities

def estimate_flash_loan_profit(buy_price, sell_price, pair_info, eth_amount=10.0, eth_price_usd=2500):
    """
    Estimate profit using flash loans for larger capital efficiency
    """
    # Flash loan allows us to use much larger amounts without capital
    flash_loan_amount = 100.0  # $100k worth of ETH for flash loan
    
    # Regular arbitrage (with own capital)
    regular_profit = estimate_profit(buy_price, sell_price, eth_amount, eth_price_usd)
    
    # Flash loan arbitrage (borrow large amount, execute arbitrage, repay)
    gross_profit_usd = (sell_price - buy_price) * flash_loan_amount * eth_price_usd
    
    # Flash loan costs
    flash_loan_fee = flash_loan_amount * eth_price_usd * 0.0009  # 0.09% flash loan fee
    gas_cost_usd = 0.50  # Very low on Base
    mev_protection_cost_usd = 1.0  # Higher for flash loans
    
    flash_loan_costs = flash_loan_fee + gas_cost_usd + mev_protection_cost_usd
    flash_loan_profit = gross_profit_usd - flash_loan_costs
    
    return {
        'regular_profit': regular_profit['net_profit_usd'],
        'flash_loan_profit': flash_loan_profit,
        'flash_loan_amount_usd': flash_loan_amount * eth_price_usd,
        'flash_loan_fee': flash_loan_fee,
        'gas_cost_usd': gas_cost_usd,
        'mev_protection_cost_usd': mev_protection_cost_usd,
        'gross_profit_usd': gross_profit_usd,
        'net_profit_usd': max(regular_profit['net_profit_usd'], flash_loan_profit),
        'is_profitable': max(regular_profit['net_profit_usd'], flash_loan_profit) > MIN_PROFIT_THRESHOLD_USD
    }

def estimate_profit(buy_price, sell_price, eth_amount=None, eth_price_usd=2500, gas_cost_usd=None):
    """
    Estimate realistic arbitrage profit accounting for all costs, with correct unit conversions.
    buy_price and sell_price are in terms of output_token per input_token (e.g., WETH per bsdETH).
    All profit/costs are in USD.
    """
    if eth_amount is None:
        eth_amount = POSITION_SIZE_USD
    if buy_price < 10:
        amount_in = POSITION_SIZE_USD / eth_price_usd
        amount_in_usd = amount_in * eth_price_usd
        print(f"[DEBUG] estimate_profit: buy_price={buy_price}, sell_price={sell_price}, amount_in={amount_in} WETH, amount_in_usd={amount_in_usd}")
    else:
        amount_in = POSITION_SIZE_USD / 1
        amount_in_usd = amount_in
        print(f"[DEBUG] estimate_profit: buy_price={buy_price}, sell_price={sell_price}, amount_in={amount_in} USDC, amount_in_usd={amount_in_usd}")
    gross_profit_usd = (sell_price - buy_price) * amount_in
    print(f"[DEBUG] gross_profit_usd: {gross_profit_usd}")
    if gas_cost_usd is None:
        gas_price_eth = BASE_GAS_PRICE_GWEI / 1e9
        total_gas_eth = (GAS_LIMIT_SWAP * 2 + GAS_LIMIT_APPROVE * 2) * gas_price_eth
        gas_cost_usd = total_gas_eth * eth_price_usd
    transaction_fees_usd = POSITION_SIZE_USD * TRANSACTION_FEE_PCT * 2
    slippage_cost_usd = POSITION_SIZE_USD * SLIPPAGE_PCT * 2
    mev_protection_cost_usd = MEV_PROTECTION_COST_USD
    total_costs_usd = gas_cost_usd + transaction_fees_usd + slippage_cost_usd + mev_protection_cost_usd
    net_profit_usd = gross_profit_usd - total_costs_usd
    net_profit_pct = (net_profit_usd / POSITION_SIZE_USD) * 100 if POSITION_SIZE_USD else 0
    print(f"[DEBUG] net_profit_usd: {net_profit_usd}, total_costs_usd: {total_costs_usd}, net_profit_pct: {net_profit_pct:.2f}%")
    return {
        'gross_profit_usd': gross_profit_usd,
        'gas_cost_usd': gas_cost_usd,
        'transaction_fees_usd': transaction_fees_usd,
        'slippage_cost_usd': slippage_cost_usd,
        'mev_protection_cost_usd': mev_protection_cost_usd,
        'total_costs_usd': total_costs_usd,
        'net_profit_usd': net_profit_usd,
        'net_profit_pct': net_profit_pct,
        'is_profitable': net_profit_usd > MIN_PROFIT_THRESHOLD_USD
    }

async def monitor_once(executor):
    print("\n📊 Fetching prices from DEXes...")
    uniswap_prices = await get_uniswap_prices()
    aerodrome_prices = await get_aerodrome_prices()
    balancer_v2_prices = await get_balancer_v2_prices()
    print(f"📊 Found {len(uniswap_prices)} Uniswap pools")
    print(f"📊 Found {len(aerodrome_prices)} Aerodrome pools")
    print(f"📊 Found {len(balancer_v2_prices)} Balancer V2 pools")
    print("🔍 Analyzing arbitrage opportunities...")
    opportunities = find_arbitrage_opportunities(uniswap_prices, aerodrome_prices, balancer_v2_prices, executor=executor)
    if not opportunities:
        print("❌ No executable arbitrage opportunities found")
        opportunities = []
    if opportunities:
        print(f"\n🔥 Found {len(opportunities)} executable arbitrage opportunities:")
        print("-" * 80)
        executed = False
        for i, opp in enumerate(opportunities[:5]):  # Show top 5
            analysis = opp['profit_analysis']
            strategy = opp.get('strategy', 'regular')
            print(f"{i+1}. {opp['pair']} ({strategy.upper()})")
            print(f"   Buy on {opp['buy_dex']} @ {opp['buy_price']:.6f}")
            print(f"   Sell on {opp['sell_dex']} @ {opp['sell_price']:.6f}")
            print(f"   Profit: {opp['profit_pct']:.2f}%")
            if strategy == 'flash_loan':
                if 'flash_loan_profit' in analysis:
                    print(f"   Flash Loan Profit: ${analysis['flash_loan_profit']:.2f}")
                if 'flash_loan_amount_usd' in analysis:
                    print(f"   Flash Loan Amount: ${analysis['flash_loan_amount_usd']:,.0f}")
                if 'flash_loan_fee' in analysis:
                    print(f"   Flash Loan Fee: ${analysis['flash_loan_fee']:.2f}")
            if 'regular_profit' in analysis:
                print(f"   Regular Profit: ${analysis['regular_profit']:.2f}")
            print(f"   Net Profit: ${analysis.get('net_profit_usd', 0):.2f}")
            print(f"   Net Profit %: {analysis.get('net_profit_pct', 0):.2f}%")
            if EXECUTION_MODE and not executed:
                print(f"\n🎯 Executing opportunity: {opp['pair']}")
                print(f"   Strategy: {strategy.upper()}")
                if FLASH_LOAN_ENABLED:
                    print(f"💰 Using FLASH LOAN arbitrage for {opp['pair']}")
                    success = executor.execute_flash_loan_arbitrage(opp)
                else:
                    print(f"💰 Using REGULAR arbitrage for {opp['pair']}")
                    success = executor.execute_arbitrage(opp)
                if success:
                    print("✅ Arbitrage executed successfully!")
                    executed = True
                    break
                else:
                    print("❌ Arbitrage execution failed")
        # No break if not executed, so it tries the next opportunity

async def monitor():
    """Single-run monitoring for arbitrage opportunities"""
    executor = ArbitrageExecutor(PRIVATE_KEY)
    print(f"🔧 Execution Mode: {'LIVE' if EXECUTION_MODE else 'SIMULATION'}")
    print(f"📊 Simulation Mode: {'ENABLED' if SIMULATION_MODE else 'DISABLED'}")
    print(f"💰 Position Size: ${POSITION_SIZE_USD:,.0f}")
    print(f"📊 Profit Range: {MIN_PROFIT_PCT}%-{MAX_PROFIT_PCT}%")
    print(f"💧 Min Liquidity: ${MIN_LIQUIDITY_USD:,.0f}")
    print(f"🛡️  Safe Mode: {'ENABLED' if SAFE_MODE else 'DISABLED'}")
    print(f"🚀 Flash Loan Enabled: {FLASH_LOAN_ENABLED}")
    print("\nStarting single-run monitoring...\n")
    try:
        await monitor_once(executor)
    except Exception as e:
        print(f"❌ Error in monitor: {e}")

async def get_uniswap_prices():
    """Get all Uniswap V3 pool prices with enhanced monitoring"""
    if not UNISWAP_V3_SUBGRAPH:
        print("UNISWAP_V3_SUBGRAPH not configured")
        return {}
    
    query = {
        "query": """
        {
          pools(first: 1000, orderBy: totalValueLockedUSD, orderDirection: desc) {
            id
            token0 { id symbol }
            token1 { id symbol }
            token0Price
            token1Price
            totalValueLockedUSD
            volumeUSD
            feeTier
          }
        }
        """
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(UNISWAP_V3_SUBGRAPH, json=query) as resp:
                result = await resp.json()
                
                print(f"Uniswap subgraph response status: {resp.status}")
                if resp.status != 200:
                    print(f"Uniswap subgraph error: {result}")
                    return {}
                
                if result is None:
                    print("Uniswap subgraph returned None")
                    return {}
                
                pools = result.get("data", {}).get("pools", [])
                print(f"Found {len(pools)} Uniswap pools")
                
                # Try to get additional pools if we have less than 1000
                if len(pools) < 1000:
                    try:
                        additional_query = {
                            "query": """
                            {
                              pools(first: 1000, skip: 1000, orderBy: totalValueLockedUSD, orderDirection: desc) {
                                id
                                token0 { id symbol }
                                token1 { id symbol }
                                token0Price
                                token1Price
                                totalValueLockedUSD
                                volumeUSD
                                feeTier
                              }
                            }
                            """
                        }
                        async with session.post(UNISWAP_V3_SUBGRAPH, json=additional_query) as additional_resp:
                            additional_result = await additional_resp.json()
                            additional_pools = additional_result.get("data", {}).get("pools", [])
                            pools.extend(additional_pools)
                            print(f"Added {len(additional_pools)} additional pools")
                    except Exception as e:
                        print(f"Could not get additional pools: {e}")
                
                prices = {}
                processed_count = 0
                for i, pool in enumerate(pools):
                    if i % 1000 == 0:
                        print(f"Processing Uniswap pool {i}/{len(pools)}...")
                    
                    try:
                        tokens = pool["token0"], pool["token1"]
                        price = float(pool.get('token0Price', 0))
                        tvl = float(pool.get("totalValueLockedUSD", 0))
                        volume = float(pool.get("volumeUSD", 0))
                        fee_tier = int(pool.get("feeTier", 3000))  # Use raw value (e.g., 100, 500, 3000)
                        
                        # More aggressive filtering - look for liquid pools with recent activity
                        if price > 0 and tvl > MIN_LIQUIDITY_USD and volume > 1000:  # Higher thresholds for better opportunities
                            pair_key = f"{tokens[0]['symbol']}/{tokens[1]['symbol']}"
                            prices[pair_key] = {
                                'price': price,
                                'tvl': tvl,
                                'volume': volume,
                                'fee_tier': fee_tier,
                                'pool_id': pool['id'],
                                'token0': tokens[0]['id'],
                                'token1': tokens[1]['id']
                            }
                            processed_count += 1
                    except Exception as e:
                        continue
                
                print(f"Processed {processed_count} Uniswap pools with valid prices")
                return prices
                
    except Exception as e:
        print(f"Error fetching Uniswap prices: {e}")
        return {}

if __name__ == "__main__":
    asyncio.run(monitor())
