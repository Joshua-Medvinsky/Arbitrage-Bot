import asyncio
import os
import aiohttp
from web3 import Web3
from dotenv import load_dotenv
import sys
import time
from datetime import datetime, timedelta
from collections import defaultdict, deque
import threading
import json

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config import PAIR_ABI, SUSHI_FACTORY_ABI, DEFAULT_ETH_AMOUNT, DEFAULT_GAS_ETH, DEFAULT_SLIPPAGE_PCT, USDC_ADDRESS, WETH_ADDRESS, ZORA_ADDRESS, SUSHI_FACTORY_ADDRESS, BASE_GAS_PRICE_GWEI, TRANSACTION_FEE_PCT, SLIPPAGE_PCT, MEV_PROTECTION_COST_USD, MIN_PROFIT_THRESHOLD_USD, SAFE_MODE, POSITION_SIZE_USD, FLASH_LOAN_ENABLED, EXECUTION_MODE, SIMULATION_MODE, MIN_PROFIT_PCT, MAX_PROFIT_PCT, MIN_LIQUIDITY_USD
from scripts.monitoring.token_addresses import TOKEN_ADDRESSES, WETH_BASE, USDC_BASE, weETH_BASE

load_dotenv()

# Import missing variables from config
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

# Monitoring Configuration
MONITORING_INTERVAL_SECONDS = int(os.getenv("MONITORING_INTERVAL_SECONDS", "30"))
ERROR_RETRY_SECONDS = int(os.getenv("ERROR_RETRY_SECONDS", "10"))
MAX_LOOPS = int(os.getenv("MAX_LOOPS", "0"))  # 0 = infinite
DASHBOARD_UPDATE_INTERVAL = int(os.getenv("DASHBOARD_UPDATE_INTERVAL", "5"))  # seconds

# Web3 and API configuration
WEB3_PROVIDER = os.getenv("WEB3_PROVIDER")
UNISWAP_V3_SUBGRAPH = os.getenv("UNISWAP_V3_SUBGRAPH")
AERODROME_SUBGRAPH = os.getenv("AERODROME_SUBGRAPH")
BALANCER_V2_SUBGRAPH = os.getenv("BALANCER_V2_SUBGRAPH")
UNISWAP_API_KEY = os.getenv("UNISWAP_API_KEY")

w3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER))

# Convert addresses to checksum format
USDC = Web3.to_checksum_address(USDC_ADDRESS)
WETH = Web3.to_checksum_address(WETH_ADDRESS)

# Flash loan contract addresses (Aave V3 on Base)
AAVE_LENDING_POOL = "0xA238Dd80C259a72e81d7e4664a9801593F98d1c5"

# Flash loan receiver contract address (deploy this contract first)
FLASH_LOAN_RECEIVER_ADDRESS = "0x95DD361C6e75A93C610f359bcAb5412050976ddb"

# Flash loan settings
FLASH_LOAN_ENABLED = False  # Disable flash loans for now, focus on regular arbitrage
FLASH_LOAN_AMOUNT_USD = 1  # Reduced to $1 for testing
FLASH_LOAN_FEE_PCT = 0.0009  # 0.09% flash loan fee
FLASH_LOAN_MIN_PROFIT_USD = 0.1  # Reduced minimum profit for testing

# Direct flash loan approach (no contract deployment needed)
DIRECT_FLASH_LOAN = True  # Set to True for simpler approach

# MEV Bot detection
MEV_BOT_ADDRESSES = [
    "0x0000000000000000000000000000000000000000",  # Placeholder - real MEV bots
]

# Uniswap V3 Router for execution (Base network)
UNISWAP_V3_ROUTER = Web3.to_checksum_address("0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45")

# SushiSwap router address and ABI
SUSHISWAP_ROUTER = '0x6BDED42c6DA8FBf0d2bA55B2fa120C5e0c8D7891'

# Helper to load ABI from JSON file
def load_abi(filename):
    with open(os.path.join(os.path.dirname(__file__), 'abis', filename), 'r') as f:
        return json.load(f)

# Load ABIs from JSON files
UNISWAP_V3_ROUTER_ABI = load_abi('uniswap_v3_router.json')
SUSHISWAP_ROUTER_ABI = load_abi('sushiswap_router.json')
ERC20_ABI = load_abi('erc20.json')
AAVE_LENDING_POOL_ABI = load_abi('aave_lending_pool.json')
FLASH_LOAN_RECEIVER_ABI = load_abi('flash_loan_receiver.json')

# Uniswap V3 Factory for pool verification
UNISWAP_V3_FACTORY = Web3.to_checksum_address("0x33128a8fC17869897dcE68Ed026d694621f6FDfD")
UNISWAP_V3_FACTORY_ABI = [
    {"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint24","name":"fee","type":"uint24"}],"name":"getPool","outputs":[{"internalType":"address","name":"pool","type":"address"}],"stateMutability":"view","type":"function"}
]

# Aerodrome Router for execution (Base network)
AERODROME_ROUTER = Web3.to_checksum_address("0xcF77a3Ba9A5CA399B7c97c74d54e5b1Beb874E43")
AERODROME_ROUTER_ABI = [
    {"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"components":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"bool","name":"stable","type":"bool"},{"internalType":"address","name":"factory","type":"address"}],"internalType":"struct IRouter.Route[]","name":"routes","type":"tuple[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"}
]

# Balancer V2 Vault for execution (Base network)
BALANCER_V2_VAULT = Web3.to_checksum_address("0xBA12222222228d8Ba445958a75a0704d566BF2C8")
BALANCER_V2_VAULT_ABI = [
    {"inputs":[{"components":[{"internalType":"bytes32","name":"poolId","type":"bytes32"},{"internalType":"enum IVault.SwapKind","name":"kind","type":"uint8"},{"internalType":"contract IAsset","name":"assetIn","type":"address"},{"internalType":"contract IAsset","name":"assetOut","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"bytes","name":"userData","type":"bytes"}],"internalType":"struct IVault.SingleSwap","name":"singleSwap","type":"tuple"},{"components":[{"internalType":"address","name":"sender","type":"address"},{"internalType":"bool","name":"fromInternalBalance","type":"bool"},{"internalType":"address payable","name":"recipient","type":"address"},{"internalType":"bool","name":"toInternalBalance","type":"bool"}],"internalType":"struct IVault.FundManagement","name":"funds","type":"tuple"},{"internalType":"uint256","name":"limit","type":"uint256"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swap","outputs":[{"internalType":"uint256","name":"amountCalculated","type":"uint256"}],"stateMutability":"payable","type":"function"}
]

class ArbitrageExecutor:
    def __init__(self, private_key=None):
        self.w3 = w3
        self.account = None
        if private_key and private_key != "your_private_key_here" and len(private_key) == 64:
            try:
                self.account = self.w3.eth.account.from_key(private_key)
                print(f"🔐 Loaded wallet: {self.account.address}")
            except Exception as e:
                print(f"⚠️  Invalid private key - running in simulation mode: {e}")
        else:
            print("⚠️  No valid private key provided - running in simulation mode")
        
        # Initialize contracts
        self.uniswap_router = w3.eth.contract(address=UNISWAP_V3_ROUTER, abi=UNISWAP_V3_ROUTER_ABI)
        self.aerodrome_router = w3.eth.contract(address=AERODROME_ROUTER, abi=AERODROME_ROUTER_ABI)
        self.balancer_vault = w3.eth.contract(address=BALANCER_V2_VAULT, abi=BALANCER_V2_VAULT_ABI)
        
        # Initialize flash loan contracts
        self.aave_lending_pool = w3.eth.contract(address=Web3.to_checksum_address(AAVE_LENDING_POOL), abi=AAVE_LENDING_POOL_ABI)
        
        # Initialize flash loan receiver contract
        if FLASH_LOAN_RECEIVER_ADDRESS != "0x0000000000000000000000000000000000000000":
            self.flash_loan_receiver = w3.eth.contract(
                address=Web3.to_checksum_address(FLASH_LOAN_RECEIVER_ADDRESS), 
                abi=FLASH_LOAN_RECEIVER_ABI
            )
            print(f"🔐 Flash loan receiver contract: {FLASH_LOAN_RECEIVER_ADDRESS}")
        else:
            self.flash_loan_receiver = None
            print("⚠️  Flash loan receiver contract not deployed - flash loans disabled")
            print("   Deploy flash_loan_receiver.sol first and set FLASH_LOAN_RECEIVER_ADDRESS")
    
    def validate_opportunity(self, opportunity):
        """Validate if an opportunity is realistic and executable"""
        profit_pct = opportunity['profit_pct']
        # Allow any opportunity with profit_pct > 20%
        if profit_pct > 20:
            return True, "Profit percentage above 20%, running regardless of expected net profit."
        # SAFETY CHECKS FOR TESTING
        if SAFE_MODE:
            # Only allow very small amounts for testing
            if POSITION_SIZE_USD > 10:
                return False, f"Position size ${POSITION_SIZE_USD} too large for testing mode"
            # Only allow profit up to MAX_PROFIT_PCT for safety
            if profit_pct > MAX_PROFIT_PCT:
                return False, f"Profit {profit_pct:.2f}% too high for safe testing (max {MAX_PROFIT_PCT}%)"
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
    
    def execute_arbitrage(self, opportunity):
        """Execute regular arbitrage (simulation mode)"""
        if SIMULATION_MODE:
            print(f"🎮 SIMULATION: Would execute arbitrage for {opportunity['pair']}")
            print(f"   Buy on {opportunity['buy_dex']} @ {opportunity['buy_price']:.6f}")
            print(f"   Sell on {opportunity['sell_dex']} @ {opportunity['sell_price']:.6f}")
            print(f"   Expected profit: {opportunity['profit_pct']:.2f}%")
            return True
        else:
            print(f"❌ Live execution not implemented yet")
            return False
    
    def execute_flash_loan_arbitrage(self, opportunity):
        """Execute flash loan arbitrage (simulation mode)"""
        if SIMULATION_MODE:
            print(f"🎮 SIMULATION: Would execute flash loan arbitrage for {opportunity['pair']}")
            print(f"   Buy on {opportunity['buy_dex']} @ {opportunity['buy_price']:.6f}")
            print(f"   Sell on {opportunity['sell_dex']} @ {opportunity['sell_price']:.6f}")
            print(f"   Expected profit: {opportunity['profit_pct']:.2f}%")
            return True
        else:
            print(f"❌ Live flash loan execution not implemented yet")
            return False

class MonitoringDashboard:
    """Dashboard for tracking arbitrage monitoring statistics"""
    
    def __init__(self):
        self.stats = {
            'start_time': datetime.now(),
            'loop_count': 0,
            'total_opportunities_found': 0,
            'opportunities_executed': 0,
            'total_profit_usd': 0.0,
            'errors': 0,
            'last_opportunity_time': None,
            'best_opportunity': None,
            'dex_stats': defaultdict(int),
            'pair_stats': defaultdict(int),
            'execution_times': deque(maxlen=100),
            'recent_opportunities': deque(maxlen=50)
        }
        self.lock = threading.Lock()
        self.running = True
    
    def update_stats(self, **kwargs):
        """Thread-safe stats update"""
        with self.lock:
            for key, value in kwargs.items():
                if key in self.stats:
                    if isinstance(value, (int, float)):
                        self.stats[key] += value
                    else:
                        self.stats[key] = value
    
    def add_opportunity(self, opportunity):
        """Add a new opportunity to tracking"""
        with self.lock:
            self.stats['total_opportunities_found'] += 1
            self.stats['last_opportunity_time'] = datetime.now()
            
            # Track by DEX
            buy_dex = opportunity.get('buy_dex', 'Unknown')
            sell_dex = opportunity.get('sell_dex', 'Unknown')
            self.stats['dex_stats'][f"{buy_dex}->{sell_dex}"] += 1
            
            # Track by pair
            pair = opportunity.get('pair', 'Unknown')
            self.stats['pair_stats'][pair] += 1
            
            # Track best opportunity
            profit_usd = opportunity.get('profit_analysis', {}).get('net_profit_usd', 0)
            if not self.stats['best_opportunity'] or profit_usd > self.stats['best_opportunity']['profit_usd']:
                self.stats['best_opportunity'] = {
                    'pair': pair,
                    'buy_dex': buy_dex,
                    'sell_dex': sell_dex,
                    'profit_usd': profit_usd,
                    'profit_pct': opportunity.get('profit_pct', 0),
                    'time': datetime.now()
                }
            
            # Add to recent opportunities
            self.stats['recent_opportunities'].append({
                'time': datetime.now(),
                'pair': pair,
                'buy_dex': buy_dex,
                'sell_dex': sell_dex,
                'profit_usd': profit_usd,
                'profit_pct': opportunity.get('profit_pct', 0)
            })
    
    def add_execution_time(self, execution_time):
        """Add execution time to tracking"""
        with self.lock:
            self.stats['execution_times'].append(execution_time)
    
    def get_uptime(self):
        """Get uptime string"""
        uptime = datetime.now() - self.stats['start_time']
        hours = int(uptime.total_seconds() // 3600)
        minutes = int((uptime.total_seconds() % 3600) // 60)
        return f"{hours}h {minutes}m"
    
    def get_avg_execution_time(self):
        """Get average execution time"""
        if not self.stats['execution_times']:
            return 0
        return sum(self.stats['execution_times']) / len(self.stats['execution_times'])
    
    def get_opportunities_per_hour(self):
        """Get opportunities found per hour"""
        uptime_hours = (datetime.now() - self.stats['start_time']).total_seconds() / 3600
        if uptime_hours == 0:
            return 0
        return self.stats['total_opportunities_found'] / uptime_hours
    
    def print_dashboard(self):
        """Print the monitoring dashboard"""
        with self.lock:
            print("\n" + "="*80)
            print("📊 ARBITRAGE MONITORING DASHBOARD")
            print("="*80)
            
            # Basic stats
            print(f"⏱️  Uptime: {self.get_uptime()}")
            print(f"🔄 Loops completed: {self.stats['loop_count']}")
            print(f"⚡ Avg execution time: {self.get_avg_execution_time():.1f}s")
            print(f"🎯 Opportunities found: {self.stats['total_opportunities_found']}")
            print(f"💰 Opportunities executed: {self.stats['opportunities_executed']}")
            print(f"📈 Opportunities/hour: {self.get_opportunities_per_hour():.1f}")
            print(f"❌ Errors: {self.stats['errors']}")
            
            # Best opportunity
            if self.stats['best_opportunity']:
                best = self.stats['best_opportunity']
                print(f"\n🏆 Best Opportunity:")
                print(f"   Pair: {best['pair']}")
                print(f"   Route: {best['buy_dex']} → {best['sell_dex']}")
                print(f"   Profit: ${best['profit_usd']:.2f} ({best['profit_pct']:.2f}%)")
                print(f"   Time: {best['time'].strftime('%H:%M:%S')}")
            
            # Top DEX combinations
            if self.stats['dex_stats']:
                print(f"\n📊 Top DEX Routes:")
                sorted_dex = sorted(self.stats['dex_stats'].items(), key=lambda x: x[1], reverse=True)
                for route, count in sorted_dex[:5]:
                    print(f"   {route}: {count} opportunities")
            
            # Top pairs
            if self.stats['pair_stats']:
                print(f"\n🪙 Top Pairs:")
                sorted_pairs = sorted(self.stats['pair_stats'].items(), key=lambda x: x[1], reverse=True)
                for pair, count in sorted_pairs[:5]:
                    print(f"   {pair}: {count} opportunities")
            
            # Recent opportunities
            if self.stats['recent_opportunities']:
                print(f"\n🕒 Recent Opportunities:")
                for opp in list(self.stats['recent_opportunities'])[-5:]:
                    time_str = opp['time'].strftime('%H:%M:%S')
                    print(f"   {time_str} | {opp['pair']} | {opp['buy_dex']}→{opp['sell_dex']} | ${opp['profit_usd']:.2f} ({opp['profit_pct']:.2f}%)")
            
            print("="*80)
    
    def start_dashboard_thread(self):
        """Start dashboard update thread"""
        def dashboard_loop():
            while self.running:
                try:
                    self.print_dashboard()
                    time.sleep(DASHBOARD_UPDATE_INTERVAL)
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(f"Dashboard error: {e}")
        
        dashboard_thread = threading.Thread(target=dashboard_loop, daemon=True)
        dashboard_thread.start()
        return dashboard_thread
    
    def stop(self):
        """Stop the dashboard"""
        self.running = False

# Cache for token information to avoid repeated lookups
TOKEN_CACHE = {}
POOL_CACHE = {}

async def get_all_prices_parallel():
    """Get all DEX prices in parallel for better performance"""
    try:
        # Parallel execution of all DEX price fetching
        uniswap_prices, aerodrome_prices, balancer_v2_prices, sushiswap_prices = await asyncio.gather(
            get_uniswap_prices(),
            get_aerodrome_prices(),
            get_balancer_v2_prices(),
            get_sushiswap_prices(),
            return_exceptions=True
        )
        
        # Handle any exceptions from individual DEX calls
        prices = {}
        if not isinstance(uniswap_prices, Exception):
            prices['Uniswap'] = uniswap_prices
        else:
            print(f"❌ Uniswap error: {uniswap_prices}")
            prices['Uniswap'] = {}
            
        if not isinstance(aerodrome_prices, Exception):
            prices['Aerodrome'] = aerodrome_prices
        else:
            print(f"❌ Aerodrome error: {aerodrome_prices}")
            prices['Aerodrome'] = {}
            
        if not isinstance(balancer_v2_prices, Exception):
            prices['Balancer V2'] = balancer_v2_prices
        else:
            print(f"❌ Balancer V2 error: {balancer_v2_prices}")
            prices['Balancer V2'] = {}
            
        if not isinstance(sushiswap_prices, Exception):
            prices['SushiSwap'] = sushiswap_prices
        else:
            print(f"❌ SushiSwap error: {sushiswap_prices}")
            prices['SushiSwap'] = {}
        
        return prices
        
    except Exception as e:
        print(f"❌ Error in parallel price fetching: {e}")
        return {}

async def monitor_once_optimized(executor, dashboard):
    """Optimized single monitoring cycle with dashboard integration"""
    start_time = time.time()
    
    try:
        print(f"\n🔄 Monitoring cycle #{dashboard.stats['loop_count'] + 1} started at {datetime.now().strftime('%H:%M:%S')}")
        
        # Parallel price fetching
        all_prices = await get_all_prices_parallel()
        
        # Extract individual DEX prices
        uniswap_prices = all_prices.get('Uniswap', {})
        aerodrome_prices = all_prices.get('Aerodrome', {})
        balancer_v2_prices = all_prices.get('Balancer V2', {})
        sushiswap_prices = all_prices.get('SushiSwap', {})
        
        print(f"📊 Found {len(uniswap_prices)} Uniswap pools")
        print(f"📊 Found {len(aerodrome_prices)} Aerodrome pools")
        print(f"📊 Found {len(balancer_v2_prices)} Balancer V2 pools")
        print(f"📊 Found {len(sushiswap_prices)} SushiSwap pools")
        
        print("🔍 Analyzing arbitrage opportunities...")
        opportunities = find_arbitrage_opportunities(uniswap_prices, aerodrome_prices, balancer_v2_prices, sushiswap_prices, executor=executor)
        
        # Update dashboard with opportunities
        for opp in opportunities:
            dashboard.add_opportunity(opp)
        
        if not opportunities:
            print("❌ No executable arbitrage opportunities found")
        else:
            print(f"\n🔥 Found {len(opportunities)} executable arbitrage opportunities:")
            print("-" * 80)
            
            # Sort by profit percentage
            opportunities.sort(key=lambda x: x.get('profit_pct', 0), reverse=True)
            
            executed = False
            for i, opp in enumerate(opportunities[:5]):  # Show top 5
                analysis = opp['profit_analysis']
                strategy = opp.get('strategy', 'regular')
                print(f"{i+1}. {opp['pair']} ({strategy.upper()})")
                print(f"   Buy on {opp['buy_dex']} @ {opp['buy_price']:.6f}")
                print(f"   Sell on {opp['sell_dex']} @ {opp['sell_price']:.6f}")
                print(f"   Profit: {opp['profit_pct']:.2f}%")
                print(f"   Net Profit: ${analysis.get('net_profit_usd', 0):.2f}")
                print(f"   Net Profit %: {analysis.get('net_profit_pct', 0):.2f}%")
                
                if EXECUTION_MODE and not executed:
                    print(f"\n🎯 Executing opportunity: {opp['pair']}")
                    print(f"   Strategy: {strategy.upper()}")
                    
                    if FLASH_LOAN_ENABLED:
                        print(f"💰 Using FLASH LOAN arbitrage for {opp['pair']}")
                        success = executor.execute_flash_loan_arbitrage(opp)
                    else:
                        print(f"💰 Using REGULAR arbitrage for {opp['pair']}")
                        success = executor.execute_arbitrage(opp)
                    
                    if success:
                        print("✅ Arbitrage executed successfully!")
                        dashboard.update_stats(opportunities_executed=1)
                        executed = True
                        break
                    else:
                        print("❌ Arbitrage execution failed")
        
        # Update execution time
        execution_time = time.time() - start_time
        dashboard.add_execution_time(execution_time)
        dashboard.update_stats(loop_count=1)
        
        print(f"⏱️  Cycle completed in {execution_time:.1f}s")
        
    except Exception as e:
        print(f"❌ Error in monitoring cycle: {e}")
        dashboard.update_stats(errors=1)

async def monitor_continuously():
    """Continuous monitoring with dashboard"""
    executor = ArbitrageExecutor(PRIVATE_KEY)
    dashboard = MonitoringDashboard()
    
    print(f"🚀 Starting continuous arbitrage monitoring...")
    print(f"🔧 Execution Mode: {'LIVE' if EXECUTION_MODE else 'SIMULATION'}")
    print(f"📊 Simulation Mode: {'ENABLED' if SIMULATION_MODE else 'DISABLED'}")
    print(f"💰 Position Size: ${POSITION_SIZE_USD:,.0f}")
    print(f"📊 Profit Range: {MIN_PROFIT_PCT}%-{MAX_PROFIT_PCT}%")
    print(f"💧 Min Liquidity: ${MIN_LIQUIDITY_USD:,.0f}")
    print(f"⏱️  Monitoring Interval: {MONITORING_INTERVAL_SECONDS}s")
    print(f"📊 Dashboard Update: {DASHBOARD_UPDATE_INTERVAL}s")
    print(f"🛡️  Safe Mode: {'ENABLED' if SAFE_MODE else 'DISABLED'}")
    print(f"🚀 Flash Loan Enabled: {FLASH_LOAN_ENABLED}")
    print("\nPress Ctrl+C to stop monitoring\n")
    
    # Start dashboard thread
    dashboard.start_dashboard_thread()
    
    try:
        loop_count = 0
        while True:
            if MAX_LOOPS > 0 and loop_count >= MAX_LOOPS:
                print(f"✅ Reached maximum loops ({MAX_LOOPS}), stopping...")
                break
                
            await monitor_once_optimized(executor, dashboard)
            loop_count += 1
            
            # Wait for next cycle
            print(f"⏳ Waiting {MONITORING_INTERVAL_SECONDS}s until next cycle...")
            await asyncio.sleep(MONITORING_INTERVAL_SECONDS)
            
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped by user")
    except Exception as e:
        print(f"❌ Fatal error in monitoring: {e}")
    finally:
        dashboard.stop()
        print("\n📊 Final Dashboard:")
        dashboard.print_dashboard()
        print("👋 Monitoring stopped")

# Keep the original monitor function for backward compatibility
async def monitor():
    """Single-run monitoring for arbitrage opportunities (backward compatibility)"""
    executor = ArbitrageExecutor(PRIVATE_KEY)
    dashboard = MonitoringDashboard()
    print(f"🔧 Execution Mode: {'LIVE' if EXECUTION_MODE else 'SIMULATION'}")
    print(f"📊 Simulation Mode: {'ENABLED' if SIMULATION_MODE else 'DISABLED'}")
    print(f"💰 Position Size: ${POSITION_SIZE_USD:,.0f}")
    print(f"📊 Profit Range: {MIN_PROFIT_PCT}%-{MAX_PROFIT_PCT}%")
    print(f"💧 Min Liquidity: ${MIN_LIQUIDITY_USD:,.0f}")
    print(f"🛡️  Safe Mode: {'ENABLED' if SAFE_MODE else 'DISABLED'}")
    print(f"🚀 Flash Loan Enabled: {FLASH_LOAN_ENABLED}")
    print("\nStarting single-run monitoring...\n")
    try:
        await monitor_once_optimized(executor, dashboard)
    except Exception as e:
        print(f"❌ Error in monitor: {e}")

# Add missing functions that were in the original file
async def get_uniswap_prices():
    """Get all Uniswap V3 pool prices with enhanced monitoring"""
    if not UNISWAP_V3_SUBGRAPH:
        print("UNISWAP_V3_SUBGRAPH not configured")
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
            feeTier
          }
        }
        """
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(UNISWAP_V3_SUBGRAPH, json=query) as resp:
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
                        fee_tier = int(pool.get("feeTier", 3000))
                        
                        if price > 0 and tvl > MIN_LIQUIDITY_USD and volume > 1000:
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
                        if 'token0Price' in pair and pair['token0Price']:
                            price = float(pair['token0Price'])
                        elif 'token1Price' in pair and pair['token1Price']:
                            price = float(pair['token1Price'])
                        
                        tvl = float(pair.get("totalValueLockedUSD", 0))
                        volume = float(pair.get("volumeUSD", 0))
                        
                        if 0.0001 < price < 1000000 and tvl > MIN_LIQUIDITY_USD and volume > 1000:
                            prices[pair_key] = {
                                'price': price,
                                'tvl': tvl,
                                'volume': volume,
                                'pool_id': pair['id'],
                                'token0': t0['id'],
                                'token1': t1['id'],
                                'fee_tier': None
                            }
                            processed_count += 1
                    except Exception as e:
                        continue
                
                print(f"Processed {processed_count} Aerodrome pools")
                return prices
                
    except Exception as e:
        print(f"Error fetching Aerodrome prices: {e}")
        return {}

async def get_balancer_v2_prices():
    """Get all Balancer V2 pool prices with enhanced monitoring"""
    if not BALANCER_V2_SUBGRAPH:
        print("BALANCER_V2_SUBGRAPH not configured")
        return {}
    
    try:
        async with aiohttp.ClientSession() as session:
            # Step 1: Get all pool IDs from balancers
            print("🔍 Step 1: Fetching Balancer V2 pool IDs...")
            pool_ids_query = {
                "query": """
                {
                  balancers {
                    id
                    poolCount
                    pools {
                      id
                    }
                  }
                }
                """
            }
            
            async with session.post(BALANCER_V2_SUBGRAPH, json=pool_ids_query) as resp:
                result = await resp.json()
                
                print(f"Balancer V2 subgraph response status: {resp.status}")
                if resp.status != 200:
                    print(f"Balancer V2 subgraph error: {result}")
                    return {}
                
                if result is None:
                    print("Balancer V2 subgraph returned None")
                    return {}
                
                # Extract pool IDs from balancers
                pool_ids = []
                balancers = result.get("data", {}).get("balancers", [])
                for balancer in balancers:
                    pools = balancer.get("pools", [])
                    for pool in pools:
                        pool_ids.append(pool["id"])
                
                print(f"Found {len(pool_ids)} Balancer V2 pool IDs")
                
                if not pool_ids:
                    print("No pool IDs found")
                    return {}
                
                # Step 2: Query each pool for details (limit to first 100 for performance)
                print("🔍 Step 2: Fetching pool details...")
                prices = {}
                processed_count = 0
                
                # Limit to first 100 pools for performance
                pool_ids_to_query = pool_ids[:100]
                
                for i, pool_id in enumerate(pool_ids_to_query):
                    if i % 10 == 0:
                        print(f"Processing Balancer V2 pool {i}/{len(pool_ids_to_query)}...")
                    
                    try:
                        # Query individual pool details
                        pool_query = {
                            "query": f"""
                            {{
                              pool(id: "{pool_id}") {{
                                id
                                address
                                poolType
                                poolTypeVersion
                                tokens {{
                                  id
                                  symbol
                                  decimals
                                  balance
                                  weight
                                }}
                                swaps(first: 1, orderBy: timestamp, orderDirection: desc) {{
                                  tokenAmountIn
                                  tokenAmountOut
                                  tokenIn
                                  tokenOut
                                }}
                                totalLiquidity
                                totalShares
                              }}
                            }}
                            """
                        }
                        
                        async with session.post(BALANCER_V2_SUBGRAPH, json=pool_query) as pool_resp:
                            pool_result = await pool_resp.json()
                            
                            if pool_resp.status != 200:
                                continue
                            
                            pool_data = pool_result.get("data", {}).get("pool")
                            if not pool_data:
                                continue
                            
                            tokens = pool_data.get("tokens", [])
                            if len(tokens) < 2:
                                continue
                            
                            # Get the first two tokens for price calculation
                            token0 = tokens[0]
                            token1 = tokens[1]
                            
                            # Calculate price based on token balances and weights
                            balance0 = token0.get("balance")
                            balance1 = token1.get("balance")
                            weight0 = token0.get("weight")
                            weight1 = token1.get("weight")
                            
                            # Check for null values before converting to float
                            if balance0 is None or balance1 is None:
                                continue
                            
                            # Convert to float after null checks
                            balance0 = float(balance0)
                            balance1 = float(balance1)
                            
                            if balance0 == 0 or balance1 == 0:
                                continue
                            
                            # Calculate price based on pool type
                            if weight0 is None or weight1 is None:
                                # For pools without weights (Gyro, Stable, etc.), use balance-based pricing
                                decimals0 = int(token0.get("decimals", 18))
                                decimals1 = int(token1.get("decimals", 18))
                                balance0_float = balance0 / (10 ** decimals0)
                                balance1_float = balance1 / (10 ** decimals1)
                                price = balance1_float / balance0_float if balance0_float > 0 else 0
                            else:
                                # For weighted pools, use weight-based pricing
                                weight0 = float(weight0)
                                weight1 = float(weight1)
                                decimals0 = int(token0.get("decimals", 18))
                                decimals1 = int(token1.get("decimals", 18))
                                balance0_float = balance0 / (10 ** decimals0)
                                balance1_float = balance1 / (10 ** decimals1)
                                price = (balance1_float / weight1) / (balance0_float / weight0) if balance0_float > 0 and weight0 > 0 else 0
                            
                            # Get total liquidity
                            total_liquidity = float(pool_data.get("totalLiquidity", 0))
                            
                            # Estimate TVL (rough calculation)
                            tvl = total_liquidity * 2  # Rough estimate
                            
                            pair_key = f"{token0['symbol']}/{token1['symbol']}"
                            
                            # Filter for liquid pools
                            if 0.0001 < price < 1000000 and tvl > MIN_LIQUIDITY_USD:
                                prices[pair_key] = {
                                    'price': price,
                                    'tvl': tvl,
                                    'volume': 0,
                                    'pool_id': pool_data['id'],
                                    'pool_address': pool_data['address'],
                                    'token0': token0['id'],
                                    'token1': token1['id'],
                                    'fee_tier': None
                                }
                                processed_count += 1
                                
                    except Exception as e:
                        print(f"Error processing pool {pool_id}: {e}")
                        continue
                
                print(f"Processed {processed_count} Balancer V2 pools")
                return prices
                
    except Exception as e:
        print(f"Error fetching Balancer V2 prices: {e}")
        return {}

async def get_sushiswap_prices():
    """Get all SushiSwap pool prices with enhanced monitoring"""
    # SushiSwap factory address on Base (from official documentation)
    SUSHISWAP_FACTORY = "0x71524B4f93c58fcbF659783284E38825f0622859"
    
    # SushiSwap router address on Base (from official documentation)
    SUSHISWAP_ROUTER = "0x6BDED42c6DA8FBf0d2bA55B2fa120C5e0c8D7891"
    
    # SushiSwap Factory ABI (minimal for pair enumeration)
    FACTORY_ABI = [
        {"constant":True,"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"allPairs","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":False,"stateMutability":"view","type":"function"},
        {"constant":True,"inputs":[],"name":"allPairsLength","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},
        {"constant":True,"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"address","name":"","type":"address"}],"name":"getPair","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":False,"stateMutability":"view","type":"function"}
    ]
    
    # SushiSwap Pair ABI (minimal for price calculation)
    PAIR_ABI = [
        {"constant":True,"inputs":[],"name":"getReserves","outputs":[{"internalType":"uint112","name":"_reserve0","type":"uint112"},{"internalType":"uint112","name":"_reserve1","type":"uint112"},{"internalType":"uint32","name":"_blockTimestampLast","type":"uint32"}],"payable":False,"stateMutability":"view","type":"function"},
        {"constant":True,"inputs":[],"name":"token0","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":False,"stateMutability":"view","type":"function"},
        {"constant":True,"inputs":[],"name":"token1","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":False,"stateMutability":"view","type":"function"}
    ]
    
    try:
        print("🔍 Fetching SushiSwap V2 prices from Base network...")
        
        # Create factory contract
        factory_contract = w3.eth.contract(address=Web3.to_checksum_address(SUSHISWAP_FACTORY), abi=FACTORY_ABI)
        
        # Get total number of pairs
        pair_count = factory_contract.functions.allPairsLength().call()
        print(f"   Found {pair_count} SushiSwap pairs on Base")
        
        if pair_count == 0:
            print("   No SushiSwap pairs found on Base")
            return {}
        
        # Limit to first 100 pairs for performance
        pairs_to_check = min(pair_count, 100)
        print(f"   Checking first {pairs_to_check} pairs...")
        
        prices = {}
        processed_count = 0
        
        for i in range(pairs_to_check):
            if i % 10 == 0:
                print(f"   Processing pair {i}/{pairs_to_check}...")
            
            try:
                # Get pair address
                pair_address = factory_contract.functions.allPairs(i).call()
                
                # Create pair contract
                pair_contract = w3.eth.contract(address=pair_address, abi=PAIR_ABI)
                
                # Get reserves
                reserves = pair_contract.functions.getReserves().call()
                reserve0, reserve1 = reserves[0], reserves[1]
                
                if reserve0 == 0 or reserve1 == 0:
                    continue  # Skip pairs with no liquidity
                
                # Get token addresses
                token0_address = pair_contract.functions.token0().call()
                token1_address = pair_contract.functions.token1().call()
                
                # Get token symbols and decimals
                try:
                    token0_contract = w3.eth.contract(address=token0_address, abi=ERC20_ABI)
                    token1_contract = w3.eth.contract(address=token1_address, abi=ERC20_ABI)
                    
                    token0_symbol = token0_contract.functions.symbol().call()
                    token1_symbol = token1_contract.functions.symbol().call()
                    token0_decimals = token0_contract.functions.decimals().call()
                    token1_decimals = token1_contract.functions.decimals().call()
                    
                except Exception as e:
                    # Skip pairs with inaccessible tokens
                    continue
                
                # Calculate price (token0/token1) with proper decimal handling - consistent with Uniswap V3
                reserve0_float = reserve0 / (10 ** token0_decimals)
                reserve1_float = reserve1 / (10 ** token1_decimals)
                
                if reserve1_float == 0:
                    continue
                
                # Price is token0/token1 (consistent with Uniswap V3 token0Price)
                price = reserve0_float / reserve1_float
                
                # Filter for realistic prices and liquid pairs
                if 0.0001 < price < 1000000 and reserve0_float > 0.001 and reserve1_float > 0.001:
                    pair_key = f"{token0_symbol}/{token1_symbol}"
                    
                    # Estimate TVL (rough calculation)
                    tvl_estimate = 0
                    if token0_symbol == 'WETH' or token1_symbol == 'WETH':
                        weth_price_usd = 2500
                        if token0_symbol == 'WETH':
                            tvl_estimate = reserve0_float * weth_price_usd * 2
                        else:
                            tvl_estimate = reserve1_float * weth_price_usd * 2
                    elif token0_symbol == 'USDC' or token1_symbol == 'USDC':
                        usdc_price_usd = 1
                        if token0_symbol == 'USDC':
                            tvl_estimate = reserve0_float * usdc_price_usd * 2
                        else:
                            tvl_estimate = reserve1_float * usdc_price_usd * 2
                    else:
                        # Rough estimate for other tokens
                        tvl_estimate = (reserve0_float + reserve1_float) * 1000
                    
                    prices[pair_key] = {
                        'price': price,
                        'tvl': tvl_estimate,
                        'volume': 0,
                        'pool_id': pair_address,
                        'token0': token0_address,
                        'token1': token1_address,
                        'fee_tier': None
                    }
                    processed_count += 1
                    
            except Exception as e:
                # Skip problematic pairs
                continue
        
        print(f"   Processed {processed_count} SushiSwap pairs with valid prices")
        return prices
        
    except Exception as e:
        print(f"Error fetching SushiSwap prices: {e}")
        return {}

def validate_token_match(pair, all_prices):
    """Validate that the same tokens are being compared across DEXes"""
    # Extract token addresses for this pair from all DEXes
    token_addresses = {}
    
    for dex_name, dex_prices in all_prices.items():
        if pair in dex_prices:
            pool_info = dex_prices[pair]
            token0 = pool_info.get('token0')
            token1 = pool_info.get('token1')
            if token0 and token1:
                token_addresses[dex_name] = (token0.lower(), token1.lower())
    
    if len(token_addresses) < 2:
        return False, "Not enough DEXes with token addresses"
    
    # Check if all DEXes have the same token addresses
    first_dex = list(token_addresses.keys())[0]
    first_tokens = token_addresses[first_dex]
    
    for dex_name, tokens in token_addresses.items():
        if tokens != first_tokens:
            print(f"[TOKEN_MISMATCH] {pair}: {dex_name} has different token addresses")
            print(f"   {first_dex}: {first_tokens}")
            print(f"   {dex_name}: {tokens}")
            return False, f"Token addresses don't match between {first_dex} and {dex_name}"
    
    return True, "Token addresses match"

def find_arbitrage_opportunities(uniswap_prices, aerodrome_prices, balancer_v2_prices, sushiswap_prices, executor=None):
    """Find arbitrage opportunities with enhanced analysis"""
    opportunities = []
    all_prices = {
        'Uniswap': uniswap_prices,
        'Aerodrome': aerodrome_prices,
        'Balancer V2': balancer_v2_prices,
        'SushiSwap': sushiswap_prices
    }
    all_pairs = set()
    for dex_prices in all_prices.values():
        all_pairs.update(dex_prices.keys())
    
    for pair in all_pairs:
        prices = {dex: all_prices[dex][pair] for dex in all_prices if pair in all_prices[dex]}
        if len(prices) < 2:
            print(f"[SKIP] {pair}: not enough DEXes ({list(prices.keys())})")
            continue
        
        # Validate that we're comparing the same tokens
        is_valid, reason = validate_token_match(pair, all_prices)
        if not is_valid:
            print(f"[SKIP] {pair}: {reason}")
            continue
        
        # Extract prices for this pair
        pair_prices = {}
        for dex_name, dex_prices in all_prices.items():
            if pair in dex_prices:
                price = dex_prices[pair]['price']
                pair_prices[dex_name] = price
        
        if len(pair_prices) >= 2:
            prices_list = list(pair_prices.values())
            min_price = min(prices_list)
            max_price = max(prices_list)
            
            # Calculate profit percentage correctly
            profit_pct = ((max_price - min_price) / min_price) * 100 if min_price > 0 else 0
            
            # DEBUG: Log problematic pairs
            if profit_pct > 100:  # Unrealistic profit
                print(f"[DEBUG] {pair}: min={min_price:.8f}, max={max_price:.8f}, profit={profit_pct:.2f}%")
                print(f"[DEBUG] {pair} prices by DEX: {pair_prices}")
            
            print(f"[PAIR] {pair}: min={min_price}, max={max_price}, profit={profit_pct:.2f}%")
            
            # Find which DEX has the minimum and maximum prices
            min_dex = min(pair_prices.keys(), key=lambda k: pair_prices[k])
            max_dex = max(pair_prices.keys(), key=lambda k: pair_prices[k])
            
            # For arbitrage: buy at lower price, sell at higher price
            buy_dex = min_dex
            sell_dex = max_dex
            buy_price = min_price
            sell_price = max_price
            
            # Skip if no price difference
            if buy_price >= sell_price:
                continue
            
            # Get token addresses and fee tiers if available
            buy_info = all_prices[buy_dex][pair]
            sell_info = all_prices[sell_dex][pair]
            token0 = buy_info.get('token0')
            token1 = buy_info.get('token1')
            fee_tier_buy = buy_info.get('fee_tier')
            fee_tier_sell = sell_info.get('fee_tier')
            tvl = min(buy_info.get('tvl', 0), sell_info.get('tvl', 0))
            
            # Estimate profit
            profit_analysis = estimate_profit(buy_price, sell_price)
            
            opportunity = {
                'pair': pair,
                'buy_dex': buy_dex,
                'sell_dex': sell_dex,
                'buy_price': buy_price,
                'sell_price': sell_price,
                'profit_pct': profit_pct,
                'profit_analysis': profit_analysis,
                'token0_address': token0,
                'token1_address': token1,
                'uniswap_fee_tier': fee_tier_buy if buy_dex == 'Uniswap' else fee_tier_sell if sell_dex == 'Uniswap' else None,
                'aerodrome_fee_tier': fee_tier_buy if buy_dex == 'Aerodrome' else fee_tier_sell if sell_dex == 'Aerodrome' else None,
                'uniswap_pool_address': buy_info.get('pool_id') if buy_dex == 'Uniswap' else sell_info.get('pool_id') if sell_dex == 'Uniswap' else None,
                'aerodrome_pool_address': buy_info.get('pool_id') if buy_dex == 'Aerodrome' else sell_info.get('pool_id') if sell_dex == 'Aerodrome' else None,
            }
            
            # Use executor.validate_opportunity for filtering if provided
            if executor is not None:
                is_valid, reason = executor.validate_opportunity(opportunity)
                if is_valid:
                    opportunities.append(opportunity)
                else:
                    print(f"[FILTERED] {pair} ({buy_dex}->{sell_dex}): {reason}")
            else:
                if profit_analysis['net_profit_usd'] > 0 and tvl > MIN_LIQUIDITY_USD:
                    opportunities.append(opportunity)
    
    return opportunities

def estimate_profit(buy_price, sell_price, eth_amount=None, eth_price_usd=2500, gas_cost_usd=None):
    """
    Estimate realistic arbitrage profit accounting for all costs.
    buy_price and sell_price are in terms of token1/token0 (e.g., USDC/WETH).
    For arbitrage: buy at lower price, sell at higher price.
    All profit/costs are in USD.
    """
    if eth_amount is None:
        eth_amount = POSITION_SIZE_USD / eth_price_usd  # Convert USD to ETH amount
    
    # For arbitrage, we want to:
    # 1. Buy token1 at the lower price (buy_price)
    # 2. Sell token1 at the higher price (sell_price)
    # This means we're converting token0 -> token1 -> token0
    
    # Start with token0 (e.g., WETH)
    amount_token0_in = eth_amount  # e.g., 0.4 WETH
    
    # Buy token1 at buy_price (lower price)
    amount_token1_out = amount_token0_in * buy_price  # e.g., 0.4 * 0.000337 = 0.000135 USDC
    
    # Sell token1 at sell_price (higher price)
    amount_token0_out = amount_token1_out / sell_price  # e.g., 0.000135 / 0.000339 = 0.398 WETH
    
    # Calculate gross profit in token0 terms
    gross_profit_token0 = amount_token0_out - amount_token0_in
    gross_profit_usd = gross_profit_token0 * eth_price_usd
    
    # Calculate costs dynamically based on position size
    if gas_cost_usd is None:
        # Base gas price for Base network (very low)
        gas_price_eth = BASE_GAS_PRICE_GWEI / 1e9
        
        # Dynamic gas limits based on position size
        # Smaller positions = lower gas limits, larger positions = higher gas limits
        position_size_eth = POSITION_SIZE_USD / eth_price_usd
        
        # Scale gas limits based on position size (logarithmic scaling)
        if position_size_eth < 0.01:  # Very small positions
            gas_limit_swap = 100000
            gas_limit_approve = 20000
        elif position_size_eth < 0.1:  # Small positions
            gas_limit_swap = 150000
            gas_limit_approve = 30000
        elif position_size_eth < 1.0:  # Medium positions
            gas_limit_swap = 200000
            gas_limit_approve = 40000
        else:  # Large positions
            gas_limit_swap = 250000
            gas_limit_approve = 50000
        
        # Calculate total gas cost (2 swaps + 2 approvals)
        total_gas_eth = (gas_limit_swap * 2 + gas_limit_approve * 2) * gas_price_eth
        gas_cost_usd = total_gas_eth * eth_price_usd
    
    # Scale other costs based on position size
    transaction_fees_usd = POSITION_SIZE_USD * TRANSACTION_FEE_PCT * 2
    slippage_cost_usd = POSITION_SIZE_USD * SLIPPAGE_PCT * 2
    mev_protection_cost_usd = MEV_PROTECTION_COST_USD  # Fixed cost
    
    total_costs_usd = gas_cost_usd + transaction_fees_usd + slippage_cost_usd + mev_protection_cost_usd
    
    net_profit_usd = gross_profit_usd - total_costs_usd
    net_profit_pct = (net_profit_usd / POSITION_SIZE_USD) * 100 if POSITION_SIZE_USD else 0
    
    return {
        'gross_profit_usd': gross_profit_usd,
        'gas_cost_usd': gas_cost_usd,
        'transaction_fees_usd': transaction_fees_usd,
        'slippage_cost_usd': slippage_cost_usd,
        'mev_protection_cost_usd': mev_protection_cost_usd,
        'total_costs_usd': total_costs_usd,
        'net_profit_usd': net_profit_usd,
        'net_profit_pct': net_profit_pct,
        'is_profitable': net_profit_usd > MIN_PROFIT_THRESHOLD_USD
    }

if __name__ == "__main__":
    # Check if continuous mode is enabled
    CONTINUOUS_MODE = os.getenv("CONTINUOUS_MODE", "true").lower() == "true"
    
    if CONTINUOUS_MODE:
        asyncio.run(monitor_continuously())
    else:
        asyncio.run(monitor())
