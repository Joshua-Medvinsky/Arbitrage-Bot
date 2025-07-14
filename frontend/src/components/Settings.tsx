import { useState, useEffect } from 'react'
import { 
  Save, 
  RotateCcw, 
  Shield, 
  Zap, 
  DollarSign, 
  Settings as SettingsIcon,
  TrendingUp,
  AlertTriangle,
  Activity,
  Target,
  Gauge,
  Lock
} from 'lucide-react'
import { loadSettings, saveSettingsWithServerSync } from '../utils/settings'

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
  const [isOnline, setIsOnline] = useState(navigator.onLine)

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

  useEffect(() => {
    // Load settings from local file first
    const loadLocalSettings = async () => {
      try {
        console.log('Loading settings from local file...')
        const localSettings = await loadSettings()
        console.log('Loaded local settings:', localSettings)
        setSettings(localSettings)
      } catch (error) {
        console.error('Failed to load local settings:', error)
      }
    }

    loadLocalSettings()

    // Also request current settings from server if available
    if (socket) {
      console.log('Requesting settings from server...')
      socket.emit('get_settings')
      
      socket.on('settings_data', (data: SettingsData) => {
        console.log('Received settings data from server:', data)
        // Server settings take precedence over local (in case of discrepancies)
        setSettings(data)
      })

      // Add handler for save confirmation
      socket.on('settings_updated', (response: { success: boolean; message: string; settings?: SettingsData }) => {
        console.log('Received settings_updated response from server:', response)
        if (response.success && response.settings) {
          console.log('Server confirmed settings update')
        } else if (!response.success) {
          console.error('Server failed to save settings:', response.message)
        }
      })
    }

    return () => {
      if (socket) {
        socket.off('settings_data')
        socket.off('settings_updated')
      }
    }
  }, [socket])

  // Internet connectivity monitoring
  useEffect(() => {
    const handleOnline = () => setIsOnline(true)
    const handleOffline = () => setIsOnline(false)
    
    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)
    
    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [])

  const handleInputChange = (key: keyof SettingsData, value: any) => {
    setSettings(prev => ({
      ...prev,
      [key]: value
    }))
    setHasChanges(true)
  }

  const handleSaveSettings = async () => {
    console.log('Saving settings:', settings)
    setIsSaving(true)
    
    try {
      // Use local-first save approach
      const result = await saveSettingsWithServerSync(settings, socket)
      
      setIsSaving(false)
      if (result.success) {
        setHasChanges(false)
        console.log('Settings saved successfully:', result.message)
      } else {
        console.error('Failed to save settings:', result.message)
      }
    } catch (error) {
      console.error('Failed to save settings:', error)
      setIsSaving(false)
    }
  }

  const handleResetSettings = async () => {
    try {
      console.log('Resetting settings to saved values...')
      const savedSettings = await loadSettings()
      setSettings(savedSettings)
      setHasChanges(false)
      console.log('Settings reset successfully')
    } catch (error) {
      console.error('Failed to reset settings:', error)
      // Fallback: request from server if local load fails
      if (socket) {
        socket.emit('get_settings')
      }
    }
  }

  const ToggleSwitch = ({ 
    id, 
    checked, 
    onChange, 
    label, 
    description,
    icon,
    color = '#00D4AA'
  }: {
    id: string
    checked: boolean
    onChange: (value: boolean) => void
    label: string
    description?: string
    icon?: React.ReactNode
    color?: string
  }) => (
    <div style={smallCardStyle}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flex: 1 }}>
          {icon && (
            <div style={{ 
              backgroundColor: `${color}20`, 
              borderRadius: '12px', 
              padding: '12px',
              color: color
            }}>
              {icon}
            </div>
          )}
          <div style={{ flex: 1 }}>
            <label htmlFor={id} style={{ 
              fontSize: '16px', 
              fontWeight: '600', 
              color: '#ffffff', 
              cursor: 'pointer',
              margin: 0,
              display: 'block'
            }}>
              {label}
            </label>
            {description && (
              <p style={{ 
                fontSize: '14px', 
                color: '#9CA3AF', 
                margin: '4px 0 0 0'
              }}>
                {description}
              </p>
            )}
          </div>
        </div>
        
        <button
          type="button"
          onClick={() => onChange(!checked)}
          style={{
            position: 'relative',
            display: 'inline-flex',
            height: '24px',
            width: '44px',
            alignItems: 'center',
            borderRadius: '12px',
            backgroundColor: checked ? color : '#6B7280',
            border: 'none',
            cursor: 'pointer',
            transition: 'background-color 0.2s ease'
          }}
        >
          <span
            style={{
              display: 'inline-block',
              height: '16px',
              width: '16px',
              borderRadius: '8px',
              backgroundColor: '#ffffff',
              transform: checked ? 'translateX(24px)' : 'translateX(4px)',
              transition: 'transform 0.2s ease'
            }}
          />
        </button>
      </div>
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
    unit = '',
    icon,
    color = '#4F46E5'
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
    icon?: React.ReactNode
    color?: string
  }) => {
    const [isFocused, setIsFocused] = useState(false)
    const [localValue, setLocalValue] = useState(value.toString())
    
    // Update local value when prop value changes (from external sources)
    useEffect(() => {
      if (!isFocused) {
        setLocalValue(value.toString())
      }
    }, [value, isFocused])
    
    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      const newValue = e.target.value
      setLocalValue(newValue)
      // Don't call onChange here - only update local state
    }
    
    const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
      if (e.key === 'Enter') {
        // User pressed Enter - sync the value
        const numValue = parseFloat(localValue)
        if (!isNaN(numValue)) {
          onChange(numValue)
        } else if (localValue === '') {
          onChange(0)
        }
        // Remove focus from the input
        e.currentTarget.blur()
      }
    }
    
    const handleBlur = () => {
      setIsFocused(false)
      // User clicked out - sync the value
      const numValue = parseFloat(localValue)
      if (!isNaN(numValue)) {
        onChange(numValue)
      } else if (localValue === '') {
        onChange(0)
        setLocalValue('0')
      } else {
        // Invalid input - revert to original value
        setLocalValue(value.toString())
      }
    }
    
    return (
      <div style={smallCardStyle}>
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '16px', marginBottom: '16px' }}>
          {icon && (
            <div style={{ 
              backgroundColor: `${color}20`, 
              borderRadius: '12px', 
              padding: '12px',
              color: color
            }}>
              {icon}
            </div>
          )}
          <div style={{ flex: 1 }}>
            <label htmlFor={id} style={{ 
              fontSize: '16px', 
              fontWeight: '600', 
              color: '#ffffff', 
              margin: '0 0 4px 0',
              display: 'block'
            }}>
              {label}
            </label>
            {description && (
              <p style={{ 
                fontSize: '14px', 
                color: '#9CA3AF', 
                margin: 0
              }}>
                {description}
              </p>
            )}
          </div>
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <input
            type="number"
            id={id}
            value={localValue}
            onChange={handleChange}
            onKeyPress={handleKeyPress}
            onFocus={() => setIsFocused(true)}
            onBlur={handleBlur}
            min={min}
            max={max}
            step={step}
            style={{
              flex: 1,
              backgroundColor: '#2D3748',
              border: `1px solid ${isFocused ? color : '#4A5568'}`,
              borderRadius: '8px',
              padding: '12px 16px',
              color: '#ffffff',
              fontSize: '14px',
              outline: 'none',
              boxShadow: isFocused ? `0 0 0 3px ${color}20` : 'none',
              transition: 'border-color 0.2s ease, box-shadow 0.2s ease'
            }}
          />
          {unit && (
            <span style={{ 
              fontSize: '14px', 
              color: '#9CA3AF', 
              fontWeight: '600',
              minWidth: 'fit-content'
            }}>
              {unit}
            </span>
          )}
        </div>
      </div>
    )
  }

  return (
    <div style={{ padding: '0 8px' }}>
      {/* Header */}
      <div style={{ marginBottom: '32px' }}>
        <h1 style={{ fontSize: '32px', fontWeight: '700', margin: '0 0 8px 0', color: '#ffffff' }}>
          Bot Configuration
        </h1>
        <p style={{ color: '#9CA3AF', fontSize: '16px', margin: 0 }}>
          Fine-tune your arbitrage trading parameters and safety settings
        </p>
      </div>

      {/* Action Buttons */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between',
        alignItems: 'center',
        gap: '12px', 
        marginBottom: '32px' 
      }}>
        {/* Network Status */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          fontSize: '14px',
          color: isOnline ? '#10B981' : '#9CA3AF'
        }}>
          <div style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            backgroundColor: isOnline ? '#10B981' : '#9CA3AF'
          }} />
          {isOnline ? 'Online - Ready for Live Trading' : 'Offline - Simulation Only'}
        </div>

        <div style={{ display: 'flex', gap: '12px' }}>
          {hasChanges && (
            <button
              onClick={handleResetSettings}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '12px 20px',
                backgroundColor: 'transparent',
                border: '1px solid #6B7280',
                borderRadius: '8px',
                color: '#9CA3AF',
                fontSize: '14px',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'all 0.2s ease'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = '#9CA3AF'
                e.currentTarget.style.color = '#ffffff'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = '#6B7280'
                e.currentTarget.style.color = '#9CA3AF'
              }}
            >
              <RotateCcw size={16} />
              Reset Changes
            </button>
          )}
          
          <button
            onClick={handleSaveSettings}
            disabled={!hasChanges || isSaving}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '12px 24px',
              backgroundColor: hasChanges && !isSaving ? '#00D4AA' : '#6B7280',
              border: 'none',
              borderRadius: '8px',
              color: '#ffffff',
              fontSize: '14px',
              fontWeight: '600',
              cursor: hasChanges && !isSaving ? 'pointer' : 'not-allowed',
              opacity: hasChanges && !isSaving ? 1 : 0.5,
              transition: 'all 0.2s ease'
            }}
            title={socket?.connected ? 'Save to file and sync with server' : 'Save to local file (backend disconnected)'}
          >
            <Save size={16} />
            {isSaving ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </div>

      {/* Execution Settings */}
      <div style={cardStyle}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
          <div style={{ 
            backgroundColor: '#00D4AA20', 
            borderRadius: '12px', 
            padding: '12px',
            color: '#00D4AA'
          }}>
            <SettingsIcon size={24} />
          </div>
          <div>
            <h3 style={{ fontSize: '20px', fontWeight: '600', margin: 0, color: '#ffffff' }}>
              Execution Settings
            </h3>
            <p style={{ fontSize: '14px', color: '#9CA3AF', margin: 0 }}>
              Core trading behavior and safety controls
            </p>
          </div>
        </div>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '16px' }}>
          <ToggleSwitch
            id="simulation_mode"
            checked={settings.SIMULATION_MODE}
            onChange={(value) => {
              handleInputChange('SIMULATION_MODE', value)
              // Always ensure the opposite mode is set to the inverse
              handleInputChange('EXECUTION_MODE', !value)
            }}
            label="Simulation Mode"
            description="Safe testing without real transactions"
            icon={<Shield size={20} />}
            color="#4F46E5"
          />
          
          <ToggleSwitch
            id="execution_mode"
            checked={settings.EXECUTION_MODE}
            onChange={(value) => {
              handleInputChange('EXECUTION_MODE', value)
              // Always ensure the opposite mode is set to the inverse
              handleInputChange('SIMULATION_MODE', !value)
            }}
            label="Live Trading"
            description="Execute real transactions"
            icon={<Zap size={20} />}
            color="#F59E0B"
          />
          
          <ToggleSwitch
            id="safe_mode"
            checked={settings.SAFE_MODE}
            onChange={(value) => handleInputChange('SAFE_MODE', value)}
            label="Safe Mode"
            description="Restrict to small amounts and major tokens"
            icon={<Lock size={20} />}
            color="#10B981"
          />
          
          <ToggleSwitch
            id="flash_loan_enabled"
            checked={settings.FLASH_LOAN_ENABLED}
            onChange={(value) => handleInputChange('FLASH_LOAN_ENABLED', value)}
            label="Flash Loans"
            description="Enable capital-efficient arbitrage"
            icon={<Activity size={20} />}
            color="#8B5CF6"
          />
        </div>
      </div>

      {/* Profit & Risk Settings */}
      <div style={cardStyle}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
          <div style={{ 
            backgroundColor: '#00D4AA20', 
            borderRadius: '12px', 
            padding: '12px',
            color: '#00D4AA'
          }}>
            <TrendingUp size={24} />
          </div>
          <div>
            <h3 style={{ fontSize: '20px', fontWeight: '600', margin: 0, color: '#ffffff' }}>
              Profit & Risk Management
            </h3>
            <p style={{ fontSize: '14px', color: '#9CA3AF', margin: 0 }}>
              Define profit thresholds and position sizing
            </p>
          </div>
        </div>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
          <NumberInput
            id="min_profit_pct"
            value={settings.MIN_PROFIT_PCT}
            onChange={(value) => handleInputChange('MIN_PROFIT_PCT', value)}
            label="Minimum Profit"
            description="Ignore opportunities below this threshold"
            min={0.1}
            max={50}
            step={0.1}
            unit="%"
            icon={<Target size={20} />}
            color="#00D4AA"
          />
          
          <NumberInput
            id="max_profit_pct"
            value={settings.MAX_PROFIT_PCT}
            onChange={(value) => handleInputChange('MAX_PROFIT_PCT', value)}
            label="Maximum Profit"
            description="Flag unrealistic opportunities above this"
            min={1}
            max={500}
            step={1}
            unit="%"
            icon={<AlertTriangle size={20} />}
            color="#F59E0B"
          />
          
          <NumberInput
            id="position_size_usd"
            value={settings.POSITION_SIZE_USD}
            onChange={(value) => handleInputChange('POSITION_SIZE_USD', value)}
            label="Position Size"
            description="USD amount per arbitrage trade"
            min={1}
            max={10000}
            step={1}
            unit="USD"
            icon={<DollarSign size={20} />}
            color="#10B981"
          />
          
          <NumberInput
            id="min_liquidity_usd"
            value={settings.MIN_LIQUIDITY_USD}
            onChange={(value) => handleInputChange('MIN_LIQUIDITY_USD', value)}
            label="Minimum Liquidity"
            description="Required pool depth for safe trading"
            min={1000}
            max={10000000}
            step={1000}
            unit="USD"
            icon={<Gauge size={20} />}
            color="#6366F1"
          />
        </div>
      </div>

      {/* Trading Parameters */}
      <div style={cardStyle}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
          <div style={{ 
            backgroundColor: '#4F46E520', 
            borderRadius: '12px', 
            padding: '12px',
            color: '#4F46E5'
          }}>
            <Activity size={24} />
          </div>
          <div>
            <h3 style={{ fontSize: '20px', fontWeight: '600', margin: 0, color: '#ffffff' }}>
              Trading Parameters
            </h3>
            <p style={{ fontSize: '14px', color: '#9CA3AF', margin: 0 }}>
              Fine-tune execution behavior and costs
            </p>
          </div>
        </div>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
          <NumberInput
            id="max_slippage"
            value={settings.MAX_SLIPPAGE * 100}
            onChange={(value) => handleInputChange('MAX_SLIPPAGE', value / 100)}
            label="Maximum Slippage"
            description="Price movement tolerance during execution"
            min={0.1}
            max={10}
            step={0.1}
            unit="%"
            icon={<Gauge size={20} />}
            color="#F59E0B"
          />
          
          <NumberInput
            id="mev_protection_cost"
            value={settings.MEV_PROTECTION_COST_USD}
            onChange={(value) => handleInputChange('MEV_PROTECTION_COST_USD', value)}
            label="MEV Protection"
            description="Estimated MEV protection cost per trade"
            min={0.1}
            max={50}
            step={0.1}
            unit="USD"
            icon={<Shield size={20} />}
            color="#8B5CF6"
          />
          
          <NumberInput
            id="min_profit_threshold"
            value={settings.MIN_PROFIT_THRESHOLD_USD}
            onChange={(value) => handleInputChange('MIN_PROFIT_THRESHOLD_USD', value)}
            label="Profit Threshold"
            description="Minimum USD profit to execute trade"
            min={0.01}
            max={100}
            step={0.01}
            unit="USD"
            icon={<DollarSign size={20} />}
            color="#10B981"
          />
          
          <NumberInput
            id="base_gas_price"
            value={settings.BASE_GAS_PRICE_GWEI}
            onChange={(value) => handleInputChange('BASE_GAS_PRICE_GWEI', value)}
            label="Base Gas Price"
            description="Network gas price in Gwei"
            min={1000}
            max={10000000}
            step={1000}
            unit="Gwei"
            icon={<Zap size={20} />}
            color="#F59E0B"
          />
        </div>
      </div>

      {/* Flash Loan Settings */}
      <div style={cardStyle}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
          <div style={{ 
            backgroundColor: '#8B5CF620', 
            borderRadius: '12px', 
            padding: '12px',
            color: '#8B5CF6'
          }}>
            <Activity size={24} />
          </div>
          <div>
            <h3 style={{ fontSize: '20px', fontWeight: '600', margin: 0, color: '#ffffff' }}>
              Flash Loan Configuration
            </h3>
            <p style={{ fontSize: '14px', color: '#9CA3AF', margin: 0 }}>
              Advanced capital efficiency settings
            </p>
          </div>
        </div>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
          <NumberInput
            id="flash_loan_amount"
            value={settings.FLASH_LOAN_AMOUNT_USD}
            onChange={(value) => handleInputChange('FLASH_LOAN_AMOUNT_USD', value)}
            label="Flash Loan Amount"
            description="Capital to borrow for arbitrage execution"
            min={1000}
            max={1000000}
            step={1000}
            unit="USD"
            icon={<DollarSign size={20} />}
            color="#8B5CF6"
          />
        </div>
      </div>

      {/* Safety Warning */}
      <div style={{
        backgroundColor: '#F59E0B20',
        border: '1px solid #F59E0B',
        borderRadius: '12px',
        padding: '20px',
        marginBottom: '24px'
      }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '16px' }}>
          <div style={{ 
            backgroundColor: '#F59E0B30', 
            borderRadius: '8px', 
            padding: '8px',
            color: '#F59E0B'
          }}>
            <AlertTriangle size={20} />
          </div>
          <div>
            <h4 style={{ fontSize: '16px', fontWeight: '600', color: '#F59E0B', margin: '0 0 8px 0' }}>
              Safety Reminder
            </h4>
            <p style={{ fontSize: '14px', color: '#FCD34D', margin: 0, lineHeight: '1.5' }}>
              Always test with Simulation Mode enabled before live trading. Start with small position sizes 
              and gradually increase as you gain confidence. These settings directly affect your trading 
              behavior and financial risk.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Settings
