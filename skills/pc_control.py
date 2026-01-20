import pyautogui
import subprocess
import time


# Whitelisted applications
ALLOWED_APPS = {
    "chrome": "chrome.exe",
    "notepad": "notepad.exe", 
    "calculator": "calc.exe",
    "vscode": "code.exe"
}

# Blocked dangerous key combinations
BLOCKED_KEYS = [
    "alt+f4", "win+r", "shutdown", "taskkill", "ctrl+alt+del"
]


def type_text(text: str) -> str:
    """Type text using pyautogui."""
    try:
        if not text or len(text) > 500:  # Safety limit
            return "Text too long or empty."
        
        time.sleep(0.5)  # Small delay
        pyautogui.typewrite(text, interval=0.05)
        return f"Typed: {text[:50]}..."
    
    except Exception:
        return "Failed to type text."


def press_key(key: str) -> str:
    """Press a key combination using pyautogui."""
    try:
        key_lower = key.lower().strip()
        
        # Check for blocked keys
        if any(blocked in key_lower for blocked in BLOCKED_KEYS):
            return "Key combination blocked for security."
        
        time.sleep(0.5)  # Small delay
        pyautogui.press(key_lower)
        return f"Pressed: {key}"
    
    except Exception:
        return "Failed to press key."


def open_app(app_name: str) -> str:
    """Open an application using subprocess."""
    try:
        app_lower = app_name.lower().strip()
        
        # Check whitelist
        if app_lower not in ALLOWED_APPS:
            return f"Application '{app_name}' not allowed. Available: chrome, notepad, calculator, vscode."
        
        executable = ALLOWED_APPS[app_lower]
        subprocess.Popen(executable, shell=True)
        time.sleep(1)  # Allow app to start
        
        return f"Opened {app_name}."
    
    except Exception:
        return f"Failed to open {app_name}."