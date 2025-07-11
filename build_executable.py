"""
Build script to create a standalone     cmd = [
        python_exe, "-m", "PyInstaller",
        "--onefile",                    # Create single executable
        "--name=arbitrage-bot-server",  # Executable name
        "--hidden-import=websockets",   # Include WebSocket library
        "--hidden-import=dotenv",       # Include dotenv library
        "--hidden-import=asyncio",      # Include asyncio
        "--hidden-import=json",         # Include json
        "--hidden-import=os",           # Include os
        "--hidden-import=configparser", # Include configparser
        "--hidden-import=logging",      # Include logging
        "--hidden-import=threading",    # Include threading
        "--hidden-import=web3",         # Include Web3 library
        "--hidden-import=aiohttp",      # Include aiohttp
        "--hidden-import=aiohttp.web",  # Include aiohttp web
        "--hidden-import=aiohttp.client", # Include aiohttp client
        "--hidden-import=aiohttp.connector", # Include aiohttp connector
        "--hidden-import=multidict",    # Include multidict
        "--hidden-import=yarl",         # Include yarl
        "--hidden-import=web3.auto",    # Include Web3 auto
        "--hidden-import=web3.contract", # Include Web3 contract
        "--hidden-import=web3.providers", # Include Web3 providers
        "--hidden-import=web3.providers.http", # Include Web3 HTTP provider
        "--collect-all=aiohttp",        # Collect all aiohttp modules
        "--collect-all=web3",           # Collect all web3 modules
        "--console",                    # Keep console for debugging
        "websocket_server.py"
    ]le for the WebSocket server
This allows the Tauri app to run without requiring Python to be installed
"""
import subprocess
import sys
import os

def install_pyinstaller():
    """Install PyInstaller and required dependencies if not already installed"""
    required_packages = [
        'pyinstaller',
        'web3',
        'aiohttp', 
        'python-dotenv',
        'websockets'
    ]
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} already installed")
        except ImportError:
            print(f"📦 Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ {package} installed")

def build_executable():
    """Build standalone executable for the WebSocket server"""
    print("🔨 Building WebSocket server executable...")
    
    # Detect the current Python executable (works with venv, conda, system Python)
    python_exe = sys.executable
    print(f"Using Python: {python_exe}")
    
    # Determine the correct path separator for --add-data
    if os.name == 'nt':  # Windows
        data_sep = ";"
    else:  # Unix/Linux/macOS
        data_sep = ":"
    
    cmd = [
        python_exe, "-m", "PyInstaller",
        "--onefile",                    # Create single executable
        "--name=arbitrage-bot-server",  # Executable name
        "--hidden-import=websockets",   # Include WebSocket library
        "--hidden-import=dotenv",       # Include dotenv library (correct import name)
        "--hidden-import=asyncio",      # Include asyncio
        "--hidden-import=json",         # Include json
        "--hidden-import=os",           # Include os
        "--hidden-import=configparser", # Include configparser
        "--hidden-import=logging",      # Include logging
        "--hidden-import=threading",    # Include threading
        "--console",                    # Keep console for debugging
        "websocket_server.py"
    ]
    
    # Add optional data files if they exist
    optional_files = [
        ("config.py", "."),
        ("scripts", "scripts"),
        (".env", "."),
    ]
    
    for src, dst in optional_files:
        if os.path.exists(src):
            cmd.append(f"--add-data={src}{data_sep}{dst}")
            print(f"✅ Including: {src}")
        else:
            print(f"⚠️  Optional file not found: {src}")
    
    print(f"📋 Build command: {' '.join(cmd)}")
    
    try:
        subprocess.check_call(cmd)
        print("✅ Executable built successfully!")
        print("📁 Executable location: dist/arbitrage-bot-server.exe")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False

def main():
    """Main build process"""
    print("🚀 Building Arbitrage Bot Standalone Executable\n")
    
    # Check if we're in the right directory
    if not os.path.exists("websocket_server.py"):
        print("❌ websocket_server.py not found!")
        print("   Please run this script from the project root directory")
        return False
    
    # Install PyInstaller
    install_pyinstaller()
    
    # Build executable
    success = build_executable()
    
    if success:
        print("\n🎉 Build completed successfully!")
        print("\n📋 Next steps:")
        print("1. Copy dist/arbitrage-bot-server.exe to your app bundle")
        print("2. Update Tauri to launch this executable instead of Python")
        print("3. Build your desktop app with: npm run tauri:build")
    else:
        print("\n💥 Build failed! Check error messages above.")
    
    return success

if __name__ == "__main__":
    main()
