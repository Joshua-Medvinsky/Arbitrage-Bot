import asyncio
import aiohttp
import json
import os
import logging
from web3 import Web3
from eth_abi.codec import encode_abi
from dotenv import load_dotenv
import requests
from eth_account import Account
from eth_account.messages import encode_defunct
from web3.types import TxParams

# Load environment variables
load_dotenv()

# --- CONFIGURATION ---
MEV_SHARE_SSE = os.getenv("MEV_SHARE_SSE", "https://mev-share.flashbots.net/sse")
ARBITRUM_RPC = os.getenv("ARBITRUM_RPC", "https://arb1.arbitrum.io/rpc")
FLASHBOTS_BUNDLE_API = os.getenv("FLASHBOTS_BUNDLE_API", "https://relay.flashbots.net")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
SEARCHER_ADDRESS = Account.from_key(PRIVATE_KEY).address

# DEX factories & pair ABIs
UNISWAP_V2_FACTORY = Web3.to_checksum_address("0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f")
SUSHISWAP_FACTORY = Web3.to_checksum_address("0xC0AEe478e3658e2610c5F7A4A2E1777cE9e4f2Ac")
PAIR_ABI = json.load(open(os.getenv("PAIR_ABI_PATH", "./uniswap_v2_pair_abi.json")))
FACTORY_ABI = json.load(open(os.getenv("FACTORY_ABI_PATH", "./uniswap_v2_factory_abi.json")))
SWAP_TOPIC = Web3.keccak(text="Swap(address,address,uint256,uint256,uint256,uint256)").hex()  # UniswapV2 Swap event topic

# Custom flashloan arb contract
CONTRACT_ADDRESS = Web3.to_checksum_address(os.getenv("CONTRACT_ADDRESS"))
CONTRACT_ABI = json.load(open(os.getenv("CONTRACT_ABI_PATH", "./flashloan_arb_contract_abi.json")))

# Trade params
WETH_ADDRESS = Web3.to_checksum_address(os.getenv("WETH_ADDRESS", "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1"))
PERCENTAGE_TO_KEEP = int(os.getenv("PERCENTAGE_TO_KEEP", "9000"))  # basis points
GAS_LIMIT = int(os.getenv("GAS_LIMIT", "400000"))

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# Setup Web3
w3 = Web3(Web3.HTTPProvider(ARBITRUM_RPC))
account = w3.eth.account.from_key(PRIVATE_KEY)

# Helper: get alt DEX pair address
def get_alt_pair(factory_addr: str, token0: str, token1: str) -> str:
    factory = w3.eth.contract(address=factory_addr, abi=FACTORY_ABI)
    return factory.functions.getPair(token0, token1).call()

# Sign Flashbots payload
def sign_message(message: str) -> str:
    msg = encode_defunct(text=message)
    signed = Account.sign_message(msg, private_key=PRIVATE_KEY)
    return signed.signature.hex()

# Bundle wrapper
def bundle_with_params(block_number: int, blocks_to_try: int, bundle: list) -> dict:
    return {
        "version": "beta-1",
        "inclusion": {
            "block": hex(block_number),
            "maxBlock": hex(block_number + blocks_to_try)
        },
        "body": bundle
    }

# Send JSON-RPC to Flashbots
async def send_bundle(bundle: dict, signer: Account):
    payload = {"jsonrpc": "2.0", "id": 1, "method": "mev_sendBundle", "params": [bundle]}
    sig = sign_message(json.dumps(payload))
    headers = {
        "Content-Type": "application/json",
        "X-Flashbots-Signature": f"{signer.address}:{sig}"
    }
    logger.info(f"Sending bundle: %s", payload)
    resp = requests.post(FLASHBOTS_BUNDLE_API, json=payload, headers=headers)
    logger.info(f"Flashbots response: %s %s", resp.status_code, resp.text)

async def send_bundles(bundle_one: dict, bundle_two: dict):
    await asyncio.gather(
        send_bundle(bundle_one, account),
        send_bundle(bundle_two, account)
    )

# Backrun executor
def execute_backrun(start_pair: str, end_pair: str, tx_hash: str):
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)
    block_number = w3.eth.block_number
    nonce = w3.eth.get_transaction_count(account.address)
    gas_price = w3.eth.gas_price

    # Encode parameters
    types = ['address', 'address', 'uint256']
    params_a = encode_abi(types, [start_pair, end_pair, PERCENTAGE_TO_KEEP])
    params_b = encode_abi(types, [end_pair, start_pair, PERCENTAGE_TO_KEEP])

    # Build tx
    tx_common = {'gas': GAS_LIMIT, 'gasPrice': gas_price}
    tx1 = contract.functions.makeFlashLoan(WETH_ADDRESS, 10**18, params_a).build_transaction({**tx_common, 'nonce': nonce})
    tx2 = contract.functions.makeFlashLoan(WETH_ADDRESS, 10**18, params_b).build_transaction({**tx_common, 'nonce': nonce + 1})

    # Sign
    signed1 = w3.eth.account.sign_transaction(tx1, PRIVATE_KEY)
    signed2 = w3.eth.account.sign_transaction(tx2, PRIVATE_KEY)

    # Create bundles
    bun_a = [ {"hash": tx_hash}, {"tx": signed1.rawTransaction.hex(), "canRevert": False} ]
    bun_b = [ {"hash": tx_hash}, {"tx": signed2.rawTransaction.hex(), "canRevert": False} ]
    bundle_one = bundle_with_params(block_number + 1, 5, bun_a)
    bundle_two = bundle_with_params(block_number + 1, 5, bun_b)

    # Dispatch
    return bundle_one, bundle_two

# Handle each incoming event
async def handle_event(event: dict):
    logs = event.get("logs", [])
    tx_hash = event.get("hash")
    for log in logs:
        if log["topics"][0].lower() != SWAP_TOPIC.lower():
            continue
        pair_addr = Web3.to_checksum_address(log["address"])
        pair = w3.eth.contract(address=pair_addr, abi=PAIR_ABI)
        token0, token1 = pair.functions.token0().call(), pair.functions.token1().call()
        factory = pair.functions.factory().call()
        alt_factory = SUSHISWAP_FACTORY if factory.lower() == UNISWAP_V2_FACTORY.lower() else UNISWAP_V2_FACTORY
        alt_pair = get_alt_pair(alt_factory, token0, token1)
        if int(alt_pair, 16) == 0:
            logger.debug("No alt pair for %s", pair_addr)
            continue
        logger.info("Swap detected on %s, alt pair: %s", pair_addr, alt_pair)

        # Optionally add reserve checks here
        bundle_one, bundle_two = execute_backrun(pair_addr, alt_pair, tx_hash)
        await send_bundles(bundle_one, bundle_two)

# Listen to MEV-Share SSE stream
async def listen_mev_share():
    async with aiohttp.ClientSession() as session:
        async with session.get(MEV_SHARE_SSE) as resp:
            async for line in resp.content:
                if not line or not line.startswith(b"data:"):
                    continue
                try:
                    payload = json.loads(line.lstrip(b"data: ").decode())
                    await handle_event(payload)
                except Exception as e:
                    logger.error("Event parse error: %s", e)

# Entry point
if __name__ == "__main__":
    logger.info("Starting MEV-backrun listener...")
    asyncio.run(listen_mev_share())
