"""
Status Utility Module
Track application state and status
"""
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum
import threading


class StatusLevel(Enum):
    """Status severity levels"""
    IDLE = "idle"
    ACTIVE = "active"
    BUSY = "busy"
    WARNING = "warning"
    ERROR = "error"


class StatusManager:
    """
    Centralized status tracking for JARVIS
    
    Thread-safe status management for tracking
    application state across modules
    """
    
    def __init__(self):
        self._status: Dict[str, Any] = {
            "state": StatusLevel.IDLE.value,
            "message": "System ready",
            "updated_at": datetime.now().isoformat(),
            "modules": {}
        }
        self._lock = threading.Lock()
        self._listeners = []
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status"""
        with self._lock:
            return self._status.copy()
    
    def set_status(
        self,
        state: StatusLevel,
        message: str = "",
        module: str = None
    ):
        """
        Update status
        
        Args:
            state: Status level
            message: Status message
            module: Optional module name
        """
        with self._lock:
            self._status["state"] = state.value
            self._status["message"] = message
            self._status["updated_at"] = datetime.now().isoformat()
            
            if module:
                self._status["modules"][module] = {
                    "state": state.value,
                    "message": message,
                    "updated_at": datetime.now().isoformat()
                }
        
        # Notify listeners
        self._notify(state, message, module)
    
    def set_module_status(
        self,
        module: str,
        state: StatusLevel,
        message: str = ""
    ):
        """Update status for a specific module"""
        with self._lock:
            self._status["modules"][module] = {
                "state": state.value,
                "message": message,
                "updated_at": datetime.now().isoformat()
            }
    
    def get_module_status(self, module: str) -> Optional[Dict[str, Any]]:
        """Get status for a specific module"""
        with self._lock:
            return self._status["modules"].get(module)
    
    def clear_module_status(self, module: str):
        """Remove module status"""
        with self._lock:
            self._status["modules"].pop(module, None)
    
    def add_listener(self, callback):
        """Add status change listener"""
        self._listeners.append(callback)
    
    def remove_listener(self, callback):
        """Remove status change listener"""
        if callback in self._listeners:
            self._listeners.remove(callback)
    
    def _notify(self, state: StatusLevel, message: str, module: str = None):
        """Notify all listeners of status change"""
        for listener in self._listeners:
            try:
                listener(state, message, module)
            except Exception:
                pass


# Global status manager instance
_manager = StatusManager()


# Convenience functions
def get_status() -> Dict[str, Any]:
    """Get current status"""
    return _manager.get_status()


def set_idle(message: str = "Ready"):
    """Set idle status"""
    _manager.set_status(StatusLevel.IDLE, message)


def set_active(message: str = "Processing"):
    """Set active status"""
    _manager.set_status(StatusLevel.ACTIVE, message)


def set_busy(message: str = "Busy"):
    """Set busy status"""
    _manager.set_status(StatusLevel.BUSY, message)


def set_warning(message: str = "Warning"):
    """Set warning status"""
    _manager.set_status(StatusLevel.WARNING, message)


def set_error(message: str = "Error"):
    """Set error status"""
    _manager.set_status(StatusLevel.ERROR, message)


# Module-level status tracking
def module_idle(module: str, message: str = "Ready"):
    _manager.set_module_status(module, StatusLevel.IDLE, message)


def module_active(module: str, message: str = "Processing"):
    _manager.set_module_status(module, StatusLevel.ACTIVE, message)


def module_error(module: str, message: str = "Error"):
    _manager.set_module_status(module, StatusLevel.ERROR, message)


# Legacy compatibility
status = {"state": "idle"}
