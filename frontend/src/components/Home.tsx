import { ArbitrageOpportunity, BotStatus } from '../App'
import Dashboard from './Dashboard'
import Controls from './Controls'
import OpportunityList from './OpportunityList'

interface HomeProps {
  opportunities: ArbitrageOpportunity[]
  status: BotStatus
  isConnected: boolean
  onStart: () => void
  onStop: () => void
  onToggleMode: () => void
  onToggleSafeMode: () => void
  onExecuteTrade: (opportunity: ArbitrageOpportunity) => void
}

const Home = ({
  opportunities,
  status,
  isConnected,
  onStart,
  onStop,
  onToggleMode,
  onToggleSafeMode,
  onExecuteTrade
}: HomeProps) => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-white">Dashboard</h2>
        <p className="text-gray-400 mt-1">Monitor arbitrage opportunities and control your trading bot</p>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Dashboard - Takes up 2 columns on large screens */}
        <div className="lg:col-span-2">
          <Dashboard 
            opportunities={opportunities}
            status={status}
          />
        </div>
        
        {/* Controls - Takes up 1 column on large screens */}
        <div>
          <Controls
            status={status}
            onStart={onStart}
            onStop={onStop}
            onToggleMode={onToggleMode}
            onToggleSafeMode={onToggleSafeMode}
            isConnected={isConnected}
          />
        </div>
      </div>

      {/* Opportunities List */}
      <OpportunityList
        opportunities={opportunities}
        onExecuteTrade={onExecuteTrade}
        canExecute={isConnected && status.isRunning}
      />
    </div>
  )
}

export default Home
