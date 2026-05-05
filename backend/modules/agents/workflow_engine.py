"""
Workflow Engine Module - FULLY FUNCTIONAL
Orchestrates multi-step automation workflows
"""
import asyncio
import json
import subprocess
import httpx
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from modules.agents.base_agent import BaseAgent, AgentStep, AgentContext, register_agent, get_agent
from modules.llm.ollama_client import OllamaClient, OllamaError
from modules.utils.logger import logger


@dataclass
class WorkflowDefinition:
    """Defines a complete workflow"""
    name: str
    description: str = ""
    steps: List[Dict[str, Any]] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)
    on_error: str = "stop"  # stop, continue, retry
    max_retries: int = 3


class WorkflowEngine(BaseAgent):
    """
    Workflow execution engine
    
    Features:
    - Load workflows from JSON
    - Built-in actions (log, wait, http, llm, command)
    - Variable substitution
    - Conditional execution
    - Error handling with retries
    """
    
    # Built-in action registry
    BUILTIN_ACTIONS = [
        "log", "wait", "set_variable", "http_request", 
        "run_command", "llm_query", "llm_chat",
        "read_screen", "mouse_click", "keyboard_type",
        "open_app", "save_file", "read_file"
    ]
    
    def __init__(self, workflow: WorkflowDefinition = None):
        super().__init__(workflow.name if workflow else "Workflow")
        self.workflow = workflow
        self.llm_client = None
        self._custom_actions: Dict[str, Callable] = {}
    
    def define_steps(self) -> List[AgentStep]:
        """Convert workflow definition to agent steps"""
        if not self.workflow:
            return []
        
        steps = []
        for step_def in self.workflow.steps:
            step = AgentStep(
                name=step_def.get("name", f"step_{len(steps)}"),
                action=step_def.get("action", "log"),
                params=step_def.get("params", {}),
                condition=step_def.get("condition"),
                on_success=step_def.get("on_success"),
                on_failure=step_def.get("on_failure"),
                retries=step_def.get("retries", 0),
                timeout=step_def.get("timeout", 30.0)
            )
            steps.append(step)
        
        return steps
    
    def register_action(self, name: str, handler: Callable):
        """Register a custom action handler"""
        self._custom_actions[name] = handler
        logger.info(f"[Workflow] Registered action: {name}")
    
    async def _execute_action(self, action: str, params: Dict[str, Any]) -> Any:
        """Execute an action with variable substitution"""
        # Substitute variables in params
        params = self._substitute_variables(params)
        
        # Check custom actions first
        if action in self._custom_actions:
            handler = self._custom_actions[action]
            if asyncio.iscoroutinefunction(handler):
                return await handler(params, self.context)
            return handler(params, self.context)
        
        # Built-in actions
        return await self._execute_builtin(action, params)
    
    def _substitute_variables(self, obj: Any) -> Any:
        """Recursively substitute ${var} in strings"""
        if isinstance(obj, str):
            result = obj
            for key, value in self.context.variables.items():
                result = result.replace(f"${{{key}}}", str(value))
            return result
        elif isinstance(obj, dict):
            return {k: self._substitute_variables(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._substitute_variables(item) for item in obj]
        return obj
    
    async def _execute_builtin(self, action: str, params: Dict[str, Any]) -> Any:
        """Execute built-in actions"""
        
        # === LOG ===
        if action == "log":
            message = params.get("message", "")
            level = params.get("level", "info")
            logger.log(getattr(logger, level.upper(), logger.info), message)
            return message
        
        # === WAIT ===
        if action == "wait":
            seconds = float(params.get("seconds", 1))
            await asyncio.sleep(seconds)
            return f"Waited {seconds}s"
        
        # === SET VARIABLE ===
        if action == "set_variable":
            name = params.get("name")
            value = params.get("value")
            self.context.set(name, value)
            return value
        
        # === HTTP REQUEST ===
        if action == "http_request":
            return await self._action_http(params)
        
        # === RUN COMMAND ===
        if action == "run_command":
            return await self._action_command(params)
        
        # === LLM QUERY ===
        if action == "llm_query":
            return await self._action_llm_query(params)
        
        # === LLM CHAT ===
        if action == "llm_chat":
            return await self._action_llm_chat(params)
        
        # === READ SCREEN ===
        if action == "read_screen":
            return await self._action_read_screen(params)
        
        # === MOUSE CLICK ===
        if action == "mouse_click":
            return await self._action_mouse_click(params)
        
        # === KEYBOARD TYPE ===
        if action == "keyboard_type":
            return await self._action_keyboard_type(params)
        
        # === OPEN APP ===
        if action == "open_app":
            return await self._action_open_app(params)
        
        # === SAVE FILE ===
        if action == "save_file":
            return await self._action_save_file(params)
        
        # === READ FILE ===
        if action == "read_file":
            return await self._action_read_file(params)
        
        raise ValueError(f"Unknown action: {action}")
    
    async def _action_http(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """HTTP request action"""
        method = params.get("method", "GET").upper()
        url = params.get("url")
        headers = params.get("headers", {})
        body = params.get("body")
        timeout = params.get("timeout", 30)
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            if method == "GET":
                response = await client.get(url, headers=headers)
            elif method == "POST":
                response = await client.post(url, headers=headers, json=body)
            elif method == "PUT":
                response = await client.put(url, headers=headers, json=body)
            elif method == "DELETE":
                response = await client.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
        
        try:
            data = response.json()
        except:
            data = response.text
        
        return {
            "status_code": response.status_code,
            "data": data
        }
    
    async def _action_command(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run system command"""
        command = params.get("command")
        shell = params.get("shell", True)
        timeout = params.get("timeout", 30)
        
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
            
            return {
                "returncode": process.returncode,
                "stdout": stdout.decode() if stdout else "",
                "stderr": stderr.decode() if stderr else ""
            }
        except asyncio.TimeoutError:
            process.kill()
            return {"error": "Command timed out", "returncode": -1}
    
    async def _action_llm_query(self, params: Dict[str, Any]) -> str:
        """Query LLM"""
        if not self.llm_client:
            self.llm_client = OllamaClient()
        
        prompt = params.get("prompt", "")
        model = params.get("model", "llama3.1:8b")
        system = params.get("system")
        temperature = params.get("temperature", 0.7)
        
        try:
            result = self.llm_client.generate(
                model=model,
                prompt=prompt,
                system=system,
                temperature=temperature
            )
            return result.get("response", "")
        except OllamaError as e:
            return f"LLM Error: {e}"
    
    async def _action_llm_chat(self, params: Dict[str, Any]) -> str:
        """Chat with LLM (uses context history)"""
        if not self.llm_client:
            self.llm_client = OllamaClient()
        
        message = params.get("message", "")
        model = params.get("model", "llama3.1:8b")
        
        # Get conversation history from context
        messages = self.context.get("_llm_messages", [])
        messages.append({"role": "user", "content": message})
        
        try:
            result = self.llm_client.chat(model=model, messages=messages)
            response = result.get("response", "")
            
            # Update history
            messages.append({"role": "assistant", "content": response})
            self.context.set("_llm_messages", messages)
            
            return response
        except OllamaError as e:
            return f"LLM Error: {e}"
    
    async def _action_read_screen(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Capture and OCR screen"""
        from modules.ocr.screen_capture import ScreenCapture
        from modules.ocr.ocr_engine import OCREngine
        
        monitor = params.get("monitor", 1)
        preprocess = params.get("preprocess", True)
        
        capture = ScreenCapture()
        ocr = OCREngine()
        
        image_path, dims = capture.capture(monitor=monitor)
        text = ocr.extract_text(image_path, preprocess=preprocess)
        
        return {
            "text": text,
            "image_path": image_path,
            "width": dims["width"],
            "height": dims["height"]
        }
    
    async def _action_mouse_click(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Click mouse"""
        from modules.control import mouse
        
        x = params.get("x", 0)
        y = params.get("y", 0)
        button = params.get("button", "left")
        clicks = params.get("clicks", 1)
        
        mouse.click(x, y, button, clicks)
        return {"x": x, "y": y, "button": button}
    
    async def _action_keyboard_type(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Type text"""
        from modules.control import keyboard
        
        text = params.get("text", "")
        interval = params.get("interval", 0.05)
        
        keyboard.type_text(text, interval)
        return {"typed": len(text)}
    
    async def _action_open_app(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Open application"""
        from modules.control import apps
        
        app_name = params.get("app", params.get("name", ""))
        args = params.get("args", [])
        
        apps.open_application(app_name, args)
        
        # Wait for app to start
        await asyncio.sleep(params.get("wait", 1))
        
        return {"opened": app_name}
    
    async def _action_save_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Save content to file"""
        path = params.get("path")
        content = params.get("content", "")
        mode = params.get("mode", "w")
        
        with open(path, mode, encoding="utf-8") as f:
            f.write(content)
        
        return {"path": path, "size": len(content)}
    
    async def _action_read_file(self, params: Dict[str, Any]) -> str:
        """Read file content"""
        path = params.get("path")
        
        with open(path, "r", encoding="utf-8") as f:
            return f.read()


def load_workflow(data: Dict[str, Any]) -> WorkflowDefinition:
    """Load workflow from dict"""
    return WorkflowDefinition(
        name=data.get("name", "Unnamed"),
        description=data.get("description", ""),
        steps=data.get("steps", []),
        variables=data.get("variables", {}),
        on_error=data.get("on_error", "stop"),
        max_retries=data.get("max_retries", 3)
    )


def load_workflow_from_file(path: str) -> WorkflowDefinition:
    """Load workflow from JSON file"""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return load_workflow(data)


async def run_workflow(workflow: WorkflowDefinition, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Execute a workflow and return results"""
    engine = WorkflowEngine(workflow)
    register_agent(engine)
    
    # Add initial variables
    initial = workflow.variables.copy()
    if context:
        initial.update(context)
    
    try:
        result = await engine.run(initial)
        return result
    finally:
        pass  # Keep agent in registry for status checking


# Singleton engine for quick access
_engine: Optional[WorkflowEngine] = None

def get_workflow_engine() -> WorkflowEngine:
    """Get or create workflow engine"""
    global _engine
    if _engine is None:
        _engine = WorkflowEngine()
    return _engine


def list_available_actions() -> List[str]:
    """List all available workflow actions"""
    return WorkflowEngine.BUILTIN_ACTIONS.copy()
