"""
Advanced System Automation
==========================
Upgrade 4: Powerful System Control
- Advanced OS automation
- File management
- Process control
- Screen capture and automation
"""

import os
import sys
import subprocess
import psutil
import pyautogui
import time
from typing import Dict, List, Optional, Tuple
import json
import winreg
from pathlib import Path

# Disable pyautogui failsafe for automation
pyautogui.FAILSAFE = False

class SystemAutomation:
    """Advanced system automation and control."""
    
    def __init__(self):
        self.common_apps = self._discover_installed_apps()
        print(f"✅ System automation initialized")
        print(f"📱 Found {len(self.common_apps)} installed applications")
    
    def _discover_installed_apps(self) -> Dict[str, str]:
        """Discover installed applications."""
        apps = {}
        
        # Common application paths
        common_paths = {
            'chrome': [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
            ],
            'firefox': [
                r"C:\Program Files\Mozilla Firefox\firefox.exe",
                r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe"
            ],
            'edge': [
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
            ],
            'vscode': [
                r"C:\Users\{}\AppData\Local\Programs\Microsoft VS Code\Code.exe".format(os.getenv('USERNAME')),
                r"C:\Program Files\Microsoft VS Code\Code.exe"
            ],
            'notepad++': [
                r"C:\Program Files\Notepad++\notepad++.exe",
                r"C:\Program Files (x86)\Notepad++\notepad++.exe"
            ],
            'vlc': [
                r"C:\Program Files\VideoLAN\VLC\vlc.exe",
                r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe"
            ],
            'spotify': [
                r"C:\Users\{}\AppData\Roaming\Spotify\Spotify.exe".format(os.getenv('USERNAME'))
            ]
        }
        
        # Check which apps exist
        for app_name, paths in common_paths.items():
            for path in paths:
                if os.path.exists(path):
                    apps[app_name] = path
                    break
        
        # Add system apps
        apps.update({
            'notepad': 'notepad.exe',
            'calculator': 'calc.exe',
            'paint': 'mspaint.exe',
            'cmd': 'cmd.exe',
            'powershell': 'powershell.exe',
            'task_manager': 'taskmgr.exe',
            'control_panel': 'control.exe',
            'file_explorer': 'explorer.exe'
        })
        
        return apps
    
    def open_application(self, app_name: str, args: str = "") -> bool:
        """Open an application with optional arguments."""
        app_name = app_name.lower().replace(' ', '_')
        
        # Check if it's a known app
        if app_name in self.common_apps:
            try:
                app_path = self.common_apps[app_name]
                if args:
                    subprocess.Popen(f'"{app_path}" {args}', shell=True)
                else:
                    subprocess.Popen(app_path, shell=True)
                return True
            except Exception as e:
                print(f"❌ Failed to open {app_name}: {e}")
                return False
        
        # Try to open as URL
        if app_name in ['youtube', 'gmail', 'google', 'facebook', 'twitter']:
            urls = {
                'youtube': 'https://www.youtube.com',
                'gmail': 'https://mail.google.com',
                'google': 'https://www.google.com',
                'facebook': 'https://www.facebook.com',
                'twitter': 'https://www.twitter.com'
            }
            import webbrowser
            webbrowser.open(urls.get(app_name, f'https://www.{app_name}.com'))
            return True
        
        # Try to run as system command
        try:
            subprocess.Popen(app_name, shell=True)
            return True
        except:
            return False
    
    def close_application(self, app_name: str) -> bool:
        """Close an application by name."""
        try:
            # Get process name
            process_names = {
                'chrome': 'chrome.exe',
                'firefox': 'firefox.exe',
                'edge': 'msedge.exe',
                'vscode': 'Code.exe',
                'notepad': 'notepad.exe',
                'calculator': 'Calculator.exe',
                'spotify': 'Spotify.exe'
            }
            
            process_name = process_names.get(app_name.lower(), f"{app_name}.exe")
            
            # Kill process
            subprocess.run(['taskkill', '/f', '/im', process_name], 
                         capture_output=True, check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def get_system_info(self) -> Dict[str, any]:
        """Get comprehensive system information."""
        try:
            # CPU info
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # Memory info
            memory = psutil.virtual_memory()
            
            # Disk info
            disk = psutil.disk_usage('/')
            
            # Network info
            network = psutil.net_io_counters()
            
            # Battery info (if available)
            battery = None
            try:
                battery = psutil.sensors_battery()
            except:
                pass
            
            return {
                'cpu': {
                    'usage_percent': cpu_percent,
                    'cores': cpu_count,
                    'frequency_mhz': cpu_freq.current if cpu_freq else None
                },
                'memory': {
                    'total_gb': round(memory.total / (1024**3), 2),
                    'available_gb': round(memory.available / (1024**3), 2),
                    'usage_percent': memory.percent
                },
                'disk': {
                    'total_gb': round(disk.total / (1024**3), 2),
                    'free_gb': round(disk.free / (1024**3), 2),
                    'usage_percent': round((disk.used / disk.total) * 100, 1)
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_received': network.bytes_recv
                },
                'battery': {
                    'percent': battery.percent if battery else None,
                    'plugged': battery.power_plugged if battery else None
                } if battery else None
            }
        except Exception as e:
            print(f"❌ System info error: {e}")
            return {}
    
    def control_volume(self, action: str, level: int = None) -> bool:
        """Control system volume."""
        try:
            if action == 'mute':
                subprocess.run(['nircmd', 'mutesysvolume', '1'], check=True)
            elif action == 'unmute':
                subprocess.run(['nircmd', 'mutesysvolume', '0'], check=True)
            elif action == 'set' and level is not None:
                # Convert percentage to Windows volume level (0-65535)
                volume_level = int((level / 100) * 65535)
                subprocess.run(['nircmd', 'setsysvolume', str(volume_level)], check=True)
            elif action == 'increase':
                subprocess.run(['nircmd', 'changesysvolume', '6553'], check=True)  # +10%
            elif action == 'decrease':
                subprocess.run(['nircmd', 'changesysvolume', '-6553'], check=True)  # -10%
            return True
        except subprocess.CalledProcessError:
            # Fallback to PowerShell
            try:
                if action == 'mute':
                    subprocess.run(['powershell', '-c', 
                                  '(New-Object -comObject VolumeControl.Application).Mute()'], 
                                  check=True)
                return True
            except:
                return False
    
    def take_screenshot(self, filename: str = None) -> str:
        """Take a screenshot."""
        try:
            if filename is None:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
            
            screenshot = pyautogui.screenshot()
            screenshot.save(filename)
            return os.path.abspath(filename)
        except Exception as e:
            print(f"❌ Screenshot error: {e}")
            return None
    
    def type_text(self, text: str, delay: float = 0.05):
        """Type text with optional delay."""
        try:
            pyautogui.typewrite(text, interval=delay)
            return True
        except Exception as e:
            print(f"❌ Type text error: {e}")
            return False
    
    def press_keys(self, keys: str):
        """Press key combination."""
        try:
            if '+' in keys:
                # Handle key combinations like 'ctrl+c'
                key_list = keys.split('+')
                pyautogui.hotkey(*key_list)
            else:
                pyautogui.press(keys)
            return True
        except Exception as e:
            print(f"❌ Key press error: {e}")
            return False
    
    def move_mouse(self, x: int, y: int, duration: float = 0.5):
        """Move mouse to coordinates."""
        try:
            pyautogui.moveTo(x, y, duration=duration)
            return True
        except Exception as e:
            print(f"❌ Mouse move error: {e}")
            return False
    
    def click_mouse(self, x: int = None, y: int = None, button: str = 'left'):
        """Click mouse at coordinates or current position."""
        try:
            if x is not None and y is not None:
                pyautogui.click(x, y, button=button)
            else:
                pyautogui.click(button=button)
            return True
        except Exception as e:
            print(f"❌ Mouse click error: {e}")
            return False
    
    def get_running_processes(self) -> List[Dict[str, any]]:
        """Get list of running processes."""
        processes = []
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cpu_percent': proc.info['cpu_percent'],
                        'memory_percent': proc.info['memory_percent']
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except Exception as e:
            print(f"❌ Process list error: {e}")
        
        return sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:20]
    
    def manage_files(self, action: str, source: str, destination: str = None) -> bool:
        """File management operations."""
        try:
            source_path = Path(source)
            
            if action == 'copy' and destination:
                import shutil
                shutil.copy2(source, destination)
                return True
            
            elif action == 'move' and destination:
                import shutil
                shutil.move(source, destination)
                return True
            
            elif action == 'delete':
                if source_path.is_file():
                    source_path.unlink()
                elif source_path.is_dir():
                    import shutil
                    shutil.rmtree(source)
                return True
            
            elif action == 'create_folder':
                source_path.mkdir(parents=True, exist_ok=True)
                return True
            
            return False
        except Exception as e:
            print(f"❌ File operation error: {e}")
            return False
    
    def system_power(self, action: str, delay: int = 5) -> bool:
        """System power operations."""
        try:
            if action == 'shutdown':
                subprocess.run(['shutdown', '/s', f'/t', str(delay)], check=True)
            elif action == 'restart':
                subprocess.run(['shutdown', '/r', f'/t', str(delay)], check=True)
            elif action == 'sleep':
                subprocess.run(['rundll32.exe', 'powrprof.dll,SetSuspendState', '0,1,0'], check=True)
            elif action == 'hibernate':
                subprocess.run(['shutdown', '/h'], check=True)
            elif action == 'lock':
                subprocess.run(['rundll32.exe', 'user32.dll,LockWorkStation'], check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Power operation error: {e}")
            return False
    
    def get_window_info(self) -> List[Dict[str, any]]:
        """Get information about open windows."""
        windows = []
        try:
            import win32gui
            
            def enum_windows_callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    window_text = win32gui.GetWindowText(hwnd)
                    if window_text:
                        rect = win32gui.GetWindowRect(hwnd)
                        windows.append({
                            'handle': hwnd,
                            'title': window_text,
                            'rect': rect
                        })
            
            win32gui.EnumWindows(enum_windows_callback, windows)
        except ImportError:
            print("⚠️ win32gui not available - window management limited")
        except Exception as e:
            print(f"❌ Window info error: {e}")
        
        return windows
    
    def set_brightness(self, level: int) -> bool:
        """Set screen brightness (0-100)."""
        try:
            # Use WMI to control brightness
            subprocess.run([
                'powershell', '-c',
                f'(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{level})'
            ], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            return False