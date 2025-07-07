#!/usr/bin/env python3
"""
Test Flash Loan Receiver Contract
Tests the deployed flash loan receiver contract functionality
"""

import os
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

# Configuration
WEB3_PROVIDER = os.getenv("WEB3_PROVIDER")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

# Contract addresses (update with your deployed contract)
FLASH_LOAN_RECEIVER_ADDRESS = "0x0000000000000000000000000000000000000000"  # Set your deployed address
AAVE_POOL_ADDRESS = "0xA238Dd80C259a72e81d7e4664a9801593F98d1c5"

# Token addresses on Base
WETH_BASE = "0x4200000000000000000000000000000000000006"
USDC_BASE = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"

# Flash loan receiver contract ABI
FLASH_LOAN_RECEIVER_ABI = [
    {"inputs":[{"internalType":"address","name":"_pool","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},
    {"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"tokenIn","type":"address"},{"indexed":True,"internalType":"address","name":"tokenOut","type":"address"},{"indexed":False,"internalType":"uint256","name":"amountIn","type":"uint256"},{"indexed":False,"internalType":"uint256","name":"amountOut","type":"uint256"},{"indexed":False,"internalType":"string","name":"dex","type":"string"}],"name":"ArbitrageExecuted","type":"event"},
    {"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"asset","type":"address"},{"indexed":False,"internalType":"uint256","name":"amount","type":"uint256"},{"indexed":False,"internalType":"uint256","name":"premium","type":"uint256"},{"indexed":True,"internalType":"address","name":"initiator","type":"address"}],"name":"FlashLoanExecuted","type":"event"},
    {"inputs":[{"internalType":"address[]","name":"assets","type":"address[]"},{"internalType":"uint256[]","name":"amounts","type":"uint256[]"},{"internalType":"uint256[]","name":"premiums","type":"uint256[]"},{"internalType":"address","name":"initiator","type":"address"},{"internalType":"bytes","name":"params","type":"bytes"}],"name":"executeOperation","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},
    {"inputs":[],"name":"pool","outputs":[{"internalType":"contract IPool","name":"","type":"address"}],"stateMutability":"view","type":"function"},
    {"inputs":[{"internalType":"address","name":"asset","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"address","name":"tokenIn","type":"address"},{"internalType":"address","name":"tokenOut","type":"address"},{"internalType":"string","name":"buyDex","type":"string"},{"internalType":"string","name":"sellDex","type":"string"},{"internalType":"uint256","name":"buyAmount","type":"uint256"},{"internalType":"uint256","name":"sellAmount","type":"uint256"}],"name":"requestFlashLoan","outputs":[],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[],"name":"withdrawETH","outputs":[],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"withdrawToken","outputs":[],"stateMutability":"nonpayable","type":"function"}
]

def test_contract_deployment():
    """Test if the contract is deployed and accessible"""
    
    if not PRIVATE_KEY:
        print("❌ PRIVATE_KEY not found in .env file")
        return False
    
    if not WEB3_PROVIDER:
        print("❌ WEB3_PROVIDER not found in .env file")
        return False
    
    if FLASH_LOAN_RECEIVER_ADDRESS == "0x0000000000000000000000000000000000000000":
        print("❌ FLASH_LOAN_RECEIVER_ADDRESS not set")
        print("   Deploy the contract first using deploy_flash_loan_receiver.py")
        return False
    
    # Initialize Web3
    w3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER))
    
    if not w3.is_connected():
        print("❌ Failed to connect to Web3 provider")
        return False
    
    # Create account
    account = w3.eth.account.from_key(PRIVATE_KEY)
    print(f"🔐 Testing from wallet: {account.address}")
    
    try:
        # Create contract instance
        contract = w3.eth.contract(
            address=Web3.to_checksum_address(FLASH_LOAN_RECEIVER_ADDRESS),
            abi=FLASH_LOAN_RECEIVER_ABI
        )
        
        # Test contract calls
        print(f"📍 Contract address: {FLASH_LOAN_RECEIVER_ADDRESS}")
        
        # Test owner function
        try:
            owner = contract.functions.owner().call()
            print(f"👤 Contract owner: {owner}")
            
            if owner.lower() != account.address.lower():
                print("⚠️  Warning: You are not the contract owner")
                print("   Only the owner can call flash loan functions")
        except Exception as e:
            print(f"❌ Could not get owner: {e}")
            return False
        
        # Test pool function
        try:
            pool_address = contract.functions.pool().call()
            print(f"🏊 Pool address: {pool_address}")
            
            if pool_address.lower() != AAVE_POOL_ADDRESS.lower():
                print("⚠️  Warning: Pool address mismatch")
                print(f"   Expected: {AAVE_POOL_ADDRESS}")
                print(f"   Got: {pool_address}")
        except Exception as e:
            print(f"❌ Could not get pool: {e}")
            return False
        
        print("✅ Contract deployment test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Contract test failed: {e}")
        return False

def test_flash_loan_request():
    """Test flash loan request (simulation)"""
    
    if not PRIVATE_KEY:
        print("❌ PRIVATE_KEY not found in .env file")
        return False
    
    if not WEB3_PROVIDER:
        print("❌ WEB3_PROVIDER not found in .env file")
        return False
    
    if FLASH_LOAN_RECEIVER_ADDRESS == "0x0000000000000000000000000000000000000000":
        print("❌ FLASH_LOAN_RECEIVER_ADDRESS not set")
        return False
    
    # Initialize Web3
    w3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER))
    
    if not w3.is_connected():
        print("❌ Failed to connect to Web3 provider")
        return False
    
    # Create account
    account = w3.eth.account.from_key(PRIVATE_KEY)
    print(f"🔐 Testing flash loan from wallet: {account.address}")
    
    try:
        # Create contract instance
        contract = w3.eth.contract(
            address=Web3.to_checksum_address(FLASH_LOAN_RECEIVER_ADDRESS),
            abi=FLASH_LOAN_RECEIVER_ABI
        )
        
        # Test parameters
        flash_loan_token = WETH_BASE
        flash_loan_amount = int(0.1 * 1e18)  # 0.1 WETH
        token_in = WETH_BASE
        token_out = USDC_BASE
        buy_dex = "Uniswap"
        sell_dex = "SushiSwap"
        buy_amount = int(0.1 * 1e18)
        sell_amount = int(0.09 * 1e18)
        
        print(f"🧪 Testing flash loan request:")
        print(f"   Asset: {flash_loan_token}")
        print(f"   Amount: {flash_loan_amount} wei")
        print(f"   Token In: {token_in}")
        print(f"   Token Out: {token_out}")
        print(f"   Buy DEX: {buy_dex}")
        print(f"   Sell DEX: {sell_dex}")
        print(f"   Buy Amount: {buy_amount} wei")
        print(f"   Sell Amount: {sell_amount} wei")
        
        # Build transaction (simulation)
        flash_loan_function = contract.functions.requestFlashLoan(
            flash_loan_token,
            flash_loan_amount,
            token_in,
            token_out,
            buy_dex,
            sell_dex,
            buy_amount,
            sell_amount
        )
        
        # Estimate gas
        try:
            gas_estimate = flash_loan_function.estimate_gas({'from': account.address})
            print(f"⛽ Estimated gas: {gas_estimate}")
            
            if gas_estimate > 2000000:
                print("⚠️  High gas estimate - transaction may be expensive")
            
        except Exception as e:
            print(f"❌ Gas estimation failed: {e}")
            print("   This might indicate the contract is not properly deployed")
            return False
        
        print("✅ Flash loan request test passed!")
        print("   Contract is ready for flash loan execution")
        return True
        
    except Exception as e:
        print(f"❌ Flash loan test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Flash Loan Receiver Contract Test")
    print("=" * 40)
    
    # Test 1: Contract deployment
    print("\n1️⃣ Testing contract deployment...")
    deployment_ok = test_contract_deployment()
    
    if not deployment_ok:
        print("\n❌ Contract deployment test failed")
        print("   Deploy the contract first using deploy_flash_loan_receiver.py")
        return
    
    # Test 2: Flash loan request
    print("\n2️⃣ Testing flash loan request...")
    flash_loan_ok = test_flash_loan_request()
    
    if not flash_loan_ok:
        print("\n❌ Flash loan test failed")
        print("   Check contract deployment and configuration")
        return
    
    print("\n🎉 All tests passed!")
    print("✅ Contract is ready for flash loan arbitrage")
    print("\n📝 Next steps:")
    print("   1. Run the arbitrage bot with flash loans enabled")
    print("   2. Monitor for arbitrage opportunities")
    print("   3. Execute flash loan arbitrage when profitable")

if __name__ == "__main__":
    main() 