from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()
w3 = Web3(Web3.HTTPProvider(os.getenv('WEB3_PROVIDER')))

account = '0x2f3981B253B83A4C801cB6EF9A82a14232ed1ebD'

# Check current balances
weth_address = Web3.to_checksum_address('0x4200000000000000000000000000000000000006')
usdc_address = Web3.to_checksum_address('0x833589fcd6edb6e08f4c7c32d4f71b54bda02913')

erc20_abi = [
    {'constant': True, 'inputs': [{'name': '_owner', 'type': 'address'}], 'name': 'balanceOf', 'outputs': [{'name': 'balance', 'type': 'uint256'}], 'type': 'function'},
    {'constant': True, 'inputs': [], 'name': 'decimals', 'outputs': [{'name': '', 'type': 'uint8'}], 'type': 'function'},
    {'constant': True, 'inputs': [], 'name': 'symbol', 'outputs': [{'name': '', 'type': 'string'}], 'type': 'function'}
]

weth_contract = w3.eth.contract(address=weth_address, abi=erc20_abi)
usdc_contract = w3.eth.contract(address=usdc_address, abi=erc20_abi)

weth_balance = weth_contract.functions.balanceOf(account).call()
usdc_balance = usdc_contract.functions.balanceOf(account).call()

weth_decimals = weth_contract.functions.decimals().call()
usdc_decimals = usdc_contract.functions.decimals().call()

weth_balance_formatted = weth_balance / (10 ** weth_decimals)
usdc_balance_formatted = usdc_balance / (10 ** usdc_decimals)

print('💰 Current Token Balances:')
print(f'   WETH: {weth_balance_formatted:.6f} WETH')
print(f'   USDC: {usdc_balance_formatted:.2f} USDC')

# Calculate USD values
eth_price_usd = 2500  # Rough estimate
weth_usd_value = weth_balance_formatted * eth_price_usd
usdc_usd_value = usdc_balance_formatted
total_portfolio_usd = weth_usd_value + usdc_usd_value

print(f'\n💵 Portfolio Value:')
print(f'   WETH Value: ${weth_usd_value:.2f}')
print(f'   USDC Value: ${usdc_usd_value:.2f}')
print(f'   Total Portfolio: ${total_portfolio_usd:.2f}')

print(f'\n🔍 For $10 Position:')
print(f'   You have: ${total_portfolio_usd:.2f} total')
print(f'   You need: $10.00')
print(f'   Sufficient: {"✅ YES" if total_portfolio_usd >= 10 else "❌ NO"}')

# Check what the bot uses for $10 position
position_size_usd = 10.0
eth_amount = position_size_usd / 2500  # Convert USD to ETH
weth_amount = eth_amount * 1e18  # Convert to wei

print(f'\n📊 Bot Requirements for $10 Position:')
print(f'   Position Size: ${position_size_usd}')
print(f'   Required WETH: {eth_amount:.6f} WETH')
print(f'   Required WETH (wei): {int(weth_amount)} wei')
print(f'   You have WETH: {weth_balance_formatted:.6f} WETH')
print(f'   Sufficient WETH: {"✅ YES" if weth_balance_formatted >= eth_amount else "❌ NO"}')

print(f'\n💡 Auto-conversion:')
print(f'   The bot uses WETH as the input token for arbitrage')
print(f'   It does NOT auto-convert ETH→WETH or USDC→WETH')
print(f'   You need to have WETH available')

# Check ETH balance too
eth_balance = w3.eth.get_balance(Web3.to_checksum_address(account))
eth_balance_formatted = eth_balance / 1e18
eth_balance_usd = eth_balance_formatted * 2500

print(f'\n🔍 ETH Balance:')
print(f'   ETH: {eth_balance_formatted:.6f} ETH')
print(f'   ETH Value: ${eth_balance_usd:.2f}')
print(f'   Can convert to WETH: {"✅ YES" if eth_balance_formatted >= eth_amount else "❌ NO"}') 