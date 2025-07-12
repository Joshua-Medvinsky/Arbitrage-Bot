import { ArbitrageOpportunity, BotStatus, Portfolio, LogEntry } from '../App'
import { TrendingUp, Activity, DollarSign, Target, Shield, Play, Square, BarChart3, Clock, Users, Zap, ScrollText, AlertCircle, CheckCircle, Info, XCircle } from 'lucide-react'

interface HomeProps {
  opportunities: ArbitrageOpportunity[]
  status: BotStatus
  portfolio: Portfolio
  isConnected: boolean
  logs: LogEntry[]
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
  onStart,
  onStop,
  onToggleMode,
  onToggleSafeMode,
  onExecuteTrade
}: HomeProps) => {
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

        {/* Active Opportunities */}
        <div style={smallCardStyle}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <p style={{ color: '#9CA3AF', fontSize: '14px', margin: '0 0 4px 0' }}>Active Opportunities</p>
              <p style={{ fontSize: '28px', fontWeight: '700', margin: 0, color: '#ffffff' }}>
                {opportunities.length}
              </p>
              <p style={{ fontSize: '14px', margin: '4px 0 0 0', color: '#9CA3AF' }}>
                Avg profit: 2.3%
              </p>
            </div>
            <div style={{ 
              backgroundColor: '#10B98120', 
              borderRadius: '12px', 
              padding: '12px',
              color: '#10B981'
            }}>
              <Zap size={24} />
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
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
              <button
                onClick={status.isRunning ? onStop : onStart}
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
              
              <button
                onClick={onToggleMode}
                style={{
                  ...buttonStyle,
                  backgroundColor: status.mode === 'simulation' ? '#4F46E5' : '#F59E0B',
                  color: '#ffffff'
                }}
              >
                {status.mode === 'simulation' ? 'Simulation Mode' : 'Live Trading'}
              </button>
              
              <button
                onClick={onToggleSafeMode}
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
                Live Arbitrage Opportunities
              </h3>
              <div style={{ 
                padding: '4px 12px', 
                borderRadius: '20px', 
                backgroundColor: isConnected ? '#00D4AA20' : '#FF6B6B20',
                color: isConnected ? '#00D4AA' : '#FF6B6B',
                fontSize: '12px',
                fontWeight: '600'
              }}>
                {isConnected ? 'CONNECTED' : 'DISCONNECTED'}
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
                  {isConnected ? 'Scanning for arbitrage opportunities...' : 'Please check your connection'}
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
                    {opportunities.slice(0, 10).map((opportunity) => (
                      <tr key={opportunity.id} style={{ borderBottom: '1px solid #2D3748' }}>
                        <td style={{ padding: '12px', fontWeight: '600', color: '#ffffff' }}>{opportunity.pair}</td>
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
                            disabled={!isConnected || !status.isRunning}
                            style={{
                              padding: '6px 12px',
                              borderRadius: '6px',
                              border: 'none',
                              backgroundColor: isConnected && status.isRunning ? '#00D4AA' : '#6B7280',
                              color: '#ffffff',
                              fontSize: '12px',
                              fontWeight: '600',
                              cursor: isConnected && status.isRunning ? 'pointer' : 'not-allowed',
                              opacity: isConnected && status.isRunning ? 1 : 0.5
                            }}
                          >
                            Execute
                          </button>
                        </td>
                      </tr>
                    ))}
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
