import { ArbitrageOpportunity, BotStatus, Portfolio, LogEntry } from '../App'
import { TrendingUp, Activity, DollarSign, Target, Shield, Play, Square, BarChart3, Clock, Users, ScrollText, AlertCircle, CheckCircle, Info, XCircle, Wifi, WifiOff } from 'lucide-react'
import { useState, useEffect } from 'react'
import { getBotStatus, startBotLocal, stopBotLocal, toggleTradingMode, toggleSafeMode, type LocalBotState } from '../utils/botControl'

interface HomeProps {
  opportunities: ArbitrageOpportunity[]
  status: BotStatus
  portfolio: Portfolio
  isConnected: boolean
  logs: LogEntry[]
  socket?: any // Add socket for server sync
  onStart: () => void
  onStop: () => void
  onToggleMode: () => void
  onToggleSafeMode: () => void
  onExecuteTrade: (opportunity: ArbitrageOpportunity) => void
}

const Home = ({
  opportunities,
  status,
  portfolio,
  isConnected,
  logs,
  socket,
  onStart,
  onStop,
  onToggleMode,
  onToggleSafeMode,
  onExecuteTrade
}: HomeProps) => {
  const [localBotState, setLocalBotState] = useState<LocalBotState | null>(null)

  // Load local bot state on component mount
  useEffect(() => {
    const loadLocalState = async () => {
      try {
        const state = await getBotStatus()
        setLocalBotState(state)
        console.log('Loaded local bot state:', state)
      } catch (error) {
        console.error('Failed to load local bot state:', error)
        // Set a default state that matches the current .env settings
        const fallbackState = {
          isRunning: false,
          mode: 'live' as const, // Based on .env: SIMULATION_MODE=false
          safeMode: true, // Based on .env: SAFE_MODE=true
          sessionTrades: 0,
          sessionProfit: 0
        }
        setLocalBotState(fallbackState)
        console.log('Using fallback bot state:', fallbackState)
      }
    }
    loadLocalState()
  }, [])

  // Debug: Log server status changes
  useEffect(() => {
    console.log('Server status prop changed:', {
      isRunning: status.isRunning,
      mode: status.mode,
      safeMode: status.safeMode,
      isConnected
    })
  }, [status.isRunning, status.mode, status.safeMode, isConnected])

  // Handle connection loss in live mode - auto-stop bot
  useEffect(() => {
    if (localBotState && localBotState.mode === 'live' && !isConnected && localBotState.isRunning) {
      // Connection lost while bot was running in live mode - stop the bot
      console.log('Connection lost in live mode - stopping bot automatically')
      const stopBotDueToConnectionLoss = async () => {
        try {
          // Stop the bot locally first to update UI immediately
          const updatedState = { ...localBotState, isRunning: false }
          setLocalBotState(updatedState)
          
          // Try to stop the bot via Tauri if possible
          try {
            await stopBotLocal()
            console.log('Bot successfully stopped due to connection loss in live mode')
          } catch (taruiError) {
            console.warn('Could not stop bot via Tauri, but local state updated:', taruiError)
          }
        } catch (error) {
          console.error('Failed to handle connection loss:', error)
        }
      }
      stopBotDueToConnectionLoss()
    }
  }, [isConnected, localBotState?.mode, localBotState?.isRunning, localBotState])

  // Update local state when connection status changes (for re-rendering)
  useEffect(() => {
    // This effect is just to trigger re-renders when connection status changes
    // The actual logic is handled in the component functions
  }, [isConnected, localBotState?.mode])

  // Sync local state with server when connection is restored
  useEffect(() => {
    if (isConnected && localBotState && socket?.connected) {
      // Sync any local changes made while offline
      try {
        socket.emit('sync_bot_state', {
          isRunning: localBotState.isRunning,
          mode: localBotState.mode,
          safeMode: localBotState.safeMode,
          sessionTrades: localBotState.sessionTrades,
          sessionProfit: localBotState.sessionProfit
        })
        console.log('Bot state synced with server after reconnection:', {
          mode: localBotState.mode,
          isRunning: localBotState.isRunning,
          safeMode: localBotState.safeMode
        })
      } catch (error) {
        console.warn('Failed to sync bot state with server:', error)
      }
    }
  }, [isConnected, localBotState, socket])

  // Update local state when server status changes (for live mode)
  useEffect(() => {
    if (localBotState && isConnected && localBotState.mode === 'live') {
      // In live mode when connected, only sync the running status from server
      // Keep mode and safeMode from local state (which comes from .env)
      if (status.isRunning !== localBotState.isRunning) {
        
        const syncedState = {
          ...localBotState,
          isRunning: status.isRunning,
          // Don't override mode and safeMode - keep local values from .env
        }
        
        // Only update if there's actually a change to prevent loops
        console.log('Local running status synced with server:', { 
          isRunning: status.isRunning, 
          keepingLocalMode: localBotState.mode,
          keepingLocalSafeMode: localBotState.safeMode 
        })
        setLocalBotState(syncedState)
      }
    }
  }, [status.isRunning, localBotState?.mode, localBotState?.isRunning, isConnected])

  // Get effective bot status (prioritize local state when available)
  const effectiveBotStatus = (() => {
    if (localBotState) {
      // Use local state when available
      let effectiveIsRunning = localBotState.isRunning
      
      // In live mode without connection, bot cannot be running
      if (localBotState.mode === 'live' && !isConnected) {
        effectiveIsRunning = false
      }
      
      return {
        ...status,
        isRunning: effectiveIsRunning,
        mode: localBotState.mode,
        safeMode: localBotState.safeMode
      }
    }
    // Fall back to server status only when local state is not available
    return status
  })()

  // Determine if controls should be enabled based on mode and connection
  const canControlBot = (() => {
    if (!localBotState) return false // Can't control if we don't know the state
    
    if (localBotState.mode === 'simulation') {
      // Simulation mode: always allow controls (offline capable)
      return true
    } else {
      // Live mode: require connection for bot controls
      return isConnected
    }
  })()

  // Handle bot start with mode awareness
  const handleStart = async () => {
    if (!localBotState) return
    
    if (localBotState.mode === 'simulation') {
      // Simulation mode: always use local control
      const result = await startBotLocal()
      if (result.success) {
        const updatedState = { ...localBotState, isRunning: true, lastStartTime: Date.now() }
        setLocalBotState(updatedState)
      }
    } else if (localBotState.mode === 'live' && isConnected) {
      // Live mode: use server control when connected, but also update local state optimistically
      try {
        // Optimistically update local state for immediate UI feedback
        const optimisticState = { ...localBotState, isRunning: true, lastStartTime: Date.now() }
        setLocalBotState(optimisticState)
        
        // Call server function
        onStart()
        
        console.log('Bot start initiated for live mode')
      } catch (error) {
        console.error('Failed to start bot in live mode:', error)
        // Revert optimistic update on error
        setLocalBotState(localBotState)
      }
    } else if (localBotState.mode === 'live' && !isConnected) {
      // Live mode when offline: show error message
      console.warn('Cannot start bot in live mode without internet connection')
      // Could add a toast notification here in the future
    }
  }

  // Handle bot stop with mode awareness
  const handleStop = async () => {
    if (!localBotState) return
    
    if (localBotState.mode === 'simulation') {
      // Simulation mode: always use local control
      const result = await stopBotLocal()
      if (result.success) {
        const updatedState = { ...localBotState, isRunning: false }
        setLocalBotState(updatedState)
      }
    } else if (isConnected) {
      // Live mode: use server control when connected, but also update local state optimistically
      try {
        // Optimistically update local state for immediate UI feedback
        const optimisticState = { ...localBotState, isRunning: false }
        setLocalBotState(optimisticState)
        
        // Call server function
        onStop()
        
        console.log('Bot stop initiated for live mode')
      } catch (error) {
        console.error('Failed to stop bot in live mode:', error)
        // Revert optimistic update on error
        setLocalBotState(localBotState)
      }
    } else {
      // Live mode when offline: force stop locally (shouldn't be running anyway)
      const updatedState = { ...localBotState, isRunning: false }
      setLocalBotState(updatedState)
    }
  }

  // Handle mode toggle with mode awareness
  const handleToggleMode = async () => {
    if (!localBotState) return
    
    if (!isConnected) {
      // When offline: always use local control
      const result = await toggleTradingMode()
      if (result.success) {
        const updatedState = { ...localBotState, mode: result.newMode }
        setLocalBotState(updatedState)
      }
    } else {
      // When connected: use local control first, then notify server
      try {
        // Update local state first (this updates .env file)
        const result = await toggleTradingMode()
        if (result.success) {
          const updatedState = { ...localBotState, mode: result.newMode }
          setLocalBotState(updatedState)
          
          // Then notify server of the change
          onToggleMode()
          
          console.log('Mode toggle completed:', result.newMode)
        }
      } catch (error) {
        console.error('Failed to toggle mode:', error)
      }
    }
  }

  // Handle safe mode toggle with mode awareness
  const handleToggleSafeMode = async () => {
    if (!localBotState) return
    
    if (!isConnected) {
      // When offline: always use local control
      const result = await toggleSafeMode()
      if (result.success) {
        const updatedState = { ...localBotState, safeMode: result.newSafeMode }
        setLocalBotState(updatedState)
      }
    } else {
      // When connected: use local control first, then notify server
      try {
        // Update local state first (this updates .env file)
        const result = await toggleSafeMode()
        if (result.success) {
          const updatedState = { ...localBotState, safeMode: result.newSafeMode }
          setLocalBotState(updatedState)
          
          // Then notify server of the change
          onToggleSafeMode()
          
          console.log('Safe mode toggle completed:', result.newSafeMode)
        }
      } catch (error) {
        console.error('Failed to toggle safe mode:', error)
      }
    }
  }
  const cardStyle = {
    backgroundColor: '#1A1F2E',
    border: '1px solid #2D3748',
    borderRadius: '16px',
    padding: '24px',
    marginBottom: '24px'
  }

  const smallCardStyle = {
    backgroundColor: '#1A1F2E',
    border: '1px solid #2D3748',
    borderRadius: '12px',
    padding: '20px'
  }

  const buttonStyle = {
    padding: '12px 24px',
    borderRadius: '8px',
    border: 'none',
    fontWeight: '600',
    cursor: 'pointer',
    fontSize: '14px',
    transition: 'all 0.2s ease'
  }

  const successRate = status.totalTrades > 0 ? Math.round(((status.totalTrades - opportunities.length) / status.totalTrades) * 100) : 95

  return (
    <div style={{ padding: '0 8px' }}>
      {/* Header */}
      <div style={{ marginBottom: '32px' }}>
        <h1 style={{ fontSize: '32px', fontWeight: '700', margin: '0 0 8px 0', color: '#ffffff' }}>
          Good Evening, Trader!
        </h1>
        <p style={{ color: '#9CA3AF', fontSize: '16px', margin: 0 }}>
          Monitor your arbitrage opportunities and portfolio performance
        </p>
      </div>

      {/* Top Stats Cards */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', 
        gap: '20px',
        marginBottom: '32px'
      }}>
        {/* Portfolio Value */}
        <div style={smallCardStyle}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <p style={{ color: '#9CA3AF', fontSize: '14px', margin: '0 0 4px 0' }}>Portfolio Value</p>
              <p style={{ fontSize: '28px', fontWeight: '700', margin: 0, color: '#ffffff' }}>
                ${portfolio.totalValue.toLocaleString()}
              </p>
              <p style={{ 
                fontSize: '14px', 
                margin: '4px 0 0 0',
                color: portfolio.profitPercentage >= 0 ? '#00D4AA' : '#FF6B6B'
              }}>
                {portfolio.profitPercentage >= 0 ? '+' : ''}{portfolio.profitPercentage}% 
                (${portfolio.totalProfit.toLocaleString()})
              </p>
            </div>
            <div style={{ 
              backgroundColor: '#00D4AA20', 
              borderRadius: '12px', 
              padding: '12px',
              color: '#00D4AA'
            }}>
              <DollarSign size={24} />
            </div>
          </div>
        </div>

        {/* Total Trades */}
        <div style={smallCardStyle}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <p style={{ color: '#9CA3AF', fontSize: '14px', margin: '0 0 4px 0' }}>Total Trades</p>
              <p style={{ fontSize: '28px', fontWeight: '700', margin: 0, color: '#ffffff' }}>
                {status.totalTrades.toLocaleString()}
              </p>
              <p style={{ fontSize: '14px', margin: '4px 0 0 0', color: '#00D4AA' }}>
                24h volume: $2.4M
              </p>
            </div>
            <div style={{ 
              backgroundColor: '#4F46E520', 
              borderRadius: '12px', 
              padding: '12px',
              color: '#4F46E5'
            }}>
              <Target size={24} />
            </div>
          </div>
        </div>

        {/* Success Rate */}
        <div style={smallCardStyle}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <p style={{ color: '#9CA3AF', fontSize: '14px', margin: '0 0 4px 0' }}>Success Rate</p>
              <p style={{ fontSize: '28px', fontWeight: '700', margin: 0, color: '#ffffff' }}>
                {successRate}%
              </p>
              <p style={{ fontSize: '14px', margin: '4px 0 0 0', color: '#9CA3AF' }}>
                Last 30 days
              </p>
            </div>
            <div style={{ 
              backgroundColor: '#F59E0B20', 
              borderRadius: '12px', 
              padding: '12px',
              color: '#F59E0B'
            }}>
              <Activity size={24} />
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px' }}>
        
        {/* Left Column - Opportunities */}
        <div>
          {/* Bot Controls */}
          <div style={cardStyle}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <h3 style={{ fontSize: '20px', fontWeight: '600', margin: 0, color: '#ffffff' }}>
                Trading Bot Controls
              </h3>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                {/* Mode indicator */}
                <div style={{ 
                  padding: '4px 12px', 
                  borderRadius: '20px', 
                  backgroundColor: effectiveBotStatus.mode === 'simulation' ? '#4F46E520' : '#F59E0B20',
                  color: effectiveBotStatus.mode === 'simulation' ? '#4F46E5' : '#F59E0B',
                  fontSize: '12px',
                  fontWeight: '600'
                }}>
                  {effectiveBotStatus.mode === 'simulation' ? 'SIMULATION' : 'LIVE TRADING'}
                </div>
                {/* Status indicator */}
                <div style={{ 
                  padding: '4px 12px', 
                  borderRadius: '20px', 
                  backgroundColor: effectiveBotStatus.isRunning ? '#00D4AA20' : '#FF6B6B20',
                  color: effectiveBotStatus.isRunning ? '#00D4AA' : '#FF6B6B',
                  fontSize: '12px',
                  fontWeight: '600'
                }}>
                  {effectiveBotStatus.isRunning ? 'ACTIVE' : 'INACTIVE'}
                </div>
              </div>
            </div>

            {/* Connection status warning for live mode */}
            {effectiveBotStatus.mode === 'live' && !isConnected && (
              <div style={{
                padding: '12px',
                borderRadius: '8px',
                backgroundColor: '#FF6B6B20',
                border: '1px solid #FF6B6B',
                marginBottom: '16px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}>
                <WifiOff size={16} style={{ color: '#FF6B6B' }} />
                <span style={{ color: '#FF6B6B', fontSize: '14px', fontWeight: '500' }}>
                  {localBotState?.isRunning ? 
                    'Connection lost - bot automatically stopped. Live trading requires internet connection.' :
                    'Live trading requires internet connection. Bot controls disabled until reconnected.'
                  }
                </span>
              </div>
            )}

            {/* Simulation mode indicator - shown for both online and offline */}
            {effectiveBotStatus.mode === 'simulation' && (
              <div style={{
                padding: '12px',
                borderRadius: '8px',
                backgroundColor: '#4F46E520',
                border: '1px solid #4F46E5',
                marginBottom: '16px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}>
                <Shield size={16} style={{ color: '#4F46E5' }} />
                <span style={{ color: '#4F46E5', fontSize: '14px', fontWeight: '500' }}>
                  Simulation mode: Safe testing environment with mock data. No real money at risk.
                </span>
              </div>
            )}
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
              <button
                onClick={effectiveBotStatus.isRunning ? handleStop : handleStart}
                disabled={!canControlBot}
                style={{
                  ...buttonStyle,
                  backgroundColor: canControlBot 
                    ? (effectiveBotStatus.isRunning ? '#FF6B6B' : '#00D4AA')
                    : '#6B7280',
                  color: '#ffffff',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  justifyContent: 'center',
                  opacity: canControlBot ? 1 : 0.5,
                  cursor: canControlBot ? 'pointer' : 'not-allowed'
                }}
              >
                {effectiveBotStatus.isRunning ? <Square size={16} /> : <Play size={16} />}
                {effectiveBotStatus.isRunning ? 'Stop Bot' : 'Start Bot'}
              </button>
              
              <button
                onClick={handleToggleMode}
                disabled={effectiveBotStatus.isRunning || (!isConnected && effectiveBotStatus.mode === 'live')}
                style={{
                  ...buttonStyle,
                  backgroundColor: effectiveBotStatus.mode === 'simulation' ? '#4F46E5' : '#F59E0B',
                  color: '#ffffff',
                  opacity: (effectiveBotStatus.isRunning || (!isConnected && effectiveBotStatus.mode === 'live')) ? 0.5 : 1,
                  cursor: (effectiveBotStatus.isRunning || (!isConnected && effectiveBotStatus.mode === 'live')) ? 'not-allowed' : 'pointer'
                }}
              >
                {effectiveBotStatus.mode === 'simulation' ? 'Simulation Mode' : 'Live Trading'}
              </button>
              
              <button
                onClick={handleToggleSafeMode}
                disabled={!canControlBot}
                style={{
                  ...buttonStyle,
                  backgroundColor: canControlBot 
                    ? (effectiveBotStatus.safeMode ? '#10B981' : '#6B7280')
                    : '#6B7280',
                  color: '#ffffff',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  justifyContent: 'center',
                  opacity: canControlBot ? 1 : 0.5,
                  cursor: canControlBot ? 'pointer' : 'not-allowed'
                }}
              >
                <Shield size={16} />
                {effectiveBotStatus.safeMode ? 'Safe Mode ON' : 'Safe Mode OFF'}
              </button>
            </div>
          </div>

          {/* Opportunities Table */}
          <div style={cardStyle}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <h3 style={{ fontSize: '20px', fontWeight: '600', margin: 0, color: '#ffffff' }}>
                {effectiveBotStatus.mode === 'simulation' ? 'Simulated' : 'Live'} Arbitrage Opportunities
              </h3>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                {/* Connection status */}
                <div style={{ 
                  padding: '4px 12px', 
                  borderRadius: '20px', 
                  backgroundColor: isConnected ? '#00D4AA20' : '#FF6B6B20',
                  color: isConnected ? '#00D4AA' : '#FF6B6B',
                  fontSize: '12px',
                  fontWeight: '600',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px'
                }}>
                  {isConnected ? <Wifi size={12} /> : <WifiOff size={12} />}
                  {isConnected ? 'CONNECTED' : 'OFFLINE'}
                </div>
              </div>
            </div>

            {/* Mode-specific messaging */}
            {effectiveBotStatus.mode === 'simulation' && !isConnected && (
              <div style={{
                padding: '12px',
                borderRadius: '8px',
                backgroundColor: '#4F46E520',
                border: '1px solid #4F46E5',
                marginBottom: '16px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}>
                <Info size={16} style={{ color: '#4F46E5' }} />
                <span style={{ color: '#4F46E5', fontSize: '14px' }}>
                  Simulation mode: Showing mock opportunities for testing. No real trades will be executed.
                </span>
              </div>
            )}

            {effectiveBotStatus.mode === 'live' && !isConnected && (
              <div style={{
                padding: '12px',
                borderRadius: '8px',
                backgroundColor: '#FF6B6B20',
                border: '1px solid #FF6B6B',
                marginBottom: '16px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}>
                <AlertCircle size={16} style={{ color: '#FF6B6B' }} />
                <span style={{ color: '#FF6B6B', fontSize: '14px' }}>
                  Live trading mode requires internet connection to fetch real market data.
                </span>
              </div>
            )}
            
            {opportunities.length === 0 ? (
              <div style={{ 
                textAlign: 'center', 
                padding: '40px 20px',
                color: '#9CA3AF'
              }}>
                <BarChart3 size={48} style={{ margin: '0 auto 16px', opacity: 0.5 }} />
                <p style={{ margin: 0, fontSize: '16px' }}>No opportunities found</p>
                <p style={{ margin: '8px 0 0 0', fontSize: '14px' }}>
                  {isConnected 
                    ? `Scanning for ${effectiveBotStatus.mode === 'simulation' ? 'simulated' : 'real'} arbitrage opportunities...`
                    : effectiveBotStatus.mode === 'simulation' 
                      ? 'Simulation mode: Mock data will appear when bot is running'
                      : 'Please check your internet connection'
                  }
                </p>
              </div>
            ) : (
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid #2D3748' }}>
                      <th style={{ padding: '12px', textAlign: 'left', color: '#9CA3AF', fontSize: '14px' }}>Pair</th>
                      <th style={{ padding: '12px', textAlign: 'left', color: '#9CA3AF', fontSize: '14px' }}>Buy Exchange</th>
                      <th style={{ padding: '12px', textAlign: 'left', color: '#9CA3AF', fontSize: '14px' }}>Sell Exchange</th>
                      <th style={{ padding: '12px', textAlign: 'right', color: '#9CA3AF', fontSize: '14px' }}>Profit %</th>
                      <th style={{ padding: '12px', textAlign: 'right', color: '#9CA3AF', fontSize: '14px' }}>Profit USD</th>
                      <th style={{ padding: '12px', textAlign: 'center', color: '#9CA3AF', fontSize: '14px' }}>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {opportunities.slice(0, 10).map((opportunity) => {
                      // Determine if execution is allowed
                      const canExecute = effectiveBotStatus.mode === 'simulation' 
                        ? effectiveBotStatus.isRunning  // Simulation: only need bot running
                        : isConnected && effectiveBotStatus.isRunning  // Live: need connection + bot running
                      
                      return (
                        <tr key={opportunity.id} style={{ borderBottom: '1px solid #2D3748' }}>
                          <td style={{ padding: '12px', fontWeight: '600', color: '#ffffff' }}>
                            {opportunity.pair}
                            {effectiveBotStatus.mode === 'simulation' && (
                              <span style={{ 
                                marginLeft: '8px', 
                                fontSize: '10px', 
                                color: '#4F46E5',
                                backgroundColor: '#4F46E520',
                                padding: '2px 6px',
                                borderRadius: '4px',
                                fontWeight: '500'
                              }}>
                                SIM
                              </span>
                            )}
                          </td>
                          <td style={{ padding: '12px', color: '#9CA3AF' }}>{opportunity.buyDex}</td>
                          <td style={{ padding: '12px', color: '#9CA3AF' }}>{opportunity.sellDex}</td>
                          <td style={{ 
                            padding: '12px', 
                            textAlign: 'right', 
                            fontWeight: '600',
                            color: opportunity.profitPct >= 0 ? '#00D4AA' : '#FF6B6B'
                          }}>
                            {opportunity.profitPct.toFixed(2)}%
                          </td>
                          <td style={{ 
                            padding: '12px', 
                            textAlign: 'right', 
                            fontWeight: '600',
                            color: opportunity.profitUsd >= 0 ? '#00D4AA' : '#FF6B6B'
                          }}>
                            ${opportunity.profitUsd.toFixed(2)}
                          </td>
                          <td style={{ padding: '12px', textAlign: 'center' }}>
                            <button
                              onClick={() => onExecuteTrade(opportunity)}
                              disabled={!canExecute}
                              style={{
                                padding: '6px 12px',
                                borderRadius: '6px',
                                border: 'none',
                                backgroundColor: canExecute ? '#00D4AA' : '#6B7280',
                                color: '#ffffff',
                                fontSize: '12px',
                                fontWeight: '600',
                                cursor: canExecute ? 'pointer' : 'not-allowed',
                                opacity: canExecute ? 1 : 0.5
                              }}
                              title={
                                !canExecute 
                                  ? effectiveBotStatus.mode === 'live' 
                                    ? 'Requires internet connection for live trading'
                                    : 'Bot must be running to execute trades'
                                  : `Execute ${effectiveBotStatus.mode === 'simulation' ? 'simulated' : 'live'} trade`
                              }
                            >
                              {effectiveBotStatus.mode === 'simulation' ? 'Simulate' : 'Execute'}
                            </button>
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Bot Activity Logs */}
          <div style={cardStyle}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <h3 style={{ fontSize: '20px', fontWeight: '600', margin: 0, color: '#ffffff' }}>
                Bot Activity Logs
              </h3>
              <div style={{ 
                padding: '4px 12px', 
                borderRadius: '20px', 
                backgroundColor: '#4F46E520',
                color: '#4F46E5',
                fontSize: '12px',
                fontWeight: '600',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}>
                <ScrollText size={14} />
                {logs.length} entries
              </div>
            </div>
            
            <div style={{
              backgroundColor: '#0D1421',
              borderRadius: '12px',
              border: '1px solid #2D3748',
              height: '300px',
              overflowY: 'auto',
              padding: '16px'
            }}>
              {logs.length === 0 ? (
                <div style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  height: '100%',
                  color: '#9CA3AF',
                  textAlign: 'center'
                }}>
                  <ScrollText size={48} style={{ marginBottom: '16px', opacity: 0.5 }} />
                  <p style={{ margin: 0, fontSize: '16px' }}>No logs available</p>
                  <p style={{ margin: '4px 0 0 0', fontSize: '14px' }}>
                    Start the bot to see activity logs here
                  </p>
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {logs.slice(0, 50).map((log) => {
                    const getLogIcon = (level: LogEntry['level']) => {
                      switch (level) {
                        case 'success': return <CheckCircle size={14} style={{ color: '#00D4AA' }} />
                        case 'error': return <XCircle size={14} style={{ color: '#EF4444' }} />
                        case 'warning': return <AlertCircle size={14} style={{ color: '#F59E0B' }} />
                        default: return <Info size={14} style={{ color: '#4F46E5' }} />
                      }
                    }

                    const getLogColor = (level: LogEntry['level']) => {
                      switch (level) {
                        case 'success': return '#00D4AA'
                        case 'error': return '#EF4444'
                        case 'warning': return '#F59E0B'
                        default: return '#9CA3AF'
                      }
                    }

                    return (
                      <div key={log.id} style={{
                        display: 'flex',
                        alignItems: 'flex-start',
                        gap: '12px',
                        padding: '12px',
                        backgroundColor: '#1A1F2E',
                        borderRadius: '8px',
                        border: '1px solid #2D3748'
                      }}>
                        <div style={{ marginTop: '2px' }}>
                          {getLogIcon(log.level)}
                        </div>
                        <div style={{ flex: 1, minWidth: 0 }}>
                          <div style={{ 
                            display: 'flex', 
                            justifyContent: 'space-between', 
                            alignItems: 'flex-start',
                            marginBottom: '4px'
                          }}>
                            <p style={{
                              margin: 0,
                              fontSize: '14px',
                              color: '#ffffff',
                              lineHeight: '1.4',
                              wordBreak: 'break-word'
                            }}>
                              {log.message}
                            </p>
                            <span style={{
                              fontSize: '12px',
                              color: '#6B7280',
                              marginLeft: '12px',
                              flexShrink: 0
                            }}>
                              {new Date(log.timestamp).toLocaleTimeString()}
                            </span>
                          </div>
                          {log.source && (
                            <div style={{
                              fontSize: '12px',
                              color: getLogColor(log.level),
                              fontWeight: '500'
                            }}>
                              {log.source}
                            </div>
                          )}
                        </div>
                      </div>
                    )
                  })}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Right Column - Portfolio & Stats */}
        <div>
          {/* Portfolio Assets */}
          <div style={cardStyle}>
            <h3 style={{ fontSize: '20px', fontWeight: '600', margin: '0 0 20px 0', color: '#ffffff' }}>
              Portfolio Assets
            </h3>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {portfolio.assets.map((asset) => (
                <div key={asset.symbol} style={{ 
                  display: 'flex', 
                  justifyContent: 'space-between', 
                  alignItems: 'center',
                  padding: '16px',
                  backgroundColor: '#0D1421',
                  borderRadius: '12px',
                  border: '1px solid #2D3748'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <div style={{ 
                      width: '40px', 
                      height: '40px', 
                      borderRadius: '50%', 
                      backgroundColor: '#2D3748',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '18px',
                      fontWeight: '700'
                    }}>
                      {asset.icon}
                    </div>
                    <div>
                      <p style={{ margin: 0, fontWeight: '600', color: '#ffffff' }}>{asset.symbol}</p>
                      <p style={{ margin: 0, fontSize: '14px', color: '#9CA3AF' }}>{asset.name}</p>
                    </div>
                  </div>
                  
                  <div style={{ textAlign: 'right' }}>
                    <p style={{ margin: 0, fontWeight: '600', color: '#ffffff' }}>
                      ${asset.value.toLocaleString()}
                    </p>
                    <p style={{ 
                      margin: 0, 
                      fontSize: '14px',
                      color: asset.change24h >= 0 ? '#00D4AA' : '#FF6B6B'
                    }}>
                      {asset.change24h >= 0 ? '+' : ''}{asset.change24h}%
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Quick Stats */}
          <div style={cardStyle}>
            <h3 style={{ fontSize: '20px', fontWeight: '600', margin: '0 0 20px 0', color: '#ffffff' }}>
              Quick Stats
            </h3>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Clock size={16} style={{ color: '#9CA3AF' }} />
                  <span style={{ color: '#9CA3AF' }}>Uptime</span>
                </div>
                <span style={{ color: '#ffffff', fontWeight: '600' }}>
                  {Math.floor(status.uptime / 3600)}h {Math.floor((status.uptime % 3600) / 60)}m
                </span>
              </div>
              
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Users size={16} style={{ color: '#9CA3AF' }} />
                  <span style={{ color: '#9CA3AF' }}>Active Exchanges</span>
                </div>
                <span style={{ color: '#ffffff', fontWeight: '600' }}>12</span>
              </div>
              
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <TrendingUp size={16} style={{ color: '#00D4AA' }} />
                  <span style={{ color: '#9CA3AF' }}>Total Profit</span>
                </div>
                <span style={{ color: '#00D4AA', fontWeight: '600' }}>
                  ${status.totalProfit.toFixed(2)}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Home
