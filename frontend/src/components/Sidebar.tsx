export type TabType = 'home' | 'settings' | 'info'

interface SidebarProps {
  activeTab: TabType
  onTabChange: (tab: TabType) => void
}

const Sidebar = ({ activeTab, onTabChange }: SidebarProps) => {
  const tabs = [
    {
      id: 'home' as TabType,
      name: 'Home',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
        </svg>
      ),
      description: 'Dashboard & Trading'
    },
    {
      id: 'settings' as TabType,
      name: 'Settings',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
      ),
      description: 'Configuration & Preferences'
    },
    {
      id: 'info' as TabType,
      name: 'Info',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      description: 'Help & Documentation'
    }
  ]

  return (
    <div className="h-screen flex flex-col flex-shrink-0" style={{ 
      backgroundColor: '#1a1f2e',
      width: '20%',
      minWidth: '250px'
    }}>
      {/* Header */}
      <div className="p-6 border-b flex-shrink-0" style={{ backgroundColor: '#161922', borderBottomColor: '#374151' }}>
        <h1 className="text-xl font-bold text-white mb-1">
          Arbitrage Bot
        </h1>
        <p className="text-xs text-gray-400">
          v1.0.0
        </p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4" style={{ backgroundColor: '#1a1f2e' }}>
        <div className="space-y-2">
          {tabs.map((tab) => (
            <div key={tab.id}>
              <button
                onClick={() => onTabChange(tab.id)}
                className={`w-full flex items-start space-x-3 px-4 py-3 rounded-lg text-left transition-all duration-200 group ${
                  activeTab === tab.id
                    ? 'bg-crypto-blue text-white shadow-lg'
                    : 'text-gray-300 hover:text-white'
                }`}
                style={activeTab !== tab.id ? { 
                  backgroundColor: 'transparent',
                  transition: 'background-color 0.2s'
                } : {}}
                onMouseEnter={(e) => {
                  if (activeTab !== tab.id) {
                    e.currentTarget.style.backgroundColor = '#374151'
                  }
                }}
                onMouseLeave={(e) => {
                  if (activeTab !== tab.id) {
                    e.currentTarget.style.backgroundColor = 'transparent'
                  }
                }}
              >
                <div className={`mt-0.5 ${
                  activeTab === tab.id ? 'text-white' : 'text-gray-400 group-hover:text-gray-300'
                }`}>
                  {tab.icon}
                </div>
                <div className="flex-1">
                  <div className="font-medium">
                    {tab.name}
                  </div>
                  <div className={`text-xs ${
                    activeTab === tab.id ? 'text-gray-200' : 'text-gray-500 group-hover:text-gray-400'
                  }`}>
                    {tab.description}
                  </div>
                </div>
              </button>
            </div>
          ))}
        </div>
      </nav>

      {/* Footer */}
      <div className="p-4 border-t flex-shrink-0" style={{ backgroundColor: '#161922', borderTopColor: '#374151' }}>
        <div className="text-xs text-gray-500 text-center">
          <div className="mb-1">Built with React + Tauri</div>
          <div>© 2025 Arbitrage Bot</div>
        </div>
      </div>
    </div>
  )
}

export default Sidebar
