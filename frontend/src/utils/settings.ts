import { invoke } from '@tauri-apps/api/tauri'

export interface SettingsData {
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

const DEFAULT_SETTINGS: SettingsData = {
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
}

/**
 * Parse .env file content into settings object
 */
function parseEnvContent(content: string): SettingsData {
  const settings = { ...DEFAULT_SETTINGS }
  
  const lines = content.split('\n')
  for (const line of lines) {
    const trimmed = line.trim()
    if (trimmed && !trimmed.startsWith('#')) {
      const [key, value] = trimmed.split('=')
      if (key && value && key in settings) {
        const settingKey = key as keyof SettingsData
        const settingValue = value.replace(/"/g, '').trim()
        
        if (typeof settings[settingKey] === 'boolean') {
          (settings as any)[settingKey] = settingValue.toLowerCase() === 'true'
        } else if (typeof settings[settingKey] === 'number') {
          const numValue = parseFloat(settingValue)
          if (!isNaN(numValue)) {
            (settings as any)[settingKey] = numValue
          }
        }
      }
    }
  }
  
  return settings
}

/**
 * Convert settings object to .env file content, preserving comments and formatting
 */
function formatEnvContent(settings: SettingsData, existingContent?: string): string {
  const lines: string[] = []
  
  if (existingContent) {
    // Preserve existing file structure and comments
    const existingLines = existingContent.split('\n')
    const settingKeys = Object.keys(settings) as (keyof SettingsData)[]
    const usedKeys = new Set<string>()
    
    for (const line of existingLines) {
      const trimmed = line.trim()
      if (!trimmed || trimmed.startsWith('#')) {
        // Keep comments and empty lines
        lines.push(line)
      } else {
        const [key] = trimmed.split('=')
        if (key && settingKeys.includes(key as keyof SettingsData)) {
          // Update existing setting
          const value = settings[key as keyof SettingsData]
          lines.push(`${key}=${value}`)
          usedKeys.add(key)
        } else {
          // Keep other environment variables
          lines.push(line)
        }
      }
    }
    
    // Add any new settings that weren't in the original file
    for (const key of settingKeys) {
      if (!usedKeys.has(key)) {
        lines.push(`${key}=${settings[key]}`)
      }
    }
  } else {
    // Create new file with all settings
    lines.push('# Arbitrage Bot Configuration')
    lines.push('')
    lines.push('# Execution Settings')
    lines.push(`SIMULATION_MODE=${settings.SIMULATION_MODE}`)
    lines.push(`FLASH_LOAN_ENABLED=${settings.FLASH_LOAN_ENABLED}`)
    lines.push(`SAFE_MODE=${settings.SAFE_MODE}`)
    lines.push(`EXECUTION_MODE=${settings.EXECUTION_MODE}`)
    lines.push('')
    lines.push('# Profit & Risk Management')
    lines.push(`MIN_PROFIT_PCT=${settings.MIN_PROFIT_PCT}`)
    lines.push(`MAX_PROFIT_PCT=${settings.MAX_PROFIT_PCT}`)
    lines.push(`POSITION_SIZE_USD=${settings.POSITION_SIZE_USD}`)
    lines.push(`MIN_LIQUIDITY_USD=${settings.MIN_LIQUIDITY_USD}`)
    lines.push('')
    lines.push('# Trading Parameters')
    lines.push(`MAX_SLIPPAGE=${settings.MAX_SLIPPAGE}`)
    lines.push(`MEV_PROTECTION_COST_USD=${settings.MEV_PROTECTION_COST_USD}`)
    lines.push(`MIN_PROFIT_THRESHOLD_USD=${settings.MIN_PROFIT_THRESHOLD_USD}`)
    lines.push(`BASE_GAS_PRICE_GWEI=${settings.BASE_GAS_PRICE_GWEI}`)
    lines.push('')
    lines.push('# Flash Loan Configuration')
    lines.push(`FLASH_LOAN_AMOUNT_USD=${settings.FLASH_LOAN_AMOUNT_USD}`)
  }
  
  return lines.join('\n')
}

/**
 * Load settings from local .env file
 */
export async function loadSettings(): Promise<SettingsData> {
  try {
    const content = await invoke<string>('read_settings_file')
    return parseEnvContent(content)
  } catch (error) {
    console.warn('Failed to load settings from file, using defaults:', error)
    return DEFAULT_SETTINGS
  }
}

/**
 * Save settings to local .env file
 */
export async function saveSettings(settings: SettingsData): Promise<{ success: boolean; message: string }> {
  try {
    // Read existing content to preserve formatting
    let existingContent: string | undefined
    try {
      existingContent = await invoke<string>('read_settings_file')
    } catch {
      // File doesn't exist yet, that's okay
    }
    
    // Format new content preserving structure
    const newContent = formatEnvContent(settings, existingContent)
    
    // Write to file
    await invoke('write_settings_file', { content: newContent })
    
    console.log('Settings saved to local file successfully')
    return { success: true, message: 'Settings saved successfully' }
  } catch (error) {
    console.error('Failed to save settings to file:', error)
    return { success: false, message: `Failed to save settings: ${error}` }
  }
}

/**
 * Notify server of settings changes (optional, for real-time updates)
 */
export async function notifyServerOfSettingsChange(settings: SettingsData, socket?: any): Promise<void> {
  if (socket && socket.connected) {
    try {
      console.log('Notifying server of settings change...')
      socket.emit('update_settings', settings)
    } catch (error) {
      console.warn('Failed to notify server of settings change (server offline):', error)
    }
  } else {
    console.log('Server offline, settings saved locally only')
  }
}

/**
 * Complete settings save operation with local-first approach
 */
export async function saveSettingsWithServerSync(
  settings: SettingsData, 
  socket?: any
): Promise<{ success: boolean; message: string }> {
  // 1. Save locally first (always works)
  const localResult = await saveSettings(settings)
  
  if (!localResult.success) {
    return localResult
  }
  
  // 2. Notify server if available (optional)
  await notifyServerOfSettingsChange(settings, socket)
  
  return { success: true, message: 'Settings saved successfully' }
}
