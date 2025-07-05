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

async def get_uniswap_prices():
    """Get all Uniswap v3 pool prices"""
    if not UNISWAP_V3_SUBGRAPH:
        print("UNISWAP_V3_SUBGRAPH not configured")
        return {}
    
    query = {
        "query": """
        {
          pools(first: 1000) {
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
                
                # Debug: Print the response to see what we're getting
                print(f"Uniswap subgraph response status: {resp.status}")
                if resp.status != 200:
                    print(f"Uniswap subgraph error: {result}")
                    return {}
                
                if result is None:
                    print("Uniswap subgraph returned None")
                    return {}
                
                # Debug: Print the actual response structure
                print(f"Uniswap response keys: {result.keys() if result else 'None'}")
                if 'data' in result:
                    print(f"Uniswap data keys: {result['data'].keys() if result['data'] else 'None'}")
                if 'errors' in result:
                    print(f"Uniswap errors: {result['errors']}")
                    # Continue processing even if there are some indexer errors
                    if 'data' not in result:
                        print("No data available due to subgraph errors")
                        return {}
                
                pools = result.get("data", {}).get("pools", [])
                print(f"Found {len(pools)} Uniswap pools")
                
                # If we got data successfully, try to get more pools with offset
                if pools and len(pools) == 1000:
                    print("Attempting to get more pools with offset...")
                    try:
                        offset_query = {
                            "query": """
                            {
                              pools(first: 1000, skip: 1000) {
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
                    if i % 1000 == 0:  # Progress indicator every 1000 pools
                        print(f"Processing Uniswap pool {i}/{len(pools)}...")
                    
                    try:
                        tokens = pool["token0"], pool["token1"]
                        price = float(pool.get('token0Price', 0))
                        tvl = float(pool.get("totalValueLockedUSD", 0))
                        
                        if price > 0 and tvl > 1000:  # Only pools with >$1k TVL
                            pair_key = f"{tokens[0]['symbol']}/{tokens[1]['symbol']}"
                            prices[pair_key] = {
                                'price': price,
                                'tvl': tvl,
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
    """Get all SushiSwap pool prices"""
    if not SUSHI_FACTORY_ADDRESS:
        print("SUSHI_FACTORY_ADDRESS not configured")
        return {}
    
    factory = w3.eth.contract(address=Web3.to_checksum_address(SUSHI_FACTORY_ADDRESS), abi=SUSHI_FACTORY_ABI)
    prices = {}
    
    try:
        # Test if factory is accessible
        total_pairs = factory.functions.allPairsLength().call()
        print(f"Scanning {min(200, total_pairs)} SushiSwap pairs...")
        
        for i in range(min(200, total_pairs)):  # Limit to first 200 pairs
            if i % 50 == 0:  # Progress indicator every 50 pairs
                print(f"Processing SushiSwap pair {i}/{min(200, total_pairs)}...")
            
            try:
                pair_addr = factory.functions.allPairs(i).call()
                pair = w3.eth.contract(address=pair_addr, abi=PAIR_ABI)
                
                reserves = pair.functions.getReserves().call()
                token0 = pair.functions.token0().call()
                token1 = pair.functions.token1().call()
                
                if reserves[0] > 0 and reserves[1] > 0:
                    # Get token symbols and decimals
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
                            decimals.append(18)  # Default to 18 decimals
                    
                    # Calculate price with normalized reserves
                    reserve0_normalized = reserves[0] / (10 ** decimals[0])
                    reserve1_normalized = reserves[1] / (10 ** decimals[1])
                    
                    # Calculate price with normalized reserves
                    # Always use token1/token0 for consistency
                    price = reserve1_normalized / reserve0_normalized if reserve0_normalized > 0 else 0
                    
                    # If price is too small, try the inverse
                    if price < 0.0001 and reserve1_normalized > 0:
                        price = reserve0_normalized / reserve1_normalized
                    
                    pair_key = f"{symbols[0]}/{symbols[1]}"
                    
                    if price > 0:
                        prices[pair_key] = {
                            'price': price,
                            'pair_address': pair_addr,
                            'token0': token0,
                            'token1': token1
                        }
                        
            except Exception as e:
                continue  # Skip problematic pairs
                
    except Exception as e:
        print(f"SushiSwap factory not accessible: {e}")
        print("This might mean the factory address is wrong for Base network")
        return {}
    
    return prices

async def get_aerodrome_prices():
    """Get all Aerodrome pool prices"""
    if not AERODROME_SUBGRAPH:
        print("AERODROME_SUBGRAPH not configured")
        return {}
    
    query = {
        "query": """
        {
          pools(first: 500) {
            id
            token0 { id symbol }
            token1 { id symbol }
            token0Price
            token1Price
            totalValueLockedUSD
          }
        }
        """
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(AERODROME_SUBGRAPH, json=query) as resp:
                result = await resp.json()
                
                # Debug: Print the response to see what we're getting
                print(f"Aerodrome subgraph response status: {resp.status}")
                if resp.status != 200:
                    print(f"Aerodrome subgraph error: {result}")
                    return {}
                
                if result is None:
                    print("Aerodrome subgraph returned None")
                    return {}
                
                # Debug: Print the actual response structure
                print(f"Aerodrome response keys: {result.keys() if result else 'None'}")
                if 'data' in result:
                    print(f"Aerodrome data keys: {result['data'].keys() if result['data'] else 'None'}")
                if 'errors' in result:
                    print(f"Aerodrome errors: {result['errors']}")
                
                pairs = result.get("data", {}).get("pools", [])
                print(f"Found {len(pairs)} Aerodrome pools")
                
                prices = {}
                processed_count = 0
                for i, pair in enumerate(pairs):
                    if i % 100 == 0:  # Progress indicator every 100 pools
                        print(f"Processing Aerodrome pool {i}/{len(pairs)}...")
                    
                    try:
                        t0 = pair["token0"]
                        t1 = pair["token1"]
                        pair_key = f"{t0['symbol']}/{t1['symbol']}"
                        
                        # Try to get real price data - use token1Price for consistency
                        price = 1.0  # Default placeholder
                        if 'token1Price' in pair and pair['token1Price']:
                            price = float(pair['token1Price'])
                        elif 'token0Price' in pair and pair['token0Price']:
                            price = float(pair['token0Price'])
                        
                        # Only add if price is reasonable
                        if 0.0001 < price < 1000000:
                            prices[pair_key] = {
                                'price': price,
                                'pool_id': pair['id'],
                                'token0': t0['id'],
                                'token1': t1['id']
                            }
                            processed_count += 1
                    except Exception as e:
                        print(f"Error processing Aerodrome pair: {e}")
                        continue
                
                print(f"Processed {processed_count} Aerodrome pools")
                return prices
                
    except Exception as e:
        print(f"Error fetching Aerodrome prices: {e}")
        return {}

def find_arbitrage_opportunities(uniswap_prices, sushiswap_prices, aerodrome_prices):
    """Find arbitrage opportunities across all DEXes"""
    opportunities = []
    
    # Combine all prices
    all_prices = {
        'Uniswap': uniswap_prices,
        'SushiSwap': sushiswap_prices,
        'Aerodrome': aerodrome_prices
    }
    
    # Debug: Show what we have
    print(f"Uniswap pairs: {list(uniswap_prices.keys())}")
    print(f"SushiSwap pairs: {list(sushiswap_prices.keys())[:5]}...")  # Show first 5
    print(f"Aerodrome pairs: {list(aerodrome_prices.keys())[:5]}...")  # Show first 5
    
    # Find common pairs across DEXes
    all_pairs = set()
    for dex_prices in all_prices.values():
        all_pairs.update(dex_prices.keys())
    
    print(f"Total unique pairs found: {len(all_pairs)}")
    
    # Check for common pairs
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
        
        if len(pair_prices) >= 2:  # Need at least 2 DEXes for arbitrage
            prices = list(pair_prices.values())
            min_price = min(prices)
            max_price = max(prices)
            
            if max_price > min_price and min_price > 0:  # Prevent division by zero
                # Find which DEX has min/max prices
                buy_dex = [k for k, v in pair_prices.items() if v == min_price][0]
                sell_dex = [k for k, v in pair_prices.items() if v == max_price][0]
                
                profit_pct = ((max_price - min_price) / min_price) * 100
                
                # Debug: Show the actual prices
                # print(f"DEBUG: {pair} - {buy_dex}: {min_price}, {sell_dex}: {max_price}, Profit: {profit_pct:.2f}%")
                
                if profit_pct > 0.1 and profit_pct < 1000:  # Only show realistic opportunities (0.1% to 1000%)
                    profit_analysis = estimate_profit(min_price, max_price, DEFAULT_ETH_AMOUNT)
                    
                    # Only add if actually profitable after costs
                    if profit_analysis['is_profitable']:
                        opportunities.append({
                            'pair': pair,
                            'buy_dex': buy_dex,
                            'sell_dex': sell_dex,
                            'buy_price': min_price,
                            'sell_price': max_price,
                            'profit_pct': profit_pct,
                            'profit_analysis': profit_analysis
                        })
    
    return sorted(opportunities, key=lambda x: x['profit_pct'], reverse=True)

def estimate_profit(buy_price, sell_price, eth_amount=DEFAULT_ETH_AMOUNT, eth_price_usd=2500):
    """
    Estimate realistic arbitrage profit accounting for all costs
    """
    # Calculate gross profit
    gross_profit_usd = (sell_price - buy_price) * eth_amount * eth_price_usd
    
    # Calculate costs
    
    # 1. Gas costs (Base network has very low gas)
    gas_price_eth = BASE_GAS_PRICE_GWEI / 1e9  # Convert gwei to ETH
    total_gas_eth = (GAS_LIMIT_SWAP * 2 + GAS_LIMIT_APPROVE * 2) * gas_price_eth  # 2 swaps + 2 approvals
    gas_cost_usd = total_gas_eth * eth_price_usd
    
    # 2. Transaction fees (0.3% per swap)
    transaction_fees_usd = (buy_price + sell_price) * eth_amount * eth_price_usd * TRANSACTION_FEE_PCT * 2  # 2 swaps
    
    # 3. Slippage costs (0.5% on each trade)
    slippage_cost_usd = (buy_price + sell_price) * eth_amount * eth_price_usd * SLIPPAGE_PCT * 2  # 2 trades
    
    # 4. MEV protection cost
    mev_protection_cost_usd = MEV_PROTECTION_COST_USD
    
    # 5. Total costs
    total_costs_usd = gas_cost_usd + transaction_fees_usd + slippage_cost_usd + mev_protection_cost_usd
    
    # 6. Net profit
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
    """Main monitoring loop that finds the best arbitrage opportunities"""
    while True:
        print("\n" + "="*60)
        print("🔍 Scanning for arbitrage opportunities...")
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
            
            for i, opp in enumerate(opportunities[:5]):  # Show top 5
                analysis = opp['profit_analysis']
                print(f"{i+1}. {opp['pair']}")
                print(f"   Buy on {opp['buy_dex']} @ {opp['buy_price']:.6f}")
                print(f"   Sell on {opp['sell_dex']} @ {opp['sell_price']:.6f}")
                print(f"   Gross Profit: ${analysis['gross_profit_usd']:.2f}")
                print(f"   Costs Breakdown:")
                print(f"     - Gas: ${analysis['gas_cost_usd']:.2f}")
                print(f"     - Transaction Fees: ${analysis['transaction_fees_usd']:.2f}")
                print(f"     - Slippage: ${analysis['slippage_cost_usd']:.2f}")
                print(f"     - MEV Protection: ${analysis['mev_protection_cost_usd']:.2f}")
                print(f"     - Total Costs: ${analysis['total_costs_usd']:.2f}")
                print(f"   Net Profit: ${analysis['net_profit_usd']:.2f}")
                print()
        else:
            print("❌ No profitable arbitrage opportunities found (after accounting for all costs)")
        
        print(f"⏰ Next scan in 30 seconds...")
        await asyncio.sleep(30)

if __name__ == "__main__":
    asyncio.run(monitor())
