# Arbitrage-Bot

## Overview

Arbitrage-Bot is a Python-based tool designed to simulate arbitrage opportunities between two decentralized exchange (DEX) liquidity pools, such as Uniswap and SushiSwap. The bot fetches real-time price data from these pools and estimates potential arbitrage profits by comparing prices and accounting for slippage and gas costs.

## Features
- Fetches and compares token prices from multiple DEX liquidity pools (Uniswap, SushiSwap, Aerodrome)
- Estimates arbitrage profit opportunities based on real-time data
- Prints out arbitrage opportunities and simulated profits
- Modular code structure for easy extension

## Project Status
This bot is currently **in progress**. The current version focuses on simulation: it fetches prices, estimates profits, and prints out potential arbitrage trades. **No real trades are executed.**

## Roadmap
- [x] Simulate arbitrage opportunities between two or more DEX pools
- [x] Add a simulation mode (current default)
- [ ] Add a live mode to execute real trades on-chain (coming soon)
- [ ] Improve error handling and logging
- [ ] Add configuration options for tokens, pools, and strategies

## Usage
1. Clone the repository and install dependencies (see requirements.txt).
2. Set up your `.env` file with the required API keys and contract addresses.
3. Run the bot with Python:
   ```bash
   python script.py
   ```

## Disclaimer
This project is for educational and research purposes only. **Do not use with real funds unless you fully understand the risks.**

---

*Final version will allow you to choose between simulation mode and live mode for real trading.*