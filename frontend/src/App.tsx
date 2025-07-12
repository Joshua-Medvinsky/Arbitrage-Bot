import { useState, useEffect } from 'react'
import Sidebar, { TabType } from './components/Sidebar'
import Home from './components/Home'
import Settings from './components/Settings'
import Info from './components/Info'
import StatusBar from './components/StatusBar'
import { io, Socket } from 'socket.io-client'
import { showNotification } from './utils/platform'
import { invoke } from '@tauri-apps/api/tauri'

export interface ArbitrageOpportunity {
  id: string
  pair: string
  buyDex: string
  sellDex: string
  buyPrice: number
  sellPrice: number
  profitPct: number
  profitUsd: number
  volume: number
  timestamp: number
}

export interface BotStatus {
  isRunning: boolean
  mode: 'simulation' | 'live'
  safeMode: boolean
  totalProfit: number
  totalTrades: number
  uptime: number
}

function App() {
  const [socket, setSocket] = useState<Socket | null>(null)
  const [opportunities, setOpportunities] = useState<ArbitrageOpportunity[]>([])
  const [botStatus, setBotStatus] = useState<BotStatus>({
    isRunning: false,
    mode: 'simulation',
    safeMode: true,
    totalProfit: 0,
    totalTrades: 0,
    uptime: 0
  })
  const [isConnected, setIsConnected] = useState(false)
  const [activeTab, setActiveTab] = useState<TabType>('home')
  const [backendStatus, setBackendStatus] = useState<'starting' | 'running' | 'stopped'>('starting')

  // Auto-start Python backend when app loads
  useEffect(() => {
    const initializeBackend = async () => {
      try {
        console.log('Starting Python backend...')
        const result = await invoke('start_python_backend') as string
        console.log('Backend start result:', result)
        setBackendStatus('running')
        
        // Wait a bit for the server to be ready, then connect WebSocket
        setTimeout(initializeWebSocket, 3000)
      } catch (error) {
        console.error('Failed to start Python backend:', error)
        setBackendStatus('stopped')
        // Try to connect anyway in case backend is already running
        setTimeout(initializeWebSocket, 1000)
      }
    }

    initializeBackend()

    // Cleanup function
    return () => {
      if (socket) {
        socket.disconnect()
      }
    }
  }, [socket])

  const initializeWebSocket = () => {
    console.log('Connecting to WebSocket...')
    // Initialize WebSocket connection
    const newSocket = io('http://localhost:8000')
    
    newSocket.on('connect', () => {
      console.log('Connected to arbitrage bot')
      setIsConnected(true)
    })
    
    newSocket.on('disconnect', () => {
      console.log('Disconnected from arbitrage bot')
      setIsConnected(false)
    })
    
    newSocket.on('opportunity', (data: ArbitrageOpportunity) => {
      setOpportunities(prev => {
        // Add new opportunity and keep only latest 100
        const updated = [data, ...prev].slice(0, 100)
        return updated
      })
    })
    
    newSocket.on('status', (data: BotStatus) => {
      setBotStatus(data)
    })
    
    newSocket.on('trade_executed', (data: { profit: number }) => {
      if (data.profit > 0) {
        showNotification('Trade Executed!', `Profit: $${data.profit.toFixed(2)}`)
      }
      
      setBotStatus(prev => ({
        ...prev,
        totalProfit: prev.totalProfit + data.profit,
        totalTrades: prev.totalTrades + 1
      }))
    })

    setSocket(newSocket)
  }

  const handleStartBot = () => {
    if (socket) {
      socket.emit('start_bot')
    }
  }

  const handleStopBot = () => {
    if (socket) {
      socket.emit('stop_bot')
    }
  }

  const handleExecuteTrade = (opportunity: ArbitrageOpportunity) => {
    if (socket) {
      socket.emit('execute_trade', opportunity)
    }
  }

  const handleToggleMode = () => {
    if (socket) {
      const newMode = botStatus.mode === 'simulation' ? 'live' : 'simulation'
      socket.emit('toggle_mode', newMode)
    }
  }

  const handleToggleSafeMode = () => {
    if (socket) {
      socket.emit('toggle_safe_mode', !botStatus.safeMode)
    }
  }

  const renderTabContent = () => {
    switch (activeTab) {
      case 'home':
        return (
          <Home
            opportunities={opportunities}
            status={botStatus}
            isConnected={isConnected}
            onStart={handleStartBot}
            onStop={handleStopBot}
            onToggleMode={handleToggleMode}
            onToggleSafeMode={handleToggleSafeMode}
            onExecuteTrade={handleExecuteTrade}
          />
        )
      case 'settings':
        return <Settings socket={socket} />
      case 'info':
        return <Info />
      default:
        return null
    }
  }

  // Show loading screen while backend is starting
  if (backendStatus === 'starting') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-crypto-dark to-crypto-gray text-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-crypto-blue mx-auto mb-4"></div>
          <h2 className="text-2xl font-bold mb-2">Starting Arbitrage Bot</h2>
          <p className="text-gray-400">Initializing backend services...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="h-screen w-screen text-white" style={{ 
      backgroundColor: '#2D3748',
      display: 'flex',
      flexDirection: 'row',
      gap: '16px'
    }}>
      {/* Sidebar - 20% width */}
      <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />
      
      {/* Main Content Area - 80% width */}
      <div className="h-screen flex flex-col" style={{ 
        backgroundColor: '#2D3748',
        width: 'calc(80% - 16px)',
        flex: '1 1 auto',
        marginRight: '16px'
      }}>
        {/* Status Bar */}
        <div className="flex-shrink-0" style={{ 
          backgroundColor: '#1A1D29', 
          borderBottomColor: '#4A5568',
          borderBottomWidth: '1px',
          borderBottomStyle: 'solid',
          height: 'auto',
          minHeight: '50px',
          display: 'flex',
          alignItems: 'center'
        }}>
          <StatusBar 
            status={botStatus} 
            isConnected={isConnected}
          />
        </div>
        
        {/* Scrollable Content */}
        <div className="flex-1 p-6" style={{ 
          backgroundColor: '#2D3748', 
          overflowY: 'auto'
        }}>
          {renderTabContent()}
        </div>
      </div>
    </div>
  )
}

export default App
