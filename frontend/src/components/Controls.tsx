import { BotStatus } from '../App'
import { Play, Pause, Shield, AlertTriangle, Zap } from 'lucide-react'

interface ControlsProps {
  status: BotStatus
  onStart: () => void
  onStop: () => void
  onToggleMode: () => void
  onToggleSafeMode: () => void
  isConnected: boolean
}

const Controls = ({ 
  status, 
  onStart, 
  onStop, 
  onToggleMode, 
  onToggleSafeMode, 
  isConnected 
}: ControlsProps) => {
  return (
    <div className="bg-crypto-gray p-6 rounded-lg space-y-4">
      <h3 className="text-lg font-semibold mb-4">Bot Controls</h3>
      
      {/* Start/Stop Button */}
      <div className="space-y-2">
        <button
          onClick={status.isRunning ? onStop : onStart}
          disabled={!isConnected}
          className={`w-full flex items-center justify-center gap-2 py-3 px-4 rounded-lg font-medium transition-colors ${
            status.isRunning
              ? 'bg-crypto-red hover:bg-red-600 text-white'
              : 'bg-crypto-green hover:bg-green-600 text-white'
          } ${!isConnected ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          {status.isRunning ? <Pause size={20} /> : <Play size={20} />}
          {status.isRunning ? 'Stop Bot' : 'Start Bot'}
        </button>
        <p className="text-xs text-gray-400 text-center">
          {!isConnected && 'WebSocket disconnected'}
        </p>
      </div>

      {/* Mode Toggle */}
      <div className="space-y-2">
        <label className="block text-sm font-medium">Trading Mode</label>
        <button
          onClick={onToggleMode}
          disabled={!isConnected || status.isRunning}
          className={`w-full flex items-center justify-center gap-2 py-2 px-4 rounded-lg transition-colors ${
            status.mode === 'simulation'
              ? 'bg-crypto-blue hover:bg-blue-600 text-white'
              : 'bg-orange-500 hover:bg-orange-600 text-white'
          } ${(!isConnected || status.isRunning) ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          <Zap size={16} />
          {status.mode === 'simulation' ? 'Simulation Mode' : 'Live Trading'}
        </button>
        <p className="text-xs text-gray-400">
          {status.mode === 'simulation' 
            ? 'No real transactions will be executed'
            : 'Real money will be used for trades'
          }
        </p>
      </div>

      {/* Safe Mode Toggle */}
      <div className="space-y-2">
        <label className="block text-sm font-medium">Safety Settings</label>
        <button
          onClick={onToggleSafeMode}
          disabled={!isConnected}
          className={`w-full flex items-center justify-center gap-2 py-2 px-4 rounded-lg transition-colors ${
            status.safeMode
              ? 'bg-crypto-green hover:bg-green-600 text-white'
              : 'bg-crypto-red hover:bg-red-600 text-white'
          } ${!isConnected ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          {status.safeMode ? <Shield size={16} /> : <AlertTriangle size={16} />}
          {status.safeMode ? 'Safe Mode ON' : 'Safe Mode OFF'}
        </button>
        <p className="text-xs text-gray-400">
          {status.safeMode 
            ? 'Small amounts, safe tokens only'
            : 'Full trading capabilities enabled'
          }
        </p>
      </div>

      {/* Status Information */}
      <div className="border-t border-gray-600 pt-4 space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-gray-400">Uptime:</span>
          <span>{Math.floor(status.uptime / 60)}m {status.uptime % 60}s</span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-gray-400">Connection:</span>
          <span className={isConnected ? 'text-crypto-green' : 'text-crypto-red'}>
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-gray-400">Status:</span>
          <span className={status.isRunning ? 'text-crypto-green' : 'text-gray-400'}>
            {status.isRunning ? 'Running' : 'Stopped'}
          </span>
        </div>
      </div>
    </div>
  )
}

export default Controls
