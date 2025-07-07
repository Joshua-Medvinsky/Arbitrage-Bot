// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@aave/core-v3/contracts/interfaces/IPool.sol";
import "@aave/core-v3/contracts/flashloan/interfaces/IFlashLoanReceiver.sol";

/**
 * @title FlashLoanReceiver
 * @dev Aave V3 Flash Loan Receiver for Arbitrage
 * This contract implements the executeOperation callback required by Aave
 */
contract FlashLoanReceiver is IFlashLoanReceiver {
    using SafeERC20 for IERC20;
    
    IPool public immutable pool;
    address public owner;
    
    // DEX Router addresses (Base network)
    address public constant UNISWAP_V3_ROUTER = 0x2626664c2603336E57B271c5C0b26F421741e481;
    address public constant SUSHI_ROUTER = 0x6B3595068778DD592e39A122f4f5a5cF09C90fE2;
    
    // Flag to disable DEX calls in test environment
    bool public disableDexCalls;
    
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
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner");
        _;
    }
    
    constructor(address _pool) {
        pool = IPool(_pool);
        owner = msg.sender;
    }
    
    function setDisableDexCalls(bool _disable) external onlyOwner {
        disableDexCalls = _disable;
    }
    
    /**
     * @dev Executes arbitrage during flash loan
     * This is the callback function called by Aave after providing flash loan
     */
    function executeOperation(
        address[] calldata assets,
        uint256[] calldata amounts,
        uint256[] calldata premiums,
        address initiator,
        bytes calldata params
    ) external override returns (bool) {
        require(msg.sender == address(pool), "Caller must be pool");
        require(assets.length == amounts.length, "Invalid input");
        
        // Decode arbitrage parameters
        (
            address tokenIn,
            address tokenOut,
            string memory buyDex,
            string memory sellDex,
            uint256 buyAmount,
            uint256 sellAmount,
            uint24 buyFee,
            uint24 sellFee
        ) = abi.decode(params, (address, address, string, string, uint256, uint256, uint24, uint24));
        
        // Execute arbitrage with flash loaned funds
        _executeArbitrage(
            assets[0],  // flash loaned asset
            amounts[0], // flash loaned amount
            premiums[0], // flash loan fee
            tokenIn,
            tokenOut,
            buyDex,
            sellDex,
            buyAmount,
            sellAmount,
            buyFee,
            sellFee
        );
        
        // Approve pool to pull back flash loan amount + premium
        uint256 amountOwed = amounts[0] + premiums[0];
        IERC20(assets[0]).approve(address(pool), amountOwed);
        
        emit FlashLoanExecuted(assets[0], amounts[0], premiums[0], initiator);
        
        return true;
    }
    
    /**
     * @dev Execute arbitrage with flash loaned funds
     */
    function _executeArbitrage(
        address flashLoanAsset,
        uint256 flashLoanAmount,
        uint256 flashLoanPremium,
        address tokenIn,
        address tokenOut,
        string memory buyDex,
        string memory sellDex,
        uint256 buyAmount,
        uint256 sellAmount,
        uint24 buyFee,
        uint24 sellFee
    ) internal {
        if (disableDexCalls) {
            // In test mode, just emit events without actual swaps
            emit ArbitrageExecuted(tokenIn, tokenOut, buyAmount, buyAmount, buyDex);
            emit ArbitrageExecuted(tokenOut, tokenIn, sellAmount, sellAmount, sellDex);
        } else {
            // Step 1: Buy on first DEX
            if (keccak256(abi.encodePacked(buyDex)) == keccak256(abi.encodePacked("Uniswap"))) {
                _executeUniswapSwap(tokenIn, tokenOut, buyAmount, buyFee);
            } else if (keccak256(abi.encodePacked(buyDex)) == keccak256(abi.encodePacked("SushiSwap"))) {
                _executeSushiSwap(tokenIn, tokenOut, buyAmount);
            }
            
            // Step 2: Sell on second DEX
            if (keccak256(abi.encodePacked(sellDex)) == keccak256(abi.encodePacked("Uniswap"))) {
                _executeUniswapSwap(tokenOut, tokenIn, sellAmount, sellFee);
            } else if (keccak256(abi.encodePacked(sellDex)) == keccak256(abi.encodePacked("SushiSwap"))) {
                _executeSushiSwap(tokenOut, tokenIn, sellAmount);
            }
        }
        
        // Step 3: Ensure we have enough to repay flash loan
        uint256 amountOwed = flashLoanAmount + flashLoanPremium;
        require(
            IERC20(flashLoanAsset).balanceOf(address(this)) >= amountOwed,
            "Insufficient funds to repay flash loan"
        );
    }
    
    /**
     * @dev Execute swap on Uniswap V3
     */
    function _executeUniswapSwap(
        address tokenIn,
        address tokenOut,
        uint256 amountIn,
        uint24 fee
    ) internal {
        // Approve Uniswap router
        IERC20(tokenIn).approve(UNISWAP_V3_ROUTER, amountIn);
        
        // Build swap parameters
        ISwapRouter.ExactInputSingleParams memory params = ISwapRouter.ExactInputSingleParams({
            tokenIn: tokenIn,
            tokenOut: tokenOut,
            fee: fee,
            recipient: address(this),
            deadline: block.timestamp + 300,
            amountIn: amountIn,
            amountOutMinimum: 0, // No slippage protection for simplicity
            sqrtPriceLimitX96: 0
        });
        
        // Execute swap
        ISwapRouter(UNISWAP_V3_ROUTER).exactInputSingle(params);
        
        emit ArbitrageExecuted(tokenIn, tokenOut, amountIn, 0, "Uniswap");
    }
    
    /**
     * @dev Execute swap on SushiSwap
     */
    function _executeSushiSwap(
        address tokenIn,
        address tokenOut,
        uint256 amountIn
    ) internal {
        // Approve SushiSwap router
        IERC20(tokenIn).approve(SUSHI_ROUTER, amountIn);
        
        // Build path
        address[] memory path = new address[](2);
        path[0] = tokenIn;
        path[1] = tokenOut;
        
        // Execute swap
        ISushiRouter(SUSHI_ROUTER).swapExactTokensForTokens(
            amountIn,
            0, // No slippage protection for simplicity
            path,
            address(this),
            block.timestamp + 300
        );
        
        emit ArbitrageExecuted(tokenIn, tokenOut, amountIn, 0, "SushiSwap");
    }
    
    /**
     * @dev Request flash loan from Aave
     */
    function requestFlashLoan(
        address asset,
        uint256 amount,
        address tokenIn,
        address tokenOut,
        string memory buyDex,
        string memory sellDex,
        uint256 buyAmount,
        uint256 sellAmount,
        uint24 buyFee,
        uint24 sellFee
    ) external onlyOwner {
        // Encode arbitrage parameters
        bytes memory params = abi.encode(
            tokenIn,
            tokenOut,
            buyDex,
            sellDex,
            buyAmount,
            sellAmount,
            buyFee,
            sellFee
        );
        
        // Create arrays for flash loan
        address[] memory assets = new address[](1);
        uint256[] memory amounts = new uint256[](1);
        uint256[] memory interestRateModes = new uint256[](1);
        
        assets[0] = asset;
        amounts[0] = amount;
        interestRateModes[0] = 0;
        
        // Request flash loan
        pool.flashLoan(
            address(this),
            assets,
            amounts,
            interestRateModes,
            address(this),
            params,
            0
        );
    }
    
    /**
     * @dev Withdraw tokens from contract (emergency)
     */
    function withdrawToken(address token, uint256 amount) external onlyOwner {
        IERC20(token).safeTransfer(owner, amount);
    }
    
    /**
     * @dev Withdraw ETH from contract (emergency)
     */
    function withdrawETH() external onlyOwner {
        payable(owner).transfer(address(this).balance);
    }

    function ADDRESSES_PROVIDER() external view override returns (IPoolAddressesProvider) {
        revert("Not implemented");
    }

    function POOL() external view override returns (IPool) {
        return pool;
    }
}

// Interfaces for DEX routers
interface ISwapRouter {
    struct ExactInputSingleParams {
        address tokenIn;
        address tokenOut;
        uint24 fee;
        address recipient;
        uint256 deadline;
        uint256 amountIn;
        uint256 amountOutMinimum;
        uint160 sqrtPriceLimitX96;
    }
    
    function exactInputSingle(ExactInputSingleParams calldata params) external payable returns (uint256 amountOut);
}

interface ISushiRouter {
    function swapExactTokensForTokens(
        uint256 amountIn,
        uint256 amountOutMin,
        address[] calldata path,
        address to,
        uint256 deadline
    ) external returns (uint256[] memory amounts);
} 