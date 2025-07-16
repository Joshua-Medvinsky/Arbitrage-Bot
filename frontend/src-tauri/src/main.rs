// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use tauri::{CustomMenuItem, SystemTray, SystemTrayMenu, SystemTrayEvent};
use tauri::{Manager, WindowEvent, State};
use std::process::{Command, Child, Stdio};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Duration;
use serde_json::json;
use std::fs;
use std::path::PathBuf;
use serde::{Deserialize, Serialize};
use chrono;

// Shared state for the Python process
#[derive(Debug, Clone)]
struct PythonProcess(Arc<Mutex<Option<Child>>>);

// Shared state for the arbitrage bot process
#[derive(Debug, Clone)]
struct ArbitrageBot(Arc<Mutex<Option<Child>>>);

// Monitoring stats structure for frontend
#[derive(Serialize, Deserialize, Clone)]
struct MonitoringStats {
    #[serde(rename = "startTime")]
    start_time: i64,
    #[serde(rename = "loopCount")]
    loop_count: i64,
    #[serde(rename = "totalOpportunitiesFound")]
    total_opportunities_found: i64,
    #[serde(rename = "opportunitiesExecuted")]
    opportunities_executed: i64,
    #[serde(rename = "totalProfitUsd")]
    total_profit_usd: f64,
    errors: i64,
    #[serde(rename = "avgExecutionTime")]
    avg_execution_time: f64,
    #[serde(rename = "opportunitiesPerHour")]
    opportunities_per_hour: f64,
    uptime: i64, // Uptime in seconds
    #[serde(rename = "lastOpportunityTime")]
    last_opportunity_time: Option<i64>,
    #[serde(rename = "bestOpportunity")]
    best_opportunity: Option<BestOpportunity>,
}

#[derive(Serialize, Deserialize, Clone)]
struct BestOpportunity {
    pair: String,
    #[serde(rename = "buyDex")]
    buy_dex: String,
    #[serde(rename = "sellDex")]
    sell_dex: String,
    #[serde(rename = "profitUsd")]
    profit_usd: f64,
    #[serde(rename = "profitPct")]
    profit_pct: f64,
    time: i64,
}

// Learn more about Tauri commands at https://tauri.app/v1/guides/features/command
#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

#[tauri::command]
async fn test_monitoring_command() -> Result<String, String> {
    Ok("Test monitoring command works!".to_string())
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
            .arg("../socketio_server.py")
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
    
    // Check if script file exists
    if !script_path.exists() {
        return Err(format!("Arbitrage bot script not found at: {:?}", script_path));
    }
    
    // Try to find the right Python command for the platform
    let python_cmd = if cfg!(target_os = "windows") {
        "python"
    } else {
        // On macOS and Linux, try python3 first, then python
        if Command::new("python3").arg("--version").output().is_ok() {
            "python3"
        } else {
            "python"
        }
    };
    
    // Test if Python command works before starting the script
    if Command::new(python_cmd).arg("--version").output().is_err() {
        return Err(format!("Python command '{}' not found. Please ensure Python is installed and available in PATH.", python_cmd));
    }
    
    let mut child = Command::new(python_cmd)
        .arg("-u") // Force unbuffered stdout/stderr
        .arg(&script_path)
        .env("PYTHONIOENCODING", "utf-8") // Set UTF-8 encoding for Python
        .stdout(Stdio::piped())
        .stderr(Stdio::piped()) // Capture stderr to get error details
        .spawn()
        .map_err(|e| format!("Failed to start arbitrage bot with {} at {:?}: {}", python_cmd, script_path, e))?;

    // Capture BOTH stdout and stderr for logging and error handling
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

    if let Some(stderr) = child.stderr.take() {
        let app_handle_clone = app_handle.clone();
        thread::spawn(move || {
            use std::io::{BufRead, BufReader};
            let reader = BufReader::new(stderr);
            for line in reader.lines() {
                if let Ok(line) = line {
                    let cleaned_line = line.trim();
                    if !cleaned_line.is_empty() {
                        // Send error logs to frontend
                        if let Some(window) = app_handle_clone.get_window("main") {
                            let _ = window.emit("bot-log", json!({
                                "level": "error",
                                "message": format!("ERROR: {}", cleaned_line),
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

#[tauri::command]
async fn read_settings_file() -> Result<String, String> {
    let env_path = get_env_file_path()?;
    
    match fs::read_to_string(&env_path) {
        Ok(content) => Ok(content),
        Err(e) => {
            // If file doesn't exist, return empty string (will create default settings)
            if e.kind() == std::io::ErrorKind::NotFound {
                Ok(String::new())
            } else {
                Err(format!("Failed to read settings file: {}", e))
            }
        }
    }
}

#[tauri::command]
async fn write_settings_file(content: String) -> Result<(), String> {
    let env_path = get_env_file_path()?;
    
    // Ensure parent directory exists
    if let Some(parent) = env_path.parent() {
        fs::create_dir_all(parent).map_err(|e| format!("Failed to create directory: {}", e))?;
    }
    
    fs::write(&env_path, content).map_err(|e| format!("Failed to write settings file: {}", e))?;
    Ok(())
}

fn get_env_file_path() -> Result<PathBuf, String> {
    let current_dir = std::env::current_dir().map_err(|e| format!("Failed to get current directory: {}", e))?;
    
    let env_path = if current_dir.ends_with("src-tauri") {
        // Running from frontend/src-tauri (development mode)
        current_dir.parent().unwrap().parent().unwrap().join(".env")
    } else {
        // Running from project root or other location
        current_dir.join(".env")
    };
    
    Ok(env_path)
}

#[tauri::command]
async fn get_monitoring_stats() -> Result<MonitoringStats, String> {
    // For now, return mock data. In a real implementation, this would read from
    // a shared file or communicate with the Python monitoring script
    let current_time = chrono::Utc::now().timestamp_millis();
    
    // Check if there's a monitoring data file we can read from
    let monitoring_file = get_monitoring_file_path()?;
    
    if monitoring_file.exists() {
        // Try to read actual monitoring data
        match fs::read_to_string(&monitoring_file) {
            Ok(content) => {
                if let Ok(stats) = serde_json::from_str::<MonitoringStats>(&content) {
                    return Ok(stats);
                }
            }
            Err(_) => {
                // File exists but can't read, continue to return mock data
            }
        }
    }
    
    // Return mock/default monitoring stats if no file or parsing fails
    Ok(MonitoringStats {
        start_time: current_time - 3600000, // 1 hour ago
        loop_count: 1234,
        total_opportunities_found: 45,
        opportunities_executed: 12,
        total_profit_usd: 123.45,
        errors: 2,
        avg_execution_time: 2.3,
        opportunities_per_hour: 12.5,
        uptime: 3600, // 1 hour in seconds
        last_opportunity_time: Some(current_time - 300000), // 5 minutes ago
        best_opportunity: Some(BestOpportunity {
            pair: "ETH/USDC".to_string(),
            buy_dex: "Uniswap".to_string(),
            sell_dex: "SushiSwap".to_string(),
            profit_usd: 25.67,
            profit_pct: 2.45,
            time: current_time - 1800000, // 30 minutes ago
        }),
    })
}

fn get_monitoring_file_path() -> Result<PathBuf, String> {
    let current_dir = std::env::current_dir().map_err(|e| format!("Failed to get current directory: {}", e))?;
    
    let monitoring_path = if current_dir.ends_with("src-tauri") {
        // Running from frontend/src-tauri (development mode)
        current_dir.parent().unwrap().parent().unwrap().join("logs").join("monitoring_stats.json")
    } else {
        // Running from project root or other location
        current_dir.join("logs").join("monitoring_stats.json")
    };
    
    Ok(monitoring_path)
}

#[tauri::command]
async fn get_arbitrage_opportunities() -> Result<Vec<serde_json::Value>, String> {
    // For now, return mock opportunities. In a real implementation, this would read from
    // a shared file or communicate with the Python monitoring script
    let current_time = chrono::Utc::now().timestamp_millis();
    
    let opportunities = vec![
        json!({
            "id": "1",
            "pair": "ETH/USDC",
            "buyDex": "Uniswap V3",
            "sellDex": "SushiSwap",
            "buyPrice": 2456.78,
            "sellPrice": 2478.90,
            "profitPct": 0.89,
            "profitUsd": 12.34,
            "volume": 50000.0,
            "timestamp": current_time
        }),
        json!({
            "id": "2", 
            "pair": "BTC/USDC",
            "buyDex": "Aerodrome",
            "sellDex": "Balancer V2",
            "buyPrice": 67890.12,
            "sellPrice": 68234.56,
            "profitPct": 0.51,
            "profitUsd": 8.76,
            "volume": 25000.0,
            "timestamp": current_time - 30000
        })
    ];
    
    Ok(opportunities)
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
            test_monitoring_command,
            show_notification, 
            start_python_backend, 
            stop_python_backend, 
            get_backend_status,
            start_arbitrage_bot,
            stop_arbitrage_bot,
            get_arbitrage_bot_status,
            read_settings_file,
            write_settings_file,
            get_monitoring_stats,
            get_arbitrage_opportunities
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
