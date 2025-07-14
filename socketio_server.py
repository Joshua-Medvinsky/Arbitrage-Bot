"""
Flask-SocketIO server to bridge between the React frontend and the arbitrage bot
"""
from flask import Flask, request
from flask_socketio import SocketIO, emit
import json
import logging
from datetime import datetime
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'arbitrage-bot-secret'

# Create SocketIO instance with CORS enabled
socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)

class ArbitrageBotServer:
    def __init__(self):
        self.clients = set()
        self.bot_running = False
        self.mode = 'simulation'
        self.safe_mode = True
        self.total_profit = 0.0
        self.total_trades = 0
        self.start_time = datetime.now()
        self.opportunities = []
        self.settings = self.load_settings()
        
    def load_settings(self):
        """Load current settings from environment variables"""
        # Ensure .env is loaded fresh
        load_dotenv(override=True)
        
        return {
            'SIMULATION_MODE': os.getenv('SIMULATION_MODE', 'True').lower() == 'true',
            'FLASH_LOAN_ENABLED': os.getenv('FLASH_LOAN_ENABLED', 'False').lower() == 'true',
            'SAFE_MODE': os.getenv('SAFE_MODE', 'True').lower() == 'true',
            'EXECUTION_MODE': os.getenv('EXECUTION_MODE', 'False').lower() == 'true',
            'MIN_PROFIT_PCT': float(os.getenv('MIN_PROFIT_PCT', '1.0')),
            'MAX_PROFIT_PCT': float(os.getenv('MAX_PROFIT_PCT', '20.0')),
            'POSITION_SIZE_USD': float(os.getenv('POSITION_SIZE_USD', '5')),
            'MIN_LIQUIDITY_USD': float(os.getenv('MIN_LIQUIDITY_USD', '100000')),
            'MAX_SLIPPAGE': float(os.getenv('MAX_SLIPPAGE', '0.01')),
            'BASE_GAS_PRICE_GWEI': float(os.getenv('BASE_GAS_PRICE_GWEI', '1000000')),
            'MEV_PROTECTION_COST_USD': float(os.getenv('MEV_PROTECTION_COST_USD', '1.0')),
            'MIN_PROFIT_THRESHOLD_USD': float(os.getenv('MIN_PROFIT_THRESHOLD_USD', '0.50')),
            'FLASH_LOAN_AMOUNT_USD': float(os.getenv('FLASH_LOAN_AMOUNT_USD', '100000'))
        }
    
    def save_settings(self, new_settings):
        """Save settings to .env file while preserving formatting"""
        env_file = '.env'
        try:
            # Read the entire .env file
            with open(env_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Update only the specific keys while preserving formatting
            updated_lines = []
            for line in lines:
                line_updated = False
                stripped = line.strip()
                
                # Skip comments and empty lines
                if not stripped or stripped.startswith('#'):
                    updated_lines.append(line)
                    continue
                
                # Check if this line contains a setting we need to update
                if '=' in stripped:
                    key_part = stripped.split('=')[0].strip()
                    if key_part in new_settings:
                        # Update this setting while preserving any inline comments
                        value = new_settings[key_part]
                        if isinstance(value, bool):
                            value = str(value)
                        else:
                            value = str(value)
                        
                        # Check if there's an inline comment
                        if '#' in line and line.index('#') > line.index('='):
                            # Preserve inline comment
                            comment_part = line[line.index('#'):]
                            updated_lines.append(f"{key_part}={value}  {comment_part}")
                        else:
                            # No inline comment, preserve line ending
                            if line.endswith('\n'):
                                updated_lines.append(f"{key_part}={value}\n")
                            else:
                                updated_lines.append(f"{key_part}={value}")
                        line_updated = True
                
                if not line_updated:
                    updated_lines.append(line)
            
            # Write the updated content back to the file
            with open(env_file, 'w', encoding='utf-8') as f:
                f.writelines(updated_lines)
            
            # Reload settings
            load_dotenv(override=True)
            self.settings = self.load_settings()
            logger.info("Settings saved successfully with preserved formatting")
            return True
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            return False

# Create the server instance
server = ArbitrageBotServer()

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    server.clients.add(request.sid)
    logger.info(f"Client {request.sid} connected. Total clients: {len(server.clients)}")
    
    # Send initial status
    emit('status', {
        'isRunning': server.bot_running,
        'mode': server.mode,
        'safeMode': server.safe_mode,
        'totalProfit': server.total_profit,
        'totalTrades': server.total_trades,
        'uptime': int((datetime.now() - server.start_time).total_seconds())
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    server.clients.discard(request.sid)
    logger.info(f"Client {request.sid} disconnected. Total clients: {len(server.clients)}")

@socketio.on('get_settings')
def handle_get_settings():
    """Handle get_settings request"""
    logger.info(f"Client {request.sid} requested settings")
    emit('settings_data', server.settings)

@socketio.on('update_settings')
def handle_update_settings(data):
    """Handle update_settings request"""
    logger.info(f"Client {request.sid} updating settings: {data}")
    
    success = server.save_settings(data)
    
    response = {
        'success': success,
        'settings': server.settings if success else None,
        'message': 'Settings saved successfully' if success else 'Failed to save settings'
    }
    
    emit('settings_updated', response)

@socketio.on('start_bot')
def handle_start_bot():
    """Handle start_bot request"""
    logger.info(f"Client {request.sid} requested to start bot")
    server.bot_running = True
    
    # Broadcast status to all clients
    socketio.emit('status', {
        'isRunning': server.bot_running,
        'mode': server.mode,
        'safeMode': server.safe_mode,
        'totalProfit': server.total_profit,
        'totalTrades': server.total_trades,
        'uptime': int((datetime.now() - server.start_time).total_seconds())
    })

@socketio.on('stop_bot')
def handle_stop_bot():
    """Handle stop_bot request"""
    logger.info(f"Client {request.sid} requested to stop bot")
    server.bot_running = False
    
    # Broadcast status to all clients
    socketio.emit('status', {
        'isRunning': server.bot_running,
        'mode': server.mode,
        'safeMode': server.safe_mode,
        'totalProfit': server.total_profit,
        'totalTrades': server.total_trades,
        'uptime': int((datetime.now() - server.start_time).total_seconds())
    })

@socketio.on('toggle_mode')
def handle_toggle_mode(data):
    """Handle toggle_mode request"""
    mode = data.get('mode', 'simulation')
    logger.info(f"Client {request.sid} toggled mode to: {mode}")
    server.mode = mode
    
    # Broadcast status to all clients
    socketio.emit('status', {
        'isRunning': server.bot_running,
        'mode': server.mode,
        'safeMode': server.safe_mode,
        'totalProfit': server.total_profit,
        'totalTrades': server.total_trades,
        'uptime': int((datetime.now() - server.start_time).total_seconds())
    })

@socketio.on('toggle_safe_mode')
def handle_toggle_safe_mode(data):
    """Handle toggle_safe_mode request"""
    safe_mode = data.get('safeMode', True)
    logger.info(f"Client {request.sid} toggled safe mode to: {safe_mode}")
    server.safe_mode = safe_mode
    
    # Broadcast status to all clients
    socketio.emit('status', {
        'isRunning': server.bot_running,
        'mode': server.mode,
        'safeMode': server.safe_mode,
        'totalProfit': server.total_profit,
        'totalTrades': server.total_trades,
        'uptime': int((datetime.now() - server.start_time).total_seconds())
    })

@socketio.on('execute_trade')
def handle_execute_trade(data):
    """Handle execute_trade request"""
    opportunity = data.get('opportunity')
    logger.info(f"Client {request.sid} requested to execute trade: {opportunity}")
    
    # Simulate trade execution
    profit = opportunity.get('profitUsd', 0) if opportunity else 0
    server.total_profit += profit
    server.total_trades += 1
    
    # Emit trade executed event
    socketio.emit('trade_executed', {'profit': profit})

if __name__ == "__main__":
    logger.info("Starting arbitrage bot Flask-SocketIO server on port 8000")
    socketio.run(app, host="127.0.0.1", port=8000, debug=False, allow_unsafe_werkzeug=True)
