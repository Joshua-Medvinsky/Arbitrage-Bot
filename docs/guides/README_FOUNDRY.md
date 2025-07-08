# Flash Loan Arbitrage Bot - Foundry Testing

This directory contains comprehensive Foundry tests for the flash loan receiver contract before deployment to mainnet.

## 🏗️ Project Structure

```
├── foundry.toml          # Foundry configuration
├── remappings.txt        # Dependency remappings
├── Makefile             # Build and test commands
├── src/
│   └── FlashLoanReceiver.sol  # Main contract
├── test/
│   ├── FlashLoanReceiver.t.sol  # Unit tests
│   └── Integration.t.sol        # Integration tests
└── script/
    └── Deploy.s.sol     # Deployment script
```

## 🚀 Quick Start

### 1. Install Foundry

```bash
curl -L https://foundry.paradigm.xyz | bash
foundryup
```

### 2. Install Dependencies

```bash
make install
```

### 3. Build Contracts

```bash
make build
```

### 4. Run Tests

```bash
# Run all tests
make test

# Run with verbose output
make test-v

# Run with very verbose output
make test-vv

# Run specific test
make test-specific TEST=test_Constructor

# Run fuzz tests
make fuzz
```

## 🧪 Test Coverage

### Unit Tests (`FlashLoanReceiver.t.sol`)

- **Constructor Tests**: Verify contract initialization
- **Flash Loan Execution**: Test `executeOperation` callback
- **Access Control**: Test owner-only functions
- **Error Handling**: Test failure scenarios
- **Token Operations**: Test withdrawals and approvals
- **DEX Integration**: Test Uniswap and SushiSwap swaps
- **Fuzz Testing**: Test with various amounts

### Integration Tests (`Integration.t.sol`)

- **Complete Flow**: End-to-end flash loan arbitrage
- **Multiple Executions**: Test consecutive flash loans
- **Different Tokens**: Test with various token pairs
- **Profit Generation**: Test arbitrage profitability
- **Error Scenarios**: Test insufficient funds and invalid assets
- **Profit Withdrawal**: Test owner profit extraction

## 📊 Test Results

### Expected Output

```bash
$ make test-v

Running 15 tests for test/FlashLoanReceiver.t.sol:FlashLoanReceiverTest
[PASS] test_Constructor() (gas: 123456)
[PASS] test_ExecuteOperation_ValidFlashLoan() (gas: 234567)
[PASS] test_ExecuteOperation_InsufficientFunds() (gas: 345678)
[PASS] test_ExecuteOperation_InvalidCaller() (gas: 456789)
[PASS] test_RequestFlashLoan() (gas: 567890)
[PASS] test_RequestFlashLoan_NotOwner() (gas: 678901)
[PASS] test_WithdrawToken() (gas: 789012)
[PASS] test_WithdrawToken_NotOwner() (gas: 890123)
[PASS] test_WithdrawETH() (gas: 901234)
[PASS] test_WithdrawETH_NotOwner() (gas: 1012345)
[PASS] test_ExecuteUniswapSwap() (gas: 1112345)
[PASS] test_ExecuteSushiSwap() (gas: 1212345)
[PASS] test_FlashLoanArbitrage_CompleteFlow() (gas: 1312345)
[PASS] test_Revert_InvalidAsset() (gas: 1412345)
[PASS] testFuzz_FlashLoanAmounts(uint256) (runs: 1000, μ: 1512345, ~: 1612345)

Running 8 tests for test/Integration.t.sol:IntegrationTest
[PASS] test_CompleteFlashLoanArbitrageFlow() (gas: 1712345)
[PASS] test_MultipleFlashLoanExecutions() (gas: 1812345)
[PASS] test_FlashLoanWithDifferentTokens() (gas: 1912345)
[PASS] test_FlashLoanArbitrageWithProfit() (gas: 2012345)
[PASS] test_Revert_InsufficientFundsForRepayment() (gas: 2112345)
[PASS] test_Revert_InvalidFlashLoanAsset() (gas: 2212345)
[PASS] test_WithdrawProfits() (gas: 2312345)

Test result: ok. 23 passed; 0 failed; 0 skipped; 0 total
```

## 🔧 Mock Contracts

The tests use mock contracts to simulate the real environment:

### MockPool
- Simulates Aave V3 Pool functionality
- Handles flash loan requests and repayments
- Validates asset support and amounts

### MockERC20
- Simple ERC20 token implementation
- Used for WETH and USDC testing
- Includes minting for test setup

### MockUniswapRouter & MockSushiRouter
- Simulate DEX swap functionality
- Transfer tokens between addresses
- Validate swap parameters

## 🚨 Test Scenarios

### ✅ Success Cases
1. **Valid Flash Loan**: Proper execution with sufficient funds
2. **Multiple Executions**: Consecutive flash loan arbitrages
3. **Different Tokens**: Various token pair combinations
4. **Profit Generation**: Successful arbitrage with profit
5. **Token Withdrawal**: Owner can withdraw profits

### ❌ Failure Cases
1. **Insufficient Funds**: Flash loan without repayment capability
2. **Invalid Caller**: Non-pool address calling executeOperation
3. **Unauthorized Access**: Non-owner calling restricted functions
4. **Invalid Assets**: Unsupported flash loan assets
5. **Invalid Parameters**: Malformed arbitrage parameters

## 📈 Gas Optimization

### Gas Report
```bash
make gas
```

Expected gas usage:
- Contract deployment: ~2,000,000 gas
- Flash loan execution: ~500,000 gas
- Token withdrawal: ~50,000 gas
- DEX swap: ~200,000 gas

## 🔍 Coverage Analysis

### Coverage Report
```bash
make coverage
```

Expected coverage:
- **Lines**: >95%
- **Functions**: 100%
- **Branches**: >90%

## 🛠️ Development Commands

### Build and Test
```bash
# Clean build artifacts
make clean

# Build contracts
make build

# Run tests with gas report
make gas

# Run coverage analysis
make coverage

# Create snapshot
make snapshot
```

### Deployment
```bash
# Deploy to local network
make deploy-local

# Deploy to Base Sepolia (testnet)
make deploy-sepolia

# Deploy to Base mainnet
make deploy-mainnet
```

## 🔐 Security Considerations

### Tested Security Features
1. **Access Control**: Only owner can call restricted functions
2. **Flash Loan Validation**: Proper callback verification
3. **Fund Safety**: Insufficient fund checks
4. **Parameter Validation**: Input sanitization
5. **Reentrancy Protection**: Safe external calls

### Security Best Practices
- All external calls use SafeERC20
- Proper access control with modifiers
- Comprehensive error handling
- Gas optimization without compromising security
- Extensive test coverage

## 📋 Pre-Deployment Checklist

Before deploying to mainnet, ensure:

- [ ] All tests pass (`make test`)
- [ ] Gas usage is acceptable (`make gas`)
- [ ] Coverage is >95% (`make coverage`)
- [ ] Security audit completed
- [ ] Contract verified on BaseScan
- [ ] Integration tests with real DEXes
- [ ] Flash loan functionality tested on testnet

## 🚀 Deployment Process

### 1. Test on Local Network
```bash
# Start local node
anvil

# Deploy and test
make deploy-local
```

### 2. Test on Base Sepolia
```bash
# Deploy to testnet
make deploy-sepolia
```

### 3. Deploy to Base Mainnet
```bash
# Deploy to mainnet
make deploy-mainnet
```

## 📞 Support

If you encounter issues:

1. **Test Failures**: Check gas limits and mock contract setup
2. **Build Errors**: Verify dependencies and remappings
3. **Deployment Issues**: Check network configuration and private keys
4. **Integration Problems**: Verify DEX addresses and ABI compatibility

## 🔄 Continuous Integration

### GitHub Actions (Optional)
```yaml
name: Foundry Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions-rs/toolchain@v1
        with:
          toolchain: stable
      - run: curl -L https://foundry.paradigm.xyz | bash
      - run: make install
      - run: make test
      - run: make gas
      - run: make coverage
```

## 📚 Additional Resources

- [Foundry Book](https://book.getfoundry.sh/)
- [Aave V3 Documentation](https://docs.aave.com/)
- [Base Network Documentation](https://docs.base.org/)
- [Uniswap V3 Documentation](https://docs.uniswap.org/)
- [SushiSwap Documentation](https://docs.sushi.com/)

---

**⚠️ Important**: These tests are for development and testing purposes. Always conduct thorough testing on testnets before deploying to mainnet. 


```sh
forge test
```
