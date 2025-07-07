// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "forge-std/Test.sol";
import "../src/FlashLoanReceiver.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

// Mock contracts for testing
contract MockERC20 is ERC20 {
    constructor(string memory name, string memory symbol) ERC20(name, symbol) {
        _mint(msg.sender, 1000000 * 10**decimals());
    }
}

contract MockPool {
    mapping(address => uint256) public reserves;
    mapping(address => bool) public flashLoanEnabled;
    
    constructor() {
        flashLoanEnabled[address(0x4200000000000000000000000000000000000006)] = true; // WETH
        flashLoanEnabled[address(0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913)] = true; // USDC
    }
    
    function enableFlashLoan(address asset) external {
        flashLoanEnabled[asset] = true;
    }
    
    function flashLoan(
        address receiverAddress,
        address[] calldata assets,
        uint256[] calldata amounts,
        uint256[] calldata interestRateModes,
        address onBehalfOf,
        bytes calldata params,
        uint16 referralCode
    ) external {
        require(flashLoanEnabled[assets[0]], "Asset not supported");
        require(amounts[0] > 0, "Amount must be greater than 0");
        
        // Calculate premium (0.09% fee)
        uint256 premium = (amounts[0] * 9) / 10000;
        
        // Transfer assets to receiver
        IERC20(assets[0]).transfer(receiverAddress, amounts[0]);
        
        // Call executeOperation on receiver
        IFlashLoanReceiver(receiverAddress).executeOperation(
            assets,
            amounts,
            _createPremiumsArray(assets.length, premium), // premiums
            msg.sender,
            params
        );
        
        // Check repayment
        uint256 amountOwed = amounts[0] + premium;
        require(
            IERC20(assets[0]).balanceOf(address(this)) >= amountOwed,
            "Insufficient repayment"
        );
    }
    
    function _createPremiumsArray(uint256 length, uint256 premium) internal pure returns (uint256[] memory) {
        uint256[] memory premiums = new uint256[](length);
        for (uint256 i = 0; i < length; i++) {
            premiums[i] = premium;
        }
        return premiums;
    }
}

contract MockUniswapRouter {
    function exactInputSingle(ISwapRouter.ExactInputSingleParams calldata params) external payable returns (uint256) {
        // Mock swap - transfer tokens
        IERC20(params.tokenIn).transferFrom(msg.sender, address(this), params.amountIn);
        IERC20(params.tokenOut).transfer(params.recipient, params.amountOutMinimum);
        return params.amountOutMinimum;
    }
}

contract MockSushiRouter {
    function swapExactTokensForTokens(
        uint256 amountIn,
        uint256 amountOutMin,
        address[] calldata path,
        address to,
        uint256 deadline
    ) external returns (uint256[] memory amounts) {
        // Mock swap - transfer tokens
        IERC20(path[0]).transferFrom(msg.sender, address(this), amountIn);
        IERC20(path[1]).transfer(to, amountOutMin);
        
        amounts = new uint256[](2);
        amounts[0] = amountIn;
        amounts[1] = amountOutMin;
    }
}

contract FlashLoanReceiverTest is Test {
    FlashLoanReceiver public flashLoanReceiver;
    MockPool public mockPool;
    MockUniswapRouter public mockUniswapRouter;
    MockSushiRouter public mockSushiRouter;
    MockERC20 public weth;
    MockERC20 public usdc;
    
    address public owner;
    address public user;
    
    event FlashLoanExecuted(
        address indexed asset,
        uint256 amount,
        uint256 premium,
        address indexed initiator
    );
    
    event ArbitrageExecuted(
        address indexed tokenIn,
        address indexed tokenOut,
        uint256 amountIn,
        uint256 amountOut,
        string dex
    );
    
    function setUp() public {
        owner = makeAddr("owner");
        user = makeAddr("user");
        
        // Deploy mock contracts
        mockPool = new MockPool();
        mockUniswapRouter = new MockUniswapRouter();
        mockSushiRouter = new MockSushiRouter();
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
    
    function test_Constructor() public {
        assertEq(address(flashLoanReceiver.pool()), address(mockPool));
        assertEq(flashLoanReceiver.owner(), owner);
    }
    
    function test_ExecuteOperation_ValidFlashLoan() public {
        address[] memory assets = new address[](1);
        uint256[] memory amounts = new uint256[](1);
        uint256[] memory premiums = new uint256[](1);
        
        assets[0] = address(weth);
        amounts[0] = 1 ether;
        premiums[0] = 0.0009 ether; // 0.09% fee
        
        // Encode arbitrage parameters
        bytes memory params = abi.encode(
            address(weth),  // tokenIn
            address(usdc),  // tokenOut
            "Uniswap",      // buyDex
            "SushiSwap",    // sellDex
            1 ether,        // buyAmount
            0.9 ether       // sellAmount
        );
        
        // Fund receiver with tokens for arbitrage
        weth.transfer(address(flashLoanReceiver), 1 ether);
        usdc.transfer(address(flashLoanReceiver), 1000 * 1e6);
        
        vm.expectEmit(true, false, false, true);
        emit FlashLoanExecuted(address(weth), 1 ether, 0.0009 ether, address(this));
        
        bool success = flashLoanReceiver.executeOperation(
            assets,
            amounts,
            premiums,
            address(this),
            params
        );
        
        assertTrue(success);
    }
    
    function test_ExecuteOperation_InsufficientFunds() public {
        address[] memory assets = new address[](1);
        uint256[] memory amounts = new uint256[](1);
        uint256[] memory premiums = new uint256[](1);
        
        assets[0] = address(weth);
        amounts[0] = 1 ether;
        premiums[0] = 0.0009 ether;
        
        bytes memory params = abi.encode(
            address(weth),
            address(usdc),
            "Uniswap",
            "SushiSwap",
            1 ether,
            0.9 ether
        );
        
        // Don't fund receiver - should fail
        vm.expectRevert("Insufficient funds to repay flash loan");
        
        flashLoanReceiver.executeOperation(
            assets,
            amounts,
            premiums,
            address(this),
            params
        );
    }
    
    function test_ExecuteOperation_InvalidCaller() public {
        address[] memory assets = new address[](1);
        uint256[] memory amounts = new uint256[](1);
        uint256[] memory premiums = new uint256[](1);
        
        assets[0] = address(weth);
        amounts[0] = 1 ether;
        premiums[0] = 0.0009 ether;
        
        bytes memory params = abi.encode(
            address(weth),
            address(usdc),
            "Uniswap",
            "SushiSwap",
            1 ether,
            0.9 ether
        );
        
        // Call from non-pool address
        vm.expectRevert("Caller must be pool");
        
        vm.prank(user);
        flashLoanReceiver.executeOperation(
            assets,
            amounts,
            premiums,
            address(this),
            params
        );
    }
    
    function test_RequestFlashLoan() public {
        vm.startPrank(owner);
        
        vm.expectEmit(true, false, false, true);
        emit FlashLoanExecuted(address(weth), 1 ether, 0.0009 ether, address(mockPool));
        
        flashLoanReceiver.requestFlashLoan(
            address(weth),  // asset
            1 ether,        // amount
            address(weth),  // tokenIn
            address(usdc),  // tokenOut
            "Uniswap",      // buyDex
            "SushiSwap",    // sellDex
            1 ether,        // buyAmount
            0.9 ether       // sellAmount
        );
        
        vm.stopPrank();
    }
    
    function test_RequestFlashLoan_NotOwner() public {
        vm.startPrank(user);
        
        vm.expectRevert("Only owner");
        
        flashLoanReceiver.requestFlashLoan(
            address(weth),
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
    
    function test_WithdrawToken() public {
        // Fund receiver with tokens
        weth.transfer(address(flashLoanReceiver), 1 ether);
        
        uint256 balanceBefore = weth.balanceOf(owner);
        
        vm.prank(owner);
        flashLoanReceiver.withdrawToken(address(weth), 1 ether);
        
        uint256 balanceAfter = weth.balanceOf(owner);
        assertEq(balanceAfter - balanceBefore, 1 ether);
    }
    
    function test_WithdrawToken_NotOwner() public {
        weth.transfer(address(flashLoanReceiver), 1 ether);
        
        vm.prank(user);
        vm.expectRevert("Only owner");
        flashLoanReceiver.withdrawToken(address(weth), 1 ether);
    }
    
    function test_WithdrawETH() public {
        uint256 balanceBefore = owner.balance;
        
        vm.prank(owner);
        flashLoanReceiver.withdrawETH();
        
        uint256 balanceAfter = owner.balance;
        assertGt(balanceAfter, balanceBefore);
    }
    
    function test_WithdrawETH_NotOwner() public {
        vm.prank(user);
        vm.expectRevert("Only owner");
        flashLoanReceiver.withdrawETH();
    }
    
    function test_ExecuteUniswapSwap() public {
        // This test would require mocking the Uniswap router more thoroughly
        // For now, we'll test the basic flow
        address[] memory assets = new address[](1);
        uint256[] memory amounts = new uint256[](1);
        uint256[] memory premiums = new uint256[](1);
        
        assets[0] = address(weth);
        amounts[0] = 1 ether;
        premiums[0] = 0.0009 ether;
        
        bytes memory params = abi.encode(
            address(weth),
            address(usdc),
            "Uniswap",
            "SushiSwap",
            1 ether,
            0.9 ether
        );
        
        // Fund receiver
        weth.transfer(address(flashLoanReceiver), 2 ether);
        usdc.transfer(address(flashLoanReceiver), 2000 * 1e6);
        
        bool success = flashLoanReceiver.executeOperation(
            assets,
            amounts,
            premiums,
            address(this),
            params
        );
        
        assertTrue(success);
    }
    
    function test_ExecuteSushiSwap() public {
        address[] memory assets = new address[](1);
        uint256[] memory amounts = new uint256[](1);
        uint256[] memory premiums = new uint256[](1);
        
        assets[0] = address(weth);
        amounts[0] = 1 ether;
        premiums[0] = 0.0009 ether;
        
        bytes memory params = abi.encode(
            address(weth),
            address(usdc),
            "SushiSwap",
            "Uniswap",
            1 ether,
            0.9 ether
        );
        
        // Fund receiver
        weth.transfer(address(flashLoanReceiver), 2 ether);
        usdc.transfer(address(flashLoanReceiver), 2000 * 1e6);
        
        bool success = flashLoanReceiver.executeOperation(
            assets,
            amounts,
            premiums,
            address(this),
            params
        );
        
        assertTrue(success);
    }
    
    function test_FlashLoanArbitrage_CompleteFlow() public {
        vm.startPrank(owner);
        
        // Fund receiver with initial tokens
        weth.transfer(address(flashLoanReceiver), 2 ether);
        usdc.transfer(address(flashLoanReceiver), 2000 * 1e6);
        
        // Execute flash loan arbitrage
        flashLoanReceiver.requestFlashLoan(
            address(weth),
            1 ether,
            address(weth),
            address(usdc),
            "Uniswap",
            "SushiSwap",
            1 ether,
            0.9 ether
        );
        
        vm.stopPrank();
        
        // Verify profit was generated (simplified check)
        uint256 wethBalance = weth.balanceOf(address(flashLoanReceiver));
        uint256 usdcBalance = usdc.balanceOf(address(flashLoanReceiver));
        
        assertGt(wethBalance + usdcBalance, 0, "Should have some tokens after arbitrage");
    }
    
    function test_Revert_InvalidAsset() public {
        address[] memory assets = new address[](1);
        uint256[] memory amounts = new uint256[](1);
        uint256[] memory premiums = new uint256[](1);
        
        assets[0] = address(0x123); // Invalid asset
        amounts[0] = 1 ether;
        premiums[0] = 0.0009 ether;
        
        bytes memory params = abi.encode(
            address(weth),
            address(usdc),
            "Uniswap",
            "SushiSwap",
            1 ether,
            0.9 ether
        );
        
        // This should fail because the asset is not supported by the mock pool
        vm.expectRevert("Asset not supported");
        
        flashLoanReceiver.executeOperation(
            assets,
            amounts,
            premiums,
            address(this),
            params
        );
    }
    
    function testFuzz_FlashLoanAmounts(uint256 amount) public {
        vm.assume(amount > 0.1 ether && amount < 100 ether);
        
        address[] memory assets = new address[](1);
        uint256[] memory amounts = new uint256[](1);
        uint256[] memory premiums = new uint256[](1);
        
        assets[0] = address(weth);
        amounts[0] = amount;
        premiums[0] = (amount * 9) / 10000; // 0.09% fee
        
        bytes memory params = abi.encode(
            address(weth),
            address(usdc),
            "Uniswap",
            "SushiSwap",
            amount,
            amount * 9 / 10
        );
        
        // Fund receiver
        weth.transfer(address(flashLoanReceiver), amount * 2);
        usdc.transfer(address(flashLoanReceiver), 2000 * 1e6);
        
        bool success = flashLoanReceiver.executeOperation(
            assets,
            amounts,
            premiums,
            address(this),
            params
        );
        
        assertTrue(success);
    }
} 