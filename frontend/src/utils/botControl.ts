import { invoke } from '@tauri-apps/api/tauri'
import { loadSettings, saveSettings } from './settings'

export interface LocalBotState {
  isRunning: boolean
  mode: 'simulation' | 'live'
  safeMode: boolean
  lastStartTime?: number
  sessionTrades: number
  sessionProfit: number
}

const DEFAULT_BOT_STATE: LocalBotState = {
  isRunning: false,
  mode: 'live', // Default to live mode to match .env default (SIMULATION_MODE=false)
  safeMode: true,
  sessionTrades: 0,
  sessionProfit: 0
}

/**
 * Get bot status from both local state and Tauri backend
 */
export async function getBotStatus(): Promise<LocalBotState> {
  try {
    // Get local settings for mode/safeMode - this should work offline
    const settings = await loadSettings()
    
    // Try to get actual bot running status from Tauri
    let isRunning = false
    try {
      isRunning = await invoke<boolean>('get_arbitrage_bot_status')
    } catch (error) {
      console.warn('Could not get bot running status from Tauri, assuming stopped:', error)
      // When Tauri is not available, assume bot is not running
      isRunning = false
    }
    
    // Load session data from local storage
    const sessionData = localStorage.getItem('bot_session_data')
    const session = sessionData ? JSON.parse(sessionData) : {}
    
    // Determine mode from settings - SIMULATION_MODE=false means live mode
    const mode = settings.SIMULATION_MODE === true ? 'simulation' : 'live'
    
    return {
      isRunning,
      mode,
      safeMode: settings.SAFE_MODE !== false, // Default to true if not specified
      lastStartTime: session.lastStartTime,
      sessionTrades: session.sessionTrades || 0,
      sessionProfit: session.sessionProfit || 0
    }
  } catch (error) {
    console.error('Failed to get bot status:', error)
    // If everything fails, return a safe default state
    return {
      ...DEFAULT_BOT_STATE,
      mode: 'live' // Default to live mode to show proper warnings when offline
    }
  }
}

/**
 * Start bot with offline-first approach
 */
export async function startBotLocal(): Promise<{ success: boolean; message: string }> {
  try {
    // Start the bot via Tauri
    const result = await invoke<string>('start_arbitrage_bot')
    
    // Update session data
    const sessionData = {
      lastStartTime: Date.now(),
      sessionTrades: 0,
      sessionProfit: 0
    }
    localStorage.setItem('bot_session_data', JSON.stringify(sessionData))
    
    return { success: true, message: result }
  } catch (error) {
    console.error('Failed to start bot:', error)
    return { success: false, message: `Failed to start bot: ${error}` }
  }
}

/**
 * Stop bot with offline-first approach
 */
export async function stopBotLocal(): Promise<{ success: boolean; message: string }> {
  try {
    const result = await invoke<string>('stop_arbitrage_bot')
    return { success: true, message: result }
  } catch (error) {
    console.error('Failed to stop bot:', error)
    return { success: false, message: `Failed to stop bot: ${error}` }
  }
}

/**
 * Toggle trading mode (simulation/live) with local persistence
 */
export async function toggleTradingMode(): Promise<{ success: boolean; message: string; newMode: 'simulation' | 'live' }> {
  try {
    const settings = await loadSettings()
    
    // Toggle mode
    const newSimulationMode = !settings.SIMULATION_MODE
    const newExecutionMode = !newSimulationMode
    
    const updatedSettings = {
      ...settings,
      SIMULATION_MODE: newSimulationMode,
      EXECUTION_MODE: newExecutionMode
    }
    
    const result = await saveSettings(updatedSettings)
    
    if (result.success) {
      const newMode = newSimulationMode ? 'simulation' : 'live'
      return { 
        success: true, 
        message: `Switched to ${newMode} mode`, 
        newMode 
      }
    } else {
      return { success: false, message: result.message, newMode: 'simulation' }
    }
  } catch (error) {
    console.error('Failed to toggle trading mode:', error)
    return { 
      success: false, 
      message: `Failed to toggle mode: ${error}`, 
      newMode: 'simulation' 
    }
  }
}

/**
 * Toggle safe mode with local persistence
 */
export async function toggleSafeMode(): Promise<{ success: boolean; message: string; newSafeMode: boolean }> {
  try {
    const settings = await loadSettings()
    
    const newSafeMode = !settings.SAFE_MODE
    const updatedSettings = {
      ...settings,
      SAFE_MODE: newSafeMode
    }
    
    const result = await saveSettings(updatedSettings)
    
    if (result.success) {
      return { 
        success: true, 
        message: `Safe mode ${newSafeMode ? 'enabled' : 'disabled'}`, 
        newSafeMode 
      }
    } else {
      return { success: false, message: result.message, newSafeMode: settings.SAFE_MODE }
    }
  } catch (error) {
    console.error('Failed to toggle safe mode:', error)
    return { 
      success: false, 
      message: `Failed to toggle safe mode: ${error}`, 
      newSafeMode: true 
    }
  }
}

/**
 * Get uptime calculation
 */
export function calculateUptime(lastStartTime?: number): number {
  if (!lastStartTime) return 0
  return Math.floor((Date.now() - lastStartTime) / 1000)
}

/**
 * Update session statistics
 */
export function updateSessionStats(trades: number, profit: number): void {
  const sessionData = {
    lastStartTime: Date.now(),
    sessionTrades: trades,
    sessionProfit: profit
  }
  localStorage.setItem('bot_session_data', JSON.stringify(sessionData))
}

/**
 * Notify server of local changes when it comes back online
 */
export function syncWithServer(socket: any, botState: LocalBotState): void {
  if (socket?.connected) {
    try {
      // Sync current state with server
      socket.emit('sync_bot_state', {
        isRunning: botState.isRunning,
        mode: botState.mode,
        safeMode: botState.safeMode,
        sessionTrades: botState.sessionTrades,
        sessionProfit: botState.sessionProfit
      })
      console.log('Bot state synced with server')
    } catch (error) {
      console.warn('Failed to sync bot state with server:', error)
    }
  }
}
