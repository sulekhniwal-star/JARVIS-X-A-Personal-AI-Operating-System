"""System control skills."""

import subprocess

ALLOWED_APPS = {
    "chrome": "chrome",
    "notepad": "notepad",
    "calculator": "calc"
}

def open_app(app_name: str) -> str:
    """Open a whitelisted application."""
    app_lower = app_name.lower()
    if app_lower not in ALLOWED_APPS:
        return f"App '{app_name}' is not allowed"

    try:
        subprocess.Popen(ALLOWED_APPS[app_lower])
        return f"Opening {app_name}"
    except Exception as e:
        return f"Failed to open {app_name}: {str(e)}"

def shutdown_system() -> str:
    """Shutdown the system."""
    try:
        subprocess.run(["shutdown", "/s", "/t", "0"], check=True)
        return "Shutting down system"
    except Exception as e:
        return f"Failed to shutdown: {str(e)}"

def restart_system() -> str:
    """Restart the system."""
    try:
        subprocess.run(["shutdown", "/r", "/t", "0"], check=True)
        return "Restarting system"
    except Exception as e:
        return f"Failed to restart: {str(e)}"
