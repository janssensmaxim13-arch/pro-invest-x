// ============================================================================
// ProInvestiX Enterprise Desktop - Tauri Backend
// ============================================================================

#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use tauri::{
    menu::{Menu, MenuItem, PredefinedMenuItem, Submenu},
    tray::{MouseButton, TrayIconBuilder, TrayIconEvent},
    Manager, WindowEvent,
};
use tauri_plugin_notification::NotificationExt;

// =============================================================================
// COMMANDS
// =============================================================================

/// Get app version
#[tauri::command]
fn get_version() -> String {
    env!("CARGO_PKG_VERSION").to_string()
}

/// Get platform info
#[tauri::command]
fn get_platform() -> String {
    format!("{}-{}", std::env::consts::OS, std::env::consts::ARCH)
}

/// Show notification
#[tauri::command]
async fn show_notification(app: tauri::AppHandle, title: String, body: String) -> Result<(), String> {
    app.notification()
        .builder()
        .title(&title)
        .body(&body)
        .show()
        .map_err(|e| e.to_string())?;
    Ok(())
}

/// Get app data directory
#[tauri::command]
fn get_app_data_dir(app: tauri::AppHandle) -> Result<String, String> {
    app.path()
        .app_data_dir()
        .map(|p| p.to_string_lossy().to_string())
        .map_err(|e| e.to_string())
}

/// Store setting
#[tauri::command]
fn store_setting(key: String, value: String) -> Result<(), String> {
    // In production, use tauri-plugin-store
    println!("Storing setting: {} = {}", key, value);
    Ok(())
}

/// Get setting
#[tauri::command]
fn get_setting(key: String) -> Result<Option<String>, String> {
    // In production, use tauri-plugin-store
    println!("Getting setting: {}", key);
    Ok(None)
}

// =============================================================================
// MAIN
// =============================================================================

fn main() {
    tauri::Builder::default()
        // Plugins
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_notification::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_http::init())
        .plugin(tauri_plugin_os::init())
        .plugin(tauri_plugin_process::init())
        .plugin(tauri_plugin_updater::Builder::new().build())
        
        // Commands
        .invoke_handler(tauri::generate_handler![
            get_version,
            get_platform,
            show_notification,
            get_app_data_dir,
            store_setting,
            get_setting,
        ])
        
        // Setup
        .setup(|app| {
            // Create system tray
            let quit = MenuItem::with_id(app, "quit", "Afsluiten", true, None::<&str>)?;
            let show = MenuItem::with_id(app, "show", "Toon venster", true, None::<&str>)?;
            let hide = MenuItem::with_id(app, "hide", "Verberg", true, None::<&str>)?;
            let separator = PredefinedMenuItem::separator(app)?;
            
            let menu = Menu::with_items(app, &[&show, &hide, &separator, &quit])?;
            
            let _tray = TrayIconBuilder::new()
                .icon(app.default_window_icon().unwrap().clone())
                .menu(&menu)
                .menu_on_left_click(false)
                .on_menu_event(|app, event| {
                    match event.id.as_ref() {
                        "quit" => {
                            app.exit(0);
                        }
                        "show" => {
                            if let Some(window) = app.get_webview_window("main") {
                                window.show().unwrap();
                                window.set_focus().unwrap();
                            }
                        }
                        "hide" => {
                            if let Some(window) = app.get_webview_window("main") {
                                window.hide().unwrap();
                            }
                        }
                        _ => {}
                    }
                })
                .on_tray_icon_event(|tray, event| {
                    if let TrayIconEvent::Click {
                        button: MouseButton::Left,
                        ..
                    } = event
                    {
                        let app = tray.app_handle();
                        if let Some(window) = app.get_webview_window("main") {
                            window.show().unwrap();
                            window.set_focus().unwrap();
                        }
                    }
                })
                .build(app)?;
            
            // Setup window close behavior (minimize to tray)
            let main_window = app.get_webview_window("main").unwrap();
            let main_window_clone = main_window.clone();
            
            main_window.on_window_event(move |event| {
                if let WindowEvent::CloseRequested { api, .. } = event {
                    // Hide window instead of closing
                    main_window_clone.hide().unwrap();
                    api.prevent_close();
                }
            });
            
            Ok(())
        })
        
        // Run
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
