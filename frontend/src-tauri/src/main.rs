// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use tauri::{CustomMenuItem, SystemTray, SystemTrayMenu, SystemTrayEvent};
use tauri::{Manager, WindowEvent, State};
use std::process::{Command, Child, Stdio};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Duration;

// Shared state for the Python process
type PythonProcessState = Arc<Mutex<Option<Child>>>;

// Learn more about Tauri commands at https://tauri.app/v1/guides/features/command
#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

#[tauri::command]
fn show_notification(title: &str, body: &str) {
    tauri::api::notification::Notification::new("com.arbitragebot.app")
        .title(title)
        .body(body)
        .show()
        .unwrap();
}

#[tauri::command]
async fn start_python_backend(state: State<'_, PythonProcessState>) -> Result<String, String> {
    let mut process_guard = state.lock().map_err(|e| format!("Failed to lock state: {}", e))?;
    
    if process_guard.is_some() {
        return Ok("Python backend is already running".to_string());
    }

    // Try to find the bundled executable first, then fall back to Python
    let child = if cfg!(target_os = "windows") && std::path::Path::new("arbitrage-bot-server.exe").exists() {
        // Windows executable
        Command::new("arbitrage-bot-server.exe")
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .spawn()
            .map_err(|e| format!("Failed to start bundled backend: {}", e))?
    } else if std::path::Path::new("arbitrage-bot-server").exists() {
        // Unix/Linux/macOS executable
        Command::new("./arbitrage-bot-server")
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .spawn()
            .map_err(|e| format!("Failed to start bundled backend: {}", e))?
    } else {
        // Fall back to Python script
        Command::new("python")
            .arg("../websocket_server.py")
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .spawn()
            .map_err(|e| format!("Failed to start Python backend: {}", e))?
    };

    *process_guard = Some(child);
    
    // Give the server a moment to start
    thread::sleep(Duration::from_millis(2000));
    
    Ok("Python backend started successfully".to_string())
}

#[tauri::command]
async fn stop_python_backend(state: State<'_, PythonProcessState>) -> Result<String, String> {
    let mut process_guard = state.lock().map_err(|e| format!("Failed to lock state: {}", e))?;
    
    if let Some(mut child) = process_guard.take() {
        child.kill().map_err(|e| format!("Failed to kill Python process: {}", e))?;
        Ok("Python backend stopped".to_string())
    } else {
        Ok("Python backend was not running".to_string())
    }
}

#[tauri::command]
async fn get_backend_status(state: State<'_, PythonProcessState>) -> Result<bool, String> {
    let process_guard = state.lock().map_err(|e| format!("Failed to lock state: {}", e))?;
    Ok(process_guard.is_some())
}

fn main() {
    // System tray menu
    let quit = CustomMenuItem::new("quit".to_string(), "Quit");
    let show = CustomMenuItem::new("show".to_string(), "Show");
    let hide = CustomMenuItem::new("hide".to_string(), "Hide");
    let tray_menu = SystemTrayMenu::new()
        .add_item(show)
        .add_item(hide)
        .add_native_item(tauri::SystemTrayMenuItem::Separator)
        .add_item(quit);

    let system_tray = SystemTray::new().with_menu(tray_menu);

    // Initialize shared state for Python process
    let python_process_state: PythonProcessState = Arc::new(Mutex::new(None));

    tauri::Builder::default()
        .manage(python_process_state.clone())
        .system_tray(system_tray)
        .on_system_tray_event(|app, event| match event {
            SystemTrayEvent::LeftClick {
                position: _,
                size: _,
                ..
            } => {
                let window = app.get_window("main").unwrap();
                window.show().unwrap();
                window.set_focus().unwrap();
            }
            SystemTrayEvent::MenuItemClick { id, .. } => match id.as_str() {
                "quit" => {
                    // Clean up Python process before quitting
                    let state = app.state::<PythonProcessState>();
                    if let Ok(mut process_guard) = state.lock() {
                        if let Some(mut child) = process_guard.take() {
                            let _ = child.kill();
                        }
                    }
                    std::process::exit(0);
                }
                "show" => {
                    let window = app.get_window("main").unwrap();
                    window.show().unwrap();
                    window.set_focus().unwrap();
                }
                "hide" => {
                    let window = app.get_window("main").unwrap();
                    window.hide().unwrap();
                }
                _ => {}
            },
            _ => {}
        })
        .on_window_event({
            let python_process_state = python_process_state.clone();
            move |event| match event.event() {
                WindowEvent::CloseRequested { .. } => {
                    // Clean up Python process and actually close the app
                    if let Ok(mut process_guard) = python_process_state.lock() {
                        if let Some(mut child) = process_guard.take() {
                            let _ = child.kill();
                        }
                    }
                    // Allow the window to close normally (don't prevent close)
                }
                WindowEvent::Destroyed => {
                    // Clean up Python process when window is destroyed
                    if let Ok(mut process_guard) = python_process_state.lock() {
                        if let Some(mut child) = process_guard.take() {
                            let _ = child.kill();
                        }
                    }
                }
                _ => {}
            }
        })
        .invoke_handler(tauri::generate_handler![
            greet, 
            show_notification, 
            start_python_backend, 
            stop_python_backend, 
            get_backend_status
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
