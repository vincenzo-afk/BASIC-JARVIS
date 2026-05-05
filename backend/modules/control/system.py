"""
System Control Module
Handles system-level operations (shutdown, restart, sleep, etc.)
"""
import os
import platform
import subprocess
import psutil
from typing import Dict, Any
from modules.utils.logger import logger


def get_platform() -> str:
    """Get current operating system"""
    return platform.system().lower()


def shutdown(delay: int = 1):
    """
    Shutdown the system
    
    Args:
        delay: Seconds before shutdown
    """
    logger.warning(f"System shutdown initiated (delay={delay}s)")
    
    system = get_platform()
    
    if system == "windows":
        os.system(f"shutdown /s /t {delay}")
    elif system == "darwin":  # macOS
        os.system(f"sudo shutdown -h +{delay // 60 or 1}")
    else:  # Linux
        os.system(f"shutdown -h +{delay // 60 or 1}")


def restart(delay: int = 1):
    """
    Restart the system
    
    Args:
        delay: Seconds before restart
    """
    logger.warning(f"System restart initiated (delay={delay}s)")
    
    system = get_platform()
    
    if system == "windows":
        os.system(f"shutdown /r /t {delay}")
    elif system == "darwin":
        os.system(f"sudo shutdown -r +{delay // 60 or 1}")
    else:
        os.system(f"shutdown -r +{delay // 60 or 1}")


def sleep():
    """Put system to sleep/hibernate"""
    logger.info("System sleep initiated")
    
    system = get_platform()
    
    if system == "windows":
        # Sleep mode
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
    elif system == "darwin":
        os.system("pmset sleepnow")
    else:
        os.system("systemctl suspend")


def hibernate():
    """Hibernate the system (Windows)"""
    logger.info("System hibernate initiated")
    
    if get_platform() == "windows":
        os.system("shutdown /h")
    else:
        os.system("systemctl hibernate")


def lock():
    """Lock the screen"""
    logger.info("Screen lock initiated")
    
    system = get_platform()
    
    if system == "windows":
        os.system("rundll32.exe user32.dll,LockWorkStation")
    elif system == "darwin":
        os.system("pmset displaysleepnow")
    else:
        os.system("loginctl lock-session")


def logout():
    """Log out current user"""
    logger.warning("User logout initiated")
    
    system = get_platform()
    
    if system == "windows":
        os.system("shutdown /l")
    elif system == "darwin":
        os.system("osascript -e 'tell application \"System Events\" to log out'")
    else:
        os.system("loginctl terminate-user $USER")


def cancel_shutdown():
    """Cancel a pending shutdown/restart"""
    logger.info("Shutdown cancelled")
    
    system = get_platform()
    
    if system == "windows":
        os.system("shutdown /a")
    else:
        os.system("shutdown -c")


def get_info() -> Dict[str, Any]:
    """
    Get comprehensive system information
    
    Returns:
        Dict with system details
    """
    cpu_freq = psutil.cpu_freq()
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # Get battery info if available
    battery = None
    try:
        bat = psutil.sensors_battery()
        if bat:
            battery = {
                "percent": bat.percent,
                "plugged": bat.power_plugged,
                "time_left_seconds": bat.secsleft if bat.secsleft != psutil.POWER_TIME_UNLIMITED else -1
            }
    except:
        pass
    
    # Get network info
    net_io = psutil.net_io_counters()
    
    return {
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "hostname": platform.node()
        },
        "cpu": {
            "cores_physical": psutil.cpu_count(logical=False),
            "cores_logical": psutil.cpu_count(logical=True),
            "frequency_mhz": cpu_freq.current if cpu_freq else None,
            "usage_percent": psutil.cpu_percent(interval=0.5)
        },
        "memory": {
            "total_gb": round(memory.total / (1024**3), 2),
            "available_gb": round(memory.available / (1024**3), 2),
            "used_gb": round(memory.used / (1024**3), 2),
            "percent": memory.percent
        },
        "disk": {
            "total_gb": round(disk.total / (1024**3), 2),
            "used_gb": round(disk.used / (1024**3), 2),
            "free_gb": round(disk.free / (1024**3), 2),
            "percent": disk.percent
        },
        "network": {
            "bytes_sent_mb": round(net_io.bytes_sent / (1024**2), 2),
            "bytes_recv_mb": round(net_io.bytes_recv / (1024**2), 2)
        },
        "battery": battery,
        "boot_time": psutil.boot_time()
    }


def run_command(command: str, shell: bool = True) -> Dict[str, Any]:
    """
    Run a system command
    
    Args:
        command: Command string
        shell: Run in shell
        
    Returns:
        Dict with stdout, stderr, return code
    """
    logger.info(f"Running command: {command}")
    
    result = subprocess.run(
        command,
        shell=shell,
        capture_output=True,
        text=True,
        timeout=30
    )
    
    return {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode
    }
