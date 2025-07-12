import { BotStatus } from '../App'
import { 
  Wifi, 
  WifiOff, 
  Activity, 
  Clock, 
  Play, 
  Square, 
  Shield, 
  Zap,
  CheckCircle,
  AlertCircle
} from 'lucide-react'

interface StatusBarProps {
  status: BotStatus
  isConnected: boolean
}

const StatusBar = ({ status, isConnected }: StatusBarProps) => {
  const containerStyle = {
    width: '100%',
    padding: '16px 32px', // Consistent edge padding
    backgroundColor: '#1A1F2E',
    borderTop: '1px solid #2D3748',
    display: 'flex',
    alignItems: 'center',
    flexWrap: 'wrap' as const,
    gap: '16px', // Vertical and horizontal spacing between wrapped rows
    minHeight: '60px',
    overflow: 'hidden',
    justifyContent: 'space-between', // Even distribution
    boxSizing: 'border-box' as const
  }

  // Wrapper style for sections with consistent spacing
  const sectionWrapperStyle = {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    flexShrink: 0 // Prevent shrinking
  }

  const statusItemStyle = {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    padding: '8px 12px',
    backgroundColor: '#0D1421',
    borderRadius: '8px',
    border: '1px solid #2D3748'
  }

  const badgeStyle = (color: string, bgColor: string) => ({
    padding: '4px 8px',
    borderRadius: '6px',
    fontSize: '11px',
    fontWeight: '600' as const,
    color: '#ffffff',
    backgroundColor: bgColor,
    border: `1px solid ${color}30`,
    textTransform: 'uppercase' as const,
    letterSpacing: '0.5px'
  })

  return (
    <div style={containerStyle}>
      {/* Left Section - Connection & Bot Status */}
      <div style={sectionWrapperStyle}>
        {/* Connection Status */}
        <div style={statusItemStyle}>
          <div style={{ 
            backgroundColor: isConnected ? '#00D4AA20' : '#EF444420', 
            borderRadius: '6px', 
            padding: '4px',
            color: isConnected ? '#00D4AA' : '#EF4444'
          }}>
            {isConnected ? <Wifi size={14} /> : <WifiOff size={14} />}
          </div>
          <span style={{ 
            fontSize: '13px', 
            fontWeight: '600', 
            color: isConnected ? '#00D4AA' : '#EF4444' 
          }}>
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>

        {/* Bot Status */}
        <div style={statusItemStyle}>
          <div style={{ 
            backgroundColor: status.isRunning ? '#00D4AA20' : '#6B728020', 
            borderRadius: '6px', 
            padding: '4px',
            color: status.isRunning ? '#00D4AA' : '#6B7280'
          }}>
            {status.isRunning ? <Play size={14} /> : <Square size={14} />}
          </div>
          <span style={{ 
            fontSize: '13px', 
            fontWeight: '600', 
            color: status.isRunning ? '#00D4AA' : '#6B7280' 
          }}>
            {status.isRunning ? 'Active' : 'Inactive'}
          </span>
          <div style={{ 
            width: '6px', 
            height: '6px', 
            borderRadius: '50%', 
            backgroundColor: status.isRunning ? '#00D4AA' : '#6B7280',
            animation: status.isRunning ? 'pulse 2s infinite' : 'none'
          }} />
        </div>
      </div>

      {/* Center Section - Mode & Safety */}
      <div style={sectionWrapperStyle}>
        {/* Trading Mode */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{ 
            backgroundColor: status.mode === 'simulation' ? '#4F46E520' : '#F59E0B20', 
            borderRadius: '6px', 
            padding: '4px',
            color: status.mode === 'simulation' ? '#4F46E5' : '#F59E0B'
          }}>
            <Activity size={12} />
          </div>
          <span style={badgeStyle(
            status.mode === 'simulation' ? '#4F46E5' : '#F59E0B',
            status.mode === 'simulation' ? '#4F46E5' : '#F59E0B'
          )}>
            {status.mode === 'simulation' ? 'Simulation' : 'Live'}
          </span>
        </div>

        {/* Safe Mode */}
        {status.safeMode && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{ 
              backgroundColor: '#10B98120', 
              borderRadius: '6px', 
              padding: '4px',
              color: '#10B981'
            }}>
              <Shield size={12} />
            </div>
            <span style={badgeStyle('#10B981', '#10B981')}>
              Safe Mode
            </span>
          </div>
        )}
      </div>

      {/* Right Section - Performance Metrics */}
      <div style={sectionWrapperStyle}>
        {/* Uptime */}
        <div style={statusItemStyle}>
          <div style={{ 
            backgroundColor: '#6366F120', 
            borderRadius: '6px', 
            padding: '4px',
            color: '#6366F1'
          }}>
            <Clock size={14} />
          </div>
          <span style={{ fontSize: '13px', fontWeight: '600', color: '#9CA3AF' }}>
            Uptime:
          </span>
          <span style={{ fontSize: '13px', fontWeight: '700', color: '#ffffff' }}>
            {Math.floor(status.uptime / 3600)}h {Math.floor((status.uptime % 3600) / 60)}m
          </span>
        </div>

        {/* Total Profit */}
        <div style={statusItemStyle}>
          <div style={{ 
            backgroundColor: status.totalProfit >= 0 ? '#00D4AA20' : '#EF444420', 
            borderRadius: '6px', 
            padding: '4px',
            color: status.totalProfit >= 0 ? '#00D4AA' : '#EF4444'
          }}>
            {status.totalProfit >= 0 ? <CheckCircle size={14} /> : <AlertCircle size={14} />}
          </div>
          <span style={{ fontSize: '13px', fontWeight: '600', color: '#9CA3AF' }}>
            P&L:
          </span>
          <span style={{ 
            fontSize: '13px', 
            fontWeight: '700', 
            color: status.totalProfit >= 0 ? '#00D4AA' : '#EF4444' 
          }}>
            ${status.totalProfit >= 0 ? '+' : ''}${status.totalProfit.toFixed(2)}
          </span>
        </div>

        {/* Total Trades */}
        <div style={statusItemStyle}>
          <div style={{ 
            backgroundColor: '#8B5CF620', 
            borderRadius: '6px', 
            padding: '4px',
            color: '#8B5CF6'
          }}>
            <Zap size={14} />
          </div>
          <span style={{ fontSize: '13px', fontWeight: '600', color: '#9CA3AF' }}>
            Trades:
          </span>
          <span style={{ fontSize: '13px', fontWeight: '700', color: '#ffffff' }}>
            {status.totalTrades.toLocaleString()}
          </span>
        </div>
      </div>
    </div>
  )
}

export default StatusBar
