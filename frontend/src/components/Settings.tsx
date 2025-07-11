import { useState, useEffect } from 'react'

interface SettingsData {
  SIMULATION_MODE: boolean
  FLASH_LOAN_ENABLED: boolean
  SAFE_MODE: boolean
  EXECUTION_MODE: boolean
  MIN_PROFIT_PCT: number
  MAX_PROFIT_PCT: number
  POSITION_SIZE_USD: number
  MIN_LIQUIDITY_USD: number
  MAX_SLIPPAGE: number
  BASE_GAS_PRICE_GWEI: number
  MEV_PROTECTION_COST_USD: number
  MIN_PROFIT_THRESHOLD_USD: number
  FLASH_LOAN_AMOUNT_USD: number
}

interface SettingsProps {
  socket: any
}

const Settings = ({ socket }: SettingsProps) => {
  const [settings, setSettings] = useState<SettingsData>({
    SIMULATION_MODE: true,
    FLASH_LOAN_ENABLED: false,
    SAFE_MODE: true,
    EXECUTION_MODE: false,
    MIN_PROFIT_PCT: 1.0,
    MAX_PROFIT_PCT: 20.0,
    POSITION_SIZE_USD: 5,
    MIN_LIQUIDITY_USD: 100000,
    MAX_SLIPPAGE: 0.01,
    BASE_GAS_PRICE_GWEI: 1000000,
    MEV_PROTECTION_COST_USD: 1.0,
    MIN_PROFIT_THRESHOLD_USD: 0.50,
    FLASH_LOAN_AMOUNT_USD: 100000
  })

  const [hasChanges, setHasChanges] = useState(false)
  const [isSaving, setIsSaving] = useState(false)

  useEffect(() => {
    // Request current settings from server
    if (socket) {
      socket.emit('get_settings')
      
      socket.on('settings_data', (data: SettingsData) => {
        setSettings(data)
      })
    }

    return () => {
      if (socket) {
        socket.off('settings_data')
      }
    }
  }, [socket])

  const handleInputChange = (key: keyof SettingsData, value: any) => {
    setSettings(prev => ({
      ...prev,
      [key]: value
    }))
    setHasChanges(true)
  }

  const handleSaveSettings = async () => {
    if (!socket) return
    
    setIsSaving(true)
    try {
      socket.emit('update_settings', settings)
      setHasChanges(false)
      // Show success notification
      setTimeout(() => setIsSaving(false), 1000)
    } catch (error) {
      console.error('Failed to save settings:', error)
      setIsSaving(false)
    }
  }

  const handleResetSettings = () => {
    // Request fresh settings from server
    if (socket) {
      socket.emit('get_settings')
    }
    setHasChanges(false)
  }

  const ToggleSwitch = ({ 
    id, 
    checked, 
    onChange, 
    label, 
    description 
  }: {
    id: string
    checked: boolean
    onChange: (value: boolean) => void
    label: string
    description?: string
  }) => (
    <div className="flex items-start justify-between p-4 bg-crypto-dark rounded-lg">
      <div className="flex-1">
        <label htmlFor={id} className="font-medium text-white cursor-pointer">
          {label}
        </label>
        {description && (
          <p className="text-sm text-gray-400 mt-1">{description}</p>
        )}
      </div>
      <button
        type="button"
        onClick={() => onChange(!checked)}
        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-crypto-blue focus:ring-offset-2 focus:ring-offset-gray-800 ${
          checked ? 'bg-crypto-green' : 'bg-gray-600'
        }`}
      >
        <span
          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
            checked ? 'translate-x-6' : 'translate-x-1'
          }`}
        />
      </button>
    </div>
  )

  const NumberInput = ({ 
    id, 
    value, 
    onChange, 
    label, 
    description, 
    min, 
    max, 
    step = 1,
    unit = ''
  }: {
    id: string
    value: number
    onChange: (value: number) => void
    label: string
    description?: string
    min?: number
    max?: number
    step?: number
    unit?: string
  }) => (
    <div className="p-4 bg-crypto-dark rounded-lg">
      <label htmlFor={id} className="block font-medium text-white mb-1">
        {label}
      </label>
      {description && (
        <p className="text-sm text-gray-400 mb-3">{description}</p>
      )}
      <div className="flex items-center space-x-2">
        <input
          type="number"
          id={id}
          value={value}
          onChange={(e) => onChange(parseFloat(e.target.value) || 0)}
          min={min}
          max={max}
          step={step}
          className="flex-1 bg-gray-700 border border-gray-600 rounded-md px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-crypto-blue focus:border-transparent"
        />
        {unit && (
          <span className="text-gray-400 text-sm">{unit}</span>
        )}
      </div>
    </div>
  )

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">Settings</h2>
          <p className="text-gray-400 mt-1">Configure your arbitrage bot parameters</p>
        </div>
        <div className="flex space-x-3">
          {hasChanges && (
            <button
              onClick={handleResetSettings}
              className="px-4 py-2 text-gray-400 hover:text-white transition-colors"
            >
              Reset
            </button>
          )}
          <button
            onClick={handleSaveSettings}
            disabled={!hasChanges || isSaving}
            className={`px-6 py-2 rounded-lg font-medium transition-all ${
              hasChanges && !isSaving
                ? 'bg-crypto-green text-white hover:bg-green-600'
                : 'bg-gray-600 text-gray-400 cursor-not-allowed'
            }`}
          >
            {isSaving ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </div>

      {/* Execution Settings */}
      <div className="bg-crypto-gray p-6 rounded-lg">
        <h3 className="text-lg font-semibold text-white mb-4">Execution Settings</h3>
        <div className="space-y-4">
          <ToggleSwitch
            id="simulation_mode"
            checked={settings.SIMULATION_MODE}
            onChange={(value) => handleInputChange('SIMULATION_MODE', value)}
            label="Simulation Mode"
            description="When enabled, no real transactions will be executed"
          />
          
          <ToggleSwitch
            id="execution_mode"
            checked={settings.EXECUTION_MODE}
            onChange={(value) => handleInputChange('EXECUTION_MODE', value)}
            label="Execution Mode"
            description="Enable real transaction execution (requires Simulation Mode to be OFF)"
          />
          
          <ToggleSwitch
            id="safe_mode"
            checked={settings.SAFE_MODE}
            onChange={(value) => handleInputChange('SAFE_MODE', value)}
            label="Safe Mode"
            description="Restricts trading to small amounts and safe tokens"
          />
          
          <ToggleSwitch
            id="flash_loan_enabled"
            checked={settings.FLASH_LOAN_ENABLED}
            onChange={(value) => handleInputChange('FLASH_LOAN_ENABLED', value)}
            label="Flash Loan Enabled"
            description="Enable flash loan arbitrage for larger capital efficiency"
          />
        </div>
      </div>

      {/* Profit Settings */}
      <div className="bg-crypto-gray p-6 rounded-lg">
        <h3 className="text-lg font-semibold text-white mb-4">Profit & Risk Settings</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <NumberInput
            id="min_profit_pct"
            value={settings.MIN_PROFIT_PCT}
            onChange={(value) => handleInputChange('MIN_PROFIT_PCT', value)}
            label="Minimum Profit"
            description="Minimum profit percentage to consider an opportunity"
            min={0.1}
            max={50}
            step={0.1}
            unit="%"
          />
          
          <NumberInput
            id="max_profit_pct"
            value={settings.MAX_PROFIT_PCT}
            onChange={(value) => handleInputChange('MAX_PROFIT_PCT', value)}
            label="Maximum Profit"
            description="Maximum profit percentage (higher values may be unrealistic)"
            min={1}
            max={500}
            step={1}
            unit="%"
          />
          
          <NumberInput
            id="position_size_usd"
            value={settings.POSITION_SIZE_USD}
            onChange={(value) => handleInputChange('POSITION_SIZE_USD', value)}
            label="Position Size"
            description="USD amount to trade per opportunity"
            min={1}
            max={10000}
            step={1}
            unit="USD"
          />
          
          <NumberInput
            id="min_liquidity_usd"
            value={settings.MIN_LIQUIDITY_USD}
            onChange={(value) => handleInputChange('MIN_LIQUIDITY_USD', value)}
            label="Minimum Liquidity"
            description="Minimum pool liquidity required for safe trading"
            min={1000}
            max={10000000}
            step={1000}
            unit="USD"
          />
        </div>
      </div>

      {/* Trading Settings */}
      <div className="bg-crypto-gray p-6 rounded-lg">
        <h3 className="text-lg font-semibold text-white mb-4">Trading Parameters</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <NumberInput
            id="max_slippage"
            value={settings.MAX_SLIPPAGE * 100}
            onChange={(value) => handleInputChange('MAX_SLIPPAGE', value / 100)}
            label="Maximum Slippage"
            description="Maximum allowed slippage for trades"
            min={0.1}
            max={10}
            step={0.1}
            unit="%"
          />
          
          <NumberInput
            id="mev_protection_cost"
            value={settings.MEV_PROTECTION_COST_USD}
            onChange={(value) => handleInputChange('MEV_PROTECTION_COST_USD', value)}
            label="MEV Protection Cost"
            description="Estimated cost of MEV protection per trade"
            min={0.1}
            max={50}
            step={0.1}
            unit="USD"
          />
          
          <NumberInput
            id="min_profit_threshold"
            value={settings.MIN_PROFIT_THRESHOLD_USD}
            onChange={(value) => handleInputChange('MIN_PROFIT_THRESHOLD_USD', value)}
            label="Minimum Profit Threshold"
            description="Minimum USD profit required to execute trade"
            min={0.01}
            max={100}
            step={0.01}
            unit="USD"
          />
          
          <NumberInput
            id="base_gas_price"
            value={settings.BASE_GAS_PRICE_GWEI}
            onChange={(value) => handleInputChange('BASE_GAS_PRICE_GWEI', value)}
            label="Base Gas Price"
            description="Base network gas price in Gwei"
            min={1000}
            max={10000000}
            step={1000}
            unit="Gwei"
          />
        </div>
      </div>

      {/* Flash Loan Settings */}
      <div className="bg-crypto-gray p-6 rounded-lg">
        <h3 className="text-lg font-semibold text-white mb-4">Flash Loan Settings</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <NumberInput
            id="flash_loan_amount"
            value={settings.FLASH_LOAN_AMOUNT_USD}
            onChange={(value) => handleInputChange('FLASH_LOAN_AMOUNT_USD', value)}
            label="Flash Loan Amount"
            description="USD amount to borrow for flash loan arbitrage"
            min={1000}
            max={1000000}
            step={1000}
            unit="USD"
          />
        </div>
      </div>

      {/* Warning Box */}
      <div className="bg-yellow-900 border border-yellow-600 p-4 rounded-lg">
        <div className="flex items-start space-x-3">
          <svg className="w-5 h-5 text-yellow-400 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
          <div>
            <h4 className="font-medium text-yellow-400">Important Safety Notice</h4>
            <p className="text-yellow-300 text-sm mt-1">
              Always test with small amounts first. Keep Simulation Mode enabled until you're confident in your settings. 
              Real trading involves financial risk and these settings directly affect your trades.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Settings
