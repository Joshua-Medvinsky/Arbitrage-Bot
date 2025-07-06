import asyncio
import os
import aiohttp
from web3 import Web3
from dotenv import load_dotenv
from config import PAIR_ABI, SUSHI_FACTORY_ABI, DEFAULT_ETH_AMOUNT, DEFAULT_GAS_ETH, DEFAULT_SLIPPAGE_PCT, USDC_ADDRESS, WETH_ADDRESS, ZORA_ADDRESS, SUSHI_FACTORY_ADDRESS, BASE_GAS_PRICE_GWEI, GAS_LIMIT_SWAP, GAS_LIMIT_APPROVE, TRANSACTION_FEE_PCT, SLIPPAGE_PCT, MEV_PROTECTION_COST_USD, MIN_PROFIT_THRESHOLD_USD

load_dotenv()

WEB3_PROVIDER = os.getenv("WEB3_PROVIDER")
UNISWAP_V3_SUBGRAPH = os.getenv("UNISWAP_V3_SUBGRAPH")
AERODROME_SUBGRAPH = os.getenv("AERODROME_SUBGRAPH")
UNISWAP_API_KEY = os.getenv("UNISWAP_API_KEY")

# Real-time execution settings
EXECUTION_MODE = True  # Set to True for live trading
SIMULATION_MODE = False  # Set to True to simulate without sending transactions
PRIVATE_KEY = os.getenv("PRIVATE_KEY")  # Your wallet private key
MIN_LIQUIDITY_USD = 100000  # Increased to $100k liquidity for safety
MAX_PROFIT_PCT = 20.0  # Reduced to 20% max profit for realistic opportunities
MIN_PROFIT_PCT = 1.0  # Increased to 1% minimum for better opportunities
MAX_SLIPPAGE = 0.01  # Reduced to 1% slippage for safety
POSITION_SIZE_USD = 5  # Reduced to $5 for safe testing with available balance
SAFE_MODE = True  # Enable additional safety checks

w3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER))

# Convert addresses to checksum format
USDC = Web3.to_checksum_address(USDC_ADDRESS)
WETH = Web3.to_checksum_address(WETH_ADDRESS)

# Flash loan contract addresses (Aave V3 on Base)
AAVE_LENDING_POOL = "0xA238Dd80C259a72e81d7e4664a9801593F98d1c5"
AAVE_LENDING_POOL_ABI = [
    {"inputs":[{"internalType":"address","name":"asset","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"uint256","name":"interestRateMode","type":"uint256"},{"internalType":"uint16","name":"referralCode","type":"uint16"},{"internalType":"address","name":"onBehalfOf","type":"address"}],"name":"borrow","outputs":[],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[{"internalType":"address","name":"asset","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"uint256","name":"rateMode","type":"uint256"},{"internalType":"address","name":"onBehalfOf","type":"address"}],"name":"repay","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"}
]

# MEV Bot detection
MEV_BOT_ADDRESSES = [
    "0x0000000000000000000000000000000000000000",  # Placeholder - real MEV bots
]

# Uniswap V3 Router for execution (Base network)
UNISWAP_V3_ROUTER = Web3.to_checksum_address("0x2626664c2603336E57B271c5C0b26F421741e481")
UNISWAP_V3_ROUTER_ABI = [
    {"inputs":[{"components":[{"internalType":"address","name":"tokenIn","type":"address"},{"internalType":"address","name":"tokenOut","type":"address"},{"internalType":"uint24","name":"fee","type":"uint24"},{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMinimum","type":"uint256"},{"internalType":"uint160","name":"sqrtPriceLimitX96","type":"uint160"}],"internalType":"struct ISwapRouter.ExactInputSingleParams","name":"params","type":"tuple"}],"name":"exactInputSingle","outputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"}],"stateMutability":"payable","type":"function"},
    {"inputs":[{"components":[{"internalType":"address","name":"tokenIn","type":"address"},{"internalType":"address","name":"tokenOut","type":"address"},{"internalType":"uint24","name":"fee","type":"uint24"},{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"amountInMaximum","type":"uint256"},{"internalType":"uint160","name":"sqrtPriceLimitX96","type":"uint160"}],"internalType":"struct ISwapRouter.ExactOutputSingleParams","name":"params","type":"tuple"}],"name":"exactOutputSingle","outputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"}],"stateMutability":"payable","type":"function"}
]

# SushiSwap Router for execution (Base network)
SUSHI_ROUTER = Web3.to_checksum_address("0x6B3595068778DD592e39A122f4f5a5cF09C90fE2")
SUSHI_ROUTER_ABI = [
    {"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"amountInMax","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapTokensForExactTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"}
]

# Token addresses for Base network
WETH_BASE = "0x4200000000000000000000000000000000000006"
USDC_BASE = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
weETH_BASE = "0xd9aa30E1B4c60CAe79FC379ff651abACE84F5AA9"

# ERC20 Token ABI for approvals
ERC20_ABI = [
    {"constant":True,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"type":"function"},
    {"constant":False,"inputs":[{"name":"_spender","type":"address"},{"name":"_value","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"type":"function"},
    {"constant":True,"inputs":[{"name":"_owner","type":"address"},{"name":"_spender","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"type":"function"},
    {"constant":True,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"type":"function"},
    {"constant":True,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"type":"function"}
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
        self.sushi_router = w3.eth.contract(address=SUSHI_ROUTER, abi=SUSHI_ROUTER_ABI)
        
    def validate_opportunity(self, opportunity):
        """Validate if an opportunity is realistic and executable"""
        profit_pct = opportunity['profit_pct']
        
        # SAFETY CHECKS FOR TESTING
        if SAFE_MODE:
            # Only allow very small amounts for testing
            if POSITION_SIZE_USD > 10:
                return False, f"Position size ${POSITION_SIZE_USD} too large for testing mode"
            
            # Only allow very conservative profit ranges
            if profit_pct > 20.0:
                return False, f"Profit {profit_pct:.2f}% too high for safe testing (max 20%)"
            
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
    
    def execute_uniswap_swap(self, token_in, token_out, amount_in, amount_out_min, fee=3000):
        """Execute swap on Uniswap V3"""
        if not self.account:
            raise ValueError("No account loaded")
            
        # Get current block timestamp
        latest_block = self.w3.eth.get_block('latest')
        deadline = latest_block.get('timestamp', 0) + 300  # 5 minutes
        
        # Build swap parameters
        params = {
            'tokenIn': Web3.to_checksum_address(token_in),
            'tokenOut': Web3.to_checksum_address(token_out),
            'fee': fee,
            'recipient': self.account.address,
            'deadline': deadline,
            'amountIn': amount_in,
            'amountOutMinimum': amount_out_min,
            'sqrtPriceLimitX96': 0
        }
        
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
                return False
        else:
            print(f"📊 Simulation: Would swap {amount_in} tokens on Uniswap")
            return True
    
    def execute_sushiswap_swap(self, token_in, token_out, amount_in, amount_out_min):
        """Execute swap on SushiSwap"""
        if not self.account:
            raise ValueError("No account loaded")
            
        # Get current block timestamp
        latest_block = self.w3.eth.get_block('latest')
        deadline = latest_block.get('timestamp', 0) + 300  # 5 minutes
        
        # Build path
        path = [Web3.to_checksum_address(token_in), Web3.to_checksum_address(token_out)]
        
        # Build transaction
        swap_function = self.sushi_router.functions.swapExactTokensForTokens(
            amount_in,
            amount_out_min,
            path,
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
            # Sign and send swap
            signed_tx = self.account.sign_transaction(tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            print(f"✅ SushiSwap swap sent: {tx_hash.hex()}")
            
            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            if receipt["status"] == 1:
                print(f"✅ SushiSwap swap confirmed!")
                return True
            else:
                print("❌ SushiSwap swap failed")
                return False
        else:
            print(f"📊 Simulation: Would swap {amount_in} tokens on SushiSwap")
            return True
    
    def execute_arbitrage(self, opportunity):
        """Execute the arbitrage trade"""
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
            
            # Get token addresses for Base network
            token_addresses = {
                'WETH': WETH_BASE,
                'USDC': USDC_BASE,
                'weETH': weETH_BASE,
                'USDT': USDC_BASE,  # Use USDC as proxy for USDT
                'cbBTC': WETH_BASE,  # Use WETH as proxy for cbBTC
                'cbETH': WETH_BASE,  # Use WETH as proxy for cbETH
                'wstETH': WETH_BASE  # Use WETH as proxy for wstETH
            }
            
            token0_address = token_addresses.get(token0_symbol, WETH_BASE)
            token1_address = token_addresses.get(token1_symbol, WETH_BASE)
            
            print(f"   Token0: {token0_symbol} ({token0_address})")
            print(f"   Token1: {token1_symbol} ({token1_address})")
            print(f"   Required amount: {token_amount} wei (${POSITION_SIZE_USD})")
            
            # Special handling for weETH/WETH pair - we need to use weETH as input
            if token0_symbol == 'weETH' and token1_symbol == 'WETH':
                print(f"   Special handling for weETH/WETH pair")
                # For weETH/WETH, we need weETH as input token
                input_token_symbol = 'weETH'
                input_token_address = weETH_BASE
                output_token_symbol = 'WETH'
                output_token_address = WETH_BASE
            elif token1_symbol == 'weETH' and token0_symbol == 'WETH':
                print(f"   Special handling for WETH/weETH pair")
                # For WETH/weETH, we need WETH as input token
                input_token_symbol = 'WETH'
                input_token_address = WETH_BASE
                output_token_symbol = 'weETH'
                output_token_address = weETH_BASE
            else:
                # Normal case - use token0 as input
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
            
            # Check if we have the input tokens
            try:
                input_token_balance = self.check_token_balance(input_token_address)
                balance_usd = (input_token_balance / 1e18) * 2500  # Convert to USD
                print(f"   {input_token_symbol} balance: {input_token_balance} wei (${balance_usd:.2f})")
                
                # If we can't access the specific token, try with WETH as fallback
                if input_token_balance == 0 and input_token_symbol != 'WETH':
                    print(f"   Trying WETH as fallback for {input_token_symbol}...")
                    weth_balance = self.check_token_balance(WETH_BASE)
                    weth_balance_usd = (weth_balance / 1e18) * 2500
                    print(f"   WETH balance: {weth_balance} wei (${weth_balance_usd:.2f})")
                    
                    if weth_balance >= token_amount:
                        print(f"   Using WETH instead of {input_token_symbol}")
                        input_token_address = WETH_BASE
                        input_token_symbol = 'WETH'
                        input_token_balance = weth_balance
                        
                        # IMPORTANT: Don't change the output token when using WETH fallback
                        # This prevents swapping WETH for WETH
                        if output_token_symbol == input_token_symbol:
                            print(f"❌ Cannot swap {input_token_symbol} for {output_token_symbol}")
                            print(f"   This would be an invalid swap")
                            return False
                    else:
                        print(f"❌ Insufficient WETH balance: {weth_balance} < {token_amount}")
                        print(f"   Need: ${POSITION_SIZE_USD}, Have: ${weth_balance_usd:.2f}")
                        return False
                
                if input_token_balance < token_amount:
                    print(f"❌ Insufficient {input_token_symbol} balance: {input_token_balance} < {token_amount}")
                    print(f"   Need: ${POSITION_SIZE_USD}, Have: ${balance_usd:.2f}")
                    return False
                    
            except Exception as e:
                print(f"❌ Error checking {input_token_symbol} balance: {e}")
                return False
            
            # Calculate amounts with slippage
            amount_out_min = int(token_amount * (1 - MAX_SLIPPAGE))
            
            print(f"   Amount: {token_amount} wei")
            print(f"   Min out: {amount_out_min} wei")
            
            # Execute arbitrage
            success = self.execute_arbitrage_swaps(
                opportunity['buy_dex'], 
                opportunity['sell_dex'],
                input_token_address,
                output_token_address,
                token_amount,
                amount_out_min
            )
            
            if success:
                print("✅ Arbitrage executed successfully!")
                return True
            else:
                print("❌ Arbitrage execution failed")
                return False
                
        except Exception as e:
            print(f"❌ Execution failed: {e}")
            return False
    
    def execute_arbitrage_swaps(self, buy_dex, sell_dex, token0, token1, amount, amount_out_min):
        """Execute the actual arbitrage swaps"""
        try:
            # Step 1: Approve tokens for buy DEX
            print(f"🔐 Approving tokens for {buy_dex}...")
            if buy_dex == 'Uniswap':
                if not self.approve_token(token0, UNISWAP_V3_ROUTER, amount):
                    return False
            elif buy_dex == 'SushiSwap':
                if not self.approve_token(token0, SUSHI_ROUTER, amount):
                    return False
            else:
                print(f"❌ Unsupported DEX: {buy_dex}")
                return False
            
            # Step 2: Execute buy swap
            print(f"🔄 Executing buy on {buy_dex}...")
            try:
                if buy_dex == 'Uniswap':
                    if not self.execute_uniswap_swap(token0, token1, amount, amount_out_min):
                        return False
                elif buy_dex == 'SushiSwap':
                    if not self.execute_sushiswap_swap(token0, token1, amount, amount_out_min):
                        return False
            except Exception as e:
                print(f"❌ Buy swap failed on {buy_dex}: {e}")
                return False
            
            # Step 3: Approve tokens for sell DEX
            print(f"🔐 Approving tokens for {sell_dex}...")
            if sell_dex == 'Uniswap':
                if not self.approve_token(token1, UNISWAP_V3_ROUTER, amount_out_min):
                    return False
            elif sell_dex == 'SushiSwap':
                if not self.approve_token(token1, SUSHI_ROUTER, amount_out_min):
                    return False
            else:
                print(f"❌ Unsupported DEX: {sell_dex}")
                return False
            
            # Step 4: Execute sell swap
            print(f"🔄 Executing sell on {sell_dex}...")
            try:
                if sell_dex == 'Uniswap':
                    if not self.execute_uniswap_swap(token1, token0, amount_out_min, amount):
                        return False
                elif sell_dex == 'SushiSwap':
                    if not self.execute_sushiswap_swap(token1, token0, amount_out_min, amount):
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

async def get_uniswap_prices():
    """Get all Uniswap v3 pool prices with enhanced monitoring"""
    if not UNISWAP_V3_SUBGRAPH:
        print("UNISWAP_V3_SUBGRAPH not configured")
        return {}
    
    query = {
        "query": """
        {
          pools(first: 1000, orderBy: totalValueLockedUSD, orderDirection: desc) {
            id
            token0 {
              id
              symbol
            }
            token1 {
              id
              symbol
            }
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
            headers = {
                "Authorization": f"Bearer {UNISWAP_API_KEY}" if UNISWAP_API_KEY else "",
                "Content-Type": "application/json"
            }
            async with session.post(UNISWAP_V3_SUBGRAPH, json=query, headers=headers) as resp:
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
                
                # Get more pools with offset for better coverage
                if pools and len(pools) == 1000:
                    print("Attempting to get more pools with offset...")
                    try:
                        offset_query = {
                            "query": """
                            {
                              pools(first: 1000, skip: 1000, orderBy: totalValueLockedUSD, orderDirection: desc) {
                                id
                                token0 {
                                  id
                                  symbol
                                }
                                token1 {
                                  id
                                  symbol
                                }
                                token0Price
                                token1Price
                                totalValueLockedUSD
                                volumeUSD
                                feeTier
                              }
                            }
                            """
                        }
                        async with session.post(UNISWAP_V3_SUBGRAPH, json=offset_query, headers=headers) as offset_resp:
                            offset_result = await offset_resp.json()
                            if offset_result.get("data", {}).get("pools"):
                                pools.extend(offset_result["data"]["pools"])
                                print(f"Added {len(offset_result['data']['pools'])} more pools (total: {len(pools)})")
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
                        fee_tier = int(pool.get("feeTier", 3000)) / 10000  # Convert to percentage
                        
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

async def get_sushiswap_prices():
    """Get all SushiSwap pool prices with enhanced monitoring"""
    if not SUSHI_FACTORY_ADDRESS:
        print("SUSHI_FACTORY_ADDRESS not configured")
        return {}
    
    factory = w3.eth.contract(address=Web3.to_checksum_address(SUSHI_FACTORY_ADDRESS), abi=SUSHI_FACTORY_ABI)
    prices = {}
    
    try:
        total_pairs = factory.functions.allPairsLength().call()
        print(f"Scanning {min(500, total_pairs)} SushiSwap pairs...")  # Increased limit
        
        for i in range(min(500, total_pairs)):
            if i % 100 == 0:
                print(f"Processing SushiSwap pair {i}/{min(500, total_pairs)}...")
            
            try:
                pair_addr = factory.functions.allPairs(i).call()
                pair = w3.eth.contract(address=pair_addr, abi=PAIR_ABI)
                
                reserves = pair.functions.getReserves().call()
                token0 = pair.functions.token0().call()
                token1 = pair.functions.token1().call()
                
                if reserves[0] > 0 and reserves[1] > 0:
                    symbols = []
                    decimals = []
                    for token in [token0, token1]:
                        try:
                            erc20 = w3.eth.contract(address=token, abi=[
                                {"constant":True,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"type":"function"},
                                {"constant":True,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"type":"function"}
                            ])
                            symbol = erc20.functions.symbol().call()
                            decimal = erc20.functions.decimals().call()
                            symbols.append(symbol)
                            decimals.append(decimal)
                        except Exception:
                            symbols.append("?")
                            decimals.append(18)
                    
                    reserve0_normalized = reserves[0] / (10 ** decimals[0])
                    reserve1_normalized = reserves[1] / (10 ** decimals[1])
                    
                    price = reserve1_normalized / reserve0_normalized if reserve0_normalized > 0 else 0
                    
                    if price < 0.0001 and reserve1_normalized > 0:
                        price = reserve0_normalized / reserve1_normalized
                    
                    pair_key = f"{symbols[0]}/{symbols[1]}"
                    
                    # More aggressive filtering - look for pairs with significant liquidity
                    total_liquidity_usd = (reserve0_normalized + reserve1_normalized) * 2500  # Rough USD estimate
                    
                    if price > 0 and total_liquidity_usd > MIN_LIQUIDITY_USD:  # Only pairs with >$50k liquidity
                        prices[pair_key] = {
                            'price': price,
                            'pair_address': pair_addr,
                            'token0': token0,
                            'token1': token1,
                            'liquidity_usd': total_liquidity_usd
                        }
                        
            except Exception as e:
                continue
                
    except Exception as e:
        print(f"SushiSwap factory not accessible: {e}")
        return {}
    
    return prices

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
                                'token1': t1['id']
                            }
                            processed_count += 1
                    except Exception as e:
                        continue
                
                print(f"Processed {processed_count} Aerodrome pools")
                return prices
                
    except Exception as e:
        print(f"Error fetching Aerodrome prices: {e}")
        return {}

def find_arbitrage_opportunities(uniswap_prices, sushiswap_prices, aerodrome_prices):
    """Find arbitrage opportunities with enhanced analysis"""
    opportunities = []
    
    all_prices = {
        'Uniswap': uniswap_prices,
        'SushiSwap': sushiswap_prices,
        'Aerodrome': aerodrome_prices
    }
    
    print(f"Uniswap pairs: {list(uniswap_prices.keys())}")
    print(f"SushiSwap pairs: {list(sushiswap_prices.keys())[:5]}...")
    print(f"Aerodrome pairs: {list(aerodrome_prices.keys())[:5]}...")
    
    all_pairs = set()
    for dex_prices in all_prices.values():
        all_pairs.update(dex_prices.keys())
    
    print(f"Total unique pairs found: {len(all_pairs)}")
    
    uniswap_pairs = set(uniswap_prices.keys())
    sushiswap_pairs = set(sushiswap_prices.keys())
    aerodrome_pairs = set(aerodrome_prices.keys())
    
    common_uni_sushi = uniswap_pairs.intersection(sushiswap_pairs)
    common_uni_aero = uniswap_pairs.intersection(aerodrome_pairs)
    common_sushi_aero = sushiswap_pairs.intersection(aerodrome_pairs)
    
    print(f"Common Uniswap-SushiSwap pairs: {list(common_uni_sushi)}")
    print(f"Common Uniswap-Aerodrome pairs: {list(common_uni_aero)}")
    print(f"Common SushiSwap-Aerodrome pairs: {list(common_sushi_aero)}")
    
    for pair in all_pairs:
        pair_prices = {}
        for dex_name, dex_prices in all_prices.items():
            if pair in dex_prices:
                pair_prices[dex_name] = dex_prices[pair]['price']
        
        if len(pair_prices) >= 2:
            prices = list(pair_prices.values())
            min_price = min(prices)
            max_price = max(prices)
            
            if max_price > min_price and min_price > 0:
                buy_dex = [k for k, v in pair_prices.items() if v == min_price][0]
                sell_dex = [k for k, v in pair_prices.items() if v == max_price][0]
                
                profit_pct = ((max_price - min_price) / min_price) * 100
                
                # Realistic thresholds for executable arbitrage
                if MIN_PROFIT_PCT <= profit_pct <= MAX_PROFIT_PCT:
                    # Enhanced profit analysis with flash loan capabilities
                    profit_analysis = estimate_flash_loan_profit(min_price, max_price, pair)
                    
                    if profit_analysis['is_profitable']:
                        opportunities.append({
                            'pair': pair,
                            'buy_dex': buy_dex,
                            'sell_dex': sell_dex,
                            'buy_price': min_price,
                            'sell_price': max_price,
                            'profit_pct': profit_pct,
                            'profit_analysis': profit_analysis,
                            'strategy': 'flash_loan' if profit_analysis['flash_loan_profit'] > profit_analysis['regular_profit'] else 'regular'
                        })
    
    return sorted(opportunities, key=lambda x: x['profit_analysis']['net_profit_usd'], reverse=True)

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

def estimate_profit(buy_price, sell_price, eth_amount=DEFAULT_ETH_AMOUNT, eth_price_usd=2500):
    """
    Estimate realistic arbitrage profit accounting for all costs
    """
    gross_profit_usd = (sell_price - buy_price) * eth_amount * eth_price_usd
    
    gas_price_eth = BASE_GAS_PRICE_GWEI / 1e9
    total_gas_eth = (GAS_LIMIT_SWAP * 2 + GAS_LIMIT_APPROVE * 2) * gas_price_eth
    gas_cost_usd = total_gas_eth * eth_price_usd
    
    transaction_fees_usd = (buy_price + sell_price) * eth_amount * eth_price_usd * TRANSACTION_FEE_PCT * 2
    slippage_cost_usd = (buy_price + sell_price) * eth_amount * eth_price_usd * SLIPPAGE_PCT * 2
    mev_protection_cost_usd = MEV_PROTECTION_COST_USD
    
    total_costs_usd = gas_cost_usd + transaction_fees_usd + slippage_cost_usd + mev_protection_cost_usd
    net_profit_usd = gross_profit_usd - total_costs_usd
    
    return {
        'gross_profit_usd': gross_profit_usd,
        'gas_cost_usd': gas_cost_usd,
        'transaction_fees_usd': transaction_fees_usd,
        'slippage_cost_usd': slippage_cost_usd,
        'mev_protection_cost_usd': mev_protection_cost_usd,
        'total_costs_usd': total_costs_usd,
        'net_profit_usd': net_profit_usd,
        'is_profitable': net_profit_usd > MIN_PROFIT_THRESHOLD_USD
    }

async def monitor():
    """Enhanced monitoring loop with real-time execution capabilities"""
    # Initialize executor
    executor = ArbitrageExecutor(PRIVATE_KEY)
    
    print(f"🔧 Execution Mode: {'LIVE' if EXECUTION_MODE else 'SIMULATION'}")
    print(f"📊 Simulation Mode: {'ENABLED' if SIMULATION_MODE else 'DISABLED'}")
    print(f"💰 Position Size: ${POSITION_SIZE_USD:,.0f}")
    print(f"📊 Profit Range: {MIN_PROFIT_PCT}%-{MAX_PROFIT_PCT}%")
    print(f"💧 Min Liquidity: ${MIN_LIQUIDITY_USD:,.0f}")
    print(f"🛡️  Safe Mode: {'ENABLED' if SAFE_MODE else 'DISABLED'}")
    
    if SAFE_MODE:
        print(f"⚠️  SAFE TESTING MODE:")
        print(f"   - Max position size: $10")
        print(f"   - Max profit: 20%")
        print(f"   - Only safe tokens allowed")
        print(f"   - Current position size: ${POSITION_SIZE_USD}")
    
    if SIMULATION_MODE:
        print(f"🎮 SIMULATION MODE:")
        print(f"   - No real transactions will be sent")
        print(f"   - All operations will be simulated")
        print(f"   - Safe for testing without risk")
    
    # Check available tokens first
    if executor.account:
        executor.check_available_tokens()
    
    first_trade = True
    
    while True:
        print("\n" + "="*60)
        print("🚀 Real-Time Arbitrage Bot - Safe Testing Mode")
        print("="*60)
        
        # Get prices from all DEXes
        uniswap_prices = await get_uniswap_prices()
        sushiswap_prices = await get_sushiswap_prices()
        aerodrome_prices = await get_aerodrome_prices()
        
        print(f"📊 Found {len(uniswap_prices)} Uniswap pools")
        print(f"📊 Found {len(sushiswap_prices)} SushiSwap pools")
        print(f"📊 Found {len(aerodrome_prices)} Aerodrome pools")
        
        # Find arbitrage opportunities
        opportunities = find_arbitrage_opportunities(uniswap_prices, sushiswap_prices, aerodrome_prices)
        
        if opportunities:
            print(f"\n🔥 Found {len(opportunities)} executable arbitrage opportunities:")
            print("-" * 80)
            
            for i, opp in enumerate(opportunities[:5]):  # Show top 5
                analysis = opp['profit_analysis']
                strategy = opp.get('strategy', 'regular')
                
                print(f"{i+1}. {opp['pair']} ({strategy.upper()})")
                print(f"   Buy on {opp['buy_dex']} @ {opp['buy_price']:.6f}")
                print(f"   Sell on {opp['sell_dex']} @ {opp['sell_price']:.6f}")
                print(f"   Profit: {opp['profit_pct']:.2f}%")
                
                if strategy == 'flash_loan':
                    print(f"   Flash Loan Profit: ${analysis['flash_loan_profit']:.2f}")
                    print(f"   Flash Loan Amount: ${analysis['flash_loan_amount_usd']:,.0f}")
                    print(f"   Flash Loan Fee: ${analysis['flash_loan_fee']:.2f}")
                else:
                    print(f"   Regular Profit: ${analysis['regular_profit']:.2f}")
                
                print(f"   Net Profit: ${analysis['net_profit_usd']:.2f}")
                
                # Execute the best opportunity
                if i == 0 and EXECUTION_MODE:
                    print(f"\n🎯 Executing best opportunity: {opp['pair']}")
                    
                    # Safety confirmation for first trade
                    if first_trade and SAFE_MODE:
                        print(f"\n⚠️  FIRST TRADE CONFIRMATION:")
                        print(f"   This will execute a real trade with ${POSITION_SIZE_USD}")
                        print(f"   Max potential loss: ${POSITION_SIZE_USD * 0.05:.2f}")
                        print(f"   Mode: {'SIMULATION' if SIMULATION_MODE else 'LIVE'}")
                        print(f"   Continue? (y/n): ", end="")
                        # For now, auto-continue but you can add input() here
                        print("AUTO-CONTINUING (remove this line to add manual confirmation)")
                    
                    success = executor.execute_arbitrage(opp)
                    if success:
                        print("✅ Arbitrage executed successfully!")
                        first_trade = False
                    else:
                        print("❌ Arbitrage execution failed")
                
                print()
        else:
            print("❌ No executable arbitrage opportunities found")
        
        print(f"⏰ Next scan in 15 seconds...")
        await asyncio.sleep(15)

if __name__ == "__main__":
    asyncio.run(monitor())
