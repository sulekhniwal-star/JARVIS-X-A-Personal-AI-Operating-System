import pyautogui
import subprocess
import time
import ctypes
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


def get_volume() -> int:
    """Get the current system volume."""
    try:
        sessions = AudioUtilities.GetSpeakers()
        volume = sessions.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        return int(volume.GetMasterVolumeLevelScalar() * 100)
    except Exception:
        return -1


def set_volume(level: int) -> str:
    """Set the system volume to a specific level (0-100)."""
    try:
        if not 0 <= level <= 100:
            return "Volume level must be between 0 and 100."

        sessions = AudioUtilities.GetSpeakers()
        volume = sessions.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume.SetMasterVolumeLevelScalar(level / 100, None)
        return f"Volume set to {level}%"
    except Exception:
        return "Failed to set volume."


def change_volume(change: int) -> str:
    """Change the system volume by a specific amount."""
    try:
        current_volume = get_volume()
        if current_volume == -1:
            return "Failed to get current volume."

        new_volume = current_volume + change
        return set_volume(new_volume)

    except Exception:
        return "Failed to change volume."


def mute_volume() -> str:
    """Mute the system volume."""
    try:
        sessions = AudioUtilities.GetSpeakers()
        volume = sessions.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume.SetMute(1, None)
        return "Volume muted."
    except Exception:
        return "Failed to mute volume."


def unmute_volume() -> str:
    """Unmute the system volume."""
    try:
        sessions = AudioUtilities.GetSpeakers()
        volume = sessions.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume.SetMute(0, None)
        return "Volume unmuted."
    except Exception:
        return "Failed to unmute volume."


def lock_workstation() -> str:
    """Lock the workstation."""
    try:
        ctypes.windll.user32.LockWorkStation()
        return "Workstation locked."
    except Exception:
        return "Failed to lock workstation."


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
