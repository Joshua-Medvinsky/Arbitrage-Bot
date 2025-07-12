import { 
  Zap, 
  Shield, 
  AlertTriangle, 
  HelpCircle, 
  Settings, 
  DollarSign,
  Activity,
  Target,
  Network,
  Code,
  Lightbulb,
  Info as InfoIcon,
  CheckCircle,
  XCircle,
  BarChart3,
  Cpu
} from 'lucide-react'

const Info = () => {
  const cardStyle = {
    backgroundColor: '#1A1F2E',
    border: '1px solid #2D3748',
    borderRadius: '16px',
    padding: '24px',
    marginBottom: '24px'
  }

  const smallCardStyle = {
    backgroundColor: '#0D1421',
    border: '1px solid #2D3748',
    borderRadius: '12px',
    padding: '20px'
  }

  const stepStyle = {
    backgroundColor: '#0D1421',
    border: '1px solid #2D3748',
    borderRadius: '12px',
    padding: '20px',
    marginBottom: '16px'
  }

  return (
    <div style={{ padding: '0 8px' }}>
      {/* Header */}
      <div style={{ marginBottom: '32px' }}>
        <h1 style={{ fontSize: '32px', fontWeight: '700', margin: '0 0 8px 0', color: '#ffffff' }}>
          Help & Documentation
        </h1>
        <p style={{ color: '#9CA3AF', fontSize: '16px', margin: 0 }}>
          Learn how to use ArbiBot effectively and safely for arbitrage trading
        </p>
      </div>

      {/* Quick Start Guide */}
      <div style={cardStyle}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
          <div style={{ 
            backgroundColor: '#00D4AA20', 
            borderRadius: '12px', 
            padding: '12px',
            color: '#00D4AA'
          }}>
            <Zap size={24} />
          </div>
          <div>
            <h3 style={{ fontSize: '20px', fontWeight: '600', margin: 0, color: '#ffffff' }}>
              Quick Start Guide
            </h3>
            <p style={{ fontSize: '14px', color: '#9CA3AF', margin: 0 }}>
              Get started with arbitrage trading in 4 simple steps
            </p>
          </div>
        </div>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
          <div style={stepStyle}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '12px' }}>
              <div style={{ 
                backgroundColor: '#4F46E5', 
                borderRadius: '50%', 
                width: '32px', 
                height: '32px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#ffffff',
                fontSize: '14px',
                fontWeight: '700'
              }}>
                1
              </div>
              <h4 style={{ fontSize: '16px', fontWeight: '600', color: '#ffffff', margin: 0 }}>
                Configure Settings
              </h4>
            </div>
            <p style={{ fontSize: '14px', color: '#9CA3AF', margin: 0, lineHeight: '1.5' }}>
              Navigate to Settings and ensure Simulation Mode is enabled for safe testing. 
              Configure your risk parameters and position sizes.
            </p>
          </div>

          <div style={stepStyle}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '12px' }}>
              <div style={{ 
                backgroundColor: '#00D4AA', 
                borderRadius: '50%', 
                width: '32px', 
                height: '32px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#ffffff',
                fontSize: '14px',
                fontWeight: '700'
              }}>
                2
              </div>
              <h4 style={{ fontSize: '16px', fontWeight: '600', color: '#ffffff', margin: 0 }}>
                Start the Bot
              </h4>
            </div>
            <p style={{ fontSize: '14px', color: '#9CA3AF', margin: 0, lineHeight: '1.5' }}>
              Return to Dashboard and click "Start Bot" to begin monitoring DEXes for 
              arbitrage opportunities across the Base network.
            </p>
          </div>

          <div style={stepStyle}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '12px' }}>
              <div style={{ 
                backgroundColor: '#F59E0B', 
                borderRadius: '50%', 
                width: '32px', 
                height: '32px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#ffffff',
                fontSize: '14px',
                fontWeight: '700'
              }}>
                3
              </div>
              <h4 style={{ fontSize: '16px', fontWeight: '600', color: '#ffffff', margin: 0 }}>
                Monitor Performance
              </h4>
            </div>
            <p style={{ fontSize: '14px', color: '#9CA3AF', margin: 0, lineHeight: '1.5' }}>
              Watch real-time opportunities, review your portfolio performance, 
              and analyze trading statistics on the dashboard.
            </p>
          </div>

          <div style={stepStyle}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '12px' }}>
              <div style={{ 
                backgroundColor: '#10B981', 
                borderRadius: '50%', 
                width: '32px', 
                height: '32px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#ffffff',
                fontSize: '14px',
                fontWeight: '700'
              }}>
                4
              </div>
              <h4 style={{ fontSize: '16px', fontWeight: '600', color: '#ffffff', margin: 0 }}>
                Go Live (Advanced)
              </h4>
            </div>
            <p style={{ fontSize: '14px', color: '#9CA3AF', margin: 0, lineHeight: '1.5' }}>
              After thorough testing, disable Simulation Mode for real trading. 
              Start with small amounts and gradually scale up.
            </p>
          </div>
        </div>
      </div>

      {/* Key Features */}
      <div style={cardStyle}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
          <div style={{ 
            backgroundColor: '#4F46E520', 
            borderRadius: '12px', 
            padding: '12px',
            color: '#4F46E5'
          }}>
            <CheckCircle size={24} />
          </div>
          <div>
            <h3 style={{ fontSize: '20px', fontWeight: '600', margin: 0, color: '#ffffff' }}>
              Platform Features
            </h3>
            <p style={{ fontSize: '14px', color: '#9CA3AF', margin: 0 }}>
              Advanced tools for professional arbitrage trading
            </p>
          </div>
        </div>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '16px' }}>
          <div style={smallCardStyle}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
              <div style={{ 
                backgroundColor: '#00D4AA20', 
                borderRadius: '8px', 
                padding: '8px',
                color: '#00D4AA'
              }}>
                <Network size={20} />
              </div>
              <h4 style={{ fontSize: '16px', fontWeight: '600', color: '#00D4AA', margin: 0 }}>
                Multi-DEX Monitoring
              </h4>
            </div>
            <p style={{ fontSize: '14px', color: '#9CA3AF', margin: 0, lineHeight: '1.5' }}>
              Real-time price monitoring across Uniswap V3, SushiSwap, and Aerodrome 
              for maximum opportunity detection.
            </p>
          </div>

          <div style={smallCardStyle}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
              <div style={{ 
                backgroundColor: '#10B98120', 
                borderRadius: '8px', 
                padding: '8px',
                color: '#10B981'
              }}>
                <Shield size={20} />
              </div>
              <h4 style={{ fontSize: '16px', fontWeight: '600', color: '#10B981', margin: 0 }}>
                Safe Mode Protection
              </h4>
            </div>
            <p style={{ fontSize: '14px', color: '#9CA3AF', margin: 0, lineHeight: '1.5' }}>
              Built-in safety features with position limits, major token restrictions, 
              and slippage protection for secure trading.
            </p>
          </div>

          <div style={smallCardStyle}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
              <div style={{ 
                backgroundColor: '#8B5CF620', 
                borderRadius: '8px', 
                padding: '8px',
                color: '#8B5CF6'
              }}>
                <Activity size={20} />
              </div>
              <h4 style={{ fontSize: '16px', fontWeight: '600', color: '#8B5CF6', margin: 0 }}>
                Flash Loan Integration
              </h4>
            </div>
            <p style={{ fontSize: '14px', color: '#9CA3AF', margin: 0, lineHeight: '1.5' }}>
              Capital-efficient arbitrage using Aave flash loans for larger 
              opportunities without requiring upfront capital.
            </p>
          </div>

          <div style={smallCardStyle}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
              <div style={{ 
                backgroundColor: '#F59E0B20', 
                borderRadius: '8px', 
                padding: '8px',
                color: '#F59E0B'
              }}>
                <Zap size={20} />
              </div>
              <h4 style={{ fontSize: '16px', fontWeight: '600', color: '#F59E0B', margin: 0 }}>
                Real-time Execution
              </h4>
            </div>
            <p style={{ fontSize: '14px', color: '#9CA3AF', margin: 0, lineHeight: '1.5' }}>
              Automated trade execution with gas optimization and MEV protection 
              for maximum profit capture.
            </p>
          </div>
        </div>
      </div>

      {/* Safety Guidelines */}
      <div style={{
        backgroundColor: '#EF444420',
        border: '1px solid #EF4444',
        borderRadius: '16px',
        padding: '24px',
        marginBottom: '24px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
          <div style={{ 
            backgroundColor: '#EF444430', 
            borderRadius: '12px', 
            padding: '12px',
            color: '#EF4444'
          }}>
            <AlertTriangle size={24} />
          </div>
          <div>
            <h3 style={{ fontSize: '20px', fontWeight: '600', margin: 0, color: '#EF4444' }}>
              Critical Safety Guidelines
            </h3>
            <p style={{ fontSize: '14px', color: '#FCA5A5', margin: 0 }}>
              Essential safety practices for risk management
            </p>
          </div>
        </div>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '16px' }}>
          {[
            {
              title: "Always Test in Simulation Mode",
              description: "Never start with real money. Understand the system behavior first."
            },
            {
              title: "Start with Small Position Sizes", 
              description: "Use $5-10 initially, even in live mode. Scale up gradually."
            },
            {
              title: "Keep Safe Mode Enabled",
              description: "Restricts trading to major tokens and reasonable position limits."
            },
            {
              title: "Monitor Gas Prices",
              description: "High network congestion can eliminate arbitrage profits."
            },
            {
              title: "Understand Financial Risks",
              description: "Arbitrage trading involves potential losses and smart contract risks."
            },
            {
              title: "Secure Your Private Keys",
              description: "Never share wallet information. Use dedicated trading wallets."
            }
          ].map((item, index) => (
            <div key={index} style={{ display: 'flex', alignItems: 'flex-start', gap: '12px' }}>
              <div style={{ 
                width: '6px', 
                height: '6px', 
                borderRadius: '50%', 
                backgroundColor: '#EF4444',
                marginTop: '8px',
                flexShrink: 0
              }} />
              <div>
                <p style={{ fontSize: '14px', fontWeight: '600', color: '#FCA5A5', margin: '0 0 4px 0' }}>
                  {item.title}
                </p>
                <p style={{ fontSize: '13px', color: '#FECACA', margin: 0, lineHeight: '1.4' }}>
                  {item.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Understanding Settings */}
      <div style={cardStyle}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
          <div style={{ 
            backgroundColor: '#4F46E520', 
            borderRadius: '12px', 
            padding: '12px',
            color: '#4F46E5'
          }}>
            <Settings size={24} />
          </div>
          <div>
            <h3 style={{ fontSize: '20px', fontWeight: '600', margin: 0, color: '#ffffff' }}>
              Understanding Key Settings
            </h3>
            <p style={{ fontSize: '14px', color: '#9CA3AF', margin: 0 }}>
              Learn what each configuration parameter controls
            </p>
          </div>
        </div>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '16px' }}>
          <div style={smallCardStyle}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
              <div style={{ 
                backgroundColor: '#4F46E520', 
                borderRadius: '8px', 
                padding: '8px',
                color: '#4F46E5'
              }}>
                <Shield size={20} />
              </div>
              <h4 style={{ fontSize: '16px', fontWeight: '600', color: '#ffffff', margin: 0 }}>
                Simulation vs Live Mode
              </h4>
            </div>
            <div style={{ fontSize: '14px', color: '#9CA3AF', lineHeight: '1.5' }}>
              <p style={{ margin: '0 0 8px 0' }}>
                <strong style={{ color: '#ffffff' }}>Simulation:</strong> Shows potential trades without spending real money
              </p>
              <p style={{ margin: 0 }}>
                <strong style={{ color: '#ffffff' }}>Live:</strong> Executes real transactions using your wallet funds
              </p>
            </div>
          </div>

          <div style={smallCardStyle}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
              <div style={{ 
                backgroundColor: '#00D4AA20', 
                borderRadius: '8px', 
                padding: '8px',
                color: '#00D4AA'
              }}>
                <Target size={20} />
              </div>
              <h4 style={{ fontSize: '16px', fontWeight: '600', color: '#ffffff', margin: 0 }}>
                Profit Thresholds
              </h4>
            </div>
            <div style={{ fontSize: '14px', color: '#9CA3AF', lineHeight: '1.5' }}>
              <p style={{ margin: '0 0 8px 0' }}>
                <strong style={{ color: '#ffffff' }}>Min Profit:</strong> Opportunities below this are ignored
              </p>
              <p style={{ margin: 0 }}>
                <strong style={{ color: '#ffffff' }}>Max Profit:</strong> High values may indicate unrealistic opportunities
              </p>
            </div>
          </div>

          <div style={smallCardStyle}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
              <div style={{ 
                backgroundColor: '#10B98120', 
                borderRadius: '8px', 
                padding: '8px',
                color: '#10B981'
              }}>
                <DollarSign size={20} />
              </div>
              <h4 style={{ fontSize: '16px', fontWeight: '600', color: '#ffffff', margin: 0 }}>
                Position Size
              </h4>
            </div>
            <p style={{ fontSize: '14px', color: '#9CA3AF', margin: 0, lineHeight: '1.5' }}>
              Amount in USD to trade per opportunity. Start small ($5-10) and increase 
              gradually as you gain confidence and experience.
            </p>
          </div>

          <div style={smallCardStyle}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
              <div style={{ 
                backgroundColor: '#F59E0B20', 
                borderRadius: '8px', 
                padding: '8px',
                color: '#F59E0B'
              }}>
                <BarChart3 size={20} />
              </div>
              <h4 style={{ fontSize: '16px', fontWeight: '600', color: '#ffffff', margin: 0 }}>
                Slippage Protection
              </h4>
            </div>
            <p style={{ fontSize: '14px', color: '#9CA3AF', margin: 0, lineHeight: '1.5' }}>
              Maximum price difference tolerated during execution. Higher values reduce 
              failed trades but increase price impact risk.
            </p>
          </div>
        </div>
      </div>

      {/* Troubleshooting */}
      <div style={cardStyle}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
          <div style={{ 
            backgroundColor: '#F59E0B20', 
            borderRadius: '12px', 
            padding: '12px',
            color: '#F59E0B'
          }}>
            <HelpCircle size={24} />
          </div>
          <div>
            <h3 style={{ fontSize: '20px', fontWeight: '600', margin: 0, color: '#ffffff' }}>
              Common Issues & Solutions
            </h3>
            <p style={{ fontSize: '14px', color: '#9CA3AF', margin: 0 }}>
              Troubleshooting guide for frequent problems
            </p>
          </div>
        </div>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '16px' }}>
          <div style={smallCardStyle}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
              <div style={{ 
                backgroundColor: '#EF444420', 
                borderRadius: '8px', 
                padding: '8px',
                color: '#EF4444'
              }}>
                <XCircle size={20} />
              </div>
              <h4 style={{ fontSize: '16px', fontWeight: '600', color: '#EF4444', margin: 0 }}>
                Bot Not Starting
              </h4>
            </div>
            <p style={{ fontSize: '14px', color: '#9CA3AF', margin: 0, lineHeight: '1.5' }}>
              Verify the Python backend is running and WebSocket connection is established. 
              Look for the green "SYSTEM ONLINE" indicator in the sidebar.
            </p>
          </div>

          <div style={smallCardStyle}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
              <div style={{ 
                backgroundColor: '#F59E0B20', 
                borderRadius: '8px', 
                padding: '8px',
                color: '#F59E0B'
              }}>
                <AlertTriangle size={20} />
              </div>
              <h4 style={{ fontSize: '16px', fontWeight: '600', color: '#F59E0B', margin: 0 }}>
                No Opportunities
              </h4>
            </div>
            <p style={{ fontSize: '14px', color: '#9CA3AF', margin: 0, lineHeight: '1.5' }}>
              Try lowering Min Profit threshold or increasing Max Slippage. Market conditions 
              and network congestion affect opportunity frequency.
            </p>
          </div>

          <div style={smallCardStyle}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
              <div style={{ 
                backgroundColor: '#EF444420', 
                borderRadius: '8px', 
                padding: '8px',
                color: '#EF4444'
              }}>
                <XCircle size={20} />
              </div>
              <h4 style={{ fontSize: '16px', fontWeight: '600', color: '#EF4444', margin: 0 }}>
                Trades Failing
              </h4>
            </div>
            <p style={{ fontSize: '14px', color: '#9CA3AF', margin: 0, lineHeight: '1.5' }}>
              Increase slippage tolerance, verify gas settings, or reduce position size. 
              Fast-moving markets can invalidate opportunities quickly.
            </p>
          </div>

          <div style={smallCardStyle}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
              <div style={{ 
                backgroundColor: '#F59E0B20', 
                borderRadius: '8px', 
                padding: '8px',
                color: '#F59E0B'
              }}>
                <Zap size={20} />
              </div>
              <h4 style={{ fontSize: '16px', fontWeight: '600', color: '#F59E0B', margin: 0 }}>
                High Gas Costs
              </h4>
            </div>
            <p style={{ fontSize: '14px', color: '#9CA3AF', margin: 0, lineHeight: '1.5' }}>
              Monitor Base network congestion. Consider increasing Min Profit Threshold 
              to account for elevated gas costs during busy periods.
            </p>
          </div>
        </div>
      </div>

      {/* Technical Information */}
      <div style={cardStyle}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
          <div style={{ 
            backgroundColor: '#6366F120', 
            borderRadius: '12px', 
            padding: '12px',
            color: '#6366F1'
          }}>
            <Code size={24} />
          </div>
          <div>
            <h3 style={{ fontSize: '20px', fontWeight: '600', margin: 0, color: '#ffffff' }}>
              Technical Specifications
            </h3>
            <p style={{ fontSize: '14px', color: '#9CA3AF', margin: 0 }}>
              Platform details and supported infrastructure
            </p>
          </div>
        </div>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '16px' }}>
          <div style={smallCardStyle}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
              <div style={{ 
                backgroundColor: '#6366F120', 
                borderRadius: '8px', 
                padding: '8px',
                color: '#6366F1'
              }}>
                <Network size={20} />
              </div>
              <h4 style={{ fontSize: '16px', fontWeight: '600', color: '#ffffff', margin: 0 }}>
                Supported Networks
              </h4>
            </div>
            <p style={{ fontSize: '14px', color: '#9CA3AF', margin: 0 }}>
              Base Network (Coinbase Layer 2)
            </p>
          </div>

          <div style={smallCardStyle}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
              <div style={{ 
                backgroundColor: '#10B98120', 
                borderRadius: '8px', 
                padding: '8px',
                color: '#10B981'
              }}>
                <Activity size={20} />
              </div>
              <h4 style={{ fontSize: '16px', fontWeight: '600', color: '#ffffff', margin: 0 }}>
                Supported DEXes
              </h4>
            </div>
            <p style={{ fontSize: '14px', color: '#9CA3AF', margin: 0 }}>
              Uniswap V3, SushiSwap, Aerodrome
            </p>
          </div>

          <div style={smallCardStyle}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
              <div style={{ 
                backgroundColor: '#8B5CF620', 
                borderRadius: '8px', 
                padding: '8px',
                color: '#8B5CF6'
              }}>
                <Cpu size={20} />
              </div>
              <h4 style={{ fontSize: '16px', fontWeight: '600', color: '#ffffff', margin: 0 }}>
                Technology Stack
              </h4>
            </div>
            <p style={{ fontSize: '14px', color: '#9CA3AF', margin: 0 }}>
              Python backend, React frontend, Tauri desktop
            </p>
          </div>

          <div style={smallCardStyle}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
              <div style={{ 
                backgroundColor: '#00D4AA20', 
                borderRadius: '8px', 
                padding: '8px',
                color: '#00D4AA'
              }}>
                <InfoIcon size={20} />
              </div>
              <h4 style={{ fontSize: '16px', fontWeight: '600', color: '#ffffff', margin: 0 }}>
                Version
              </h4>
            </div>
            <p style={{ fontSize: '14px', color: '#9CA3AF', margin: 0 }}>
              v1.0.0 - Initial Release
            </p>
          </div>
        </div>
      </div>

      {/* Support Section */}
      <div style={cardStyle}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
          <div style={{ 
            backgroundColor: '#10B98120', 
            borderRadius: '12px', 
            padding: '12px',
            color: '#10B981'
          }}>
            <Lightbulb size={24} />
          </div>
          <h3 style={{ fontSize: '20px', fontWeight: '600', margin: 0, color: '#ffffff' }}>
            Need Additional Help?
          </h3>
        </div>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '16px' }}>
          {[
            { emoji: '📖', text: 'Check project documentation for detailed setup instructions' },
            { emoji: '⚠️', text: 'This is educational software - use at your own risk' },
            { emoji: '🔒', text: 'Always prioritize security when handling private keys' },
            { emoji: '📊', text: 'Start small and scale up as you gain experience' }
          ].map((item, index) => (
            <div key={index} style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: '12px',
              padding: '16px',
              backgroundColor: '#0D1421',
              borderRadius: '8px',
              border: '1px solid #2D3748'
            }}>
              <span style={{ fontSize: '20px' }}>{item.emoji}</span>
              <p style={{ fontSize: '14px', color: '#9CA3AF', margin: 0, lineHeight: '1.4' }}>
                {item.text}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default Info
