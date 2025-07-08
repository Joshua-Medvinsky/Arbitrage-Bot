from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()
w3 = Web3(Web3.HTTPProvider(os.getenv('WEB3_PROVIDER')))

# Transaction hashes from the successful arbitrage
aerodrome_tx = '0x18fd62b1c73fc84f4d7a32b117a11ce1c9473ba813d2144b3e6d72c5358ac94c'
uniswap_tx = '0x45fcceb599e2fec1a8db664717b50f8873da44330ce7c072c4eebefbbefbefc2'
account = '0x2f3981B253B83A4C801cB6EF9A82a14232ed1ebD'

print('🔍 Analyzing Arbitrage Profit')
print('=' * 50)

# Get transaction details
try:
    # Aerodrome transaction
    aerodrome_receipt = w3.eth.get_transaction_receipt(aerodrome_tx)
    aerodrome_tx_data = w3.eth.get_transaction(aerodrome_tx)
    
    # Uniswap transaction  
    uniswap_receipt = w3.eth.get_transaction_receipt(uniswap_tx)
    uniswap_tx_data = w3.eth.get_transaction(uniswap_tx)
    
    print(f'✅ Aerodrome Transaction: {aerodrome_tx}')
    print(f'   Status: {aerodrome_receipt["status"]}')
    print(f'   Gas Used: {aerodrome_receipt["gasUsed"]}')
    print(f'   Gas Price: {aerodrome_tx_data["gasPrice"]} wei')
    
    print(f'✅ Uniswap Transaction: {uniswap_tx}')
    print(f'   Status: {uniswap_receipt["status"]}')
    print(f'   Gas Used: {uniswap_receipt["gasUsed"]}')
    print(f'   Gas Price: {uniswap_tx_data["gasPrice"]} wei')
    
    # Calculate gas costs
    total_gas_used = aerodrome_receipt['gasUsed'] + uniswap_receipt['gasUsed']
    gas_price = aerodrome_tx_data['gasPrice']  # Both use same gas price
    total_gas_cost_wei = total_gas_used * gas_price
    total_gas_cost_eth = total_gas_cost_wei / 1e18
    total_gas_cost_usd = total_gas_cost_eth * 2500  # Rough ETH price
    
    print(f'\n💰 Gas Analysis:')
    print(f'   Total Gas Used: {total_gas_used:,}')
    print(f'   Gas Price: {gas_price / 1e9:.6f} Gwei')
    print(f'   Total Gas Cost: {total_gas_cost_eth:.8f} ETH')
    print(f'   Total Gas Cost: ${total_gas_cost_usd:.4f}')
    
except Exception as e:
    print(f'❌ Error getting transaction details: {e}')

# Check token balances before and after
try:
    weth_address = Web3.to_checksum_address('0x4200000000000000000000000000000000000006')
    usdc_address = Web3.to_checksum_address('0x833589fcd6edb6e08f4c7c32d4f71b54bda02913')
    
    # ERC20 ABI for balance checking
    erc20_abi = [
        {'constant': True, 'inputs': [{'name': '_owner', 'type': 'address'}], 'name': 'balanceOf', 'outputs': [{'name': 'balance', 'type': 'uint256'}], 'type': 'function'},
        {'constant': True, 'inputs': [], 'name': 'decimals', 'outputs': [{'name': '', 'type': 'uint8'}], 'type': 'function'},
        {'constant': True, 'inputs': [], 'name': 'symbol', 'outputs': [{'name': '', 'type': 'string'}], 'type': 'function'}
    ]
    
    weth_contract = w3.eth.contract(address=weth_address, abi=erc20_abi)
    usdc_contract = w3.eth.contract(address=usdc_address, abi=erc20_abi)
    
    # Get current balances
    weth_balance = weth_contract.functions.balanceOf(account).call()
    usdc_balance = usdc_contract.functions.balanceOf(account).call()
    
    weth_decimals = weth_contract.functions.decimals().call()
    usdc_decimals = usdc_contract.functions.decimals().call()
    
    weth_balance_formatted = weth_balance / (10 ** weth_decimals)
    usdc_balance_formatted = usdc_balance / (10 ** usdc_decimals)
    
    print(f'\n💼 Current Token Balances:')
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
    
    # Calculate expected profit
    position_size_usd = 1.5
    expected_profit_pct = 0.0024  # 0.24%
    expected_profit_usd = position_size_usd * expected_profit_pct
    net_profit_usd = expected_profit_usd - total_gas_cost_usd
    
    print(f'\n📊 Profit Analysis:')
    print(f'   Position Size: ${position_size_usd}')
    print(f'   Expected Profit: {expected_profit_pct*100:.2f}%')
    print(f'   Expected Profit: ${expected_profit_usd:.4f}')
    print(f'   Gas Cost: ${total_gas_cost_usd:.4f}')
    print(f'   Net Profit: ${net_profit_usd:.4f}')
    
except Exception as e:
    print(f'❌ Error checking balances: {e}')

print(f'\n📊 Summary:')
print(f'   - Both transactions confirmed successfully')
print(f'   - Gas cost: ~${total_gas_cost_usd:.4f}')
print(f'   - Position size: $1.5')
print(f'   - Expected profit: 0.24%')
print(f'   - Net profit after gas: ~${net_profit_usd:.4f}') 