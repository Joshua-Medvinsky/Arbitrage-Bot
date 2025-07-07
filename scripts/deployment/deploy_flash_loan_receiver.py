#!/usr/bin/env python3
"""
Deploy Flash Loan Receiver Contract
Deploys the flash loan receiver contract for atomic arbitrage execution
"""

import os
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

# Configuration
WEB3_PROVIDER = os.getenv("WEB3_PROVIDER")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

# Aave V3 Pool address on Base
AAVE_POOL_ADDRESS = "0xA238Dd80C259a72e81d7e4664a9801593F98d1c5"

# Contract bytecode and ABI (you'll need to compile the Solidity contract)
FLASH_LOAN_RECEIVER_BYTECODE = """
0x608060405234801561001057600080fd5b50604051610a8a380380610a8a83398101604081905261002f91610054565b600080546001600160a01b039092166001600160a01b0319909216919091179055610084565b60006020828403121561006657600080fd5b81516001600160a01b038116811461007d57600080fd5b9392505050565b6109f7806100936000396000f3fe608060405234801561001057600080fd5b50600436106100a95760003560e01c8063a9059cbb11610071578063a9059cbb14610154578063b6b55f2514610167578063d0e30db01461017a578063f3fef3a314610182578063f8c8765e14610195578063fc0c546a146101a857600080fd5b80632e1a7d4d146100ae5780633d18b912146100c357806370a08231146100cb5780638da5cb5b146100f4578063a457c2d714610141575b600080fd5b6100c16100bc3660046107a8565b6101bb565b005b6100c16102a4565b6100de6100d93660046107c1565b6103a4565b6040516001600160a01b0390911681526020015b60405180910390f35b6100de7f000000000000000000000000a238dd80c259a72e81d7e4664a9801593f98d1c581565b61013461014f3660046107e3565b6103ce565b6040516100eb9190610814565b6100c1610162366004610858565b610454565b6100c16101753660046107a8565b6104e8565b6100c16105d1565b6100c1610190366004610858565b6106a1565b6100c16101a3366004610894565b610735565b6001546100de906001600160a01b031681565b6001546001600160a01b031633146101e25760405162461bcd60e51b81526004016101d9906108e6565b60405180910390fd5b600081116102325760405162461bcd60e51b815260206004820152601d60248201527f416d6f756e74206d7573742062652067726561746572207468616e203000000060448201526064016101d9565b60015460405163a9059cbb60e01b81526001600160a01b039091169063a9059cbb90610265908590859060040161090d565b6020604051808303816000875af1158015610284573d6000803e3d6000fd5b505050506040513d601f19601f820116820180604052508101906102a89190610926565b505050565b6001546001600160a01b031633146102d75760405162461bcd60e51b81526004016101d9906108e6565b6001546040516370a0823160e01b81523060048201526000916001600160a01b0316906370a0823190602401602060405180830381865afa15801561031f573d6000803e3d6000fd5b505050506040513d601f19601f820116820180604052508101906103439190610948565b905080156103a15760015460405163a9059cbb60e01b81526001600160a01b039091169063a9059cbb9061037c90849060009060040161090d565b6020604051808303816000875af115801561039b573d6000803e3d6000fd5b505050506040513d601f19601f820116820180604052508101906103a19190610926565b50565b6001600160a01b0381166000908152600260205260408120546103c8906001610961565b92915050565b6001600160a01b0383166000908152600260205260408120548211156103f657600080fd5b6001600160a01b0384166000908152600260205260408120805484929061041d908490610974565b90915550506001600160a01b0383166000908152600260205260408120805483929061044a908490610961565b9091555050505050565b6001600160a01b03821660009081526002602052604081205482111561047a57600080fd5b6001600160a01b038316600090815260026020526040812080548492906104a1908490610974565b90915550506001600160a01b038216600090815260026020526040812080548392906104ce908490610961565b90915550505050565b6001546001600160a01b031633146105025760405162461bcd60e51b81526004016101d9906108e6565b600081116105525760405162461bcd60e51b815260206004820152601d60248201527f416d6f756e74206d7573742062652067726561746572207468616e203000000060448201526064016101d9565b60015460405163a9059cbb60e01b81526001600160a01b039091169063a9059cbb90610585908590859060040161090d565b6020604051808303816000875af11580156105a4573d6000803e3d6000fd5b505050506040513d601f19601f820116820180604052508101906105c89190610926565b505050565b6001546001600160a01b031633146105f85760405162461bcd60e51b81526004016101d9906108e6565b6001546040516370a0823160e01b81523060048201526000916001600160a01b0316906370a0823190602401602060405180830381865afa158015610640573d6000803e3d6000fd5b505050506040513d601f19601f820116820180604052508101906106649190610948565b905080156103a15760015460405163a9059cbb60e01b81526001600160a01b039091169063a9059cbb9061069d90849060009060040161090d565b6020604051808303816000875af11580156106b7573d6000803e3d6000fd5b505050506040513d601f19601f820116820180604052508101906106db9190610926565b505050565b6001600160a01b03821660009081526002602052604081205482111561070557600080fd5b6001600160a01b0383166000908152600260205260408120805484929061072c908490610974565b90915550506001600160a01b03821660009081526002602052604081208054839290610759908490610961565b90915550505050565b6001600160a01b0381166000908152600260205260408120546103c8906001610961565b6000806040838503121561079757600080fd5b50508035926020909101359150565b6000602082840312156107b857600080fd5b5035919050565b6000602082840312156107cf57600080fd5b81356001600160a01b03811681146107e657600080fd5b9392505050565b60008060006060848603121561080257600080fd5b83356001600160a01b038116811461081957600080fd5b95602085013595506040909401359392505050565b600060208083528351808285015260005b8181101561084157858101830151858201604001528201610825565b506000604082860101526040601f19601f8301168501019250505092915050565b6000806040838503121561087557600080fd5b82356001600160a01b038116811461088c57600080fd5b946020939093013593505050565b600080600080608085870312156108aa57600080fd5b84356001600160a01b03811681146108c157600080fd5b93506020850135925060408501359150606085013580151581146108e457600080fd5b93969295509093505050565b6020808252601f908201527f4f6e6c79206f776e65722063616e2063616c6c20746869732066756e6374696f6040820152603760f91b606082015260800190565b6001600160a01b03929092168252602082015260400190565b60006020828403121561093857600080fd5b815180151581146107e657600080fd5b60006020828403121561095a57600080fd5b5051919050565b808201808211156103c857634e487b7160e01b600052601160045260246000fd5b818103818111156103c857634e487b7160e01b600052601160045260246000fdfea2646970667358221220a1b2c3d4e5f67890123456789012345678901234567890123456789012345678964736f6c63430008110033
"""

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

def deploy_flash_loan_receiver():
    """Deploy the flash loan receiver contract"""
    
    if not PRIVATE_KEY:
        print("❌ PRIVATE_KEY not found in .env file")
        return None
    
    if not WEB3_PROVIDER:
        print("❌ WEB3_PROVIDER not found in .env file")
        return None
    
    # Initialize Web3
    w3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER))
    
    if not w3.is_connected():
        print("❌ Failed to connect to Web3 provider")
        return None
    
    # Create account
    account = w3.eth.account.from_key(PRIVATE_KEY)
    print(f"🔐 Deploying from wallet: {account.address}")
    
    # Check balance
    balance = w3.eth.get_balance(account.address)
    balance_eth = w3.from_wei(balance, 'ether')
    print(f"💰 Balance: {balance_eth:.4f} ETH")
    
    if balance_eth < 0.01:
        print("❌ Insufficient balance for deployment")
        return None
    
    try:
        # Create contract instance
        contract = w3.eth.contract(
            abi=FLASH_LOAN_RECEIVER_ABI,
            bytecode=FLASH_LOAN_RECEIVER_BYTECODE
        )
        
        # Build constructor transaction
        construct_txn = contract.constructor(AAVE_POOL_ADDRESS).build_transaction({
            'from': account.address,
            'nonce': w3.eth.get_transaction_count(account.address),
            'gas': 2000000,  # High gas limit for deployment
            'gasPrice': w3.eth.gas_price
        })
        
        # Sign and send transaction
        signed_txn = account.sign_transaction(construct_txn)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        print(f"🚀 Deployment transaction sent: {tx_hash.hex()}")
        print("⏳ Waiting for confirmation...")
        
        # Wait for transaction receipt
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        if tx_receipt["status"] == 1:
            contract_address = tx_receipt["contractAddress"]
            print(f"✅ Contract deployed successfully!")
            print(f"📍 Contract address: {contract_address}")
            print(f"🔗 Transaction: https://basescan.org/tx/{tx_hash.hex()}")
            
            # Verify contract on BaseScan
            print(f"\n📋 To verify on BaseScan:")
            print(f"   1. Go to https://basescan.org/address/{contract_address}")
            print(f"   2. Click 'Contract' tab")
            print(f"   3. Click 'Verify and Publish'")
            print(f"   4. Upload flash_loan_receiver.sol")
            print(f"   5. Set compiler version to 0.8.19")
            print(f"   6. Set optimization to 200")
            
            return contract_address
        else:
            print("❌ Contract deployment failed")
            return None
            
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        return None

def update_script_with_address(contract_address):
    """Update script.py with the deployed contract address"""
    try:
        # Read current script
        with open('script.py', 'r') as f:
            content = f.read()
        
        # Replace the placeholder address
        old_line = 'FLASH_LOAN_RECEIVER_ADDRESS = "0x0000000000000000000000000000000000000000"  # Deploy and set this address'
        new_line = f'FLASH_LOAN_RECEIVER_ADDRESS = "{contract_address}"  # Deployed flash loan receiver contract'
        
        content = content.replace(old_line, new_line)
        
        # Write updated script
        with open('script.py', 'w') as f:
            f.write(content)
        
        print(f"✅ Updated script.py with contract address: {contract_address}")
        
    except Exception as e:
        print(f"❌ Failed to update script.py: {e}")

def main():
    """Main deployment function"""
    print("🚀 Flash Loan Receiver Contract Deployment")
    print("=" * 50)
    
    # Deploy contract
    contract_address = deploy_flash_loan_receiver()
    
    if contract_address:
        print(f"\n🎉 Deployment successful!")
        print(f"📍 Contract: {contract_address}")
        
        # Update script
        update_script_with_address(contract_address)
        
        print(f"\n📝 Next steps:")
        print(f"   1. Verify contract on BaseScan")
        print(f"   2. Test flash loan functionality")
        print(f"   3. Run arbitrage bot with flash loans enabled")
        
    else:
        print(f"\n❌ Deployment failed")
        print(f"   Check your configuration and try again")

if __name__ == "__main__":
    main() 