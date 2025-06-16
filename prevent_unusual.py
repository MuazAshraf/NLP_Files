import subprocess
import time
import platform
import threading
import signal
import sys

class DialogPreventer:
    def __init__(self):
        self.running = False
        self.prevention_thread = None
        
    def setup_prevention_mac(self):
        """Setup system to minimize dialogs on Mac"""
        if platform.system() != "Darwin":
            return False
            
        commands = [
            # Enable Do Not Disturb
            ['defaults', 'write', 'com.apple.ncprefs', 'dnd_prefs', '-int', '1'],
            
            # Disable software update notifications
            ['defaults', 'write', 'com.apple.SoftwareUpdate', 'ScheduleFrequency', '-int', '0'],
            ['defaults', 'write', 'com.apple.SoftwareUpdate', 'AutomaticCheckEnabled', '-bool', 'false'],
            
            # Disable Spotlight indexing notifications
            ['defaults', 'write', 'com.apple.spotlight', 'orderedItems', '-array'],
            
            # Disable app nap for current session
            ['defaults', 'write', 'NSGlobalDomain', 'NSAppSleepDisabled', '-bool', 'true'],
        ]
        
        for cmd in commands:
            try:
                subprocess.run(cmd, check=True, capture_output=True)
            except subprocess.CalledProcessError:
                pass
                
        print("✅ Prevention settings applied")
        return True
    
    def dismiss_dialogs_mac(self):
        """Actively dismiss dialogs using AppleScript"""
        dismiss_script = '''
        tell application "System Events"
            repeat with proc in application processes
                try
                    if (count of windows of proc) > 0 then
                        repeat with win in windows of proc
                            if modal of win is true then
                                -- Try to click Cancel, No, or Deny buttons
                                try
                                    click button "Cancel" of win
                                on error
                                    try
                                        click button "No" of win
                                    on error
                                        try
                                            click button "Deny" of win
                                        on error
                                            try
                                                click button "Not Now" of win
                                            on error
                                                try
                                                    click button "Later" of win
                                                on error
                                                    -- Press Escape key as last resort
                                                    key code 53
                                                end try
                                            end try
                                        end try
                                    end try
                                end try
                            end if
                        end repeat
                    end if
                end try
            end repeat
        end tell
        '''
        
        try:
            subprocess.run(['osascript', '-e', dismiss_script], 
                         capture_output=True, timeout=2)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
    
    def kill_dialog_processes(self):
        """Kill known dialog processes"""
        if platform.system() == "Darwin":
            dialog_processes = [
                'SecurityAgent',
                'UserNotificationCenter',
                'NotificationCenter',
                'CoreServicesUIAgent'
            ]
        else:
            dialog_processes = [
                'consent.exe',
                'dwm.exe'  # Windows dialog manager
            ]
        
        for process_name in dialog_processes:
            try:
                if platform.system() == "Darwin":
                    subprocess.run(['pkill', '-f', process_name], 
                                 capture_output=True)
                else:
                    subprocess.run(['taskkill', '/f', '/im', process_name], 
                                 capture_output=True)
            except subprocess.CalledProcessError:
                pass
    
    def prevention_loop(self):
        """Main prevention loop"""
        while self.running:
            if platform.system() == "Darwin":
                self.dismiss_dialogs_mac()
            
            # Kill dialog processes (aggressive approach)
            self.kill_dialog_processes()
            
            time.sleep(0.5)  # Check every 500ms
    
    def start_prevention(self):
        """Start dialog prevention"""
        if self.running:
            print("Prevention already running!")
            return
            
        print("🚀 Starting dialog prevention...")
        
        # Setup system settings
        if platform.system() == "Darwin":
            self.setup_prevention_mac()
        
        # Start prevention thread
        self.running = True
        self.prevention_thread = threading.Thread(target=self.prevention_loop)
        self.prevention_thread.daemon = True
        self.prevention_thread.start()
        
        print("✅ Dialog prevention active")
        print("Press Ctrl+C to stop")
    
    def stop_prevention(self):
        """Stop dialog prevention and restore settings"""
        if not self.running:
            return
            
        print("\n🛑 Stopping dialog prevention...")
        self.running = False
        
        if self.prevention_thread:
            self.prevention_thread.join(timeout=2)
        
        # Restore settings
        if platform.system() == "Darwin":
            restore_commands = [
                ['defaults', 'write', 'com.apple.ncprefs', 'dnd_prefs', '-int', '0'],
                ['defaults', 'write', 'com.apple.SoftwareUpdate', 'AutomaticCheckEnabled', '-bool', 'true'],
                ['defaults', 'write', 'NSGlobalDomain', 'NSAppSleepDisabled', '-bool', 'false'],
            ]
            
            for cmd in restore_commands:
                try:
                    subprocess.run(cmd, check=True, capture_output=True)
                except subprocess.CalledProcessError:
                    pass
        
        print("✅ Settings restored")

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    preventer.stop_prevention()
    sys.exit(0)

if __name__ == "__main__":
    preventer = DialogPreventer()
    
    # Setup signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    if len(sys.argv) > 1 and sys.argv[1] == "stop":
        preventer.stop_prevention()
    else:
        preventer.start_prevention()
        
        # Keep running until interrupted
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            preventer.stop_prevention()