import asyncio
import os
import aiohttp
from web3 import Web3
from dotenv import load_dotenv
from config import PAIR_ABI, SUSHI_FACTORY_ABI, DEFAULT_ETH_AMOUNT, DEFAULT_GAS_ETH, DEFAULT_SLIPPAGE_PCT, USDC_ADDRESS, WETH_ADDRESS, ZORA_ADDRESS, SUSHI_FACTORY_ADDRESS

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
                
                pools = result.get("data", {}).get("pools", [])
                print(f"Found {len(pools)} Uniswap pools")
                
                prices = {}
                processed_count = 0
                for pool in pools:
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
        print(f"Scanning {min(100, total_pairs)} SushiSwap pairs...")
        
        for i in range(min(100, total_pairs)):  # Limit to first 100 pairs
            try:
                pair_addr = factory.functions.allPairs(i).call()
                pair = w3.eth.contract(address=pair_addr, abi=PAIR_ABI)
                
                reserves = pair.functions.getReserves().call()
                token0 = pair.functions.token0().call()
                token1 = pair.functions.token1().call()
                
                if reserves[0] > 0 and reserves[1] > 0:
                    # Get token symbols
                    symbols = []
                    for token in [token0, token1]:
                        try:
                            erc20 = w3.eth.contract(address=token, abi=[{"constant":True,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"type":"function"}])
                            symbol = erc20.functions.symbol().call()
                            symbols.append(symbol)
                        except Exception:
                            symbols.append("?")
                    
                    # Calculate price
                    price = reserves[1] / reserves[0] if reserves[0] > 0 else 0
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
          pools(first: 200) {
            id
            token0 { id symbol }
            token1 { id symbol }
            reserve0
            reserve1
            totalSupply
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
                for pair in pairs:
                    try:
                        reserve0 = float(pair.get("reserve0", 0))
                        reserve1 = float(pair.get("reserve1", 0))
                        
                        if reserve0 > 0 and reserve1 > 0:
                            price = reserve1 / reserve0
                            t0 = pair["token0"]
                            t1 = pair["token1"]
                            pair_key = f"{t0['symbol']}/{t1['symbol']}"
                            
                            prices[pair_key] = {
                                'price': price,
                                'pool_id': pair['id'],
                                'token0': t0['id'],
                                'token1': t1['id']
                            }
                    except Exception:
                        continue
                
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
    
    # Find common pairs across DEXes
    all_pairs = set()
    for dex_prices in all_prices.values():
        all_pairs.update(dex_prices.keys())
    
    for pair in all_pairs:
        pair_prices = {}
        for dex_name, dex_prices in all_prices.items():
            if pair in dex_prices:
                pair_prices[dex_name] = dex_prices[pair]['price']
        
        if len(pair_prices) >= 2:  # Need at least 2 DEXes for arbitrage
            prices = list(pair_prices.values())
            min_price = min(prices)
            max_price = max(prices)
            
            if max_price > min_price:
                # Find which DEX has min/max prices
                buy_dex = [k for k, v in pair_prices.items() if v == min_price][0]
                sell_dex = [k for k, v in pair_prices.items() if v == max_price][0]
                
                profit_pct = ((max_price - min_price) / min_price) * 100
                
                if profit_pct > 0.5:  # Only show opportunities >0.5%
                    opportunities.append({
                        'pair': pair,
                        'buy_dex': buy_dex,
                        'sell_dex': sell_dex,
                        'buy_price': min_price,
                        'sell_price': max_price,
                        'profit_pct': profit_pct,
                        'estimated_profit': estimate_profit(min_price, max_price, DEFAULT_ETH_AMOUNT)
                    })
    
    return sorted(opportunities, key=lambda x: x['profit_pct'], reverse=True)

def estimate_profit(buy_price, sell_price, eth_amount=DEFAULT_ETH_AMOUNT, gas_eth=DEFAULT_GAS_ETH, slippage_pct=DEFAULT_SLIPPAGE_PCT):
    gross_profit = (sell_price - buy_price) * eth_amount
    slippage_loss = slippage_pct * (buy_price + sell_price) / 2 * eth_amount
    gas_cost_usd = gas_eth * sell_price
    net_profit = gross_profit - slippage_loss - gas_cost_usd
    return net_profit

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
            print(f"\n🔥 Found {len(opportunities)} arbitrage opportunities:")
            print("-" * 60)
            
            for i, opp in enumerate(opportunities[:5]):  # Show top 5
                print(f"{i+1}. {opp['pair']}")
                print(f"   Buy on {opp['buy_dex']} @ {opp['buy_price']:.6f}")
                print(f"   Sell on {opp['sell_dex']} @ {opp['sell_price']:.6f}")
                print(f"   Profit: {opp['profit_pct']:.2f}% | Est. Net: ${opp['estimated_profit']:.2f}")
                print()
        else:
            print("❌ No profitable arbitrage opportunities found")
        
        print(f"⏰ Next scan in 30 seconds...")
        await asyncio.sleep(30)

if __name__ == "__main__":
    asyncio.run(monitor())
