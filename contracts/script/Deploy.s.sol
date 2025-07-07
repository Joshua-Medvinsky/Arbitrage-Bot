// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "forge-std/Script.sol";
import "../src/FlashLoanReceiver.sol";

contract DeployScript is Script {
    // Aave V3 Pool address on Base
    address public constant AAVE_POOL_ADDRESS = 0xA238Dd80C259a72e81d7e4664a9801593F98d1c5;
    
    function run() external {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        
        vm.startBroadcast(deployerPrivateKey);
        
        // Deploy FlashLoanReceiver
        FlashLoanReceiver flashLoanReceiver = new FlashLoanReceiver(AAVE_POOL_ADDRESS);
        
        vm.stopBroadcast();
        
        console.log("FlashLoanReceiver deployed at:", address(flashLoanReceiver));
        console.log("Owner:", flashLoanReceiver.owner());
        console.log("Pool:", address(flashLoanReceiver.pool()));
        
        // Verify deployment
        require(flashLoanReceiver.owner() == vm.addr(deployerPrivateKey), "Owner mismatch");
        require(address(flashLoanReceiver.pool()) == AAVE_POOL_ADDRESS, "Pool mismatch");
        
        console.log("Deployment successful!");
        console.log("Next steps:");
        console.log("   1. Update script.py with contract address");
        console.log("   2. Test flash loan functionality");
        console.log("   3. Run arbitrage bot with flash loans enabled");
    }
} 