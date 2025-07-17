import asyncio
import aiohttp
import json
import os
from web3 import Web3
from eth_abi import encode_abi
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURATION ---
MEV_SHARE_SSE = "https://mev-share.flashbots.net"
ARBITRUM_RPC = os.getenv("ARBITRUM_RPC", "https://arb1.arbitrum.io/rpc")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
UNISWAP_V2_FACTORY = "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"
SUSHISWAP_FACTORY = "0xC0AEe478e3658e2610c5F7A4A2E1777cE9e4f2Ac"
PAIR_ABI = json.load(open("path/to/uniswap_v2_pair_abi.json"))
FACTORY_ABI = json.load(open("path/to/uniswap_v2_factory_abi.json"))
SWAP_TOPIC = "0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822"  # UniswapV2 Swap event

# --- SETUP WEB3 ---
w3 = Web3(Web3.HTTPProvider(ARBITRUM_RPC))
account = w3.eth.account.from_key(PRIVATE_KEY)

# --- Helper: Find alt DEX pair ---
def get_alt_pair(factory_addr, token0, token1):
    factory = w3.eth.contract(address=factory_addr, abi=FACTORY_ABI)
    return factory.functions.getPair(token0, token1).call()

# --- Main SSE Listener ---
async def listen_mev_share():
    async with aiohttp.ClientSession() as session:
        async with session.get(MEV_SHARE_SSE) as resp:
            async for line in resp.content:
                if not line or not line.startswith(b"data:"):
                    continue
                try:
                    event = json.loads(line[5:].decode())
                    await handle_event(event)
                except Exception as e:
                    print(f"Error parsing event: {e}")

# --- Event Handler ---
async def handle_event(event):
    logs = event.get("logs", [])
    tx_hash = event.get("hash")
    for log in logs:
        if log["topics"][0].lower() != SWAP_TOPIC:
            continue
        pair_address = log["address"]
        pair_contract = w3.eth.contract(address=pair_address, abi=PAIR_ABI)
        try:
            token0 = pair_contract.functions.token0().call()
            token1 = pair_contract.functions.token1().call()
            # Determine if Uniswap or SushiSwap
            factory_addr = pair_contract.functions.factory().call()
            is_uniswap = factory_addr.lower() == UNISWAP_V2_FACTORY.lower()
            alt_factory = SUSHISWAP_FACTORY if is_uniswap else UNISWAP_V2_FACTORY
            alt_pair = get_alt_pair(alt_factory, token0, token1)
            if int(alt_pair, 16) == 0:
                print("No alt pair found, skipping.")
                continue
            print(f"Found swap on {pair_address}, alt pair: {alt_pair}")
            # TODO: Check reserves, simulate profit, and send backrun bundle
            await try_backrun(pair_address, alt_pair, tx_hash)
        except Exception as e:
            print(f"Error handling log: {e}")

# --- Placeholder: Send Backrun Bundle ---
async def try_backrun(start_pair, end_pair, tx_hash):
    print(f"Would backrun: {start_pair} <-> {end_pair} after {tx_hash}")
    # TODO: Implement bundle creation and sending via Flashbots/MEV-Share
    # See: https://docs.flashbots.net/flashbots-mev-share/searchers/tutorials/flash-loan-arbitrage/bot

if __name__ == "__main__":
    asyncio.run(listen_mev_share())