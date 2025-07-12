// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use tauri::{CustomMenuItem, SystemTray, SystemTrayMenu, SystemTrayEvent};
use tauri::{Manager, WindowEvent, State};
use std::process::{Command, Child, Stdio};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Duration;
use serde_json::json;

// Shared state for the Python process
#[derive(Debug, Clone)]
struct PythonProcess(Arc<Mutex<Option<Child>>>);

// Shared state for the arbitrage bot process
#[derive(Debug, Clone)]
struct ArbitrageBot(Arc<Mutex<Option<Child>>>);

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
async fn start_python_backend(state: State<'_, PythonProcess>) -> Result<String, String> {
    let mut process_guard = state.0.lock().map_err(|e| format!("Failed to lock state: {}", e))?;
    
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
    
    // Reduced startup delay - check if process is actually running
    thread::sleep(Duration::from_millis(500)); // Reduced from 2000ms
    
    Ok("Python backend started successfully".to_string())
}

#[tauri::command]
async fn stop_python_backend(state: State<'_, PythonProcess>) -> Result<String, String> {
    let mut process_guard = state.0.lock().map_err(|e| format!("Failed to lock state: {}", e))?;
    
    if let Some(mut child) = process_guard.take() {
        child.kill().map_err(|e| format!("Failed to kill Python process: {}", e))?;
        Ok("Python backend stopped".to_string())
    } else {
        Ok("Python backend was not running".to_string())
    }
}

#[tauri::command]
async fn get_backend_status(state: State<'_, PythonProcess>) -> Result<bool, String> {
    let process_guard = state.0.lock().map_err(|e| format!("Failed to lock state: {}", e))?;
    Ok(process_guard.is_some())
}

#[tauri::command]
async fn start_arbitrage_bot(state: State<'_, ArbitrageBot>, app_handle: tauri::AppHandle) -> Result<String, String> {
    let mut process_guard = state.0.lock().map_err(|e| format!("Failed to lock state: {}", e))?;
    
    if process_guard.is_some() {
        return Ok("Arbitrage bot is already running".to_string());
    }

    // Start the arbitrage bot Python script
    // Get the current working directory and construct the path to the script
    let current_dir = std::env::current_dir().map_err(|e| format!("Failed to get current directory: {}", e))?;
    let script_path = if current_dir.ends_with("src-tauri") {
        // Running from frontend/src-tauri (development mode)
        current_dir.parent().unwrap().parent().unwrap().join("scripts/monitoring/arbitrage_bot.py")
    } else {
        // Running from project root or other location
        current_dir.join("scripts/monitoring/arbitrage_bot.py")
    };
    
    let mut child = Command::new("python")
        .arg("-u") // Force unbuffered stdout/stderr
        .arg(&script_path)
        .env("PYTHONIOENCODING", "utf-8") // Set UTF-8 encoding for Python
        .stdout(Stdio::piped())
        .stderr(Stdio::null()) // Completely ignore stderr to test for duplicates
        .spawn()
        .map_err(|e| format!("Failed to start arbitrage bot at {:?}: {}", script_path, e))?;

    // Capture ONLY stdout for logging
    if let Some(stdout) = child.stdout.take() {
        let app_handle_clone = app_handle.clone();
        thread::spawn(move || {
            use std::io::{BufRead, BufReader};
            let reader = BufReader::new(stdout);
            for line in reader.lines() {
                if let Ok(line) = line {
                    // Clean and filter the log message
                    let cleaned_line = line.trim();
                    if !cleaned_line.is_empty() && !cleaned_line.starts_with("print(") {
                        // Send log to frontend via window event to main window only
                        if let Some(window) = app_handle_clone.get_window("main") {
                            let _ = window.emit("bot-log", json!({
                                "level": "info",
                                "message": cleaned_line,
                                "timestamp": chrono::Utc::now().timestamp_millis(),
                                "source": "arbitrage_bot.py"
                            }));
                        }
                    }
                }
            }
        });
    }

    *process_guard = Some(child);
    
    Ok("Arbitrage bot started successfully".to_string())
}

#[tauri::command]
async fn stop_arbitrage_bot(state: State<'_, ArbitrageBot>) -> Result<String, String> {
    let mut process_guard = state.0.lock().map_err(|e| format!("Failed to lock state: {}", e))?;
    
    if let Some(mut child) = process_guard.take() {
        child.kill().map_err(|e| format!("Failed to kill arbitrage bot process: {}", e))?;
        Ok("Arbitrage bot stopped".to_string())
    } else {
        Ok("Arbitrage bot was not running".to_string())
    }
}

#[tauri::command]
async fn get_arbitrage_bot_status(state: State<'_, ArbitrageBot>) -> Result<bool, String> {
    let process_guard = state.0.lock().map_err(|e| format!("Failed to lock state: {}", e))?;
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
    let python_process_state = PythonProcess(Arc::new(Mutex::new(None)));
    // Initialize shared state for arbitrage bot process
    let arbitrage_bot_state = ArbitrageBot(Arc::new(Mutex::new(None)));

    tauri::Builder::default()
        .manage(python_process_state.clone())
        .manage(arbitrage_bot_state.clone())
        .system_tray(system_tray)
        .on_system_tray_event(move |app, event| match event {
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
                    let state = app.state::<PythonProcess>();
                    if let Ok(mut process_guard) = state.0.lock() {
                        if let Some(mut child) = process_guard.take() {
                            let _ = child.kill();
                        }
                    }
                    // Clean up arbitrage bot process before quitting
                    let bot_state = app.state::<ArbitrageBot>();
                    if let Ok(mut process_guard) = bot_state.0.lock() {
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
            let arbitrage_bot_state = arbitrage_bot_state.clone();
            move |event| match event.event() {
                WindowEvent::CloseRequested { .. } => {
                    // Clean up Python process and actually close the app
                    if let Ok(mut process_guard) = python_process_state.0.lock() {
                        if let Some(mut child) = process_guard.take() {
                            let _ = child.kill();
                        }
                    }
                    // Clean up arbitrage bot process
                    if let Ok(mut process_guard) = arbitrage_bot_state.0.lock() {
                        if let Some(mut child) = process_guard.take() {
                            let _ = child.kill();
                        }
                    }
                    // Allow the window to close normally (don't prevent close)
                }
                WindowEvent::Destroyed => {
                    // Clean up Python process when window is destroyed
                    if let Ok(mut process_guard) = python_process_state.0.lock() {
                        if let Some(mut child) = process_guard.take() {
                            let _ = child.kill();
                        }
                    }
                    // Clean up arbitrage bot process when window is destroyed
                    if let Ok(mut process_guard) = arbitrage_bot_state.0.lock() {
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
            get_backend_status,
            start_arbitrage_bot,
            stop_arbitrage_bot,
            get_arbitrage_bot_status
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
