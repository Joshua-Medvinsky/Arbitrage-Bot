#!/usr/bin/env python3
"""
Test script to verify the deployed FlashLoanReceiver contract
"""

import os
import sys
from web3 import Web3
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config import FLASH_LOAN_RECEIVER_ADDRESS, AAVE_LENDING_POOL, WEB3_PROVIDER

load_dotenv()

def test_deployment():
    """Test the deployed contract"""
    print("🔍 Testing deployed FlashLoanReceiver contract...")
    
    # Connect to Base mainnet
    w3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER))
    
    if not w3.is_connected():
        print("❌ Failed to connect to Base mainnet")
        return False
    
    print(f"✅ Connected to Base mainnet")
    print(f"📊 Current block: {w3.eth.block_number}")
    
    # Contract ABI (minimal for testing)
    contract_abi = [
        {"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},
        {"inputs":[],"name":"pool","outputs":[{"internalType":"contract IPool","name":"","type":"address"}],"stateMutability":"view","type":"function"},
        {"inputs":[],"name":"disableDexCalls","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"}
    ]
    
    # Create contract instance
    contract = w3.eth.contract(
        address=Web3.to_checksum_address(FLASH_LOAN_RECEIVER_ADDRESS),
        abi=contract_abi
    )
    
    try:
        # Test contract calls
        owner = contract.functions.owner().call()
        pool = contract.functions.pool().call()
        disable_dex = contract.functions.disableDexCalls().call()
        
        print(f"✅ Contract is accessible")
        print(f"   Owner: {owner}")
        print(f"   Pool: {pool}")
        print(f"   Disable DEX calls: {disable_dex}")
        
        # Verify pool address
        if pool.lower() == AAVE_LENDING_POOL.lower():
            print(f"✅ Pool address matches Aave V3 pool")
        else:
            print(f"❌ Pool address mismatch")
            print(f"   Expected: {AAVE_LENDING_POOL}")
            print(f"   Got: {pool}")
            return False
        
        print(f"✅ Contract deployment verification successful!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing contract: {e}")
        return False

if __name__ == "__main__":
    success = test_deployment()
    if success:
        print("\n🎉 Deployment verification successful!")
        print(f"📋 Contract address: {FLASH_LOAN_RECEIVER_ADDRESS}")
        print(f"🔗 View on BaseScan: https://basescan.org/address/{FLASH_LOAN_RECEIVER_ADDRESS}")
    else:
        print("\n❌ Deployment verification failed!")
        sys.exit(1) 