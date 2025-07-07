.PHONY: install test build deploy clean

# Install dependencies
install:
	forge install OpenZeppelin/openzeppelin-contracts
	forge install aave/aave-v3-core
	forge install foundry-rs/forge-std

# Build contracts
build:
	forge build

# Run tests
test:
	forge test

# Run tests with verbose output
test-v:
	forge test -vv

# Run tests with very verbose output
test-vv:
	forge test -vvv

# Run specific test
test-specific:
	forge test --match-test $(TEST)

# Run fuzz tests
fuzz:
	forge test --fuzz-runs 1000

# Clean build artifacts
clean:
	forge clean

# Deploy to local network
deploy-local:
	forge script Deploy --rpc-url http://localhost:8545 --broadcast

# Deploy to Base Sepolia
deploy-sepolia:
	forge script Deploy --rpc-url https://sepolia.base.org --broadcast --verify

# Deploy to Base mainnet
deploy-mainnet:
	forge script Deploy --rpc-url https://mainnet.base.org --broadcast --verify

# Gas report
gas:
	forge test --gas-report

# Coverage report
coverage:
	forge coverage

# Snapshot
snapshot:
	forge snapshot

# Help
help:
	@echo "Available commands:"
	@echo "  install      - Install dependencies"
	@echo "  build        - Build contracts"
	@echo "  test         - Run tests"
	@echo "  test-v       - Run tests with verbose output"
	@echo "  test-vv      - Run tests with very verbose output"
	@echo "  fuzz         - Run fuzz tests"
	@echo "  clean        - Clean build artifacts"
	@echo "  deploy-local - Deploy to local network"
	@echo "  gas          - Generate gas report"
	@echo "  coverage     - Generate coverage report"
	@echo "  snapshot     - Create snapshot" 