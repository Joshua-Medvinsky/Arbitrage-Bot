import asyncio
import os
import aiohttp
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

WEB3_PROVIDER = os.getenv("WEB3_PROVIDER")
UNISWAP_V3_SUBGRAPH = os.getenv("UNISWAP_V3_SUBGRAPH")
AERODROME_SUBGRAPH = os.getenv("AERODROME_SUBGRAPH")
UNISWAP_API_KEY = os.getenv("UNISWAP_API_KEY")

w3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER))

# Addresses
USDC = Web3.to_checksum_address(os.getenv("USDC_ADDRESS"))
WETH = Web3.to_checksum_address(os.getenv("WETH_ADDRESS"))
SUSHI_PAIR = Web3.to_checksum_address(os.getenv("SUSHI_PAIR_ADDRESS"))
ZORA = os.getenv("ZORA_ADDRESS")
SUSHI_FACTORY = Web3.to_checksum_address(os.getenv("SUSHI_FACTORY_ADDRESS"))

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

async def get_uniswap_price():
    query = {
        "query": """
        {
          liquidityPools(first: 500) {
            id
            name
            inputTokens {
              id
              symbol
            }
            inputTokenBalances
          }
        }
        """
    }

    USDC = "0xd9aa30e1b4c60cae79fc379ff651abace84f5aa9"
    WETH = "0x4200000000000000000000000000000000000006"

    async with aiohttp.ClientSession() as session:
        headers = {
            "Authorization": f"Bearer {UNISWAP_API_KEY}",
            "Content-Type": "application/json"
        }
        async with session.post(UNISWAP_V3_SUBGRAPH, json=query, headers=headers) as resp:
            result = await resp.json()
            pools = result.get("data", {}).get("liquidityPools", [])
            weth_pairs = set()
            for pool in pools:
                tokens = pool["inputTokens"]
                token_addresses = [t["id"].lower() for t in tokens]
                symbols = [t["symbol"] for t in tokens]
                if WETH in token_addresses:
                    for t in tokens:
                        if t["id"].lower() != WETH:
                            weth_pairs.add((t["symbol"], t["id"]))
            print("Uniswap v3 WETH pairs:")
            for symbol, addr in weth_pairs:
                print(f"{symbol}: {addr}")
            get_sushiswap_pairs()
            await get_aerodrome_pairs()
            await get_all_sushiswap_pairs()
            return None

def get_sushiswap_price():
    pair = w3.eth.contract(address=SUSHI_PAIR, abi=PAIR_ABI)
    reserves = pair.functions.getReserves().call()
    token0 = pair.functions.token0().call()
    
    if token0.lower() == WETH.lower():
        eth_reserve = reserves[0] / 1e18
        usdc_reserve = reserves[1] / 1e6
    else:
        eth_reserve = reserves[1] / 1e18
        usdc_reserve = reserves[0] / 1e6

    price = usdc_reserve / eth_reserve
    return price

def get_sushiswap_pairs():
    pair = w3.eth.contract(address=SUSHI_PAIR, abi=PAIR_ABI)
    token0 = pair.functions.token0().call()
    token1 = pair.functions.token1().call()
    tokens = [token0, token1]
    symbols = []
    for token in tokens:
        try:
            erc20 = w3.eth.contract(address=token, abi=[{"constant":True,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"type":"function"}])
            symbol = erc20.functions.symbol().call()
            symbols.append(symbol)
        except Exception as e:
            symbols.append("?")
    print(f"SushiSwap pair: {symbols[0]}/{symbols[1]} ({token0}/{token1})")

def estimate_profit(buy_price, sell_price, eth_amount=1.0, gas_eth=0.002, slippage_pct=0.005):
    gross_profit = (sell_price - buy_price) * eth_amount
    slippage_loss = slippage_pct * (buy_price + sell_price) / 2 * eth_amount
    gas_cost_usd = gas_eth * sell_price
    net_profit = gross_profit - slippage_loss - gas_cost_usd
    return net_profit

async def monitor():
    while True:
        uni_price = await get_uniswap_price()
        sushi_price = get_sushiswap_price()
        eth_amount = 1.0  # Simulate with 1 ETH

        if uni_price and sushi_price:
            print(f"[Uniswap] {uni_price:.2f} | [SushiSwap] {sushi_price:.2f}")

            # Arbitrage direction
            if sushi_price > uni_price:
                profit = estimate_profit(uni_price, sushi_price, eth_amount)
                if profit > 0:
                    print(f"🔥 Arbitrage: Buy Uniswap @ {uni_price:.2f}, Sell Sushi @ {sushi_price:.2f} | Net Profit: ${profit:.2f}")
            elif uni_price > sushi_price:
                profit = estimate_profit(sushi_price, uni_price, eth_amount)
                if profit > 0:
                    print(f"🔥 Arbitrage: Buy Sushi @ {sushi_price:.2f}, Sell Uniswap @ {uni_price:.2f} | Net Profit: ${profit:.2f}")
            else:
                print("No arbitrage.")
        else:
            print("Price fetch failed.")

        await asyncio.sleep(10)

async def get_aerodrome_pairs():
    query = {
        "query": """
        {
          pairs(first: 100) {
            id
            token0 { id symbol }
            token1 { id symbol }
          }
        }
        """
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(AERODROME_SUBGRAPH, json=query) as resp:
            result = await resp.json()
            print("Aerodrome subgraph response:", result)  # Debug print
            pairs = result.get("data", {}).get("pairs", [])
            print("Aerodrome pairs:")
            for pair in pairs:
                t0 = pair["token0"]
                t1 = pair["token1"]
                print(f"{t0['symbol']}/{t1['symbol']} ({t0['id']}/{t1['id']})")

async def get_all_sushiswap_pairs():
    factory = w3.eth.contract(address=SUSHI_FACTORY, abi=SUSHI_FACTORY_ABI)
    pair_abi = PAIR_ABI
    try:
        total_pairs = factory.functions.allPairsLength().call()
    except Exception as e:
        print(f"Error fetching SushiSwap allPairsLength: {e}")
        return
    print(f"SushiSwap pairs (showing first 50 of {total_pairs}):")
    for i in range(min(50, total_pairs)):
        try:
            pair_addr = factory.functions.allPairs(i).call()
            pair = w3.eth.contract(address=pair_addr, abi=pair_abi)
            token0 = pair.functions.token0().call()
            token1 = pair.functions.token1().call()
            symbols = []
            for token in [token0, token1]:
                try:
                    erc20 = w3.eth.contract(address=token, abi=[{"constant":True,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"type":"function"}])
                    symbol = erc20.functions.symbol().call()
                    symbols.append(symbol)
                except Exception:
                    symbols.append("?")
            print(f"{symbols[0]}/{symbols[1]} ({token0}/{token1})")
        except Exception as e:
            print(f"Error fetching pair {i}: {e}")

asyncio.run(monitor())
