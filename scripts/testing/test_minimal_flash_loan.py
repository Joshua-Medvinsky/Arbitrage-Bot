#!/usr/bin/env python3
"""
Minimal flash loan test to verify basic functionality
"""

import os
import sys
from web3 import Web3
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config import FLASH_LOAN_RECEIVER_ADDRESS, WEB3_PROVIDER

load_dotenv()

def test_minimal_flash_loan():
    """Test minimal flash loan functionality"""
    print("🔍 Testing Minimal Flash Loan...")
    
    # Connect to Base mainnet
    w3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER))
    
    if not w3.is_connected():
        print("❌ Failed to connect to Base mainnet")
        return False
    
    # Contract ABI
    contract_abi = [
        {"inputs":[{"internalType":"address","name":"asset","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"address","name":"tokenIn","type":"address"},{"internalType":"address","name":"tokenOut","type":"address"},{"internalType":"string","name":"buyDex","type":"string"},{"internalType":"string","name":"sellDex","type":"string"},{"internalType":"uint256","name":"buyAmount","type":"uint256"},{"internalType":"uint256","name":"sellAmount","type":"uint256"}],"name":"requestFlashLoan","outputs":[],"stateMutability":"nonpayable","type":"function"}
    ]
    
    # Create contract instance
    contract = w3.eth.contract(
        address=Web3.to_checksum_address(FLASH_LOAN_RECEIVER_ADDRESS),
        abi=contract_abi
    )
    
    try:
        # Get private key
        private_key = os.getenv("PRIVATE_KEY")
        if not private_key:
            print("❌ PRIVATE_KEY not found in environment")
            return False
        
        # Create account
        account = w3.eth.account.from_key(private_key)
        print(f"Using account: {account.address}")
        
        # Test parameters
        weth_address = "0x4200000000000000000000000000000000000006"
        usdc_address = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
        
        # Very small amount for testing (0.001 ETH)
        flash_loan_amount = 1000000000000000  # 0.001 ETH in wei
        
        print(f"Testing with minimal amount: {flash_loan_amount} wei (0.001 ETH)")
        
        # Build transaction
        flash_loan_function = contract.functions.requestFlashLoan(
            weth_address,      # asset to flash loan
            flash_loan_amount, # amount to borrow
            weth_address,      # tokenIn for arbitrage
            usdc_address,      # tokenOut for arbitrage
            "Uniswap",         # buyDex
            "Aerodrome",       # sellDex
            flash_loan_amount, # buyAmount
            flash_loan_amount  # sellAmount
        )
        
        nonce = w3.eth.get_transaction_count(account.address)
        gas_price = w3.eth.gas_price
        
        tx = flash_loan_function.build_transaction({
            'from': account.address,
            'gas': 1000000,  # Higher gas for flash loan
            'gasPrice': gas_price,
            'nonce': nonce
        })
        
        # Sign and send flash loan
        signed_tx = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        print(f"✅ Flash loan requested: {tx_hash.hex()}")
        
        # Wait for flash loan confirmation
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt["status"] == 1:
            print("✅ Flash loan executed successfully!")
            return True
        else:
            print("❌ Flash loan failed")
            print("   This might be because:")
            print("   - Insufficient liquidity in Aave pool")
            print("   - Flash loan not supported for this token")
            print("   - Arbitrage execution failed in contract")
            return False
            
    except Exception as e:
        print(f"❌ Flash loan test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_minimal_flash_loan()
    if success:
        print("\n🎉 Flash loan test successful!")
        print("✅ Basic flash loan functionality is working")
    else:
        print("\n❌ Flash loan test failed!")
        print("💡 This suggests the issue might be:")
        print("   - Aave pool liquidity")
        print("   - Token support")
        print("   - Contract logic") 