#!/usr/bin/env python3
"""
Terminal Monitor for Arbitrage Bot
This script monitors the terminal output log file and displays it in real-time.
Use this when running the bot through the frontend to see terminal output.
"""

import os
import time
import sys
from datetime import datetime

def monitor_terminal_output():
    """Monitor the terminal output log file and display new lines"""
    
    # Path to the terminal log file
    log_dir = os.path.join(os.path.dirname(__file__), 'logs')
    log_file = os.path.join(log_dir, 'terminal_output.log')
    
    print("🔍 Monitoring Arbitrage Bot Terminal Output")
    print(f"📁 Log file: {log_file}")
    print("=" * 60)
    
    # Wait for log file to be created
    while not os.path.exists(log_file):
        print("⏳ Waiting for arbitrage bot to start and create log file...")
        time.sleep(2)
    
    # Monitor the file for new content
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            # Start from the end of the file
            f.seek(0, 2)  # Seek to end
            
            print("✅ Connected to arbitrage bot terminal output")
            print("📺 Live terminal output (Ctrl+C to stop):")
            print("-" * 60)
            
            while True:
                line = f.readline()
                if line:
                    # Display the line without additional timestamp (already has one)
                    print(line.rstrip())
                    sys.stdout.flush()
                else:
                    # No new data, wait a bit
                    time.sleep(0.1)
                    
    except KeyboardInterrupt:
        print("\n🛑 Terminal monitoring stopped")
    except Exception as e:
        print(f"❌ Error monitoring terminal output: {e}")

if __name__ == "__main__":
    monitor_terminal_output()
