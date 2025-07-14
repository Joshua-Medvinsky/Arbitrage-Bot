# DEX Configuration Guide

## Overview

The arbitrage bot now supports toggling individual DEXes on/off for better performance optimization. This is especially useful when certain DEXes are slow or you want to focus on specific trading pairs.

## DEX Toggle Settings

Add these environment variables to your `.env` file:

```env
# DEX Toggle Configuration
ENABLE_UNISWAP_V3=true
ENABLE_SUSHISWAP=true
ENABLE_AERODROME=true
ENABLE_BALANCER_V2=false
```

## Performance Limits

Control how many pools each DEX processes:

```env
# DEX Performance Settings
UNISWAP_MAX_POOLS=1000
SUSHISWAP_MAX_PAIRS=100
AERODROME_MAX_POOLS=500
BALANCER_MAX_POOLS=50
```

## Recommended Configurations

### Fast Mode (Recommended)
```env
ENABLE_UNISWAP_V3=true
ENABLE_SUSHISWAP=true
ENABLE_AERODROME=true
ENABLE_BALANCER_V2=false

UNISWAP_MAX_POOLS=500
SUSHISWAP_MAX_PAIRS=50
AERODROME_MAX_POOLS=200
BALANCER_MAX_POOLS=0
```

### Comprehensive Mode
```env
ENABLE_UNISWAP_V3=true
ENABLE_SUSHISWAP=true
ENABLE_AERODROME=true
ENABLE_BALANCER_V2=true

UNISWAP_MAX_POOLS=1000
SUSHISWAP_MAX_PAIRS=100
AERODROME_MAX_POOLS=500
BALANCER_MAX_POOLS=25
```

### Minimal Mode (Fastest)
```env
ENABLE_UNISWAP_V3=true
ENABLE_SUSHISWAP=true
ENABLE_AERODROME=false
ENABLE_BALANCER_V2=false

UNISWAP_MAX_POOLS=200
SUSHISWAP_MAX_PAIRS=25
AERODROME_MAX_POOLS=0
BALANCER_MAX_POOLS=0
```

## Performance Impact

### Balancer V2 Issues
- **Very slow**: Takes 10-30 seconds per cycle
- **Limited pools**: Only ~50 pools on Base
- **Complex queries**: Requires multiple API calls per pool
- **Recommendation**: Disable by default (`ENABLE_BALANCER_V2=false`)

### Fast DEXes
- **Uniswap V3**: Fast, reliable, many pools
- **SushiSwap**: Fast, good liquidity
- **Aerodrome**: Fast, Base-native

## Usage Examples

### Disable Balancer (Recommended)
```bash
# Add to .env file
ENABLE_BALANCER_V2=false
```

### Enable Only Fast DEXes
```bash
# Add to .env file
ENABLE_UNISWAP_V3=true
ENABLE_SUSHISWAP=true
ENABLE_AERODROME=true
ENABLE_BALANCER_V2=false
```

### Minimal Configuration
```bash
# Add to .env file
ENABLE_UNISWAP_V3=true
ENABLE_SUSHISWAP=true
ENABLE_AERODROME=false
ENABLE_BALANCER_V2=false
```

## Monitoring Output

The bot will now show which DEXes are enabled:

```
🚀 Starting continuous arbitrage monitoring...
📊 Enabled DEXes: Uniswap V3, SushiSwap, Aerodrome
⚡ Performance Limits: Uniswap(500), SushiSwap(50), Aerodrome(200), Balancer(0)
```

## Troubleshooting

### No Opportunities Found
- Check that at least 2 DEXes are enabled
- Verify API endpoints are accessible
- Reduce performance limits if needed

### Slow Performance
- Disable Balancer V2: `ENABLE_BALANCER_V2=false`
- Reduce pool limits: `UNISWAP_MAX_POOLS=200`
- Enable only fast DEXes

### API Errors
- Check subgraph URLs are correct
- Verify API keys if required
- Disable problematic DEXes temporarily

## Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `ENABLE_UNISWAP_V3` | `true` | Enable Uniswap V3 monitoring |
| `ENABLE_SUSHISWAP` | `true` | Enable SushiSwap monitoring |
| `ENABLE_AERODROME` | `true` | Enable Aerodrome monitoring |
| `ENABLE_BALANCER_V2` | `false` | Enable Balancer V2 monitoring |
| `UNISWAP_MAX_POOLS` | `1000` | Max pools to process for Uniswap |
| `SUSHISWAP_MAX_PAIRS` | `100` | Max pairs to process for SushiSwap |
| `AERODROME_MAX_POOLS` | `500` | Max pools to process for Aerodrome |
| `BALANCER_MAX_POOLS` | `50` | Max pools to process for Balancer |

## Quick Start

1. **Copy configuration**:
```bash
cp .env.example .env
```

2. **Edit settings**:
```bash
# Disable Balancer for better performance
echo "ENABLE_BALANCER_V2=false" >> .env
```

3. **Run the bot**:
```bash
python scripts/monitoring/arbitrage_bot.py
```

The bot will automatically use only the enabled DEXes and respect the performance limits you've set. 