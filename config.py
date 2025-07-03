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

# Contract addresses (not secrets, but configurable)
USDC_ADDRESS = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
WETH_ADDRESS = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
SUSHI_PAIR_ADDRESS = "0x397FF1542f962076d0BFE58eA045FfA2d347ACa0"
ZORA_ADDRESS = "0x0000000000000000000000000000000000000000"
SUSHI_FACTORY_ADDRESS = "0xC0AEe478e3658e2610c5F7A4A2E1777cE9e4f2Ac"