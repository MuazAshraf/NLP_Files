import psutil
import platform

def detect_recording_interruptions():
    """Detect popups that would interrupt screen recording"""
    interruptions = []
    
    if platform.system() == "Windows":
        try:
            import win32gui
            import win32con
            
            def enum_windows_callback(hwnd, param):
                if win32gui.IsWindowVisible(hwnd):
                    window_text = win32gui.GetWindowText(hwnd)
                    class_name = win32gui.GetClassName(hwnd)
                    
                    # Check for actual interrupting popups
                    interrupting_indicators = [
                        # System dialogs
                        "User Account Control",
                        "Windows Security",
                        "Microsoft Windows",
                        "System Configuration",
                        "Windows Update",
                        "Error",
                        "Warning",
                        "Alert",
                        "Notification",
                        
                        # Permission dialogs
                        "wants to access",
                        "Allow",
                        "Permission",
                        "Security Alert",
                        
                        # Software update/install dialogs
                        "Setup",
                        "Install",
                        "Update",
                        "Restart Required"
                    ]
                    
                    # Check window properties for modal/topmost behavior
                    ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
                    is_topmost = bool(ex_style & win32con.WS_EX_TOPMOST)
                    is_modal = bool(ex_style & win32con.WS_EX_DLGMODALFRAME)
                    
                    # Check if it's an interrupting popup
                    if window_text:
                        text_lower = window_text.lower()
                        
                        # Check for interrupting keywords
                        is_interrupting = any(indicator.lower() in text_lower 
                                            for indicator in interrupting_indicators)
                        
                        # Check for modal/topmost windows with short titles (often popups)
                        is_likely_popup = (is_topmost or is_modal) and len(window_text) < 50
                        
                        # Exclude normal application windows
                        excluded_classes = [
                            'Chrome_WidgetWin_1',  # Chrome/Electron apps
                            'ApplicationFrameWindow',  # UWP apps
                            'CabinetWClass',  # File Explorer
                            'Shell_TrayWnd',  # Taskbar
                            'Progman',  # Desktop
                            'WorkerW'   # Desktop worker
                        ]
                        
                        if (is_interrupting or is_likely_popup) and class_name not in excluded_classes:
                            param.append(f"{window_text} ({class_name})")
                
                return True
            
            win32gui.EnumWindows(enum_windows_callback, interruptions)
            
        except ImportError:
            print("⚠️  Install pywin32 for better detection: pip install pywin32")
            return False, []
            
    elif platform.system() == "Darwin":  # macOS
        # Check for Mac notification/dialog processes
        interrupting_processes = [
            "SecurityAgent", "UserNotificationCenter", "NotificationCenter",
            "loginwindow", "CoreServicesUIAgent", "SoftwareUpdate"
        ]
        
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] in interrupting_processes:
                    interruptions.append(proc.info['name'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    
    return len(interruptions) > 0, interruptions

# Usage
is_present, popups = detect_recording_interruptions()
if is_present:
    print("🚨 RECORDING INTERRUPTION DETECTED:")
    for popup in popups:
        print(f"  ⚠️  {popup}")
    print("\n💡 Consider pausing recording until dialogs are dismissed")
else:
    print("✅ No interrupting popups detected - safe to record")