"""
Scheduled Tasks Plugin - FULLY FUNCTIONAL
Schedule and manage recurring tasks
"""
import os
import sys
import json
import asyncio
import threading
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
import time

# Add backend path for imports
backend_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)


@dataclass
class ScheduledTask:
    """Represents a scheduled task"""
    id: str
    name: str
    schedule_type: str  # once, interval, daily, weekly, cron
    action: str  # plugin:command or workflow:name
    params: Dict[str, Any] = field(default_factory=dict)
    
    # Schedule configuration
    interval_seconds: int = 0
    at_time: str = ""  # HH:MM format
    weekdays: List[int] = field(default_factory=list)  # 0=Monday, 6=Sunday
    
    # State
    enabled: bool = True
    last_run: Optional[str] = None
    next_run: Optional[str] = None
    run_count: int = 0
    last_result: Optional[Dict[str, Any]] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class TaskScheduler:
    """Task scheduler with persistent storage"""
    
    def __init__(self, storage_path: str = None):
        self.storage_path = storage_path or os.path.join(
            backend_path, "temp", "scheduled_tasks.json"
        )
        self.tasks: Dict[str, ScheduledTask] = {}
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._task_handlers: Dict[str, Callable] = {}
        
        # Load existing tasks
        self._load_tasks()
    
    def _load_tasks(self):
        """Load tasks from storage"""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r") as f:
                    data = json.load(f)
                    for task_data in data.get("tasks", []):
                        task = ScheduledTask(**task_data)
                        self.tasks[task.id] = task
            except Exception as e:
                print(f"[Scheduler] Error loading tasks: {e}")
    
    def _save_tasks(self):
        """Save tasks to storage"""
        try:
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            with open(self.storage_path, "w") as f:
                json.dump({
                    "tasks": [asdict(t) for t in self.tasks.values()]
                }, f, indent=2)
        except Exception as e:
            print(f"[Scheduler] Error saving tasks: {e}")
    
    def add_task(self, task: ScheduledTask) -> str:
        """Add a new task"""
        # Calculate next run
        task.next_run = self._calculate_next_run(task)
        
        self.tasks[task.id] = task
        self._save_tasks()
        return task.id
    
    def remove_task(self, task_id: str) -> bool:
        """Remove a task"""
        if task_id in self.tasks:
            del self.tasks[task_id]
            self._save_tasks()
            return True
        return False
    
    def update_task(self, task_id: str, updates: Dict[str, Any]) -> bool:
        """Update a task"""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        for key, value in updates.items():
            if hasattr(task, key):
                setattr(task, key, value)
        
        # Recalculate next run
        task.next_run = self._calculate_next_run(task)
        
        self._save_tasks()
        return True
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get a task by ID"""
        task = self.tasks.get(task_id)
        return asdict(task) if task else None
    
    def list_tasks(self) -> List[Dict[str, Any]]:
        """List all tasks"""
        return [asdict(t) for t in self.tasks.values()]
    
    def _calculate_next_run(self, task: ScheduledTask) -> str:
        """Calculate next run time"""
        now = datetime.now()
        
        if task.schedule_type == "once":
            # Parse at_time as datetime
            try:
                return task.at_time
            except:
                return now.isoformat()
        
        elif task.schedule_type == "interval":
            return (now + timedelta(seconds=task.interval_seconds)).isoformat()
        
        elif task.schedule_type == "daily":
            # Run at specific time daily
            try:
                hour, minute = map(int, task.at_time.split(":"))
                next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                if next_run <= now:
                    next_run += timedelta(days=1)
                return next_run.isoformat()
            except:
                return (now + timedelta(days=1)).isoformat()
        
        elif task.schedule_type == "weekly":
            # Run on specific weekdays
            try:
                hour, minute = map(int, task.at_time.split(":"))
                days_ahead = 0
                for i in range(7):
                    check_day = (now.weekday() + i) % 7
                    if check_day in task.weekdays:
                        days_ahead = i
                        break
                
                next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                next_run += timedelta(days=days_ahead)
                if next_run <= now:
                    # Find next occurrence
                    for i in range(1, 8):
                        check_day = (now.weekday() + i) % 7
                        if check_day in task.weekdays:
                            next_run = now.replace(hour=hour, minute=minute)
                            next_run += timedelta(days=i)
                            break
                return next_run.isoformat()
            except:
                return (now + timedelta(weeks=1)).isoformat()
        
        return now.isoformat()
    
    def register_handler(self, action_type: str, handler: Callable):
        """Register a handler for task actions"""
        self._task_handlers[action_type] = handler
    
    def _execute_task(self, task: ScheduledTask) -> Dict[str, Any]:
        """Execute a task"""
        try:
            # Parse action
            if ":" in task.action:
                action_type, action_name = task.action.split(":", 1)
            else:
                action_type = "plugin"
                action_name = task.action
            
            handler = self._task_handlers.get(action_type)
            if handler:
                result = handler(action_name, task.params)
            else:
                result = {"error": f"No handler for action type: {action_type}"}
            
            return result
            
        except Exception as e:
            return {"error": str(e)}
    
    def start(self):
        """Start the scheduler"""
        if self._running:
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
    
    def stop(self):
        """Stop the scheduler"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
    
    def _run_loop(self):
        """Main scheduler loop"""
        while self._running:
            now = datetime.now()
            
            for task_id, task in list(self.tasks.items()):
                if not task.enabled:
                    continue
                
                if not task.next_run:
                    continue
                
                try:
                    next_run = datetime.fromisoformat(task.next_run)
                    
                    if next_run <= now:
                        # Execute task
                        result = self._execute_task(task)
                        
                        # Update task state
                        task.last_run = now.isoformat()
                        task.run_count += 1
                        task.last_result = result
                        
                        # Calculate next run or disable if one-time
                        if task.schedule_type == "once":
                            task.enabled = False
                        else:
                            task.next_run = self._calculate_next_run(task)
                        
                        self._save_tasks()
                        
                except Exception as e:
                    print(f"[Scheduler] Error processing task {task_id}: {e}")
            
            # Sleep for 1 second
            time.sleep(1)


# Global scheduler instance
_scheduler: Optional[TaskScheduler] = None


def get_scheduler() -> TaskScheduler:
    """Get or create scheduler singleton"""
    global _scheduler
    if _scheduler is None:
        _scheduler = TaskScheduler()
        
        # Register default handlers
        def plugin_handler(plugin_name: str, params: Dict[str, Any]):
            """Execute a plugin command"""
            try:
                from routes.plugins import get_manager
                manager = get_manager()
                
                plugin_parts = plugin_name.split("/")
                if len(plugin_parts) == 2:
                    name, command = plugin_parts
                    result = manager.run_command(name, command, params)
                    return result.get("result", result)
                return {"error": f"Invalid plugin format: {plugin_name}. Use 'plugin_name/command'"}
            except Exception as e:
                return {"error": f"Plugin execution failed: {e}"}
        
        _scheduler.register_handler("plugin", plugin_handler)
        _scheduler.start()
    
    return _scheduler


class Plugin:
    """
    Scheduled tasks management plugin
    
    Commands:
    - list: List all scheduled tasks
    - add: Add a new task
    - remove: Remove a task
    - update: Update a task
    - enable: Enable a task
    - disable: Disable a task
    - run_now: Run a task immediately
    - status: Get scheduler status
    """
    
    def __init__(self):
        self.name = "Scheduled Tasks"
        self.version = "1.0.0"
        self.scheduler = get_scheduler()
    
    def run(self, command: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a command"""
        commands = {
            "list": self.list_tasks,
            "add": self.add_task,
            "remove": self.remove_task,
            "update": self.update_task,
            "enable": self.enable_task,
            "disable": self.disable_task,
            "run_now": self.run_now,
            "status": self.get_status,
        }
        
        handler = commands.get(command)
        if handler:
            return handler(params)
        
        return {"error": f"Unknown command: {command}"}
    
    def list_tasks(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List all scheduled tasks"""
        return {
            "tasks": self.scheduler.list_tasks(),
            "count": len(self.scheduler.tasks)
        }
    
    def add_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a new scheduled task
        
        Params:
        - name: Task name
        - schedule_type: once, interval, daily, weekly
        - action: plugin:name/command or workflow:name
        - params: Task parameters
        - interval_seconds: For interval type
        - at_time: HH:MM for daily/weekly
        - weekdays: [0-6] for weekly (0=Monday)
        """
        import uuid
        
        task_id = str(uuid.uuid4())[:8]
        
        task = ScheduledTask(
            id=task_id,
            name=params.get("name", f"Task {task_id}"),
            schedule_type=params.get("schedule_type", "once"),
            action=params.get("action", ""),
            params=params.get("params", {}),
            interval_seconds=params.get("interval_seconds", 60),
            at_time=params.get("at_time", ""),
            weekdays=params.get("weekdays", []),
            enabled=params.get("enabled", True)
        )
        
        self.scheduler.add_task(task)
        
        return {
            "status": "created",
            "task_id": task_id,
            "next_run": task.next_run
        }
    
    def remove_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Remove a scheduled task"""
        task_id = params.get("task_id", params.get("id", ""))
        
        if not task_id:
            return {"error": "No task ID provided"}
        
        if self.scheduler.remove_task(task_id):
            return {"status": "removed", "task_id": task_id}
        
        return {"error": f"Task not found: {task_id}"}
    
    def update_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update a scheduled task"""
        task_id = params.get("task_id", params.get("id", ""))
        
        if not task_id:
            return {"error": "No task ID provided"}
        
        updates = {k: v for k, v in params.items() if k not in ("task_id", "id")}
        
        if self.scheduler.update_task(task_id, updates):
            return {"status": "updated", "task_id": task_id}
        
        return {"error": f"Task not found: {task_id}"}
    
    def enable_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Enable a task"""
        task_id = params.get("task_id", params.get("id", ""))
        
        if self.scheduler.update_task(task_id, {"enabled": True}):
            return {"status": "enabled", "task_id": task_id}
        
        return {"error": f"Task not found: {task_id}"}
    
    def disable_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Disable a task"""
        task_id = params.get("task_id", params.get("id", ""))
        
        if self.scheduler.update_task(task_id, {"enabled": False}):
            return {"status": "disabled", "task_id": task_id}
        
        return {"error": f"Task not found: {task_id}"}
    
    def run_now(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run a task immediately"""
        task_id = params.get("task_id", params.get("id", ""))
        
        if not task_id:
            return {"error": "No task ID provided"}
        
        task = self.scheduler.tasks.get(task_id)
        if not task:
            return {"error": f"Task not found: {task_id}"}
        
        result = self.scheduler._execute_task(task)
        
        # Update stats
        task.last_run = datetime.now().isoformat()
        task.run_count += 1
        task.last_result = result
        self.scheduler._save_tasks()
        
        return {
            "status": "executed",
            "task_id": task_id,
            "result": result
        }
    
    def get_status(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get scheduler status"""
        return {
            "running": self.scheduler._running,
            "task_count": len(self.scheduler.tasks),
            "enabled_count": sum(1 for t in self.scheduler.tasks.values() if t.enabled),
            "handlers": list(self.scheduler._task_handlers.keys())
        }


# Export plugin instance
plugin = Plugin()
