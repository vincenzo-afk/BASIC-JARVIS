"""
Application Control Module
Handles opening, closing, and managing applications
"""
import os
import subprocess
import platform
import psutil
from typing import List, Dict, Any, Optional
from modules.utils.logger import logger


def get_platform() -> str:
    """Get current OS"""
    return platform.system().lower()


def open_application(app_name: str, args: List[str] = None):
    """
    Open an application
    
    Args:
        app_name: Application name, path, or command
        args: Optional command line arguments
    """
    logger.info(f"Opening application: {app_name}")
    
    system = get_platform()
    args = args or []
    
    if system == "windows":
        # Try different methods
        try:
            # Method 1: Direct start command
            if args:
                subprocess.Popen(["start", "", app_name] + args, shell=True)
            else:
                os.system(f'start "" "{app_name}"')
        except Exception as e:
            logger.error(f"Failed to open {app_name}: {e}")
            raise
            
    elif system == "darwin":  # macOS
        if app_name.endswith('.app'):
            subprocess.Popen(["open", app_name] + args)
        else:
            subprocess.Popen(["open", "-a", app_name] + args)
            
    else:  # Linux
        subprocess.Popen([app_name] + args)


def open_file(file_path: str):
    """Open a file with default application"""
    logger.info(f"Opening file: {file_path}")
    
    system = get_platform()
    
    if system == "windows":
        os.startfile(file_path)
    elif system == "darwin":
        subprocess.Popen(["open", file_path])
    else:
        subprocess.Popen(["xdg-open", file_path])


def open_url(url: str):
    """Open a URL in default browser"""
    logger.info(f"Opening URL: {url}")
    
    import webbrowser
    webbrowser.open(url)


def list_running() -> List[Dict[str, Any]]:
    """
    List running processes
    
    Returns:
        List of process info dicts
    """
    processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
        try:
            pinfo = proc.info
            processes.append({
                "pid": pinfo['pid'],
                "name": pinfo['name'],
                "cpu_percent": round(pinfo['cpu_percent'] or 0, 1),
                "memory_percent": round(pinfo['memory_percent'] or 0, 1),
                "status": pinfo['status']
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    # Sort by memory usage
    processes.sort(key=lambda x: x['memory_percent'], reverse=True)
    
    return processes[:100]  # Top 100


def find_process(name: str) -> List[Dict[str, Any]]:
    """Find processes by name"""
    matching = []
    name_lower = name.lower()
    
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if name_lower in proc.info['name'].lower():
                matching.append({
                    "pid": proc.info['pid'],
                    "name": proc.info['name']
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    return matching


def kill_process(name: str):
    """
    Kill process by name
    
    Args:
        name: Process name to kill
    """
    logger.warning(f"Killing process: {name}")
    
    system = get_platform()
    
    if system == "windows":
        os.system(f'taskkill /IM "{name}" /F')
    else:
        os.system(f"pkill -f '{name}'")


def kill_pid(pid: int):
    """Kill process by PID"""
    logger.warning(f"Killing PID: {pid}")
    
    try:
        proc = psutil.Process(pid)
        proc.terminate()
        proc.wait(timeout=5)
    except psutil.NoSuchProcess:
        logger.warning(f"Process {pid} not found")
    except psutil.TimeoutExpired:
        # Force kill
        proc.kill()


def get_active_window() -> Optional[Dict[str, Any]]:
    """
    Get currently active window info
    
    Note: Requires additional libraries on some platforms
    """
    system = get_platform()
    
    if system == "windows":
        try:
            import ctypes
            from ctypes import wintypes
            
            user32 = ctypes.windll.user32
            hwnd = user32.GetForegroundWindow()
            
            length = user32.GetWindowTextLengthW(hwnd) + 1
            buffer = ctypes.create_unicode_buffer(length)
            user32.GetWindowTextW(hwnd, buffer, length)
            
            return {
                "hwnd": hwnd,
                "title": buffer.value
            }
        except Exception as e:
            logger.error(f"Failed to get active window: {e}")
            return None
    
    return None


# Common application shortcuts
def open_notepad():
    """Open Notepad (Windows)"""
    open_application("notepad")


def open_calculator():
    """Open Calculator"""
    system = get_platform()
    if system == "windows":
        open_application("calc")
    elif system == "darwin":
        open_application("Calculator")
    else:
        open_application("gnome-calculator")


def open_terminal():
    """Open terminal/command prompt"""
    system = get_platform()
    if system == "windows":
        open_application("cmd")
    elif system == "darwin":
        open_application("Terminal")
    else:
        open_application("gnome-terminal")


def open_file_explorer(path: str = None):
    """Open file explorer"""
    system = get_platform()
    
    if system == "windows":
        if path:
            subprocess.Popen(["explorer", path])
        else:
            subprocess.Popen(["explorer"])
    elif system == "darwin":
        subprocess.Popen(["open", path or "."])
    else:
        subprocess.Popen(["xdg-open", path or "."])
