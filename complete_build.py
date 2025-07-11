#!/usr/bin/env python3
"""
Complete build script for the Arbitrage Bot Tauri application.
This script handles:
1. Building the standalone Python executable
2. Building the Tauri application
3. Creating a complete distribution package
"""

import os
import sys
import subprocess
import shutil
import json
from pathlib import Path

def run_command(cmd, cwd=None, shell=True):
    """Run a command and return success status"""
    print(f"Running: {cmd}")
    if cwd:
        print(f"In directory: {cwd}")
    
    try:
        result = subprocess.run(cmd, shell=shell, cwd=cwd, check=True, 
                              capture_output=True, text=True)
        print("✅ Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False

def build_python_executable():
    """Build the standalone Python executable using PyInstaller"""
    print("\n🔨 Building Python executable...")
    
    # Install PyInstaller if not present
    try:
        import PyInstaller
    except ImportError:
        print("Installing PyInstaller...")
        if not run_command("pip install pyinstaller"):
            return False
    
    # Create the PyInstaller spec file content
    spec_content = '''
import sys
from pathlib import Path

# Analysis
a = Analysis(
    ['websocket_server.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('config.py', '.'),
        ('scripts', 'scripts'),
        ('.env', '.'),
    ],
    hiddenimports=[
        'websockets',
        'asyncio',
        'json',
        'os',
        'configparser',
        'dotenv',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# PYZ
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# EXE
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='arbitrage-bot-server',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
    
    # Write the spec file
    with open('arbitrage-bot-server.spec', 'w') as f:
        f.write(spec_content)
    
    # Build the executable
    if not run_command("pyinstaller arbitrage-bot-server.spec --clean --noconfirm"):
        return False
    
    # Copy the executable to the root directory
    exe_path = Path("dist/arbitrage-bot-server.exe")
    if exe_path.exists():
        shutil.copy2(exe_path, "arbitrage-bot-server.exe")
        print(f"✅ Executable created: arbitrage-bot-server.exe")
        return True
    else:
        print("❌ Executable not found after build")
        return False

def build_frontend():
    """Build the React frontend"""
    print("\n🔨 Building React frontend...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    # Install dependencies
    if not run_command("npm install", cwd=frontend_dir):
        return False
    
    # Build the frontend
    if not run_command("npm run build", cwd=frontend_dir):
        return False
    
    print("✅ Frontend built successfully")
    return True

def build_tauri_app():
    """Build the Tauri application"""
    print("\n🔨 Building Tauri application...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    # Build the Tauri app
    if not run_command("npm run tauri build", cwd=frontend_dir):
        return False
    
    print("✅ Tauri application built successfully")
    return True

def create_distribution():
    """Create a complete distribution package"""
    print("\n📦 Creating distribution package...")
    
    dist_dir = Path("distribution")
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    
    dist_dir.mkdir()
    
    # Copy the Tauri bundle
    bundle_dir = Path("frontend/src-tauri/target/release/bundle")
    if bundle_dir.exists():
        for item in bundle_dir.iterdir():
            if item.is_dir():
                shutil.copytree(item, dist_dir / item.name)
            else:
                shutil.copy2(item, dist_dir / item.name)
    
    # Copy additional files
    additional_files = [
        "README.md",
        "DEPLOYMENT_SUMMARY.md",
        ".env.example" if Path(".env.example").exists() else None,
    ]
    
    for file_path in additional_files:
        if file_path and Path(file_path).exists():
            shutil.copy2(file_path, dist_dir / file_path)
    
    print(f"✅ Distribution package created in: {dist_dir.absolute()}")
    return True

def main():
    """Main build process"""
    print("🚀 Starting complete build process for Arbitrage Bot...")
    
    # Check if we're in the right directory
    if not Path("websocket_server.py").exists():
        print("❌ websocket_server.py not found. Please run from the project root.")
        sys.exit(1)
    
    # Step 1: Build Python executable
    if not build_python_executable():
        print("❌ Failed to build Python executable")
        sys.exit(1)
    
    # Step 2: Build frontend
    if not build_frontend():
        print("❌ Failed to build frontend")
        sys.exit(1)
    
    # Step 3: Build Tauri application
    if not build_tauri_app():
        print("❌ Failed to build Tauri application")
        sys.exit(1)
    
    # Step 4: Create distribution package
    if not create_distribution():
        print("❌ Failed to create distribution package")
        sys.exit(1)
    
    print("\n🎉 Build completed successfully!")
    print("\nNext steps:")
    print("1. Test the application in the distribution folder")
    print("2. The standalone executable includes everything needed")
    print("3. Users only need to run the installer - no additional setup required")

if __name__ == "__main__":
    main()
