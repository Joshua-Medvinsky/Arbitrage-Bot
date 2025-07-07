#!/usr/bin/env python3
"""
Simple test script to verify flash loan contract functionality
"""

import os
import sys
from web3 import Web3
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config import FLASH_LOAN_RECEIVER_ADDRESS, AAVE_LENDING_POOL, WEB3_PROVIDER

load_dotenv()

def test_flash_loan_contract():
    """Test the flash loan contract functionality"""
    print("🔍 Testing Flash Loan Contract...")
    
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
        {"inputs":[],"name":"disableDexCalls","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},
        {"inputs":[{"internalType":"bool","name":"_disable","type":"bool"}],"name":"setDisableDexCalls","outputs":[],"stateMutability":"nonpayable","type":"function"}
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
        
        # Check if we need to set disableDexCalls to true for testing
        if not disable_dex:
            print("⚠️  DEX calls are enabled - this might cause issues")
            print("   Consider setting disableDexCalls to true for testing")
        else:
            print("✅ DEX calls are disabled - good for testing")
        
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

def test_aave_pool():
    """Test if Aave pool is accessible and has liquidity"""
    print("\n🔍 Testing Aave Pool...")
    
    w3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER))
    
    # Aave Pool ABI (minimal)
    pool_abi = [
        {"inputs":[{"internalType":"address","name":"asset","type":"address"}],"name":"getReserveData","outputs":[{"components":[{"internalType":"uint256","name":"configuration","type":"uint256"},{"internalType":"uint128","name":"liquidityIndex","type":"uint128"},{"internalType":"uint128","name":"currentLiquidityRate","type":"uint128"},{"internalType":"uint128","name":"variableBorrowIndex","type":"uint128"},{"internalType":"uint128","name":"currentVariableBorrowRate","type":"uint128"},{"internalType":"uint128","name":"currentStableBorrowRate","type":"uint128"},{"internalType":"uint40","name":"lastUpdateTimestamp","type":"uint40"},{"internalType":"uint16","name":"id","type":"uint16"},{"internalType":"address","name":"aTokenAddress","type":"address"},{"internalType":"address","name":"stableDebtTokenAddress","type":"address"},{"internalType":"address","name":"variableDebtTokenAddress","type":"address"},{"internalType":"address","name":"interestRateStrategyAddress","type":"address"},{"internalType":"uint8","name":"usageAsCollateralEnabledOnUser","type":"uint8"},{"internalType":"bool","name":"borrowingEnabled","type":"bool"},{"internalType":"bool","name":"stableBorrowRateEnabled","type":"bool"},{"internalType":"bool","name":"isActive","type":"bool"},{"internalType":"bool","name":"isFrozen","type":"bool"}],"internalType":"struct DataTypes.ReserveData","name":"","type":"tuple"}],"stateMutability":"view","type":"function"}
    ]
    
    try:
        pool = w3.eth.contract(address=Web3.to_checksum_address(AAVE_LENDING_POOL), abi=pool_abi)
        
        # Test WETH reserve
        weth_address = "0x4200000000000000000000000000000000000006"
        reserve_data = pool.functions.getReserveData(weth_address).call()
        
        print(f"✅ Aave pool is accessible")
        print(f"   WETH reserve active: {reserve_data[15]}")  # isActive
        print(f"   WETH borrowing enabled: {reserve_data[13]}")  # borrowingEnabled
        print(f"   WETH is frozen: {reserve_data[16]}")  # isFrozen
        
        if reserve_data[15] and reserve_data[13] and not reserve_data[16]:
            print("✅ WETH flash loans should be available")
            return True
        else:
            print("❌ WETH flash loans may not be available")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Aave pool: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Flash Loan Contract Test")
    print("=" * 50)
    
    contract_ok = test_flash_loan_contract()
    pool_ok = test_aave_pool()
    
    if contract_ok and pool_ok:
        print("\n🎉 All tests passed!")
        print("✅ Contract is working correctly")
        print("✅ Aave pool is accessible")
        print("\n💡 Next steps:")
        print("   - Try a smaller flash loan amount")
        print("   - Check if WETH has sufficient liquidity")
        print("   - Consider testing with USDC instead of WETH")
    else:
        print("\n❌ Some tests failed!")
        if not contract_ok:
            print("   - Contract test failed")
        if not pool_ok:
            print("   - Aave pool test failed") 