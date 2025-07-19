import { ArbitrageOpportunity, BotStatus, Portfolio, LogEntry, MonitoringStats } from '../App'
import { TrendingUp, Activity, DollarSign, Target, Shield, Play, Square, BarChart3, Clock, Users, ScrollText, AlertCircle, CheckCircle, Info, XCircle, Wifi, ArrowRightLeft, Coins, History } from 'lucide-react'

interface HomeProps {
  opportunities: ArbitrageOpportunity[]
  status: BotStatus
  portfolio: Portfolio
  logs: LogEntry[]
  monitoringStats: MonitoringStats
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
  logs,
  monitoringStats,
  onStart,
  onStop,
  onToggleMode,
  onToggleSafeMode,
  onExecuteTrade
}: HomeProps) => {
  // Simple handler functions that delegate to App component
  const handleStart = () => {
    console.log('Home: Start button clicked, calling onStart')
    onStart()
  }

  const handleStop = () => {
    console.log('Home: Stop button clicked, calling onStop')
    onStop()
  }

  const handleToggleSafeMode = () => {
    console.log('Home: Safe mode toggle clicked, calling onToggleSafeMode')
    onToggleSafeMode()
  }

  // Use status directly from App
  console.log('Home: Current status from App:', status)
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

  const successRate = monitoringStats.totalOpportunitiesFound > 0 ? 
    Math.round((monitoringStats.opportunitiesExecuted / monitoringStats.totalOpportunitiesFound) * 100) : 0

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

      {/* Monitoring Dashboard - Order matches backend print_dashboard */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', 
        gap: '20px',
        marginBottom: '32px'
      }}>
        {/* Uptime */}
        <div style={smallCardStyle}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <p style={{ color: '#9CA3AF', fontSize: '14px', margin: '0 0 4px 0' }}>Uptime</p>
              <p style={{ fontSize: '28px', fontWeight: '700', margin: 0, color: '#ffffff' }}>
                {typeof monitoringStats.uptime === 'string' ? monitoringStats.uptime : `${Math.floor(monitoringStats.uptime / 3600)}h ${Math.floor((monitoringStats.uptime % 3600) / 60)}m`}
              </p>
              <p style={{ fontSize: '14px', margin: '4px 0 0 0', color: '#9CA3AF' }}>
                Session duration
              </p>
            </div>
            <div style={{ backgroundColor: '#6366F120', borderRadius: '12px', padding: '12px', color: '#6366F1' }}>
              <Clock size={24} />
            </div>
          </div>
        </div>
        {/* Loop Count */}
        <div style={smallCardStyle}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <p style={{ color: '#9CA3AF', fontSize: '14px', margin: '0 0 4px 0' }}>Loops Completed</p>
              <p style={{ fontSize: '28px', fontWeight: '700', margin: 0, color: '#ffffff' }}>
                {monitoringStats.loopCount.toLocaleString()}
              </p>
            </div>
            <div style={{ backgroundColor: '#3B82F620', borderRadius: '12px', padding: '12px', color: '#3B82F6' }}>
              <Activity size={24} />
            </div>
          </div>
        </div>
        {/* Avg Execution Time */}
        <div style={smallCardStyle}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <p style={{ color: '#9CA3AF', fontSize: '14px', margin: '0 0 4px 0' }}>Avg Execution Time</p>
              <p style={{ fontSize: '28px', fontWeight: '700', margin: 0, color: '#ffffff' }}>
                {monitoringStats.avgExecutionTime?.toFixed(1) ?? '0.0'}s
              </p>
              <p style={{ fontSize: '14px', margin: '4px 0 0 0', color: '#9CA3AF' }}>
                Per loop
              </p>
            </div>
            <div style={{ backgroundColor: '#3B82F620', borderRadius: '12px', padding: '12px', color: '#3B82F6' }}>
              <Activity size={24} />
            </div>
          </div>
        </div>
        {/* Opportunities Found */}
        <div style={smallCardStyle}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <p style={{ color: '#9CA3AF', fontSize: '14px', margin: '0 0 4px 0' }}>Opportunities Found</p>
              <p style={{ fontSize: '28px', fontWeight: '700', margin: 0, color: '#ffffff' }}>
                {monitoringStats.totalOpportunitiesFound}
              </p>
              <p style={{ fontSize: '14px', margin: '4px 0 0 0', color: '#9CA3AF' }}>
                This session
              </p>
            </div>
            <div style={{ backgroundColor: '#8B5CF620', borderRadius: '12px', padding: '12px', color: '#8B5CF6' }}>
              <Target size={24} />
            </div>
          </div>
        </div>
        {/* Opportunities Executed */}
        <div style={smallCardStyle}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <p style={{ color: '#9CA3AF', fontSize: '14px', margin: '0 0 4px 0' }}>Opportunities Executed</p>
              <p style={{ fontSize: '28px', fontWeight: '700', margin: 0, color: '#ffffff' }}>
                {monitoringStats.opportunitiesExecuted}
              </p>
              <p style={{ fontSize: '14px', margin: '4px 0 0 0', color: '#00D4AA' }}>
                ${monitoringStats.totalProfitUsd?.toFixed(2) ?? '0.00'} profit
              </p>
            </div>
            <div style={{ backgroundColor: '#00D4AA20', borderRadius: '12px', padding: '12px', color: '#00D4AA' }}>
              <BarChart3 size={24} />
            </div>
          </div>
        </div>
        {/* Opportunities Per Hour */}
        <div style={smallCardStyle}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <p style={{ color: '#9CA3AF', fontSize: '14px', margin: '0 0 4px 0' }}>Opportunities/Hour</p>
              <p style={{ fontSize: '28px', fontWeight: '700', margin: 0, color: '#ffffff' }}>
                {monitoringStats.opportunitiesPerHour?.toFixed(1) ?? '0.0'}
              </p>
              <p style={{ fontSize: '14px', margin: '4px 0 0 0', color: '#9CA3AF' }}>
                Current rate
              </p>
            </div>
            <div style={{ backgroundColor: '#F59E0B20', borderRadius: '12px', padding: '12px', color: '#F59E0B' }}>
              <TrendingUp size={24} />
            </div>
          </div>
        </div>
        {/* Errors */}
        <div style={smallCardStyle}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <p style={{ color: '#9CA3AF', fontSize: '14px', margin: '0 0 4px 0' }}>Errors</p>
              <p style={{ fontSize: '28px', fontWeight: '700', margin: 0, color: monitoringStats.errors > 0 ? '#FF6B6B' : '#00D4AA' }}>
                {monitoringStats.errors}
              </p>
              <p style={{ fontSize: '14px', margin: '4px 0 0 0', color: '#9CA3AF' }}>
                Total errors
              </p>
            </div>
            <div style={{ backgroundColor: '#FF6B6B20', borderRadius: '12px', padding: '12px', color: '#FF6B6B' }}>
              <AlertCircle size={24} />
            </div>
          </div>
        </div>
        {/* Best Opportunity */}
        <div style={smallCardStyle}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ flex: 1 }}>
              <p style={{ color: '#9CA3AF', fontSize: '14px', margin: '0 0 4px 0' }}>Best Opportunity</p>
              {monitoringStats.bestOpportunity ? (
                <>
                  <p style={{ fontSize: '24px', fontWeight: '700', margin: 0, color: '#00D4AA' }}>
                    ${monitoringStats.bestOpportunity.profitUsd.toFixed(2)}
                  </p>
                  <p style={{ fontSize: '14px', margin: '4px 0 0 0', color: '#9CA3AF' }}>
                    {monitoringStats.bestOpportunity.pair} ({monitoringStats.bestOpportunity.profitPct.toFixed(2)}%)
                  </p>
                  <p style={{ fontSize: '12px', margin: '2px 0 0 0', color: '#6B7280' }}>
                    {monitoringStats.bestOpportunity.buyDex} → {monitoringStats.bestOpportunity.sellDex}
                  </p>
                </>
              ) : (
                <>
                  <p style={{ fontSize: '24px', fontWeight: '700', margin: 0, color: '#6B7280' }}>
                    No data
                  </p>
                  <p style={{ fontSize: '14px', margin: '4px 0 0 0', color: '#9CA3AF' }}>
                    Waiting for opportunities
                  </p>
                </>
              )}
            </div>
            <div style={{ backgroundColor: '#10B98120', borderRadius: '12px', padding: '12px', color: '#10B981' }}>
              <TrendingUp size={24} />
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
                  backgroundColor: status.mode === 'simulation' ? '#4F46E520' : '#F59E0B20',
                  color: status.mode === 'simulation' ? '#4F46E5' : '#F59E0B',
                  fontSize: '12px',
                  fontWeight: '600'
                }}>
                  {status.mode === 'simulation' ? 'SIMULATION' : 'LIVE TRADING'}
                </div>
                {/* Status indicator */}
                <div style={{ 
                  padding: '4px 12px', 
                  borderRadius: '20px', 
                  backgroundColor: status.isRunning ? '#00D4AA20' : '#FF6B6B20',
                  color: status.isRunning ? '#00D4AA' : '#FF6B6B',
                  fontSize: '12px',
                  fontWeight: '600'
                }}>
                  {status.isRunning ? 'ACTIVE' : 'INACTIVE'}
                </div>
              </div>
            </div>

            {/* Simulation mode indicator */}
            {status.mode === 'simulation' && (
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
                onClick={status.isRunning ? handleStop : handleStart}
                style={{
                  ...buttonStyle,
                  backgroundColor: status.isRunning ? '#FF6B6B' : '#00D4AA',
                  color: '#ffffff',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  justifyContent: 'center'
                }}
              >
                {status.isRunning ? <Square size={16} /> : <Play size={16} />}
                {status.isRunning ? 'Stop Bot' : 'Start Bot'}
              </button>
              
              {/* Mode Toggle Button */}
              <button
                onClick={onToggleMode}
                disabled={status.isRunning}
                style={{
                  ...buttonStyle,
                  backgroundColor: status.isRunning ? '#6B7280' : 
                    (status.mode === 'simulation' ? '#4F46E5' : '#F59E0B'),
                  color: '#ffffff',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  justifyContent: 'center',
                  opacity: status.isRunning ? 0.5 : 1,
                  cursor: status.isRunning ? 'not-allowed' : 'pointer'
                }}
              >
                <Activity size={16} />
                {status.mode === 'simulation' ? 'Simulation Mode' : 'Live Trading'}
              </button>
              
              <button
                onClick={handleToggleSafeMode}
                style={{
                  ...buttonStyle,
                  backgroundColor: status.safeMode ? '#10B981' : '#6B7280',
                  color: '#ffffff',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  justifyContent: 'center'
                }}
              >
                <Shield size={16} />
                {status.safeMode ? 'Safe Mode ON' : 'Safe Mode OFF'}
              </button>
            </div>
          </div>

          {/* Opportunities Table */}
          <div style={cardStyle}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <h3 style={{ fontSize: '20px', fontWeight: '600', margin: 0, color: '#ffffff' }}>
                {status.mode === 'simulation' ? 'Simulated' : 'Live'} Arbitrage Opportunities
              </h3>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                {/* Connection status indicator - simplified */}
                <div style={{ 
                  padding: '4px 12px', 
                  borderRadius: '20px', 
                  backgroundColor: '#00D4AA20',
                  color: '#00D4AA',
                  fontSize: '12px',
                  fontWeight: '600',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px'
                }}>
                  <Wifi size={12} />
                  ONLINE
                </div>
              </div>
            </div>

            {opportunities.length === 0 ? (
              <div style={{ 
                textAlign: 'center', 
                padding: '40px 20px',
                color: '#9CA3AF'
              }}>
                <BarChart3 size={48} style={{ margin: '0 auto 16px', opacity: 0.5 }} />
                <p style={{ margin: 0, fontSize: '16px' }}>No opportunities found</p>
                <p style={{ margin: '8px 0 0 0', fontSize: '14px' }}>
                  Scanning for {status.mode === 'simulation' ? 'simulated' : 'live'} arbitrage opportunities...
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
                      // Determine if execution is allowed - bot must be running
                      const canExecute = status.isRunning
                      
                      return (
                        <tr key={opportunity.id} style={{ borderBottom: '1px solid #2D3748' }}>
                          <td style={{ padding: '12px', fontWeight: '600', color: '#ffffff' }}>
                            {opportunity.pair}
                            {status.mode === 'simulation' && (
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
                                  ? 'Bot must be running to execute trades'
                                  : `Execute ${status.mode === 'simulation' ? 'simulated' : 'live'} trade`
                              }
                            >
                              {status.mode === 'simulation' ? 'Simulate' : 'Execute'}
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
          {/* Monitoring Dashboard */}
          <div style={cardStyle}>
            <h3 style={{ fontSize: '20px', fontWeight: '600', margin: '0 0 20px 0', color: '#ffffff' }}>
              Real-Time Monitoring
            </h3>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Activity size={16} style={{ color: '#9CA3AF' }} />
                  <span style={{ color: '#9CA3AF' }}>Bot Status</span>
                </div>
                <span style={{ 
                  color: status.isRunning ? '#00D4AA' : '#FF6B6B', 
                  fontWeight: '600',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px'
                }}>
                  <div style={{ 
                    width: '8px', 
                    height: '8px', 
                    borderRadius: '50%', 
                    backgroundColor: status.isRunning ? '#00D4AA' : '#FF6B6B' 
                  }} />
                  {status.isRunning ? 'Running' : 'Stopped'}
                </span>
              </div>
              
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Shield size={16} style={{ color: '#9CA3AF' }} />
                  <span style={{ color: '#9CA3AF' }}>Mode</span>
                </div>
                <span style={{ 
                  color: status.mode === 'simulation' ? '#4F46E5' : '#F59E0B', 
                  fontWeight: '600',
                  textTransform: 'capitalize'
                }}>
                  {status.mode}
                </span>
              </div>
              
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Target size={16} style={{ color: '#9CA3AF' }} />
                  <span style={{ color: '#9CA3AF' }}>Safe Mode</span>
                </div>
                <span style={{ 
                  color: status.safeMode ? '#00D4AA' : '#FF6B6B', 
                  fontWeight: '600'
                }}>
                  {status.safeMode ? 'ON' : 'OFF'}
                </span>
              </div>
              
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <BarChart3 size={16} style={{ color: '#9CA3AF' }} />
                  <span style={{ color: '#9CA3AF' }}>Errors</span>
                </div>
                <span style={{ 
                  color: monitoringStats.errors > 0 ? '#FF6B6B' : '#00D4AA', 
                  fontWeight: '600'
                }}>
                  {monitoringStats.errors}
                </span>
              </div>

              {monitoringStats.bestOpportunity && (
                <div style={{ 
                  padding: '12px',
                  backgroundColor: '#0D1421',
                  borderRadius: '8px',
                  border: '1px solid #2D3748',
                  marginTop: '8px'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                    <span style={{ color: '#9CA3AF', fontSize: '14px' }}>Best Opportunity</span>
                    <span style={{ color: '#00D4AA', fontSize: '12px' }}>
                      {new Date(monitoringStats.bestOpportunity.time).toLocaleTimeString()}
                    </span>
                  </div>
                  <div style={{ color: '#ffffff', fontWeight: '600', fontSize: '14px', marginBottom: '4px' }}>
                    {monitoringStats.bestOpportunity.pair}
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ color: '#9CA3AF', fontSize: '12px' }}>
                      {monitoringStats.bestOpportunity.buyDex} → {monitoringStats.bestOpportunity.sellDex}
                    </span>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{ color: '#00D4AA', fontSize: '12px', fontWeight: '600' }}>
                        +${monitoringStats.bestOpportunity.profitUsd.toFixed(2)}
                      </div>
                      <div style={{ color: '#9CA3AF', fontSize: '11px' }}>
                        {monitoringStats.bestOpportunity.profitPct.toFixed(2)}%
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

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
                  <span style={{ color: '#9CA3AF' }}>Session Start</span>
                </div>
                <span style={{ color: '#ffffff', fontWeight: '600' }}>
                  {new Date(monitoringStats.startTime).toLocaleTimeString()}
                </span>
              </div>
              
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Users size={16} style={{ color: '#9CA3AF' }} />
                  <span style={{ color: '#9CA3AF' }}>Current Opportunities</span>
                </div>
                <span style={{ color: '#ffffff', fontWeight: '600' }}>
                  {opportunities.length}
                </span>
              </div>
              
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <BarChart3 size={16} style={{ color: '#9CA3AF' }} />
                  <span style={{ color: '#9CA3AF' }}>Errors</span>
                </div>
                <span style={{ color: monitoringStats.errors > 0 ? '#FF6B6B' : '#ffffff', fontWeight: '600' }}>
                  {monitoringStats.errors}
                </span>
              </div>
              
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <TrendingUp size={16} style={{ color: '#00D4AA' }} />
                  <span style={{ color: '#9CA3AF' }}>Total Profit</span>
                </div>
                <span style={{ color: '#00D4AA', fontWeight: '600' }}>
                  ${monitoringStats.totalProfitUsd?.toFixed(2) ?? '0.00'}
                </span>
              </div>
            </div>
          </div>

          {/* Top DEX Routes */}
          <div style={cardStyle}>
            <h3 style={{ fontSize: '20px', fontWeight: '600', margin: '0 0 20px 0', color: '#ffffff' }}>
              Top DEX Routes
            </h3>
            
            {monitoringStats.topDexRoutes && monitoringStats.topDexRoutes.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {monitoringStats.topDexRoutes.map((route, index) => (
                  <div key={index} style={{ 
                    display: 'flex', 
                    justifyContent: 'space-between', 
                    alignItems: 'center',
                    padding: '12px',
                    backgroundColor: '#0D1421',
                    borderRadius: '8px',
                    border: '1px solid #2D3748'
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <ArrowRightLeft size={16} style={{ color: '#4F46E5' }} />
                      <span style={{ color: '#ffffff', fontSize: '14px' }}>{route.route}</span>
                    </div>
                    <span style={{ 
                      color: '#00D4AA', 
                      fontWeight: '600',
                      fontSize: '14px'
                    }}>
                      {route.count}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ 
                textAlign: 'center', 
                padding: '20px',
                color: '#9CA3AF'
              }}>
                <ArrowRightLeft size={32} style={{ margin: '0 auto 8px', opacity: 0.5 }} />
                <p style={{ margin: 0, fontSize: '14px' }}>No routes tracked yet</p>
              </div>
            )}
          </div>

          {/* Top Pairs */}
          <div style={cardStyle}>
            <h3 style={{ fontSize: '20px', fontWeight: '600', margin: '0 0 20px 0', color: '#ffffff' }}>
              Top Trading Pairs
            </h3>
            
            {monitoringStats.topPairs && monitoringStats.topPairs.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {monitoringStats.topPairs.map((pairData, index) => (
                  <div key={index} style={{ 
                    display: 'flex', 
                    justifyContent: 'space-between', 
                    alignItems: 'center',
                    padding: '12px',
                    backgroundColor: '#0D1421',
                    borderRadius: '8px',
                    border: '1px solid #2D3748'
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <Coins size={16} style={{ color: '#F59E0B' }} />
                      <span style={{ color: '#ffffff', fontSize: '14px', fontWeight: '500' }}>
                        {pairData.pair}
                      </span>
                    </div>
                    <span style={{ 
                      color: '#00D4AA', 
                      fontWeight: '600',
                      fontSize: '14px'
                    }}>
                      {pairData.count}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ 
                textAlign: 'center', 
                padding: '20px',
                color: '#9CA3AF'
              }}>
                <Coins size={32} style={{ margin: '0 auto 8px', opacity: 0.5 }} />
                <p style={{ margin: 0, fontSize: '14px' }}>No pairs tracked yet</p>
              </div>
            )}
          </div>

          {/* Recent Opportunities */}
          <div style={cardStyle}>
            <h3 style={{ fontSize: '20px', fontWeight: '600', margin: '0 0 20px 0', color: '#ffffff' }}>
              Recent Opportunities
            </h3>
            
            {monitoringStats.recentOpportunities && monitoringStats.recentOpportunities.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {monitoringStats.recentOpportunities.map((opp, index) => (
                  <div key={index} style={{ 
                    padding: '12px',
                    backgroundColor: '#0D1421',
                    borderRadius: '8px',
                    border: '1px solid #2D3748'
                  }}>
                    <div style={{ 
                      display: 'flex', 
                      justifyContent: 'space-between', 
                      alignItems: 'flex-start',
                      marginBottom: '6px'
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <History size={14} style={{ color: '#8B5CF6' }} />
                        <span style={{ color: '#ffffff', fontSize: '14px', fontWeight: '500' }}>
                          {opp.pair}
                        </span>
                      </div>
                      <span style={{ color: '#6B7280', fontSize: '12px' }}>
                        {opp.time}
                      </span>
                    </div>
                    <div style={{ 
                      fontSize: '12px', 
                      color: '#9CA3AF',
                      marginBottom: '4px'
                    }}>
                      {opp.buyDex} → {opp.sellDex}
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ 
                        color: '#00D4AA', 
                        fontSize: '12px',
                        fontWeight: '600'
                      }}>
                        ${opp.profitUsd.toFixed(2)}
                      </span>
                      <span style={{ 
                        color: '#00D4AA', 
                        fontSize: '12px',
                        fontWeight: '600'
                      }}>
                        {opp.profitPct.toFixed(2)}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ 
                textAlign: 'center', 
                padding: '20px',
                color: '#9CA3AF'
              }}>
                <History size={32} style={{ margin: '0 auto 8px', opacity: 0.5 }} />
                <p style={{ margin: 0, fontSize: '14px' }}>No recent opportunities</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Home
