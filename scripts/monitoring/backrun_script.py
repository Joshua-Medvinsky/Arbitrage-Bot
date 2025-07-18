import asyncio
import aiohttp
import json
import os
from web3 import Web3
from eth_abi import encode_abi
from dotenv import load_dotenv
import requests
from eth_account import Account
from eth_account.messages import encode_defunct

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

# --- Config ---
FLASHBOTS_BUNDLE_API = "https://relay.flashbots.net"  # Or MEV-Share endpoint
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
SEARCHER_ADDRESS = Account.from_key(PRIVATE_KEY).address
CONTRACT_ADDRESS = "0xYourFlashLoanArbContract"
CONTRACT_ABI = ...  # Load your contract ABI here
WETH_ADDRESS = "0xYourWETHAddress"
PERCENTAGE_TO_KEEP = 9000  # Example: 90% (in basis points)
GAS_LIMIT = 400_000

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

w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER")))

def sign_message(message: str) -> str:
    msg = encode_defunct(text=message)
    signed = Account.sign_message(msg, private_key=PRIVATE_KEY)
    return signed.signature.hex()

def bundle_with_params(block_number, blocks_to_try, bundle):
    return {
        "version": "beta-1",
        "inclusion": {
            "block": hex(block_number),
            "maxBlock": hex(block_number + blocks_to_try)
        },
        "body": bundle
    }

async def try_backrun(start_pair, end_pair, tx_hash):
    contract = w3.eth.contract(address=Web3.to_checksum_address(CONTRACT_ADDRESS), abi=CONTRACT_ABI)
    account = Account.from_key(PRIVATE_KEY)
    block_number = w3.eth.block_number
    nonce = w3.eth.get_transaction_count(account.address)
    gas_price = w3.eth.gas_price

    # Prepare calldata for both trade directions
    types = ['address', 'address', 'uint256']
    values_first = [start_pair, end_pair, PERCENTAGE_TO_KEEP]
    values_second = [end_pair, start_pair, PERCENTAGE_TO_KEEP]

    params_first = w3.codec.encode_abi(types, values_first)
    params_second = w3.codec.encode_abi(types, values_second)

    # Build transactions
    tx_opts = {
        'from': account.address,
        'gas': GAS_LIMIT,
        'gasPrice': gas_price,
        'nonce': nonce,
    }

    tx1 = contract.functions.makeFlashLoan(
        WETH_ADDRESS,
        10**21,  # 1000 WETH, adjust as needed
        params_first
    ).build_transaction(tx_opts)

    tx2 = contract.functions.makeFlashLoan(
        WETH_ADDRESS,
        10**21,
        params_second
    ).build_transaction({**tx_opts, 'nonce': nonce + 1})

    # Sign transactions
    signed_tx1 = w3.eth.account.sign_transaction(tx1, private_key=PRIVATE_KEY)
    signed_tx2 = w3.eth.account.sign_transaction(tx2, private_key=PRIVATE_KEY)

    # Bundle format: [user tx, our tx]
    bundle_one = [
        {"hash": tx_hash},
        {"tx": signed_tx1.rawTransaction.hex(), "canRevert": False}
    ]
    bundle_two = [
        {"hash": tx_hash},
        {"tx": signed_tx2.rawTransaction.hex(), "canRevert": False}
    ]

    bundle_one_with_params = bundle_with_params(block_number + 1, 10, bundle_one)
    bundle_two_with_params = bundle_with_params(block_number + 1, 10, bundle_two)

    # Send both bundles
    await send_bundle_to_node(bundle_one_with_params, bundle_two_with_params, account)

async def send_bundle_to_node(bundle_one, bundle_two, account):
    await asyncio.gather(
        send_bundle(bundle_one, account),
        send_bundle(bundle_two, account)
    )

async def send_bundle(bundle, account):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "mev_sendBundle",
        "params": [bundle]
    }
    message = str(payload)
    signature = sign_message(message)
    headers = {
        "Content-Type": "application/json",
        "X-Flashbots-Signature": f"{account.address}:{signature}"
    }
    print(f"Sending bundle: {payload}")
    resp = requests.post(FLASHBOTS_BUNDLE_API, json=payload, headers=headers)
    print(f"Response: {resp.status_code} {resp.text}")

if __name__ == "__main__":
    asyncio.run(listen_mev_share())