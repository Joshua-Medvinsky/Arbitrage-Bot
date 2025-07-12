import { Home, Settings, Info, TrendingUp, Activity, Shield } from 'lucide-react'

export type TabType = 'home' | 'settings' | 'info'

interface SidebarProps {
  activeTab: TabType
  onTabChange: (tab: TabType) => void
}

const Sidebar = ({ activeTab, onTabChange }: SidebarProps) => {
  const tabs = [
    {
      id: 'home' as TabType,
      name: 'Dashboard',
      icon: <Home size={20} />,
      description: 'Trading & Analytics',
      color: '#00D4AA'
    },
    {
      id: 'settings' as TabType,
      name: 'Settings',
      icon: <Settings size={20} />,
      description: 'Configuration',
      color: '#4F46E5'
    },
    {
      id: 'info' as TabType,
      name: 'Info',
      icon: <Info size={20} />,
      description: 'Help & Docs',
      color: '#F59E0B'
    }
  ]

  const cardStyle = {
    backgroundColor: '#1A1F2E',
    border: '1px solid #2D3748',
    borderRadius: '12px',
    padding: '16px',
    marginBottom: '8px',
    transition: 'all 0.2s ease'
  }

  return (
    <div style={{ 
      width: '20%',
      minWidth: '280px',
      height: '100vh',
      backgroundColor: '#0D1421',
      borderRight: '1px solid #2D3748',
      display: 'flex',
      flexDirection: 'column'
    }}>
      {/* Header */}
      <div style={{ 
        padding: '32px 24px 24px',
        borderBottom: '1px solid #2D3748'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
          <div style={{ 
            backgroundColor: '#00D4AA20', 
            borderRadius: '12px', 
            padding: '12px',
            color: '#00D4AA'
          }}>
            <TrendingUp size={24} />
          </div>
          <div>
            <h1 style={{ 
              fontSize: '24px', 
              fontWeight: '700', 
              margin: 0, 
              color: '#ffffff',
              letterSpacing: '-0.5px'
            }}>
              ArbiBot
            </h1>
            <p style={{ 
              fontSize: '14px', 
              margin: 0, 
              color: '#9CA3AF',
              fontWeight: '500'
            }}>
              Pro Trading Suite
            </p>
          </div>
        </div>
        
        {/* Status Indicator */}
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          gap: '8px',
          padding: '8px 12px',
          backgroundColor: '#00D4AA20',
          borderRadius: '8px',
          border: '1px solid #00D4AA30'
        }}>
          <div style={{ 
            width: '8px', 
            height: '8px', 
            borderRadius: '50%', 
            backgroundColor: '#00D4AA',
            animation: 'pulse 2s infinite'
          }} />
          <span style={{ fontSize: '12px', color: '#00D4AA', fontWeight: '600' }}>
            SYSTEM ONLINE
          </span>
        </div>
      </div>

      {/* Navigation */}
      <nav style={{ 
        flex: 1, 
        padding: '24px',
        overflowY: 'auto'
      }}>
        <h3 style={{ 
          fontSize: '12px', 
          fontWeight: '600', 
          color: '#9CA3AF', 
          margin: '0 0 16px 0',
          textTransform: 'uppercase',
          letterSpacing: '0.5px'
        }}>
          Navigation
        </h3>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {tabs.map((tab) => {
            const isActive = activeTab === tab.id
            
            return (
              <button
                key={tab.id}
                onClick={() => onTabChange(tab.id)}
                style={{
                  ...cardStyle,
                  backgroundColor: isActive ? '#1A1F2E' : 'transparent',
                  borderColor: isActive ? tab.color : '#2D3748',
                  cursor: 'pointer',
                  textAlign: 'left',
                  position: 'relative',
                  overflow: 'hidden'
                }}
                onMouseEnter={(e) => {
                  if (!isActive) {
                    e.currentTarget.style.backgroundColor = '#1A1F2E'
                    e.currentTarget.style.borderColor = '#374151'
                    e.currentTarget.style.transform = 'translateX(4px)'
                  }
                }}
                onMouseLeave={(e) => {
                  if (!isActive) {
                    e.currentTarget.style.backgroundColor = 'transparent'
                    e.currentTarget.style.borderColor = '#2D3748'
                    e.currentTarget.style.transform = 'translateX(0)'
                  }
                }}
              >
                {/* Active indicator */}
                {isActive && (
                  <div style={{
                    position: 'absolute',
                    left: 0,
                    top: 0,
                    bottom: 0,
                    width: '4px',
                    backgroundColor: tab.color,
                    borderRadius: '0 4px 4px 0'
                  }} />
                )}
                
                <div style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: '16px',
                  paddingLeft: isActive ? '12px' : '8px'
                }}>
                  <div style={{ 
                    color: isActive ? tab.color : '#9CA3AF',
                    transition: 'color 0.2s ease'
                  }}>
                    {tab.icon}
                  </div>
                  
                  <div style={{ flex: 1 }}>
                    <div style={{ 
                      fontSize: '16px', 
                      fontWeight: '600', 
                      color: isActive ? '#ffffff' : '#E5E7EB',
                      marginBottom: '2px'
                    }}>
                      {tab.name}
                    </div>
                    <div style={{ 
                      fontSize: '12px', 
                      color: isActive ? '#9CA3AF' : '#6B7280'
                    }}>
                      {tab.description}
                    </div>
                  </div>
                  
                  {isActive && (
                    <div style={{
                      width: '6px',
                      height: '6px',
                      borderRadius: '50%',
                      backgroundColor: tab.color
                    }} />
                  )}
                </div>
              </button>
            )
          })}
        </div>

        {/* Quick Stats */}
        <div style={{ marginTop: '32px' }}>
          <h3 style={{ 
            fontSize: '12px', 
            fontWeight: '600', 
            color: '#9CA3AF', 
            margin: '0 0 16px 0',
            textTransform: 'uppercase',
            letterSpacing: '0.5px'
          }}>
            Quick Stats
          </h3>
          
          <div style={cardStyle}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
              <div style={{ 
                backgroundColor: '#10B98120', 
                borderRadius: '8px', 
                padding: '8px',
                color: '#10B981'
              }}>
                <Activity size={16} />
              </div>
              <div>
                <p style={{ margin: 0, fontSize: '14px', fontWeight: '600', color: '#ffffff' }}>
                  Active Trades
                </p>
                <p style={{ margin: 0, fontSize: '12px', color: '#9CA3AF' }}>
                  Real-time monitoring
                </p>
              </div>
            </div>
            
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '24px', fontWeight: '700', color: '#ffffff' }}>
                23
              </span>
              <span style={{ fontSize: '12px', color: '#10B981', fontWeight: '600' }}>
                +12%
              </span>
            </div>
          </div>

          <div style={cardStyle}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
              <div style={{ 
                backgroundColor: '#F59E0B20', 
                borderRadius: '8px', 
                padding: '8px',
                color: '#F59E0B'
              }}>
                <Shield size={16} />
              </div>
              <div>
                <p style={{ margin: 0, fontSize: '14px', fontWeight: '600', color: '#ffffff' }}>
                  Risk Level
                </p>
                <p style={{ margin: 0, fontSize: '12px', color: '#9CA3AF' }}>
                  Current exposure
                </p>
              </div>
            </div>
            
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '16px', fontWeight: '600', color: '#F59E0B' }}>
                LOW
              </span>
              <div style={{ 
                width: '40px', 
                height: '6px', 
                backgroundColor: '#2D3748', 
                borderRadius: '3px',
                overflow: 'hidden'
              }}>
                <div style={{ 
                  width: '30%', 
                  height: '100%', 
                  backgroundColor: '#F59E0B',
                  borderRadius: '3px'
                }} />
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Footer */}
      <div style={{ 
        padding: '24px',
        borderTop: '1px solid #2D3748'
      }}>
        <div style={{ 
          textAlign: 'center',
          fontSize: '12px',
          color: '#6B7280'
        }}>
          <div style={{ marginBottom: '8px', fontWeight: '600' }}>
            Built with React + Tauri
          </div>
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '4px' }}>
            <span>©</span>
            <span>2025</span>
            <span style={{ color: '#00D4AA', fontWeight: '600' }}>ArbiBot</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Sidebar
