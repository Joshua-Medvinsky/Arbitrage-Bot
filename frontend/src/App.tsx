import { useState, useEffect } from 'react'
import Sidebar, { TabType } from './components/Sidebar'
import Home from './components/Home'
import Settings from './components/Settings'
import Info from './components/Info'
import StatusBar from './components/StatusBar'
import { io, Socket } from 'socket.io-client'
import { showNotification, startArbitrageBot, stopArbitrageBot } from './utils/platform'

// Lazy load the invoke function to speed up initial load
let invokeModule: any = null
const getInvoke = async () => {
  if (!invokeModule) {
    invokeModule = await import('@tauri-apps/api/tauri')
  }
  return invokeModule.invoke
}

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

export interface Portfolio {
  totalValue: number
  totalProfit: number
  profitPercentage: number
  assets: {
    symbol: string
    name: string
    amount: number
    value: number
    change24h: number
    icon: string
  }[]
}

export interface LogEntry {
  id: string
  timestamp: number
  level: 'info' | 'warning' | 'error' | 'success'
  message: string
  source?: string
}

export interface InitializationState {
  stage: 'starting' | 'backend' | 'websocket' | 'complete'
  progress: number
  message: string
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
  const [initState, setInitState] = useState<InitializationState>({
    stage: 'starting',
    progress: 0,
    message: 'Preparing to initialize...'
  })
  const [portfolio] = useState<Portfolio>({
    totalValue: 34010.00,
    totalProfit: 2156.80,
    profitPercentage: 6.78,
    assets: [
      { symbol: 'BTC', name: 'Bitcoin', amount: 0.5, value: 20788, change24h: 2.5, icon: '₿' },
      { symbol: 'ETH', name: 'Ethereum', amount: 10, value: 21543, change24h: 4.2, icon: 'Ξ' },
      { symbol: 'BNB', name: 'Binance', amount: 50, value: 18788, change24h: -1.8, icon: 'B' },
      { symbol: 'LTC', name: 'Litecoin', amount: 20, value: 11657, change24h: -0.5, icon: 'Ł' }
    ]
  })
  const [logs, setLogs] = useState<LogEntry[]>([])

  // Listen for bot logs from Tauri events
  useEffect(() => {
    let unlistenFunction: (() => void) | null = null;

    const setupTauriListeners = async () => {
      try {
        // Lazy load the event API to speed up initial render
        const { listen } = await import('@tauri-apps/api/event')
        
        // Listen for bot logs
        const unlisten = await listen('bot-log', (event: any) => {
          const logData = event.payload
          const logEntry: LogEntry = {
            id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
            timestamp: logData.timestamp || Date.now(),
            level: logData.level as LogEntry['level'],
            message: logData.message,
            source: logData.source
          }
          
          setLogs(prev => {
            // Add new log at the end and keep only latest 200 entries
            const updated = [...prev, logEntry].slice(-200)
            return updated
          })
        })

        unlistenFunction = unlisten
      } catch (error) {
        console.error('Failed to setup Tauri listeners:', error)
      }
    }

    // Defer setup to not block initial render
    setTimeout(setupTauriListeners, 100)

    // Cleanup function
    return () => {
      if (unlistenFunction) {
        unlistenFunction()
      }
    }
  }, []) // Empty dependency array to run only once

  // Auto-start Python backend when app loads
  useEffect(() => {
    const initializeBackend = async () => {
      try {
        setInitState({ stage: 'backend', progress: 25, message: 'Starting Python backend...' })
        
        const invoke = await getInvoke()
        const result = await invoke('start_python_backend') as string
        console.log('Backend start result:', result)
        
        setInitState({ stage: 'websocket', progress: 60, message: 'Connecting to WebSocket...' })
        
        // Reduced delay for faster connection
        setTimeout(() => {
          initializeWebSocket()
          // Complete initialization after a shorter delay
          setTimeout(() => {
            setInitState({ stage: 'complete', progress: 100, message: 'Ready to trade!' })
          }, 800) // Reduced from 1500ms
        }, 1500) // Reduced from 3000ms
      } catch (error) {
        console.error('Failed to start Python backend:', error)
        setInitState({ stage: 'complete', progress: 100, message: 'Backend connection failed, trying fallback...' })
        // Try to connect anyway in case backend is already running
        setTimeout(initializeWebSocket, 500) // Reduced from 1000ms
      }
    }

    // Only initialize once when the component mounts
    initializeBackend()

    // Cleanup function
    return () => {
      if (socket) {
        socket.disconnect()
      }
    }
  }, []) // Remove socket dependency to prevent re-initialization

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
        // Add new opportunity at the end and keep only latest 100
        const updated = [...prev, data].slice(-100)
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

  const handleStartBot = async () => {
    try {
      // Start the actual arbitrage bot Python script
      const result = await startArbitrageBot()
      console.log('Arbitrage bot start result:', result)
      
      // Update bot status to running
      setBotStatus(prev => ({ ...prev, isRunning: true }))
      
      // Show notification
      showNotification('Bot Started', 'Arbitrage bot is now running')
      
      // Also emit to websocket for any additional frontend updates
      if (socket) {
        socket.emit('start_bot')
      }
    } catch (error) {
      console.error('Failed to start arbitrage bot:', error)
      showNotification('Error', 'Failed to start arbitrage bot')
    }
  }

  const handleStopBot = async () => {
    try {
      // Stop the arbitrage bot Python script
      const result = await stopArbitrageBot()
      console.log('Arbitrage bot stop result:', result)
      
      // Update bot status to stopped
      setBotStatus(prev => ({ ...prev, isRunning: false }))
      
      // Show notification
      showNotification('Bot Stopped', 'Arbitrage bot has been stopped')
      
      // Also emit to websocket for any additional frontend updates
      if (socket) {
        socket.emit('stop_bot')
      }
    } catch (error) {
      console.error('Failed to stop arbitrage bot:', error)
      showNotification('Error', 'Failed to stop arbitrage bot')
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
            portfolio={portfolio}
            isConnected={isConnected}
            logs={logs}
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

  // Show enhanced loading screen while initializing
  if (initState.stage !== 'complete') {
    return (
      <div style={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #0D1421 0%, #1A1F2E 50%, #2D3748 100%)',
        color: '#ffffff',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontFamily: 'Inter, system-ui, Avenir, Helvetica, Arial, sans-serif'
      }}>
        <div style={{ textAlign: 'center', maxWidth: '400px', padding: '2rem' }}>
          {/* Animated Logo/Icon */}
          <div style={{
            width: '80px',
            height: '80px',
            margin: '0 auto 2rem auto',
            background: 'linear-gradient(135deg, #3B82F6, #1E40AF)',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            animation: 'pulse 2s infinite',
            boxShadow: '0 0 30px rgba(59, 130, 246, 0.3)'
          }}>
            <span style={{ fontSize: '2rem', fontWeight: 'bold' }}>⚡</span>
          </div>

          {/* Title */}
          <h1 style={{
            fontSize: '2.5rem',
            fontWeight: '700',
            marginBottom: '0.5rem',
            background: 'linear-gradient(135deg, #3B82F6, #10B981)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text'
          }}>
            Arbitrage Bot
          </h1>

          <p style={{
            fontSize: '1.1rem',
            color: '#9CA3AF',
            marginBottom: '2rem',
            fontWeight: '500'
          }}>
            Advanced DeFi Trading Platform
          </p>

          {/* Progress Animation */}
          <div style={{
            width: '100%',
            height: '6px',
            backgroundColor: '#374151',
            borderRadius: '3px',
            overflow: 'hidden',
            marginBottom: '1.5rem'
          }}>
            <div style={{
              width: `${initState.progress}%`,
              height: '100%',
              background: 'linear-gradient(90deg, #3B82F6, #10B981)',
              borderRadius: '3px',
              transition: 'width 0.5s ease-in-out',
              boxShadow: '0 0 10px rgba(59, 130, 246, 0.5)'
            }}></div>
          </div>

          {/* Progress Percentage */}
          <div style={{
            fontSize: '0.9rem',
            color: '#3B82F6',
            fontWeight: '600',
            marginBottom: '1rem'
          }}>
            {initState.progress}%
          </div>

          {/* Status Text */}
          <p style={{
            fontSize: '0.95rem',
            color: '#D1D5DB',
            marginBottom: '1rem'
          }}>
            {initState.message}
          </p>

          {/* Feature List */}
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            gap: '0.5rem',
            alignItems: 'center'
          }}>
            <div style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: '0.5rem', 
              color: initState.stage === 'starting' ? '#F59E0B' : '#10B981', 
              fontSize: '0.9rem' 
            }}>
              <span>{initState.stage === 'starting' ? '⟳' : '✓'}</span> System Initialization
            </div>
            <div style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: '0.5rem', 
              color: initState.stage === 'backend' ? '#F59E0B' : initState.progress > 25 ? '#10B981' : '#9CA3AF', 
              fontSize: '0.9rem' 
            }}>
              <span>{initState.stage === 'backend' ? '⟳' : initState.progress > 25 ? '✓' : '○'}</span> Backend Services
            </div>
            <div style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: '0.5rem', 
              color: initState.stage === 'websocket' ? '#F59E0B' : initState.progress > 60 ? '#10B981' : '#9CA3AF', 
              fontSize: '0.9rem' 
            }}>
              <span>{initState.stage === 'websocket' ? '⟳' : initState.progress > 60 ? '✓' : '○'}</span> WebSocket Connection
            </div>
          </div>
        </div>

        {/* Add CSS animations */}
        <style>{`
          @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
          }
        `}</style>
      </div>
    )
  }

  return (
    <div style={{ 
      display: 'flex', 
      height: '100vh',
      width: '100vw',
      backgroundColor: '#0D1421',
      color: '#ffffff',
      fontFamily: 'Inter, system-ui, Avenir, Helvetica, Arial, sans-serif',
      overflow: 'hidden'
    }}>
      {/* Sidebar */}
      <div style={{
        width: '20%',
        minWidth: '250px',
        backgroundColor: '#1A1F2E',
        borderRight: '1px solid #2D3748',
        height: '100vh',
        overflow: 'hidden'
      }}>
        <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />
      </div>
      
      {/* Main Content Area */}
      <div style={{
        width: '80%',
        height: '100vh',
        display: 'flex',
        flexDirection: 'column',
        backgroundColor: '#0D1421',
        overflow: 'hidden'
      }}>
        {/* Status Bar */}
        <div style={{
          backgroundColor: '#1A1F2E',
          border: '1px solid #2D3748',
          borderRadius: '12px',
          minHeight: '60px',
          margin: '16px 24px 0 24px', // Increased left and right margin from 16px to 24px
          flexShrink: 0,
          overflow: 'visible' // Ensure content doesn't get clipped
        }}>
          <StatusBar 
            status={botStatus} 
            isConnected={isConnected}
          />
        </div>
        
        {/* Content */}
        <div style={{
          flex: 1,
          overflowY: 'auto',
          backgroundColor: '#0D1421',
          padding: '16px',
          paddingTop: '16px'
        }}>
          {renderTabContent()}
        </div>
      </div>
    </div>
  )
}

export default App
