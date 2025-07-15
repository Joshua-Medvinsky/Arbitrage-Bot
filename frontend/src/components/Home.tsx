import { ArbitrageOpportunity, BotStatus, Portfolio, LogEntry } from '../App'
import { TrendingUp, Activity, DollarSign, Target, Shield, Play, Square, BarChart3, Clock, Users, ScrollText, AlertCircle, CheckCircle, Info, XCircle, Wifi, WifiOff } from 'lucide-react'
import { useState, useEffect } from 'react'
import { getBotStatus, startBotLocal, stopBotLocal, toggleSafeMode, type LocalBotState } from '../utils/botControl'

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
  const [isOnline, setIsOnline] = useState(navigator.onLine)

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

  // Sync localBotState with App's status prop changes (especially mode changes)
  useEffect(() => {
    if (localBotState && status) {
      // Update localBotState when App's status changes, especially mode changes
      const updatedState = {
        ...localBotState,
        mode: status.mode, // Sync mode from App
        safeMode: status.safeMode, // Sync safe mode from App
        // Keep local running state and session data unchanged
      }
      setLocalBotState(updatedState)
      console.log('Synced localBotState with App status:', updatedState)
    }
  }, [status.mode, status.safeMode]) // Only sync when mode or safeMode changes

  // Monitor internet connectivity
  useEffect(() => {
    const handleOnline = () => setIsOnline(true)
    const handleOffline = () => setIsOnline(false)

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
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
    if (localBotState && !isOnline && localBotState.isRunning) {
      // Internet connection lost while bot was running - stop the bot for both modes
      console.log('Internet connection lost - stopping bot automatically (both simulation and live modes require real market data)')
      const stopBotDueToConnectionLoss = async () => {
        try {
          // Stop the bot locally first to update UI immediately
          const updatedState = { ...localBotState, isRunning: false }
          setLocalBotState(updatedState)
          
          // Try to stop the bot via Tauri if possible
          try {
            await stopBotLocal()
            console.log('Bot successfully stopped due to internet connection loss')
          } catch (taruiError) {
            console.warn('Could not stop bot via Tauri, but local state updated:', taruiError)
          }
        } catch (error) {
          console.error('Failed to handle internet connection loss:', error)
        }
      }
      stopBotDueToConnectionLoss()
    }
  }, [isOnline, localBotState?.mode, localBotState?.isRunning, localBotState])

  // Update local state when connection status changes (for re-rendering)
  useEffect(() => {
    // This effect is just to trigger re-renders when internet connectivity changes
    // The actual logic is handled in the component functions
  }, [isOnline, localBotState?.mode])

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
      
      // Both simulation and live modes require internet connection for real market data
      if (!isOnline) {
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
    
    // Both simulation and live modes require internet connection for real market data
    return isOnline
  })()

  // Handle bot start with mode awareness
  const handleStart = async () => {
    if (!localBotState) return
    
    if (!isOnline) {
      // Both modes require internet connection for real market data
      console.warn('Cannot start bot without internet connection - both simulation and live modes require real market data')
      return
    }
    
    if (localBotState.mode === 'simulation') {
      // Simulation mode: use local control (real data, no actual trades)
      const result = await startBotLocal()
      if (result.success) {
        const updatedState = { ...localBotState, isRunning: true, lastStartTime: Date.now() }
        setLocalBotState(updatedState)
      }
    } else if (localBotState.mode === 'live') {
      // Live mode: use server control when online, but also update local state optimistically
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
    } else if (isOnline) {
      // Live mode: use server control when online, but also update local state optimistically
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
      // When offline: force stop locally for both modes
      const updatedState = { ...localBotState, isRunning: false }
      setLocalBotState(updatedState)
    }
  }

  // Handle safe mode toggle with mode awareness
  const handleToggleSafeMode = async () => {
    if (!localBotState) return
    
    if (!isOnline) {
      // When offline: always use local control
      const result = await toggleSafeMode()
      if (result.success) {
        const updatedState = { ...localBotState, safeMode: result.newSafeMode }
        setLocalBotState(updatedState)
      }
    } else {
      // When online: use local control first, then notify server
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

            {/* Connection status warning for both modes */}
            {!isOnline && (
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
                    'Internet connection lost - bot automatically stopped. Both simulation and live modes require real market data.' :
                    'Internet connection required. Both simulation and live modes need real market data to operate.'
                  }
                </span>
              </div>
            )}

            {/* Simulation mode indicator - shown when online */}
            {effectiveBotStatus.mode === 'simulation' && isOnline && (
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
                  Simulation mode: Uses real market data but no actual trades executed. Safe testing environment.
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
              
              {/* Mode Toggle Button */}
              <button
                onClick={onToggleMode}
                disabled={effectiveBotStatus.isRunning}
                style={{
                  ...buttonStyle,
                  backgroundColor: effectiveBotStatus.isRunning ? '#6B7280' : 
                    (effectiveBotStatus.mode === 'simulation' ? '#4F46E5' : '#F59E0B'),
                  color: '#ffffff',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  justifyContent: 'center',
                  opacity: effectiveBotStatus.isRunning ? 0.5 : 1,
                  cursor: effectiveBotStatus.isRunning ? 'not-allowed' : 'pointer'
                }}
              >
                <Activity size={16} />
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
                {/* Internet connection status */}
                <div style={{ 
                  padding: '4px 12px', 
                  borderRadius: '20px', 
                  backgroundColor: isOnline ? '#00D4AA20' : '#FF6B6B20',
                  color: isOnline ? '#00D4AA' : '#FF6B6B',
                  fontSize: '12px',
                  fontWeight: '600',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px'
                }}>
                  {isOnline ? <Wifi size={12} /> : <WifiOff size={12} />}
                  {isOnline ? 'ONLINE' : 'OFFLINE'}
                </div>
              </div>
            </div>

            {/* Mode-specific messaging */}
            {!isOnline && (
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
                  Internet connection required. Both simulation and live modes need real market data to function.
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
                  {isOnline 
                    ? `Scanning for real ${effectiveBotStatus.mode === 'simulation' ? 'market data (simulation mode)' : 'arbitrage opportunities (live mode)'}...`
                    : 'Internet connection required for both simulation and live modes to access real market data'
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
                      const canExecute = effectiveBotStatus.isRunning && isOnline  // Both modes need internet + bot running
                      
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
                                  ? !isOnline 
                                    ? 'Requires internet connection for real market data'
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
