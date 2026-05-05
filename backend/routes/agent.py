"""
Agent Routes - FULLY FUNCTIONAL
API endpoints for agent and workflow automation
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import asyncio
from modules.agents.base_agent import (
    AgentStep, AgentStatus, SimpleAgent,
    register_agent, get_agent, remove_agent, list_agents
)
from modules.agents.workflow_engine import (
    WorkflowEngine, WorkflowDefinition, 
    load_workflow, run_workflow, list_available_actions
)
from modules.llm.ollama_client import OllamaClient, OllamaError
from modules.utils.logger import logger

router = APIRouter()


# === Request/Response Models ===

class TaskRequest(BaseModel):
    """Simple task request"""
    task: str = Field(..., description="Natural language task description")
    context: Dict[str, Any] = Field(default={}, description="Initial context variables")


class WorkflowStepModel(BaseModel):
    """Workflow step definition"""
    name: str
    action: str
    params: Dict[str, Any] = {}
    condition: Optional[str] = None
    on_success: Optional[str] = None
    on_failure: Optional[str] = None
    retries: int = 0
    timeout: float = 30.0


class WorkflowRequest(BaseModel):
    """Workflow execution request"""
    name: str = Field(default="Workflow", description="Workflow name")
    description: str = Field(default="", description="Workflow description")
    steps: List[WorkflowStepModel] = Field(..., description="Workflow steps")
    variables: Dict[str, Any] = Field(default={}, description="Initial variables")


class AgentStatusResponse(BaseModel):
    """Agent status response"""
    agent_id: str
    name: str
    status: str
    current_step: Optional[int] = None
    total_steps: Optional[int] = None
    progress_percent: float = 0
    current_step_name: Optional[str] = None


class WorkflowResultResponse(BaseModel):
    """Workflow execution result"""
    agent_id: str
    name: str
    status: str
    steps: List[Dict[str, Any]]
    context: Dict[str, Any]
    duration_ms: float


# === Endpoints ===

@router.post("/run")
async def run_simple_task(request: TaskRequest, background_tasks: BackgroundTasks):
    """
    Run a simple agent task
    
    Uses LLM to interpret the task and execute appropriate actions.
    
    Example tasks:
    - "Open notepad and type Hello World"
    - "Capture the screen and summarize it"
    - "Search for Python tutorials"
    """
    logger.info(f"[Agent] Task: {request.task}")
    
    try:
        # Use LLM to break down the task
        llm = OllamaClient()
        
        system_prompt = """You are JARVIS, an AI assistant that breaks down tasks into executable steps.
        
Available actions:
- log: Log a message (params: message)
- wait: Wait seconds (params: seconds)
- llm_query: Ask AI a question (params: prompt, model)
- run_command: Run shell command (params: command)
- read_screen: Capture and OCR screen
- mouse_click: Click at position (params: x, y, button)
- keyboard_type: Type text (params: text)
- open_app: Open application (params: app)
- http_request: Make HTTP request (params: url, method)

Respond with a JSON array of steps. Each step has: name, action, params.

Example response:
[
  {"name": "open_notepad", "action": "open_app", "params": {"app": "notepad"}},
  {"name": "wait_for_app", "action": "wait", "params": {"seconds": 2}},
  {"name": "type_text", "action": "keyboard_type", "params": {"text": "Hello World"}}
]

Only respond with valid JSON. No explanation text."""

        result = llm.generate(
            model="llama3.1:8b",
            prompt=f"Task: {request.task}\n\nGenerate steps:",
            system=system_prompt,
            temperature=0.3
        )
        
        response_text = result.get("response", "[]").strip()
        
        # Clean up response
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]
        
        # Parse steps
        import json
        try:
            steps_data = json.loads(response_text)
        except json.JSONDecodeError:
            # Fallback: just log the task
            steps_data = [
                {"name": "log_task", "action": "log", "params": {"message": f"Task: {request.task}"}},
                {"name": "thinking", "action": "llm_query", "params": {"prompt": request.task}}
            ]
        
        # Create workflow
        workflow = WorkflowDefinition(
            name=f"Task: {request.task[:30]}",
            description=request.task,
            steps=steps_data,
            variables=request.context
        )
        
        # Run in background
        async def execute():
            try:
                await run_workflow(workflow, request.context)
            except Exception as e:
                logger.error(f"[Agent] Task error: {e}")
        
        # Start workflow
        engine = WorkflowEngine(workflow)
        register_agent(engine)
        
        background_tasks.add_task(lambda: asyncio.run(execute()))
        
        return {
            "status": "started",
            "agent_id": engine.id,
            "task": request.task,
            "steps": len(steps_data)
        }
        
    except OllamaError as e:
        raise HTTPException(status_code=503, detail=f"LLM unavailable: {e}")
    except Exception as e:
        logger.error(f"[Agent] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflow", response_model=WorkflowResultResponse)
async def run_workflow_endpoint(request: WorkflowRequest):
    """
    Execute a defined workflow
    
    Runs a multi-step workflow with conditional logic.
    
    Example:
    ```json
    {
      "name": "Hello Workflow",
      "steps": [
        {"name": "greet", "action": "log", "params": {"message": "Hello!"}},
        {"name": "wait", "action": "wait", "params": {"seconds": 1}},
        {"name": "ask_ai", "action": "llm_query", "params": {"prompt": "Tell me a joke"}}
      ]
    }
    ```
    """
    logger.info(f"[Agent] Workflow: {request.name} ({len(request.steps)} steps)")
    
    try:
        # Convert to WorkflowDefinition
        steps = [step.dict() for step in request.steps]
        
        workflow = WorkflowDefinition(
            name=request.name,
            description=request.description,
            steps=steps,
            variables=request.variables
        )
        
        # Execute workflow
        result = await run_workflow(workflow, request.variables)
        
        return WorkflowResultResponse(
            agent_id=result.get("agent_id", ""),
            name=result.get("name", request.name),
            status=result.get("status", "unknown"),
            steps=result.get("steps", []),
            context=result.get("context", {}),
            duration_ms=result.get("duration_ms", 0)
        )
        
    except Exception as e:
        logger.error(f"[Agent] Workflow error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{agent_id}", response_model=AgentStatusResponse)
async def get_agent_status(agent_id: str):
    """
    Get the status of a running agent
    
    Returns progress information including current step.
    """
    agent = get_agent(agent_id)
    
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent not found: {agent_id}")
    
    progress = agent.get_progress()
    
    return AgentStatusResponse(
        agent_id=agent_id,
        name=agent.name,
        status=progress.get("status", "unknown"),
        current_step=progress.get("current_step"),
        total_steps=progress.get("total_steps"),
        progress_percent=progress.get("progress_percent", 0),
        current_step_name=progress.get("current_step_name")
    )


@router.post("/cancel/{agent_id}")
async def cancel_agent(agent_id: str):
    """
    Cancel a running agent
    
    Requests graceful cancellation. Agent will stop after current step.
    """
    agent = get_agent(agent_id)
    
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent not found: {agent_id}")
    
    agent.cancel()
    
    return {
        "status": "cancellation_requested",
        "agent_id": agent_id
    }


@router.post("/pause/{agent_id}")
async def pause_agent(agent_id: str):
    """Pause a running agent"""
    agent = get_agent(agent_id)
    
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent not found: {agent_id}")
    
    agent.pause()
    return {"status": "paused", "agent_id": agent_id}


@router.post("/resume/{agent_id}")
async def resume_agent(agent_id: str):
    """Resume a paused agent"""
    agent = get_agent(agent_id)
    
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent not found: {agent_id}")
    
    agent.resume()
    return {"status": "resumed", "agent_id": agent_id}


@router.get("/result/{agent_id}")
async def get_agent_result(agent_id: str):
    """
    Get the full result of a completed agent
    
    Returns all step results and context variables.
    """
    agent = get_agent(agent_id)
    
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent not found: {agent_id}")
    
    return agent._build_result()


@router.get("/list")
async def list_running_agents():
    """
    List all running agents
    
    Returns basic info about all active agents.
    """
    return {"agents": list_agents()}


@router.get("/actions")
async def get_available_actions():
    """
    List all available workflow actions
    
    Returns the list of built-in actions that can be used in workflows.
    """
    actions = list_available_actions()
    
    # Add descriptions
    action_info = {
        "log": "Log a message (params: message, level)",
        "wait": "Wait for seconds (params: seconds)",
        "set_variable": "Set context variable (params: name, value)",
        "http_request": "Make HTTP request (params: url, method, body, headers)",
        "run_command": "Run shell command (params: command, timeout)",
        "llm_query": "Query LLM (params: prompt, model, system)",
        "llm_chat": "Chat with LLM using history (params: message, model)",
        "read_screen": "Capture and OCR screen (params: monitor, preprocess)",
        "mouse_click": "Click at position (params: x, y, button, clicks)",
        "keyboard_type": "Type text (params: text, interval)",
        "open_app": "Open application (params: app, args, wait)",
        "save_file": "Save to file (params: path, content)",
        "read_file": "Read file content (params: path)"
    }
    
    return {
        "actions": [
            {"name": action, "description": action_info.get(action, "")}
            for action in actions
        ]
    }


@router.delete("/{agent_id}")
async def remove_agent_endpoint(agent_id: str):
    """Remove an agent from registry"""
    agent = get_agent(agent_id)
    
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent not found: {agent_id}")
    
    remove_agent(agent_id)
    return {"status": "removed", "agent_id": agent_id}
