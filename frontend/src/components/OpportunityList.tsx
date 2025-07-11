import { ArbitrageOpportunity } from '../App'
import { ExternalLink, TrendingUp, DollarSign } from 'lucide-react'

interface OpportunityListProps {
  opportunities: ArbitrageOpportunity[]
  onExecuteTrade: (opportunity: ArbitrageOpportunity) => void
  canExecute: boolean
}

const OpportunityList = ({ opportunities, onExecuteTrade, canExecute }: OpportunityListProps) => {
  const sortedOpportunities = opportunities
    .sort((a, b) => b.profitPct - a.profitPct)
    .slice(0, 10) // Show top 10 opportunities

  return (
    <div className="bg-crypto-gray p-6 rounded-lg">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-lg font-semibold">Live Arbitrage Opportunities</h3>
        <span className="text-sm text-gray-400">
          {opportunities.length} opportunities found
        </span>
      </div>

      {sortedOpportunities.length === 0 ? (
        <div className="text-center py-8 text-gray-400">
          <TrendingUp size={48} className="mx-auto mb-4 opacity-50" />
          <p>No arbitrage opportunities found</p>
          <p className="text-sm">The bot is scanning for profitable trades...</p>
        </div>
      ) : (
        <div className="space-y-3">
          {sortedOpportunities.map((opportunity) => (
            <div 
              key={opportunity.id} 
              className="bg-crypto-dark p-4 rounded-lg border border-gray-600 hover:border-crypto-blue transition-colors"
            >
              <div className="flex justify-between items-start mb-3">
                <div>
                  <h4 className="font-semibold text-lg">{opportunity.pair}</h4>
                  <div className="flex items-center gap-2 text-sm text-gray-400">
                    <span>Buy: {opportunity.buyDex}</span>
                    <ExternalLink size={12} />
                    <span>Sell: {opportunity.sellDex}</span>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-crypto-green">
                    {opportunity.profitPct.toFixed(2)}%
                  </div>
                  <div className="text-sm text-gray-400">
                    ${opportunity.profitUsd.toFixed(2)} profit
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 mb-4">
                <div className="text-sm">
                  <span className="text-gray-400">Buy Price:</span>
                  <span className="ml-2 font-mono">{opportunity.buyPrice.toFixed(6)}</span>
                </div>
                <div className="text-sm">
                  <span className="text-gray-400">Sell Price:</span>
                  <span className="ml-2 font-mono">{opportunity.sellPrice.toFixed(6)}</span>
                </div>
                <div className="text-sm">
                  <span className="text-gray-400">Volume:</span>
                  <span className="ml-2">${opportunity.volume.toLocaleString()}</span>
                </div>
                <div className="text-sm">
                  <span className="text-gray-400">Updated:</span>
                  <span className="ml-2">
                    {new Date(opportunity.timestamp).toLocaleTimeString()}
                  </span>
                </div>
              </div>

              <div className="flex gap-2">
                <button
                  onClick={() => onExecuteTrade(opportunity)}
                  disabled={!canExecute}
                  className={`flex-1 flex items-center justify-center gap-2 py-2 px-4 rounded-lg font-medium transition-colors ${
                    canExecute
                      ? 'bg-crypto-green hover:bg-green-600 text-white'
                      : 'bg-gray-600 text-gray-400 cursor-not-allowed'
                  }`}
                >
                  <DollarSign size={16} />
                  Execute Trade
                </button>
                
                <button className="px-4 py-2 bg-crypto-blue hover:bg-blue-600 text-white rounded-lg transition-colors">
                  <ExternalLink size={16} />
                </button>
              </div>

              {!canExecute && (
                <p className="text-xs text-gray-400 mt-2 text-center">
                  Bot must be running and connected to execute trades
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default OpportunityList
