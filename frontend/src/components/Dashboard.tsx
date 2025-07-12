import { ArbitrageOpportunity, BotStatus } from '../App'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

interface DashboardProps {
  opportunities: ArbitrageOpportunity[]
  status: BotStatus
}

const Dashboard = ({ opportunities, status }: DashboardProps) => {
  // Generate mock profit data for the chart
  const profitData = Array.from({ length: 20 }, (_, i) => ({
    time: new Date(Date.now() - (19 - i) * 5 * 60 * 1000).toLocaleTimeString(),
    profit: Math.random() * 100 - 50
  }))

  const bestOpportunities = opportunities
    .sort((a, b) => b.profitPct - a.profitPct)
    .slice(0, 5)

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-crypto-gray p-4 rounded-lg">
          <h3 className="text-sm text-gray-400 mb-1">Total Profit</h3>
          <p className={`text-2xl font-bold ${status.totalProfit >= 0 ? 'profit-positive' : 'profit-negative'}`}>
            ${status.totalProfit.toFixed(2)}
          </p>
        </div>
        
        <div className="bg-crypto-gray p-4 rounded-lg">
          <h3 className="text-sm text-gray-400 mb-1">Total Trades</h3>
          <p className="text-2xl font-bold text-white">{status.totalTrades}</p>
        </div>
        
        <div className="bg-crypto-gray p-4 rounded-lg">
          <h3 className="text-sm text-gray-400 mb-1">Opportunities</h3>
          <p className="text-2xl font-bold text-crypto-blue">{opportunities.length}</p>
        </div>
        
        <div className="bg-crypto-gray p-4 rounded-lg">
          <h3 className="text-sm text-gray-400 mb-1">Best Profit</h3>
          <p className="text-2xl font-bold text-crypto-green">
            {bestOpportunities.length > 0 ? `${bestOpportunities[0].profitPct.toFixed(2)}%` : '0%'}
          </p>
        </div>
      </div>

      {/* Profit Chart */}
      <div className="bg-crypto-gray p-6 rounded-lg">
        <h3 className="text-lg font-semibold mb-4">Profit Over Time</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={profitData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="time" stroke="#9CA3AF" />
            <YAxis stroke="#9CA3AF" />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#2D3748', 
                border: '1px solid #4A5568',
                borderRadius: '8px'
              }}
            />
            <Line 
              type="monotone" 
              dataKey="profit" 
              stroke="#00D4AA" 
              strokeWidth={2}
              dot={{ fill: '#00D4AA', strokeWidth: 2, r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Top Opportunities */}
      <div className="bg-crypto-gray p-6 rounded-lg">
        <h3 className="text-lg font-semibold mb-4">Top Opportunities</h3>
        <div className="space-y-3">
          {bestOpportunities.map((opp) => (
            <div key={opp.id} className="flex justify-between items-center p-3 bg-crypto-dark rounded-lg">
              <div>
                <span className="font-medium">{opp.pair}</span>
                <span className="text-sm text-gray-400 ml-2">
                  {opp.buyDex} → {opp.sellDex}
                </span>
              </div>
              <div className="text-right">
                <div className="text-crypto-green font-bold">
                  {opp.profitPct.toFixed(2)}%
                </div>
                <div className="text-sm text-gray-400">
                  ${opp.profitUsd.toFixed(2)}
                </div>
              </div>
            </div>
          ))}
          {bestOpportunities.length === 0 && (
            <p className="text-gray-400 text-center py-4">No opportunities found</p>
          )}
        </div>
      </div>
    </div>
  )
}

export default Dashboard
