"""
Base Agent Module - FULLY FUNCTIONAL
Foundation for all automation agents in JARVIS
"""
import asyncio
import uuid
import time
from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime
from modules.utils.logger import logger


class AgentStatus(Enum):
    """Agent execution status"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class AgentStep:
    """Represents a single step in agent execution"""
    name: str
    action: str
    params: Dict[str, Any] = field(default_factory=dict)
    condition: Optional[str] = None  # Condition to execute
    on_success: Optional[str] = None  # Next step on success
    on_failure: Optional[str] = None  # Next step on failure
    retries: int = 0
    timeout: float = 30.0
    
    # Execution state
    status: str = "pending"
    result: Any = None
    error: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    
    def duration_ms(self) -> float:
        """Get step duration in milliseconds"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time) * 1000
        return 0


@dataclass
class AgentContext:
    """Context passed between agent steps"""
    variables: Dict[str, Any] = field(default_factory=dict)
    history: List[Dict[str, Any]] = field(default_factory=list)
    current_step: int = 0
    start_time: Optional[float] = None
    
    def set(self, key: str, value: Any):
        """Set a context variable"""
        self.variables[key] = value
        self.history.append({
            "action": "set_variable",
            "key": key,
            "value": str(value)[:100],
            "timestamp": time.time()
        })
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a context variable"""
        return self.variables.get(key, default)
    
    def has(self, key: str) -> bool:
        """Check if variable exists"""
        return key in self.variables
    
    def log(self, message: str, level: str = "info"):
        """Add log entry to history"""
        self.history.append({
            "action": "log",
            "level": level,
            "message": message,
            "timestamp": time.time()
        })


class BaseAgent(ABC):
    """
    Base class for all JARVIS agents
    
    Provides:
    - Step-based execution
    - Context management
    - Error handling with retries
    - Progress tracking
    - Cancellation support
    """
    
    def __init__(self, name: str = "BaseAgent"):
        self.id = str(uuid.uuid4())[:8]
        self.name = name
        self.status = AgentStatus.IDLE
        self.context = AgentContext()
        self.steps: List[AgentStep] = []
        self.current_step_index = 0
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self._cancel_requested = False
        self._pause_requested = False
        
        # Callbacks
        self.on_step_complete: Optional[Callable] = None
        self.on_status_change: Optional[Callable] = None
    
    @abstractmethod
    def define_steps(self) -> List[AgentStep]:
        """Define the steps for this agent. Must be implemented by subclasses."""
        pass
    
    def _set_status(self, status: AgentStatus):
        """Update agent status"""
        old_status = self.status
        self.status = status
        logger.info(f"[Agent:{self.id}] Status: {old_status.value} -> {status.value}")
        
        if self.on_status_change:
            try:
                self.on_status_change(self, old_status, status)
            except Exception as e:
                logger.error(f"[Agent:{self.id}] Status callback error: {e}")
    
    async def run(self, initial_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute the agent
        
        Args:
            initial_context: Initial variables for context
            
        Returns:
            Dict with status, results, and context
        """
        self._set_status(AgentStatus.RUNNING)
        self.started_at = datetime.now()
        self.context.start_time = time.time()
        
        # Initialize context
        if initial_context:
            for key, value in initial_context.items():
                self.context.set(key, value)
        
        # Define steps
        self.steps = self.define_steps()
        
        if not self.steps:
            self._set_status(AgentStatus.COMPLETED)
            return self._build_result()
        
        logger.info(f"[Agent:{self.id}] Starting with {len(self.steps)} steps")
        
        try:
            while self.current_step_index < len(self.steps):
                # Check for cancellation
                if self._cancel_requested:
                    self._set_status(AgentStatus.CANCELLED)
                    return self._build_result()
                
                # Check for pause
                while self._pause_requested:
                    self._set_status(AgentStatus.PAUSED)
                    await asyncio.sleep(0.1)
                
                if self.status == AgentStatus.PAUSED:
                    self._set_status(AgentStatus.RUNNING)
                
                # Execute step
                step = self.steps[self.current_step_index]
                success = await self._execute_step(step)
                
                # Determine next step
                if success and step.on_success:
                    self._jump_to_step(step.on_success)
                elif not success and step.on_failure:
                    self._jump_to_step(step.on_failure)
                else:
                    self.current_step_index += 1
            
            self._set_status(AgentStatus.COMPLETED)
            
        except Exception as e:
            logger.error(f"[Agent:{self.id}] Fatal error: {e}")
            self._set_status(AgentStatus.FAILED)
            self.context.log(f"Fatal error: {e}", "error")
        
        self.completed_at = datetime.now()
        return self._build_result()
    
    async def _execute_step(self, step: AgentStep) -> bool:
        """Execute a single step with retry support"""
        step.status = "running"
        step.start_time = time.time()
        
        logger.info(f"[Agent:{self.id}] Step: {step.name} ({step.action})")
        self.context.log(f"Starting step: {step.name}")
        
        # Check condition
        if step.condition:
            if not self._evaluate_condition(step.condition):
                logger.info(f"[Agent:{self.id}] Skipping step (condition false): {step.name}")
                step.status = "skipped"
                step.end_time = time.time()
                return True
        
        # Execute with retries
        attempts = 0
        max_attempts = step.retries + 1
        last_error = None
        
        while attempts < max_attempts:
            try:
                # Execute action
                result = await asyncio.wait_for(
                    self._execute_action(step.action, step.params),
                    timeout=step.timeout
                )
                
                step.result = result
                step.status = "completed"
                step.end_time = time.time()
                
                self.context.log(f"Step completed: {step.name}")
                
                if self.on_step_complete:
                    self.on_step_complete(self, step)
                
                return True
                
            except asyncio.TimeoutError:
                last_error = "Timeout"
                logger.warning(f"[Agent:{self.id}] Step timeout: {step.name}")
            except Exception as e:
                last_error = str(e)
                logger.warning(f"[Agent:{self.id}] Step error: {e}")
            
            attempts += 1
            if attempts < max_attempts:
                await asyncio.sleep(1)  # Wait before retry
        
        # All retries failed
        step.status = "failed"
        step.error = last_error
        step.end_time = time.time()
        
        self.context.log(f"Step failed: {step.name} - {last_error}", "error")
        
        return False
    
    @abstractmethod
    async def _execute_action(self, action: str, params: Dict[str, Any]) -> Any:
        """Execute an action. Must be implemented by subclasses."""
        pass
    
    def _evaluate_condition(self, condition: str) -> bool:
        """Evaluate a condition string"""
        try:
            # Simple variable check
            if condition.startswith("has:"):
                var_name = condition[4:].strip()
                return self.context.has(var_name)
            
            if condition.startswith("not:"):
                var_name = condition[4:].strip()
                return not self.context.get(var_name)
            
            if condition.startswith("equals:"):
                parts = condition[7:].split("=")
                if len(parts) == 2:
                    var_name = parts[0].strip()
                    expected = parts[1].strip()
                    return str(self.context.get(var_name)) == expected
            
            # Evaluate as Python expression (careful!)
            return bool(eval(condition, {"ctx": self.context.variables}))
            
        except Exception as e:
            logger.warning(f"[Agent:{self.id}] Condition error: {condition} - {e}")
            return False
    
    def _jump_to_step(self, step_name: str):
        """Jump to a named step"""
        for i, step in enumerate(self.steps):
            if step.name == step_name:
                self.current_step_index = i
                return
        logger.warning(f"[Agent:{self.id}] Step not found: {step_name}")
        self.current_step_index += 1
    
    def _build_result(self) -> Dict[str, Any]:
        """Build the final result dict"""
        return {
            "agent_id": self.id,
            "name": self.name,
            "status": self.status.value,
            "steps": [
                {
                    "name": s.name,
                    "action": s.action,
                    "status": s.status,
                    "result": s.result if s.status == "completed" else None,
                    "error": s.error,
                    "duration_ms": s.duration_ms()
                }
                for s in self.steps
            ],
            "context": self.context.variables,
            "history": self.context.history,
            "duration_ms": (
                (self.completed_at - self.started_at).total_seconds() * 1000
                if self.completed_at and self.started_at else 0
            )
        }
    
    def cancel(self):
        """Request cancellation"""
        self._cancel_requested = True
        logger.info(f"[Agent:{self.id}] Cancellation requested")
    
    def pause(self):
        """Request pause"""
        self._pause_requested = True
        logger.info(f"[Agent:{self.id}] Pause requested")
    
    def resume(self):
        """Resume from pause"""
        self._pause_requested = False
        logger.info(f"[Agent:{self.id}] Resume requested")
    
    def get_progress(self) -> Dict[str, Any]:
        """Get current progress"""
        completed = sum(1 for s in self.steps if s.status in ("completed", "skipped"))
        
        return {
            "agent_id": self.id,
            "status": self.status.value,
            "current_step": self.current_step_index,
            "total_steps": len(self.steps),
            "completed_steps": completed,
            "progress_percent": (completed / len(self.steps) * 100) if self.steps else 100,
            "current_step_name": (
                self.steps[self.current_step_index].name 
                if self.current_step_index < len(self.steps) else None
            )
        }


class SimpleAgent(BaseAgent):
    """
    A simple agent that executes predefined steps
    
    Usage:
        agent = SimpleAgent("MyAgent", [
            AgentStep("step1", "log", {"message": "Hello"}),
            AgentStep("step2", "wait", {"seconds": 1})
        ])
        result = await agent.run()
    """
    
    def __init__(self, name: str, steps: List[AgentStep], actions: Dict[str, Callable] = None):
        super().__init__(name)
        self._predefined_steps = steps
        self._custom_actions = actions or {}
    
    def define_steps(self) -> List[AgentStep]:
        return self._predefined_steps
    
    async def _execute_action(self, action: str, params: Dict[str, Any]) -> Any:
        """Execute built-in or custom action"""
        # Check custom actions first
        if action in self._custom_actions:
            return await self._custom_actions[action](params, self.context)
        
        # Built-in actions
        if action == "log":
            message = params.get("message", "")
            # Substitute variables
            for key, value in self.context.variables.items():
                message = message.replace(f"${{{key}}}", str(value))
            logger.info(f"[Agent:{self.id}] LOG: {message}")
            return message
        
        if action == "wait":
            seconds = params.get("seconds", 1)
            await asyncio.sleep(seconds)
            return f"Waited {seconds}s"
        
        if action == "set_variable":
            name = params.get("name")
            value = params.get("value")
            self.context.set(name, value)
            return value
        
        raise ValueError(f"Unknown action: {action}")


# Global agent registry
_running_agents: Dict[str, BaseAgent] = {}

def register_agent(agent: BaseAgent):
    """Register a running agent"""
    _running_agents[agent.id] = agent

def get_agent(agent_id: str) -> Optional[BaseAgent]:
    """Get a running agent by ID"""
    return _running_agents.get(agent_id)

def remove_agent(agent_id: str):
    """Remove an agent from registry"""
    _running_agents.pop(agent_id, None)

def list_agents() -> List[Dict[str, Any]]:
    """List all running agents"""
    return [
        {
            "id": agent.id,
            "name": agent.name,
            "status": agent.status.value,
            "progress": agent.get_progress()
        }
        for agent in _running_agents.values()
    ]
