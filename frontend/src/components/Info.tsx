const Info = () => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-white">Information & Help</h2>
        <p className="text-gray-400 mt-1">Learn how to use the Arbitrage Bot effectively and safely</p>
      </div>

      {/* Quick Start Guide */}
      <div className="bg-crypto-gray p-6 rounded-lg">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
          <svg className="w-5 h-5 mr-2 text-crypto-green" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          Quick Start Guide
        </h3>
        <div className="space-y-4">
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0 w-6 h-6 bg-crypto-blue rounded-full flex items-center justify-center text-xs font-bold">1</div>
            <div>
              <h4 className="font-medium text-white">Configure Settings</h4>
              <p className="text-gray-400 text-sm">Go to Settings tab and ensure Simulation Mode is ON for safe testing</p>
            </div>
          </div>
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0 w-6 h-6 bg-crypto-blue rounded-full flex items-center justify-center text-xs font-bold">2</div>
            <div>
              <h4 className="font-medium text-white">Start the Bot</h4>
              <p className="text-gray-400 text-sm">Return to Home tab and click "Start Bot" to begin monitoring</p>
            </div>
          </div>
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0 w-6 h-6 bg-crypto-blue rounded-full flex items-center justify-center text-xs font-bold">3</div>
            <div>
              <h4 className="font-medium text-white">Monitor Opportunities</h4>
              <p className="text-gray-400 text-sm">Watch for arbitrage opportunities and review performance metrics</p>
            </div>
          </div>
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0 w-6 h-6 bg-crypto-blue rounded-full flex items-center justify-center text-xs font-bold">4</div>
            <div>
              <h4 className="font-medium text-white">Go Live (Advanced)</h4>
              <p className="text-gray-400 text-sm">After testing, disable Simulation Mode for real trading</p>
            </div>
          </div>
        </div>
      </div>

      {/* Key Features */}
      <div className="bg-crypto-gray p-6 rounded-lg">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
          <svg className="w-5 h-5 mr-2 text-crypto-blue" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
          </svg>
          Key Features
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 bg-crypto-dark rounded-lg">
            <h4 className="font-medium text-crypto-green mb-2">Multi-DEX Monitoring</h4>
            <p className="text-gray-400 text-sm">Real-time price monitoring across Uniswap V3, SushiSwap, and Aerodrome</p>
          </div>
          <div className="p-4 bg-crypto-dark rounded-lg">
            <h4 className="font-medium text-crypto-green mb-2">Safe Mode</h4>
            <p className="text-gray-400 text-sm">Built-in protections with small position sizes and major tokens only</p>
          </div>
          <div className="p-4 bg-crypto-dark rounded-lg">
            <h4 className="font-medium text-crypto-green mb-2">Flash Loan Support</h4>
            <p className="text-gray-400 text-sm">Capital-efficient arbitrage using Aave flash loans</p>
          </div>
          <div className="p-4 bg-crypto-dark rounded-lg">
            <h4 className="font-medium text-crypto-green mb-2">Real-time Execution</h4>
            <p className="text-gray-400 text-sm">Automatic trade execution with gas optimization</p>
          </div>
        </div>
      </div>

      {/* Safety Guidelines */}
      <div className="bg-red-900 border border-red-600 p-6 rounded-lg">
        <h3 className="text-lg font-semibold text-red-400 mb-4 flex items-center">
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
          Safety Guidelines
        </h3>
        <div className="space-y-3">
          <div className="flex items-start space-x-3">
            <div className="w-2 h-2 bg-red-400 rounded-full mt-2 flex-shrink-0"></div>
            <p className="text-red-300 text-sm">
              <strong>Always test in Simulation Mode first</strong> - Never start with real money until you understand the system
            </p>
          </div>
          <div className="flex items-start space-x-3">
            <div className="w-2 h-2 bg-red-400 rounded-full mt-2 flex-shrink-0"></div>
            <p className="text-red-300 text-sm">
              <strong>Start with small position sizes</strong> - Even in live mode, use $5-10 initially
            </p>
          </div>
          <div className="flex items-start space-x-3">
            <div className="w-2 h-2 bg-red-400 rounded-full mt-2 flex-shrink-0"></div>
            <p className="text-red-300 text-sm">
              <strong>Keep Safe Mode enabled</strong> - Restricts trading to major tokens and reasonable amounts
            </p>
          </div>
          <div className="flex items-start space-x-3">
            <div className="w-2 h-2 bg-red-400 rounded-full mt-2 flex-shrink-0"></div>
            <p className="text-red-300 text-sm">
              <strong>Monitor gas prices</strong> - High gas costs can eliminate arbitrage profits
            </p>
          </div>
          <div className="flex items-start space-x-3">
            <div className="w-2 h-2 bg-red-400 rounded-full mt-2 flex-shrink-0"></div>
            <p className="text-red-300 text-sm">
              <strong>Understand the risks</strong> - Arbitrage trading involves financial risk and potential losses
            </p>
          </div>
        </div>
      </div>

      {/* Understanding Settings */}
      <div className="bg-crypto-gray p-6 rounded-lg">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
          <svg className="w-5 h-5 mr-2 text-crypto-blue" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Understanding Key Settings
        </h3>
        <div className="space-y-4">
          <div className="p-4 bg-crypto-dark rounded-lg">
            <h4 className="font-medium text-white mb-2">Simulation vs Live Mode</h4>
            <p className="text-gray-400 text-sm">
              <strong>Simulation:</strong> Shows what trades would be executed without spending real money<br/>
              <strong>Live:</strong> Executes real transactions using your wallet funds
            </p>
          </div>
          <div className="p-4 bg-crypto-dark rounded-lg">
            <h4 className="font-medium text-white mb-2">Profit Thresholds</h4>
            <p className="text-gray-400 text-sm">
              <strong>Min Profit:</strong> Opportunities below this percentage are ignored<br/>
              <strong>Max Profit:</strong> Opportunities above this may be unrealistic or risky
            </p>
          </div>
          <div className="p-4 bg-crypto-dark rounded-lg">
            <h4 className="font-medium text-white mb-2">Position Size</h4>
            <p className="text-gray-400 text-sm">
              Amount in USD to trade per opportunity. Start small ($5-10) and increase gradually as you gain confidence.
            </p>
          </div>
          <div className="p-4 bg-crypto-dark rounded-lg">
            <h4 className="font-medium text-white mb-2">Slippage Protection</h4>
            <p className="text-gray-400 text-sm">
              Maximum price difference tolerated during trade execution. Higher values reduce failed trades but increase risk.
            </p>
          </div>
        </div>
      </div>

      {/* Troubleshooting */}
      <div className="bg-crypto-gray p-6 rounded-lg">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
          <svg className="w-5 h-5 mr-2 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Common Issues & Solutions
        </h3>
        <div className="space-y-4">
          <div className="p-4 bg-crypto-dark rounded-lg">
            <h4 className="font-medium text-yellow-400 mb-2">Bot Not Starting</h4>
            <p className="text-gray-400 text-sm">
              Check that the Python backend is running and the WebSocket connection is established (green status indicator).
            </p>
          </div>
          <div className="p-4 bg-crypto-dark rounded-lg">
            <h4 className="font-medium text-yellow-400 mb-2">No Opportunities Found</h4>
            <p className="text-gray-400 text-sm">
              Try lowering Min Profit threshold or increasing Max Slippage. Market conditions may also affect opportunity frequency.
            </p>
          </div>
          <div className="p-4 bg-crypto-dark rounded-lg">
            <h4 className="font-medium text-yellow-400 mb-2">Trades Failing</h4>
            <p className="text-gray-400 text-sm">
              Increase slippage tolerance, check gas price settings, or reduce position size. Fast-moving markets can invalidate opportunities quickly.
            </p>
          </div>
          <div className="p-4 bg-crypto-dark rounded-lg">
            <h4 className="font-medium text-yellow-400 mb-2">High Gas Costs</h4>
            <p className="text-gray-400 text-sm">
              Monitor Base network congestion. Consider increasing Min Profit Threshold to account for higher gas costs.
            </p>
          </div>
        </div>
      </div>

      {/* Technical Information */}
      <div className="bg-crypto-gray p-6 rounded-lg">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
          <svg className="w-5 h-5 mr-2 text-crypto-blue" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
          </svg>
          Technical Details
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 bg-crypto-dark rounded-lg">
            <h4 className="font-medium text-white mb-2">Supported Networks</h4>
            <p className="text-gray-400 text-sm">Base Network (Coinbase L2)</p>
          </div>
          <div className="p-4 bg-crypto-dark rounded-lg">
            <h4 className="font-medium text-white mb-2">Supported DEXes</h4>
            <p className="text-gray-400 text-sm">Uniswap V3, SushiSwap, Aerodrome</p>
          </div>
          <div className="p-4 bg-crypto-dark rounded-lg">
            <h4 className="font-medium text-white mb-2">Technology Stack</h4>
            <p className="text-gray-400 text-sm">Python backend, React frontend, Tauri desktop wrapper</p>
          </div>
          <div className="p-4 bg-crypto-dark rounded-lg">
            <h4 className="font-medium text-white mb-2">Version</h4>
            <p className="text-gray-400 text-sm">v1.0.0 - Initial Release</p>
          </div>
        </div>
      </div>

      {/* Support */}
      <div className="bg-crypto-gray p-6 rounded-lg">
        <h3 className="text-lg font-semibold text-white mb-4">Need Help?</h3>
        <div className="text-gray-400 space-y-2">
          <p>📖 Check the project documentation for detailed setup instructions</p>
          <p>⚠️ Remember: This is educational software - use at your own risk</p>
          <p>🔒 Always prioritize security when handling private keys and funds</p>
          <p>📊 Start small and gradually increase position sizes as you gain experience</p>
        </div>
      </div>
    </div>
  )
}

export default Info
