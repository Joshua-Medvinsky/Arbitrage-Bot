# Dependencies

This document outlines all the required dependencies for the Arbitrage Bot project.

## System Requirements

### Core Tools
- **Node.js**: v16+ (Recommended: v18+)
- **Rust**: v1.60+ (Recommended: v1.70+)
- **Python**: v3.9+ (Recommended: v3.11+)
- **Git**: Latest version

### Package Managers
- **npm**: Comes with Node.js
- **Cargo**: Comes with Rust
- **pip**: Comes with Python

## Installation Commands

### Node.js
```bash
# macOS (using Homebrew)
brew install node

# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs

# Windows
# Download from https://nodejs.org/
```

### Rust
```bash
# All platforms
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source "$HOME/.cargo/env"
```

### Python
```bash
# macOS (using Homebrew)
brew install python

# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3 python3-pip

# Windows
# Download from https://python.org/
```

## Project Dependencies

### Python Dependencies
See `requirements.txt` for the complete list:
- web3==6.11.3
- aiohttp==3.9.1
- python-dotenv==1.0.0
- pytest==7.4.3
- pytest-asyncio==0.21.1
- pytest-cov==4.1.0
- black==23.11.0
- flake8==6.1.0
- mypy==1.7.1
- requests==2.31.0
- pandas==2.1.4
- numpy==1.25.2

### Node.js Dependencies
See `frontend/package.json` for the complete list:
- React 18.2.0+
- TypeScript 5.2.2+
- Vite 5.0.8+
- Tauri CLI 1.5.0+
- TailwindCSS 3.3.6+

### Rust Dependencies
See `frontend/src-tauri/Cargo.toml` for the complete list:
- Tauri 1.5.0+
- Serde 1.0+
- Serde JSON 1.0+

## Verification Commands

After installation, verify all tools are working:

```bash
# Check Node.js
node --version
npm --version

# Check Rust
rustc --version
cargo --version

# Check Python
python3 --version
pip3 --version
```

## Development Setup

Run the setup script to install all dependencies:

```bash
# macOS/Linux
./setup-dev.sh

# Windows
./setup-dev.ps1
```

## Version Compatibility

| Component | Minimum Version | Recommended Version |
|-----------|----------------|-------------------|
| Node.js   | 16.x           | 18.x              |
| Rust      | 1.60           | 1.70+             |
| Python    | 3.9            | 3.11+             |
| npm       | 8.x            | 9.x+              |
| Cargo     | 1.60           | 1.70+             |
| pip       | 21.x           | 23.x+             |

## Troubleshooting

### Common Issues

1. **Node.js not found**: Install Node.js from https://nodejs.org/
2. **Rust not found**: Run `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`
3. **Python not found**: Install Python 3.9+ from https://python.org/
4. **Permission errors**: Use `sudo` for system-wide installations or install via package managers

### Platform-Specific Notes

- **macOS**: Use Homebrew for easy installation
- **Ubuntu/Debian**: Use apt package manager
- **Windows**: Download installers from official websites
- **WSL**: Follow Ubuntu/Debian instructions 