"""
Voice Agent - Intelligent Command Processing
Maps natural language to system actions using LLM
"""
import json
import asyncio
from typing import Dict, Any, Optional
from modules.llm.ollama_client import OllamaClient
from modules.agents.workflow_engine import WorkflowEngine
from modules.utils.logger import logger

class VoiceAgent:
    """
    Intelligent Voice Agent that interprets commands and executes actions
    """
    def __init__(self):
        self.llm = OllamaClient()
        self.engine = WorkflowEngine()
        
    async def process_command(self, text: str, model: str = "llama3.1:8b") -> Dict[str, Any]:
        """
        Process voice command and execute actions
        
        Args:
            text: User's spoken text
            model: LLM model to use
            
        Returns:
            Dict with success, response, action, result
        """
        logger.info(f"[VoiceAgent] Processing: {text}")
        
        # 1. Intent Classification / Tool Selection
        system_prompt = """
        You are JARVIS, an intelligent system assistant.
        Map the user's voice command to a JSON action.
        
        Available actions:
        - open_app(name): Open an application (e.g., "open notepad", "start chrome")
        - run_command(command): Run a shell command (e.g., "shutdown", "ping google")
        - read_screen(): Take a screenshot and analyze text
        - type_text(text): Type text on keyboard
        - mouse_click(x, y, button): Click mouse
        - chat(message): Just reply to the user if no action is needed
        
        Rules:
        - For "shutdown", use run_command with "shutdown /s /t 10"
        - For "restart", use run_command with "shutdown /r /t 10"
        - For "lock", use run_command with "rundll32.exe user32.dll,LockWorkStation"
        - Return ONLY valid JSON.
        
        Example:
        {"action": "open_app", "params": {"name": "notepad"}}
        """
        
        try:
            # Get intent from LLM
            llm_result = self.llm.generate(
                model=model,
                prompt=text,
                system=system_prompt,
                format="json",
                temperature=0.1 # Low temperature for deterministic actions
            )
            
            response_json = llm_result.get("response", "{}")
            logger.info(f"[VoiceAgent] Intent: {response_json}")
            
            try:
                intent = json.loads(response_json)
            except json.JSONDecodeError:
                # Fallback if LLM didn't return valid JSON
                logger.warning("[VoiceAgent] Invalid JSON from LLM")
                return {
                    "success": True,
                    "response": response_json, # Just return the text
                    "action": "chat"
                }
            
            action = intent.get("action")
            params = intent.get("params", {})
            
            # Handle Chat
            if action == "chat" or not action:
                return {
                    "success": True,
                    "response": params.get("message", response_json if not action else "I'm listening."),
                    "action": "chat"
                }
            
            # 2. Execute Action
            logger.info(f"[VoiceAgent] Executing: {action} {params}")
            
            # Execute using WorkflowEngine's builtin actions
            # We access the protected method _execute_builtin as we are extending the system
            result = await self.engine._execute_builtin(action, params)
            
            # Generate response based on result
            response_text = f"Executed {action}."
            
            if action == "read_screen":
                text_content = result.get('text', '')
                word_count = len(text_content.split())
                response_text = f"I've analyzed the screen. I see about {word_count} words. {text_content[:100]}..."
            
            elif action == "open_app":
                response_text = f"Opening {params.get('name')}."
                
            elif action == "run_command":
                if "shutdown" in params.get("command", ""):
                    response_text = "Initiating system shutdown sequence."
                else:
                    response_text = f"Command executed. Output: {result.get('stdout', '')[:50]}"
            
            return {
                "success": True,
                "response": response_text,
                "action": action,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"[VoiceAgent] Error: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": "I encountered an error while processing that command."
            }
