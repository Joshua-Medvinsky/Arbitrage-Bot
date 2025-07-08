import json
import os

# Load the token list JSON (assumed to be in the same directory)
TOKEN_LIST_PATH = os.path.join(os.path.dirname(__file__), 'token_list.json')

with open(TOKEN_LIST_PATH, 'r') as f:
    token_list = json.load(f)

# Extract only Base tokens (chainId 8453)
base_tokens = [t for t in token_list['tokens'] if t['chainId'] == 8453]

# Build a symbol->address mapping (use upper-case symbol for uniqueness)
TOKEN_ADDRESSES = {t['symbol'].upper(): t['address'] for t in base_tokens}

# Export canonical tokens for convenience (if present)
def get_token(symbol):
    return TOKEN_ADDRESSES.get(symbol.upper())

WETH_BASE = get_token('WETH')
USDC_BASE = get_token('USDC')
weETH_BASE = get_token('weETH')
cbETH_BASE = get_token('cbETH')
wstETH_BASE = get_token('wstETH') 