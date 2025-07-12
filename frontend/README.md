# Arbitrage Bot React GUI

A modern React dashboard for monitoring and controlling your cryptocurrency arbitrage bot.

## 🚀 Quick Start (Desktop & Mobile Apps)

Want to package this as a desktop or mobile app? Here's the fastest way:

1. **Install Node.js**: Download LTS version from [nodejs.org](https://nodejs.org/)
2. **Check Setup**: Run `check-setup.bat` in this directory
3. **Install Dependencies**: `npm install`
4. **Choose Platform**:
   - **Desktop**: Install [Rust](https://rustup.rs/), then `npm run tauri:dev`
   - **Mobile**: Install [Android Studio](https://developer.android.com/studio), then `npm run mobile:dev`

📖 **Detailed Instructions**: See `DESKTOP_MOBILE_SETUP.md`

## 🚀 Features

- **Real-time Monitoring**: Live arbitrage opportunities with profit calculations
- **Interactive Controls**: Start/stop bot, toggle simulation/live mode, safety settings
- **Beautiful Dashboard**: Charts, statistics, and profit tracking
- **WebSocket Communication**: Real-time updates between frontend and Python bot
- **Responsive Design**: Works on desktop and mobile devices

## 📋 Prerequisites

Before setting up the React GUI, make sure you have:

1. **Node.js** (v18 or higher)
   - Download from [nodejs.org](https://nodejs.org/)
   - Verify installation: `node --version` and `npm --version`

2. **Python Environment** (already set up for your arbitrage bot)
   - Your existing virtual environment with the arbitrage bot dependencies

## 🛠️ Setup Instructions

### Step 1: Install Node.js Dependencies

```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# If you encounter any issues, try:
npm install --legacy-peer-deps
```

### Step 2: Install Additional Python Dependencies

```bash
# Install WebSocket support for Python
pip install websockets
```

### Step 3: Start the Backend WebSocket Server

```bash
# From the project root directory
python websocket_server.py
```

You should see:
```
INFO:__main__:Starting arbitrage bot WebSocket server on port 8000
INFO:__main__:WebSocket server started
```

### Step 4: Start the React Development Server

```bash
# In a new terminal, navigate to frontend directory
cd frontend

# Start the development server
npm run dev
```

The React app will start on `http://localhost:3000`

## 🎯 Usage

### Dashboard Features

1. **Status Bar**: Shows connection status, bot running state, mode, and uptime
2. **Controls Panel**: 
   - Start/Stop bot
   - Toggle between Simulation and Live mode
   - Enable/disable Safe Mode
3. **Statistics**: Total profit, trade count, opportunities found
4. **Profit Chart**: Real-time profit tracking over time
5. **Opportunities List**: Live arbitrage opportunities with execute buttons

### Safety Features

- **Simulation Mode**: Default mode that doesn't execute real trades
- **Safe Mode**: Restricts to small amounts and safe tokens
- **Connection Status**: Visual indicators for WebSocket connectivity

## 🔧 Configuration

### Environment Variables

The React app uses the same `.env` file as your Python bot. Key settings:

```env
# Trading modes
SIMULATION_MODE=True    # Start in simulation mode
SAFE_MODE=True         # Enable safety restrictions
EXECUTION_MODE=False   # Disable live trading initially

# For live trading (when ready)
PRIVATE_KEY=your_private_key_here
```

### WebSocket Server

The WebSocket server (`websocket_server.py`) bridges your React frontend with the Python arbitrage bot:

- **Port**: 8000 (configurable)
- **Mock Data**: Generates sample opportunities for testing
- **Real Integration**: Easy to connect with your actual arbitrage bot

## 🔍 Development

### Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Dashboard.tsx      # Main dashboard with charts
│   │   ├── Controls.tsx       # Bot control panel
│   │   ├── OpportunityList.tsx # Live opportunities
│   │   └── StatusBar.tsx      # Connection status
│   ├── App.tsx               # Main app component
│   └── main.tsx             # Entry point
├── package.json             # Dependencies
└── vite.config.ts          # Vite configuration
```

### Key Dependencies

- **React 18**: Modern React with hooks
- **TypeScript**: Type safety
- **Tailwind CSS**: Utility-first styling
- **Recharts**: Beautiful charts and graphs
- **Lucide React**: Modern icons
- **Socket.io-client**: WebSocket communication
- **Vite**: Fast development server

## 🔗 Integration with Arbitrage Bot

### Connecting Real Bot Logic

To integrate with your actual arbitrage bot, modify `websocket_server.py`:

1. **Import your bot modules**:
```python
from scripts.monitoring.arbitrage_bot import monitor  # Your main monitor function
```

2. **Replace mock opportunities** with real data:
```python
async def monitor_opportunities(self):
    # Replace generate_mock_opportunities() with actual monitoring
    real_opportunities = await get_real_opportunities()
    self.opportunities = real_opportunities
```

3. **Connect trade execution**:
```python
async def execute_trade(self, opportunity):
    # Use your actual ArbitrageExecutor
    success = self.executor.execute_arbitrage(opportunity)
```

### WebSocket API

The frontend communicates with the backend via WebSocket messages:

**Outgoing (Frontend → Backend)**:
- `start_bot`: Start the arbitrage bot
- `stop_bot`: Stop the arbitrage bot
- `toggle_mode`: Switch between simulation/live
- `toggle_safe_mode`: Enable/disable safe mode
- `execute_trade`: Execute a specific trade

**Incoming (Backend → Frontend)**:
- `status`: Bot status updates
- `opportunities`: New arbitrage opportunities
- `trade_executed`: Trade execution results

## 🎨 Customization

### Styling

The app uses Tailwind CSS with a custom crypto theme:

```css
/* Custom colors in tailwind.config.js */
colors: {
  crypto: {
    green: '#00D4AA',   // Profit/positive
    red: '#FF6B6B',     // Loss/negative
    blue: '#4ECDC4',    // Accent
    dark: '#1A1D29',    // Background
    gray: '#2D3748',    // Cards
  }
}
```

### Adding New Features

1. **New Components**: Add to `src/components/`
2. **New Pages**: Create routes in `App.tsx`
3. **WebSocket Events**: Add to both frontend and `websocket_server.py`

## 🐛 Troubleshooting

### Common Issues

1. **"npm not found"**: Install Node.js from nodejs.org
2. **WebSocket connection failed**: Ensure `websocket_server.py` is running
3. **Port conflicts**: Change ports in `vite.config.ts` and `websocket_server.py`
4. **Styling issues**: Run `npm run build` to check for Tailwind CSS issues

### Logs and Debugging

- **Frontend**: Check browser developer console (F12)
- **Backend**: WebSocket server logs in terminal
- **Network**: Monitor WebSocket messages in browser Network tab

## 🚀 Production Deployment

For production deployment:

1. **Build the React app**:
```bash
cd frontend
npm run build
```

2. **Serve the built files** with a web server (nginx, Apache, etc.)

3. **Configure WebSocket server** for production:
   - Use proper SSL certificates
   - Configure reverse proxy
   - Set up process management (PM2, systemd)

## 📝 Next Steps

1. **Test the interface** with mock data
2. **Integrate with your real bot** by modifying `websocket_server.py`
3. **Customize the UI** to match your preferences
4. **Add more features** like:
   - Historical trade logs
   - Advanced settings
   - Multiple exchange support
   - Portfolio tracking

## 🔒 Security Notes

- Never expose your private keys in the frontend
- Use HTTPS in production
- Implement proper authentication for live trading
- Validate all user inputs on the backend

---

**Happy Trading! 🚀💰**
