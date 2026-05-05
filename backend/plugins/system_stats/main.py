"""
System Stats Plugin - FULLY FUNCTIONAL
Monitor system resources and processes
"""
import psutil
import platform
import os
from typing import Dict, Any, List
from datetime import datetime


class Plugin:
    """
    System statistics and monitoring plugin
    
    Commands:
    - stats: Quick system stats (CPU, RAM, Disk)
    - monitor: Detailed system information
    - processes: Top processes by resource usage
    - cpu: CPU details and per-core usage
    - memory: Memory usage details
    - disk: Disk usage and partitions
    - network: Network statistics
    - battery: Battery status (if available)
    """
    
    def __init__(self):
        self.name = "System Stats"
        self.version = "1.0.0"
    
    def run(self, command: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a command"""
        commands = {
            "stats": self.get_quick_stats,
            "monitor": self.get_full_monitor,
            "processes": self.get_processes,
            "cpu": self.get_cpu_info,
            "memory": self.get_memory_info,
            "disk": self.get_disk_info,
            "network": self.get_network_info,
            "battery": self.get_battery_info,
        }
        
        handler = commands.get(command)
        if handler:
            return handler(params)
        
        return {"error": f"Unknown command: {command}"}
    
    def get_quick_stats(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get quick system stats"""
        cpu_percent = psutil.cpu_percent(interval=0.5)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_used_gb": round(memory.used / (1024**3), 2),
            "memory_total_gb": round(memory.total / (1024**3), 2),
            "disk_percent": disk.percent,
            "disk_free_gb": round(disk.free / (1024**3), 2),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_full_monitor(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive system information"""
        return {
            "system": {
                "platform": platform.system(),
                "platform_release": platform.release(),
                "platform_version": platform.version(),
                "architecture": platform.machine(),
                "hostname": platform.node(),
                "processor": platform.processor(),
                "python_version": platform.python_version()
            },
            "cpu": self.get_cpu_info({}),
            "memory": self.get_memory_info({}),
            "disk": self.get_disk_info({}),
            "network": self.get_network_info({}),
            "battery": self.get_battery_info({}),
            "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat(),
            "uptime_hours": round((datetime.now().timestamp() - psutil.boot_time()) / 3600, 2)
        }
    
    def get_processes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get top processes"""
        count = params.get("count", 10)
        sort_by = params.get("sort_by", "memory")  # memory, cpu, name
        
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
            try:
                info = proc.info
                processes.append({
                    "pid": info['pid'],
                    "name": info['name'],
                    "cpu_percent": round(info['cpu_percent'] or 0, 1),
                    "memory_percent": round(info['memory_percent'] or 0, 1),
                    "status": info['status']
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Sort
        if sort_by == "cpu":
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
        elif sort_by == "name":
            processes.sort(key=lambda x: x['name'].lower())
        else:  # memory
            processes.sort(key=lambda x: x['memory_percent'], reverse=True)
        
        return {
            "processes": processes[:count],
            "total_count": len(processes),
            "sort_by": sort_by
        }
    
    def get_cpu_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get CPU information"""
        freq = psutil.cpu_freq()
        
        return {
            "cores_physical": psutil.cpu_count(logical=False),
            "cores_logical": psutil.cpu_count(logical=True),
            "frequency_current_mhz": round(freq.current, 2) if freq else None,
            "frequency_max_mhz": round(freq.max, 2) if freq else None,
            "usage_percent": psutil.cpu_percent(interval=0.5),
            "usage_per_core": psutil.cpu_percent(interval=0.5, percpu=True),
            "load_average": list(psutil.getloadavg()) if hasattr(psutil, "getloadavg") else None
        }
    
    def get_memory_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get memory information"""
        virtual = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return {
            "virtual": {
                "total_gb": round(virtual.total / (1024**3), 2),
                "available_gb": round(virtual.available / (1024**3), 2),
                "used_gb": round(virtual.used / (1024**3), 2),
                "percent": virtual.percent
            },
            "swap": {
                "total_gb": round(swap.total / (1024**3), 2),
                "used_gb": round(swap.used / (1024**3), 2),
                "free_gb": round(swap.free / (1024**3), 2),
                "percent": swap.percent
            }
        }
    
    def get_disk_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get disk information"""
        partitions = []
        
        for part in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(part.mountpoint)
                partitions.append({
                    "device": part.device,
                    "mountpoint": part.mountpoint,
                    "fstype": part.fstype,
                    "total_gb": round(usage.total / (1024**3), 2),
                    "used_gb": round(usage.used / (1024**3), 2),
                    "free_gb": round(usage.free / (1024**3), 2),
                    "percent": usage.percent
                })
            except (PermissionError, OSError):
                pass
        
        # Disk I/O
        io_counters = psutil.disk_io_counters()
        
        return {
            "partitions": partitions,
            "io": {
                "read_mb": round(io_counters.read_bytes / (1024**2), 2) if io_counters else 0,
                "write_mb": round(io_counters.write_bytes / (1024**2), 2) if io_counters else 0,
                "read_count": io_counters.read_count if io_counters else 0,
                "write_count": io_counters.write_count if io_counters else 0
            }
        }
    
    def get_network_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get network information"""
        io = psutil.net_io_counters()
        interfaces = {}
        
        for name, addrs in psutil.net_if_addrs().items():
            interface_addrs = []
            for addr in addrs:
                interface_addrs.append({
                    "family": str(addr.family),
                    "address": addr.address,
                    "netmask": addr.netmask
                })
            interfaces[name] = interface_addrs
        
        return {
            "io": {
                "bytes_sent_mb": round(io.bytes_sent / (1024**2), 2),
                "bytes_recv_mb": round(io.bytes_recv / (1024**2), 2),
                "packets_sent": io.packets_sent,
                "packets_recv": io.packets_recv,
                "errors_in": io.errin,
                "errors_out": io.errout
            },
            "interfaces": interfaces
        }
    
    def get_battery_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get battery information"""
        try:
            battery = psutil.sensors_battery()
            if battery:
                return {
                    "percent": battery.percent,
                    "power_plugged": battery.power_plugged,
                    "time_left_seconds": battery.secsleft if battery.secsleft != psutil.POWER_TIME_UNLIMITED else -1,
                    "time_left_hours": round(battery.secsleft / 3600, 2) if battery.secsleft > 0 else None
                }
        except:
            pass
        
        return {"available": False}


# Export plugin instance
plugin = Plugin()
