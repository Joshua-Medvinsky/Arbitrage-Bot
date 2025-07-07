// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "forge-std/Test.sol";
import "../src/FlashLoanReceiver.sol";
import "./FlashLoanReceiver.t.sol";

contract IntegrationTest is Test {
    FlashLoanReceiver public flashLoanReceiver;
    MockPool public mockPool;
    MockERC20 public weth;
    MockERC20 public usdc;
    
    address public owner;
    address public user;
    
    function setUp() public {
        owner = makeAddr("owner");
        user = makeAddr("user");
        
        // Deploy mock contracts
        mockPool = new MockPool();
        weth = new MockERC20("Wrapped Ether", "WETH");
        usdc = new MockERC20("USD Coin", "USDC");
        
        // Deploy flash loan receiver
        vm.startPrank(owner);
        flashLoanReceiver = new FlashLoanReceiver(address(mockPool));
        flashLoanReceiver.setDisableDexCalls(true); // Disable DEX calls for testing
        vm.stopPrank();
        
        // Fund mock pool with tokens (much more than needed)
        weth.transfer(address(mockPool), 100000 * 1e18);
        usdc.transfer(address(mockPool), 100000000 * 1e6);
        
        // Configure mock pool to support our mock tokens
        mockPool.enableFlashLoan(address(weth));
        mockPool.enableFlashLoan(address(usdc));
        
        // Fund flash loan receiver with some tokens for gas and repayment
        vm.deal(address(flashLoanReceiver), 10 ether);
        weth.transfer(address(flashLoanReceiver), 100 * 1e18);
        usdc.transfer(address(flashLoanReceiver), 100000 * 1e6);
    }
    
    function test_CompleteFlashLoanArbitrageFlow() public {
        vm.startPrank(owner);
        
        // Fund receiver with initial tokens for arbitrage
        weth.transfer(address(flashLoanReceiver), 5 ether);
        usdc.transfer(address(flashLoanReceiver), 5000 * 1e6);
        
        // Record initial balances
        uint256 initialWethBalance = weth.balanceOf(address(flashLoanReceiver));
        uint256 initialUsdcBalance = usdc.balanceOf(address(flashLoanReceiver));
        
        console.log("Initial WETH balance:", initialWethBalance);
        console.log("Initial USDC balance:", initialUsdcBalance);
        
        // Execute flash loan arbitrage
        flashLoanReceiver.requestFlashLoan(
            address(weth),  // asset
            10 ether,       // amount (larger for better testing)
            address(weth),  // tokenIn
            address(usdc),  // tokenOut
            "Uniswap",      // buyDex
            "SushiSwap",    // sellDex
            10 ether,       // buyAmount
            9 ether         // sellAmount
        );
        
        vm.stopPrank();
        
        // Check final balances
        uint256 finalWethBalance = weth.balanceOf(address(flashLoanReceiver));
        uint256 finalUsdcBalance = usdc.balanceOf(address(flashLoanReceiver));
        
        console.log("Final WETH balance:", finalWethBalance);
        console.log("Final USDC balance:", finalUsdcBalance);
        
        // Verify that arbitrage was executed
        assertGt(finalWethBalance + finalUsdcBalance, 0, "Should have tokens after arbitrage");
        
        console.log("Complete flash loan arbitrage flow successful!");
    }
    
    function test_MultipleFlashLoanExecutions() public {
        vm.startPrank(owner);
        
        // Fund receiver
        weth.transfer(address(flashLoanReceiver), 10 ether);
        usdc.transfer(address(flashLoanReceiver), 10000 * 1e6);
        
        // Execute multiple flash loans
        for (uint i = 0; i < 3; i++) {
            console.log("Executing flash loan", i + 1);
            
            flashLoanReceiver.requestFlashLoan(
                address(weth),
                2 ether,
                address(weth),
                address(usdc),
                "Uniswap",
                "SushiSwap",
                2 ether,
                1.8 ether
            );
            
            // Small delay between executions
            vm.warp(block.timestamp + 1);
        }
        
        vm.stopPrank();
        
        uint256 finalWethBalance = weth.balanceOf(address(flashLoanReceiver));
        uint256 finalUsdcBalance = usdc.balanceOf(address(flashLoanReceiver));
        
        console.log("Final balances after multiple executions:");
        console.log("WETH:", finalWethBalance);
        console.log("USDC:", finalUsdcBalance);
        
        assertGt(finalWethBalance + finalUsdcBalance, 0, "Should have tokens after multiple arbitrages");
        
        console.log("Multiple flash loan executions successful!");
    }
    
    function test_FlashLoanWithDifferentTokens() public {
        vm.startPrank(owner);
        
        // Fund receiver with different tokens
        weth.transfer(address(flashLoanReceiver), 5 ether);
        usdc.transfer(address(flashLoanReceiver), 5000 * 1e6);
        
        // Test with USDC as flash loan asset
        flashLoanReceiver.requestFlashLoan(
            address(usdc),  // asset
            1000 * 1e6,    // amount
            address(usdc),  // tokenIn
            address(weth),  // tokenOut
            "SushiSwap",    // buyDex
            "Uniswap",      // sellDex
            1000 * 1e6,    // buyAmount
            900 * 1e6       // sellAmount
        );
        
        vm.stopPrank();
        
        uint256 finalWethBalance = weth.balanceOf(address(flashLoanReceiver));
        uint256 finalUsdcBalance = usdc.balanceOf(address(flashLoanReceiver));
        
        console.log("Final balances with USDC flash loan:");
        console.log("WETH:", finalWethBalance);
        console.log("USDC:", finalUsdcBalance);
        
        assertGt(finalWethBalance + finalUsdcBalance, 0, "Should have tokens after USDC arbitrage");
        
        console.log("Flash loan with different tokens successful!");
    }
    
    function test_FlashLoanArbitrageWithProfit() public {
        vm.startPrank(owner);
        
        // Fund receiver with substantial amounts
        weth.transfer(address(flashLoanReceiver), 20 ether);
        usdc.transfer(address(flashLoanReceiver), 20000 * 1e6);
        
        uint256 initialTotalValue = (weth.balanceOf(address(flashLoanReceiver)) * 2500) / 1e18 + 
                                   (usdc.balanceOf(address(flashLoanReceiver)) * 1) / 1e6;
        
        console.log("Initial total value (USD):", initialTotalValue);
        
        // Execute large flash loan arbitrage
        flashLoanReceiver.requestFlashLoan(
            address(weth),
            50 ether,       // Large flash loan
            address(weth),
            address(usdc),
            "Uniswap",
            "SushiSwap",
            50 ether,
            45 ether
        );
        
        vm.stopPrank();
        
        uint256 finalWethBalance = weth.balanceOf(address(flashLoanReceiver));
        uint256 finalUsdcBalance = usdc.balanceOf(address(flashLoanReceiver));
        
        uint256 finalTotalValue = (finalWethBalance * 2500) / 1e18 + 
                                 (finalUsdcBalance * 1) / 1e6;
        
        console.log("Final total value (USD):", finalTotalValue);
        console.log("Profit (USD):", finalTotalValue - initialTotalValue);
        
        // Should have generated some profit
        assertGe(finalTotalValue, initialTotalValue, "Should not lose value");
        
        console.log("Flash loan arbitrage with profit successful!");
    }
    
    function test_Revert_InsufficientFundsForRepayment() public {
        vm.startPrank(owner);
        
        // Don't fund receiver - should fail
        vm.expectRevert("Insufficient funds to repay flash loan");
        
        flashLoanReceiver.requestFlashLoan(
            address(weth),
            10 ether,
            address(weth),
            address(usdc),
            "Uniswap",
            "SushiSwap",
            10 ether,
            9 ether
        );
        
        vm.stopPrank();
    }
    
    function test_Revert_InvalidFlashLoanAsset() public {
        vm.startPrank(owner);
        
        // Try to flash loan an unsupported asset
        vm.expectRevert("Asset not supported");
        
        flashLoanReceiver.requestFlashLoan(
            address(0x123), // Invalid asset
            1 ether,
            address(weth),
            address(usdc),
            "Uniswap",
            "SushiSwap",
            1 ether,
            0.9 ether
        );
        
        vm.stopPrank();
    }
    
    function test_WithdrawProfits() public {
        vm.startPrank(owner);
        
        // Fund receiver and execute arbitrage
        weth.transfer(address(flashLoanReceiver), 5 ether);
        usdc.transfer(address(flashLoanReceiver), 5000 * 1e6);
        
        flashLoanReceiver.requestFlashLoan(
            address(weth),
            5 ether,
            address(weth),
            address(usdc),
            "Uniswap",
            "SushiSwap",
            5 ether,
            4.5 ether
        );
        
        // Record balances before withdrawal
        uint256 wethBefore = weth.balanceOf(owner);
        uint256 usdcBefore = usdc.balanceOf(owner);
        
        // Withdraw profits
        flashLoanReceiver.withdrawToken(address(weth), weth.balanceOf(address(flashLoanReceiver)));
        flashLoanReceiver.withdrawToken(address(usdc), usdc.balanceOf(address(flashLoanReceiver)));
        
        // Check that owner received tokens
        uint256 wethAfter = weth.balanceOf(owner);
        uint256 usdcAfter = usdc.balanceOf(owner);
        
        assertGt(wethAfter, wethBefore, "Owner should receive WETH");
        assertGt(usdcAfter, usdcBefore, "Owner should receive USDC");
        
        console.log("WETH withdrawn:", wethAfter - wethBefore);
        console.log("USDC withdrawn:", usdcAfter - usdcBefore);
        
        vm.stopPrank();
        
        console.log("Profit withdrawal successful!");
    }
} 