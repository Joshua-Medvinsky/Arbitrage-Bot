# config.py
# Non-sensitive configuration for Arbitrage-Bot

# SushiSwap Pair ABI fragment
PAIR_ABI = [{
    "constant": True,
    "inputs": [],
    "name": "getReserves",
    "outputs": [
        {"name": "_reserve0", "type": "uint112"},
        {"name": "_reserve1", "type": "uint112"},
        {"name": "_blockTimestampLast", "type": "uint32"}
    ],
    "type": "function"
}, {
    "constant": True,
    "inputs": [],
    "name": "token0",
    "outputs": [{"name": "", "type": "address"}],
    "type": "function"
}, {
    "constant": True,
    "inputs": [],
    "name": "token1",
    "outputs": [{"name": "", "type": "address"}],
    "type": "function"
}]

SUSHI_FACTORY_ABI = [
    {"constant":True,"inputs":[],"name":"allPairsLength","outputs":[{"name":"","type":"uint256"}],"type":"function"},
    {"constant":True,"inputs":[{"name":"","type":"uint256"}],"name":"allPairs","outputs":[{"name":"","type":"address"}],"type":"function"}
]

# Default simulation parameters
DEFAULT_ETH_AMOUNT = 1.0
DEFAULT_GAS_ETH = 0.002
DEFAULT_SLIPPAGE_PCT = 0.005

# Realistic cost parameters for Base network
BASE_GAS_PRICE_GWEI = 0.001  # Base has very low gas prices (~0.001 gwei)
GAS_LIMIT_SWAP = 200000  # Gas limit for a swap transaction
GAS_LIMIT_APPROVE = 50000  # Gas limit for token approval
TRANSACTION_FEE_PCT = 0.003  # 0.3% transaction fee (typical for DEXes)
SLIPPAGE_PCT = 0.005  # 0.5% slippage
MEV_PROTECTION_COST_USD = 0.50  # Cost for MEV protection
MIN_PROFIT_THRESHOLD_USD = 5.0  # Minimum profit to be worth executing

# Contract addresses (not secrets, but configurable)
USDC_ADDRESS = "0xd9aA30e1b4c60CAE79Fc379fF651aBAcE84F5aA9"
WETH_ADDRESS = "0x4200000000000000000000000000000000000006"
ZORA_ADDRESS = "0x1111111111166b7FE7bd91427724B487980aFc69"
SUSHI_FACTORY_ADDRESS = "0x71524B4f93c58fcbF659783284E38825f0622859"