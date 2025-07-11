// Desktop and mobile utilities
import { useState, useEffect } from 'react'

// Check if running in Tauri (desktop app)
export const isTauri = () => {
  return typeof window !== 'undefined' && window.__TAURI__ !== undefined
}

// Check if running on mobile device
export const isMobile = () => {
  return typeof window !== 'undefined' && 
    /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)
}

// Platform-specific notifications
export const showNotification = async (title: string, body: string) => {
  if (isTauri()) {
    // Use Tauri's notification system
    const { invoke } = await import('@tauri-apps/api/tauri')
    await invoke('show_notification', { title, body })
  } else {
    // Use browser notifications
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification(title, { body })
    } else if ('Notification' in window && Notification.permission !== 'denied') {
      // Request permission first
      const permission = await Notification.requestPermission()
      if (permission === 'granted') {
        new Notification(title, { body })
      }
    }
  }
}

// Platform-specific storage
export const useStorage = (key: string, defaultValue: any) => {
  const [value, setValue] = useState(defaultValue)

  useEffect(() => {
    const loadValue = async () => {
      try {
        if (isTauri()) {
          // Use Tauri's file system
          const { invoke } = await import('@tauri-apps/api/tauri')
          const stored = await invoke('get_storage', { key })
          setValue(stored || defaultValue)
        } else {
          // Use localStorage
          const stored = localStorage.getItem(key)
          setValue(stored ? JSON.parse(stored) : defaultValue)
        }
      } catch (error) {
        console.error('Error loading storage:', error)
        setValue(defaultValue)
      }
    }

    loadValue()
  }, [key, defaultValue])

  const updateValue = async (newValue: any) => {
    setValue(newValue)
    
    try {
      if (isTauri()) {
        const { invoke } = await import('@tauri-apps/api/tauri')
        await invoke('set_storage', { key, value: newValue })
      } else {
        localStorage.setItem(key, JSON.stringify(newValue))
      }
    } catch (error) {
      console.error('Error saving to storage:', error)
    }
  }

  return [value, updateValue]
}

// Platform-specific window controls
export const useWindowControls = () => {
  const minimize = async () => {
    if (isTauri()) {
      const { appWindow } = await import('@tauri-apps/api/window')
      await appWindow.minimize()
    }
  }

  const maximize = async () => {
    if (isTauri()) {
      const { appWindow } = await import('@tauri-apps/api/window')
      await appWindow.toggleMaximize()
    }
  }

  const close = async () => {
    if (isTauri()) {
      const { appWindow } = await import('@tauri-apps/api/window')
      await appWindow.hide() // Hide instead of close to keep running in system tray
    }
  }

  return { minimize, maximize, close }
}

// Platform-specific styling
export const getPlatformClasses = () => {
  const classes = []
  
  if (isTauri()) classes.push('platform-desktop')
  if (isMobile()) classes.push('platform-mobile')
  
  return classes.join(' ')
}
