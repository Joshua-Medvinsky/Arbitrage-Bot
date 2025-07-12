import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'

// Hide the initial loader once React is ready
const hideInitialLoader = () => {
  const loader = document.getElementById('initial-loader')
  if (loader) {
    loader.style.opacity = '0'
    loader.style.transition = 'opacity 0.3s ease-out'
    setTimeout(() => loader.remove(), 300)
  }
}

// Show the Tauri window once the app is ready
const showTauriWindow = async () => {
  try {
    const { appWindow } = await import('@tauri-apps/api/window')
    await appWindow.show()
    await appWindow.setFocus()
  } catch (error) {
    // Not running in Tauri environment, ignore
    console.log('Not running in Tauri environment')
  }
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <App />
)

// Hide loader and show window after React has mounted
hideInitialLoader()
showTauriWindow()
