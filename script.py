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
                        if price > 0 and tvl > 10000 and volume > 1000:  # Higher thresholds for better opportunities
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
                    
                    if price > 0 and total_liquidity_usd > 10000:  # Only pairs with >$10k liquidity
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
                        if 0.0001 < price < 1000000 and tvl > 10000 and volume > 1000:
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
                
                # More aggressive thresholds for flash loan arbitrage
                if profit_pct > 0.05:  # Lower threshold to 0.05% for flash loans
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
    """Enhanced monitoring loop with MEV and flash loan capabilities"""
    while True:
        print("\n" + "="*60)
        print("🚀 Enhanced Arbitrage Bot - Scanning for MEV & Flash Loan Opportunities")
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
            print(f"\n🔥 Found {len(opportunities)} profitable arbitrage opportunities:")
            print("-" * 80)
            
            for i, opp in enumerate(opportunities[:10]):  # Show top 10
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
                print()
        else:
            print("❌ No profitable arbitrage opportunities found")
        
        print(f"⏰ Next scan in 15 seconds...")  # Faster scanning
        await asyncio.sleep(15)

if __name__ == "__main__":
    asyncio.run(monitor())
