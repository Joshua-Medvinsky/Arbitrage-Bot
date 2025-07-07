#!/usr/bin/env python3
"""
Script to set disableDexCalls to true for testing
"""

import os
import sys
from web3 import Web3
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config import FLASH_LOAN_RECEIVER_ADDRESS, WEB3_PROVIDER

load_dotenv()

def set_disable_dex_calls():
    """Set disableDexCalls to true for testing"""
    print("🔧 Setting disableDexCalls to true for testing...")
    
    # Connect to Base mainnet
    w3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER))
    
    if not w3.is_connected():
        print("❌ Failed to connect to Base mainnet")
        return False
    
    # Contract ABI
    contract_abi = [
        {"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},
        {"inputs":[],"name":"disableDexCalls","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},
        {"inputs":[{"internalType":"bool","name":"_disable","type":"bool"}],"name":"setDisableDexCalls","outputs":[],"stateMutability":"nonpayable","type":"function"}
    ]
    
    # Create contract instance
    contract = w3.eth.contract(
        address=Web3.to_checksum_address(FLASH_LOAN_RECEIVER_ADDRESS),
        abi=contract_abi
    )
    
    try:
        # Check current owner
        owner = contract.functions.owner().call()
        print(f"Contract owner: {owner}")
        
        # Check current setting
        current_setting = contract.functions.disableDexCalls().call()
        print(f"Current disableDexCalls setting: {current_setting}")
        
        # Always set to False, even if already False
        
        # Get private key
        private_key = os.getenv("PRIVATE_KEY")
        if not private_key:
            print("❌ PRIVATE_KEY not found in environment")
            return False
        
        # Create account
        account = w3.eth.account.from_key(private_key)
        print(f"Using account: {account.address}")
        
        # Check if we're the owner
        if account.address.lower() != owner.lower():
            print("❌ Only the contract owner can set disableDexCalls")
            return False
        
        # Build transaction
        set_function = contract.functions.setDisableDexCalls(False)
        
        nonce = w3.eth.get_transaction_count(account.address)
        gas_price = w3.eth.gas_price
        
        tx = set_function.build_transaction({
            'from': account.address,
            'gas': 100000,
            'gasPrice': gas_price,
            'nonce': nonce
        })
        
        # Sign and send transaction
        signed_tx = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        print(f"✅ Transaction sent: {tx_hash.hex()}")
        
        # Wait for confirmation
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt["status"] == 1:
            print("✅ disableDexCalls set to true successfully!")
            
            # Verify the change
            new_setting = contract.functions.disableDexCalls().call()
            print(f"New disableDexCalls setting: {new_setting}")
            
            if not new_setting:
                print("✅ disableDexCalls is now set to False (real DEX calls enabled)")
                return True
            else:
                print("❌ Failed to set disableDexCalls to False")
                return False
            
    except Exception as e:
        print(f"❌ Error setting disableDexCalls: {e}")
        return False

if __name__ == "__main__":
    success = set_disable_dex_calls()
    if success:
        print("\n🎉 disableDexCalls set successfully!")
        print("✅ Contract is now ready for testing")
    else:
        print("\n❌ Failed to set disableDexCalls")
        sys.exit(1) 