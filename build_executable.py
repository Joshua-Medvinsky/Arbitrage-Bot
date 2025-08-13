#!/usr/bin/env python3
"""
Portable build script for creating arbitrage-bot-server.exe
Platform independent and auto-detects environment dependencies.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(cmd, description=""):
    """Run a command and handle errors gracefully"""
    print(f"🔨 {description}")
    print(f"Running: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False

def check_pyinstaller():
    """Check if PyInstaller is installed, install if not"""
    try:
        subprocess.run([sys.executable, "-c", "import PyInstaller"], check=True, capture_output=True)
        print("✅ PyInstaller is already installed")
        return True
    except subprocess.CalledProcessError:
        print("📦 Installing PyInstaller...")
        return run_command(f"{sys.executable} -m pip install pyinstaller", "Installing PyInstaller")

def get_python_executable():
    """Get the current Python executable path"""
    return sys.executable

def build_executable():
    """Build the standalone executable using PyInstaller"""
    print("🚀 Building arbitrage-bot-server.exe...")
    
    # Check current directory
    if not os.path.exists("socketio_server.py"):
        print("❌ socketio_server.py not found. Please run from the project root.")
        return False
    
    # Check PyInstaller
    if not check_pyinstaller():
        print("❌ Failed to install PyInstaller")
        return False
    
    # Get the current Python executable
    python_exe = get_python_executable()
    print(f"🐍 Using Python: {python_exe}")
    
    # Determine the output name based on platform
    if platform.system() == "Windows":
        output_name = "arbitrage-bot-server.exe"
    else:
        output_name = "arbitrage-bot-server"
    
    # PyInstaller command with comprehensive options
    pyinstaller_cmd = [
        python_exe, "-m", "PyInstaller",
        "--onefile",  # Create single executable
        "--noconsole",  # No console window (for Windows)
        "--clean",  # Clean build
        "--name", "arbitrage-bot-server",
        "--add-data", "config.py;.",  # Include config file
        "--add-data", "scripts;scripts",  # Include scripts directory
        "--collect-all", "web3",  # Collect all web3 modules
        "--collect-all", "aiohttp",  # Collect all aiohttp modules
        "--collect-all", "flask",  # Collect all flask modules
        "--collect-all", "flask_socketio",  # Collect all flask_socketio modules
        "--collect-all", "engineio",  # Collect all engineio modules
        "--collect-all", "socketio",  # Collect all socketio modules
        "--hidden-import", "engineio.async_drivers.threading",
        "--hidden-import", "socketio.async_handlers",
        "--hidden-import", "dns.resolver",
        "--hidden-import", "dns.reversename",
        "socketio_server.py"  # Main script
    ]
    
    # On Windows, use --noconsole to prevent console window
    if platform.system() == "Windows":
        # Remove --noconsole and add --console for server applications
        pyinstaller_cmd = [arg for arg in pyinstaller_cmd if arg != "--noconsole"]
        pyinstaller_cmd.insert(4, "--console")
    
    cmd_str = " ".join(f'"{arg}"' if " " in arg else arg for arg in pyinstaller_cmd)
    
    if not run_command(cmd_str, "Building executable with PyInstaller"):
        return False
    
    # Check if the executable was created
    dist_path = Path("dist") / "arbitrage-bot-server.exe" if platform.system() == "Windows" else Path("dist") / "arbitrage-bot-server"
    
    if dist_path.exists():
        # Move the executable to the root directory
        target_path = Path(output_name)
        if target_path.exists():
            target_path.unlink()  # Remove existing file
        
        dist_path.rename(target_path)
        
        # Get file size
        size_mb = target_path.stat().st_size / (1024 * 1024)
        
        print(f"✅ Successfully created {output_name} ({size_mb:.1f} MB)")
        
        # Clean up build artifacts
        import shutil
        if Path("build").exists():
            shutil.rmtree("build")
        if Path("dist").exists():
            shutil.rmtree("dist")
        if Path("arbitrage-bot-server.spec").exists():
            Path("arbitrage-bot-server.spec").unlink()
        
        print("🧹 Cleaned up build artifacts")
        return True
    else:
        print(f"❌ Executable not found at {dist_path}")
        return False

def main():
    """Main build process"""
    print("🚀 Arbitrage Bot Executable Builder")
    print("=====================================")
    
    # Check Python version
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f"🐍 Python version: {python_version}")
    print(f"🖥️  Platform: {platform.system()} {platform.machine()}")
    
    if build_executable():
        print("\n🎉 Build completed successfully!")
        print("\nNext steps:")
        print("1. Test the executable: ./arbitrage-bot-server.exe (Windows) or ./arbitrage-bot-server (Unix)")
        print("2. Build the Tauri app: cd frontend && npm run tauri build")
        print("3. The final installer will be in frontend/src-tauri/target/release/bundle/")
    else:
        print("\n❌ Build failed!")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
