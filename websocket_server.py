"""
WebSocket server to bridge between the React frontend and the arbitrage bot
"""
import asyncio
import websockets
import json
import logging
from datetime import datetime
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.monitoring.arbitrage_bot import ArbitrageExecutor
from dotenv import load_dotenv, set_key

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        self.executor = None
        self.settings = self.load_settings()
        
    def load_settings(self):
        """Load current settings from environment variables"""
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
        """Save settings to .env file"""
        env_file = '.env'
        try:
            for key, value in new_settings.items():
                if isinstance(value, bool):
                    value = str(value)
                else:
                    value = str(value)
                set_key(env_file, key, value)
            
            # Reload settings
            load_dotenv(override=True)
            self.settings = self.load_settings()
            logger.info("Settings saved successfully")
            return True
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            return False

    async def register_client(self, websocket):
        """Register a new WebSocket client"""
        self.clients.add(websocket)
        logger.info(f"Client connected. Total clients: {len(self.clients)}")
        
        # Send initial status
        await self.send_status(websocket)
        await self.send_opportunities(websocket)
        
    async def unregister_client(self, websocket):
        """Unregister a WebSocket client"""
        self.clients.discard(websocket)
        logger.info(f"Client disconnected. Total clients: {len(self.clients)}")
        
    async def send_to_all_clients(self, message):
        """Send message to all connected clients"""
        if self.clients:
            await asyncio.gather(
                *[client.send(json.dumps(message)) for client in self.clients],
                return_exceptions=True
            )
            
    async def send_status(self, websocket=None):
        """Send bot status to client(s)"""
        uptime = int((datetime.now() - self.start_time).total_seconds())
        status = {
            'type': 'status',
            'data': {
                'isRunning': self.bot_running,
                'mode': self.mode,
                'safeMode': self.safe_mode,
                'totalProfit': self.total_profit,
                'totalTrades': self.total_trades,
                'uptime': uptime
            }
        }
        
        if websocket:
            await websocket.send(json.dumps(status))
        else:
            await self.send_to_all_clients(status)
            
    async def send_opportunities(self, websocket=None):
        """Send current opportunities to client(s)"""
        message = {
            'type': 'opportunities',
            'data': self.opportunities
        }
        
        if websocket:
            await websocket.send(json.dumps(message))
        else:
            await self.send_to_all_clients(message)
            
    async def handle_message(self, websocket, message):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(message)
            message_type = data.get('type')
            
            if message_type == 'start_bot':
                await self.start_bot()
            elif message_type == 'stop_bot':
                await self.stop_bot()
            elif message_type == 'toggle_mode':
                self.mode = data.get('mode', 'simulation')
                await self.send_status()
            elif message_type == 'toggle_safe_mode':
                self.safe_mode = data.get('safeMode', True)
                await self.send_status()
            elif message_type == 'execute_trade':
                opportunity = data.get('opportunity')
                await self.execute_trade(opportunity)
            elif message_type == 'get_settings':
                # Send current settings to the requesting client
                response = {
                    'type': 'settings_data',
                    'data': self.settings
                }
                await websocket.send(json.dumps(response))
            elif message_type == 'update_settings':
                new_settings = data.get('settings', {})
                success = self.save_settings(new_settings)
                
                response = {
                    'type': 'settings_updated',
                    'success': success,
                    'settings': self.settings if success else None,
                    'message': 'Settings saved successfully' if success else 'Failed to save settings'
                }
                await websocket.send(json.dumps(response))
            else:
                logger.warning(f"Unknown message type: {message_type}")
                
        except json.JSONDecodeError:
            logger.error("Invalid JSON received from client")
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            
    async def start_bot(self):
        """Start the arbitrage bot"""
        if not self.bot_running:
            self.bot_running = True
            logger.info("Arbitrage bot started")
            
            # Initialize executor if not already done
            if not self.executor:
                private_key = os.getenv('PRIVATE_KEY') if self.mode == 'live' else None
                self.executor = ArbitrageExecutor(private_key)
            
            # Start monitoring for opportunities
            asyncio.create_task(self.monitor_opportunities())
            
            await self.send_status()
            
    async def stop_bot(self):
        """Stop the arbitrage bot"""
        if self.bot_running:
            self.bot_running = False
            logger.info("Arbitrage bot stopped")
            await self.send_status()
            
    async def execute_trade(self, opportunity):
        """Execute an arbitrage trade"""
        if not self.bot_running or not self.executor:
            logger.warning("Cannot execute trade: bot not running or executor not initialized")
            return
            
        try:
            logger.info(f"Executing trade for {opportunity.get('pair')}")
            
            # Simulate trade execution (replace with actual execution logic)
            success = True  # self.executor.execute_arbitrage(opportunity)
            
            if success:
                # Update profit and trade count
                profit = opportunity.get('profitUsd', 0)
                self.total_profit += profit
                self.total_trades += 1
                
                # Send trade executed notification
                trade_message = {
                    'type': 'trade_executed',
                    'data': {
                        'opportunity': opportunity,
                        'profit': profit,
                        'success': True,
                        'timestamp': datetime.now().isoformat()
                    }
                }
                await self.send_to_all_clients(trade_message)
                await self.send_status()
                
                logger.info(f"Trade executed successfully. Profit: ${profit:.2f}")
            else:
                logger.error("Trade execution failed")
                
        except Exception as e:
            logger.error(f"Error executing trade: {e}")
            
    async def monitor_opportunities(self):
        """Monitor for arbitrage opportunities"""
        while self.bot_running:
            try:
                # Generate mock opportunities (replace with actual monitoring logic)
                new_opportunities = self.generate_mock_opportunities()
                
                if new_opportunities != self.opportunities:
                    self.opportunities = new_opportunities
                    await self.send_opportunities()
                    
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"Error monitoring opportunities: {e}")
                await asyncio.sleep(10)
                
    def generate_mock_opportunities(self):
        """Generate mock arbitrage opportunities for testing"""
        import random
        
        pairs = ['WETH/USDC', 'WETH/weETH', 'USDC/weETH']
        dexes = ['Uniswap', 'Aerodrome', 'SushiSwap']
        
        opportunities = []
        for i in range(random.randint(0, 5)):
            pair = random.choice(pairs)
            buy_dex = random.choice(dexes)
            sell_dex = random.choice([d for d in dexes if d != buy_dex])
            
            profit_pct = random.uniform(0.1, 5.0)
            profit_usd = random.uniform(1, 50)
            
            opportunity = {
                'id': f"opp_{i}_{int(datetime.now().timestamp())}",
                'pair': pair,
                'buyDex': buy_dex,
                'sellDex': sell_dex,
                'buyPrice': random.uniform(0.998, 1.002),
                'sellPrice': random.uniform(1.001, 1.005),
                'profitPct': profit_pct,
                'profitUsd': profit_usd,
                'volume': random.randint(10000, 100000),
                'timestamp': int(datetime.now().timestamp() * 1000)
            }
            opportunities.append(opportunity)
            
        return opportunities
        
    async def handle_client(self, websocket, path):
        """Handle WebSocket client connection"""
        await self.register_client(websocket)
        try:
            async for message in websocket:
                await self.handle_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            await self.unregister_client(websocket)

# Global server instance
server = ArbitrageBotServer()

async def main():
    """Start the WebSocket server"""
    port = 8000
    logger.info(f"Starting arbitrage bot WebSocket server on port {port}")
    
    start_server = websockets.serve(server.handle_client, "localhost", port)
    await start_server
    logger.info("WebSocket server started")
    
    # Keep the server running
    await asyncio.Future()  # Run forever

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped")
