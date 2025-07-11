import { BotStatus } from '../App'
import { Wifi, WifiOff, Activity, Clock } from 'lucide-react'

interface StatusBarProps {
  status: BotStatus
  isConnected: boolean
}

const StatusBar = ({ status, isConnected }: StatusBarProps) => {
  return (
    <div className="w-full px-6 py-2">
      <div className="flex flex-wrap items-center justify-between gap-4">
        {/* Connection Status */}
        <div className="flex items-center gap-2">
          {isConnected ? (
            <Wifi className="text-crypto-green" size={16} />
          ) : (
            <WifiOff className="text-crypto-red" size={16} />
          )}
          <span className={`font-medium text-sm ${isConnected ? 'text-crypto-green' : 'text-crypto-red'}`}>
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>

        {/* Bot Status */}
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${status.isRunning ? 'status-active' : 'status-inactive'}`} />
          <span className="font-medium text-sm text-white">
            {status.isRunning ? 'Running' : 'Stopped'}
          </span>
        </div>

        {/* Mode */}
        <div className="flex items-center gap-2">
          <Activity size={14} className="text-gray-400" />
          <span className={`px-2 py-1 rounded text-xs font-medium ${
            status.mode === 'simulation' 
              ? 'bg-crypto-blue text-white' 
              : 'bg-orange-500 text-white'
          }`}>
            {status.mode === 'simulation' ? 'SIMULATION' : 'LIVE'}
          </span>
        </div>

        {/* Safe Mode */}
        {status.safeMode && (
          <div className="flex items-center gap-2">
            <span className="px-2 py-1 bg-crypto-green text-white rounded text-xs font-medium">
              SAFE MODE
            </span>
          </div>
        )}

        {/* Uptime */}
        <div className="flex items-center gap-2 text-sm text-gray-300">
          <Clock size={14} />
          <span>
            {Math.floor(status.uptime / 3600)}h {Math.floor((status.uptime % 3600) / 60)}m
          </span>
        </div>
      </div>
    </div>
  )
}

export default StatusBar
