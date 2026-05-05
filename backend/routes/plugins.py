"""
Plugin Routes - FULLY FUNCTIONAL
API endpoints for plugin management and execution
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import os
import sys
import json
import importlib
import importlib.util
from pathlib import Path
from modules.utils.logger import logger
from config.settings import PLUGIN_DIR

router = APIRouter()


# === Models ===

class PluginInfo(BaseModel):
    """Plugin information"""
    name: str
    description: str
    version: str
    author: Optional[str] = None
    commands: List[str]
    dependencies: List[str] = []
    installed: bool = True
    loaded: bool = False
    error: Optional[str] = None


class PluginRunRequest(BaseModel):
    """Request to run a plugin command"""
    command: str = Field(..., description="Command to execute")
    params: Dict[str, Any] = Field(default={}, description="Command parameters")


class PluginRunResponse(BaseModel):
    """Plugin execution response"""
    plugin: str
    command: str
    status: str
    result: Optional[Any] = None
    error: Optional[str] = None


# === Plugin Manager ===

class PluginManager:
    """
    Manages plugin discovery, loading, and execution
    """
    
    def __init__(self, plugin_dir: str = None):
        self.plugin_dir = Path(plugin_dir or PLUGIN_DIR)
        self.plugins: Dict[str, Dict[str, Any]] = {}
        self._loaded_modules: Dict[str, Any] = {}
        
        # Ensure plugin directory exists
        self.plugin_dir.mkdir(parents=True, exist_ok=True)
        
        # Discover plugins
        self._discover_plugins()
    
    def _discover_plugins(self):
        """Scan plugin directory for available plugins"""
        self.plugins = {}
        
        if not self.plugin_dir.exists():
            return
        
        for item in self.plugin_dir.iterdir():
            if item.is_dir() and not item.name.startswith("_"):
                manifest_path = item / "manifest.json"
                
                if manifest_path.exists():
                    try:
                        with open(manifest_path, "r", encoding="utf-8") as f:
                            manifest = json.load(f)
                        
                        self.plugins[manifest.get("name", item.name)] = {
                            "path": str(item),
                            "manifest": manifest,
                            "loaded": False,
                            "error": None,
                            "instance": None
                        }
                        
                        logger.info(f"[Plugin] Discovered: {manifest.get('name', item.name)}")
                        
                    except json.JSONDecodeError as e:
                        logger.error(f"[Plugin] Invalid manifest: {manifest_path} - {e}")
                    except Exception as e:
                        logger.error(f"[Plugin] Error reading manifest: {manifest_path} - {e}")
    
    def list_plugins(self) -> List[PluginInfo]:
        """Get list of all plugins"""
        plugins = []
        
        for name, data in self.plugins.items():
            manifest = data.get("manifest", {})
            plugins.append(PluginInfo(
                name=name,
                description=manifest.get("description", ""),
                version=manifest.get("version", "0.0.0"),
                author=manifest.get("author"),
                commands=manifest.get("commands", []),
                dependencies=manifest.get("dependencies", []),
                installed=True,
                loaded=data.get("loaded", False),
                error=data.get("error")
            ))
        
        return plugins
    
    def get_plugin(self, name: str) -> Optional[PluginInfo]:
        """Get plugin info by name"""
        if name not in self.plugins:
            return None
        
        data = self.plugins[name]
        manifest = data.get("manifest", {})
        
        return PluginInfo(
            name=name,
            description=manifest.get("description", ""),
            version=manifest.get("version", "0.0.0"),
            author=manifest.get("author"),
            commands=manifest.get("commands", []),
            dependencies=manifest.get("dependencies", []),
            installed=True,
            loaded=data.get("loaded", False),
            error=data.get("error")
        )
    
    def load_plugin(self, name: str) -> bool:
        """Load a plugin module"""
        if name not in self.plugins:
            logger.error(f"[Plugin] Not found: {name}")
            return False
        
        plugin_data = self.plugins[name]
        
        if plugin_data.get("loaded"):
            return True
        
        try:
            plugin_path = Path(plugin_data["path"])
            manifest = plugin_data["manifest"]
            entry_file = manifest.get("entry", "main.py")
            entry_path = plugin_path / entry_file
            
            if not entry_path.exists():
                raise FileNotFoundError(f"Entry file not found: {entry_path}")
            
            # Load module dynamically
            spec = importlib.util.spec_from_file_location(
                f"plugins.{name}",
                str(entry_path)
            )
            module = importlib.util.module_from_spec(spec)
            
            # Add plugin path to sys.path temporarily
            sys.path.insert(0, str(plugin_path))
            
            try:
                spec.loader.exec_module(module)
            finally:
                sys.path.remove(str(plugin_path))
            
            # Get plugin instance
            if hasattr(module, "plugin"):
                instance = module.plugin
            elif hasattr(module, "Plugin"):
                instance = module.Plugin()
            else:
                raise AttributeError("Plugin must export 'plugin' instance or 'Plugin' class")
            
            # Store
            plugin_data["loaded"] = True
            plugin_data["instance"] = instance
            plugin_data["error"] = None
            self._loaded_modules[name] = module
            
            logger.info(f"[Plugin] Loaded: {name}")
            return True
            
        except Exception as e:
            plugin_data["loaded"] = False
            plugin_data["error"] = str(e)
            logger.error(f"[Plugin] Failed to load {name}: {e}")
            return False
    
    def unload_plugin(self, name: str) -> bool:
        """Unload a plugin"""
        if name not in self.plugins:
            return False
        
        plugin_data = self.plugins[name]
        plugin_data["loaded"] = False
        plugin_data["instance"] = None
        
        if name in self._loaded_modules:
            del self._loaded_modules[name]
        
        logger.info(f"[Plugin] Unloaded: {name}")
        return True
    
    def reload_plugin(self, name: str) -> bool:
        """Reload a plugin"""
        self.unload_plugin(name)
        return self.load_plugin(name)
    
    def run_command(self, name: str, command: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Run a plugin command"""
        if name not in self.plugins:
            return {"error": f"Plugin not found: {name}"}
        
        plugin_data = self.plugins[name]
        
        # Load if needed
        if not plugin_data.get("loaded"):
            if not self.load_plugin(name):
                return {"error": f"Failed to load plugin: {plugin_data.get('error')}"}
        
        instance = plugin_data.get("instance")
        
        if not instance:
            return {"error": "Plugin instance not available"}
        
        # Check if command is valid
        manifest = plugin_data.get("manifest", {})
        valid_commands = manifest.get("commands", [])
        
        if valid_commands and command not in valid_commands:
            return {"error": f"Unknown command: {command}. Available: {valid_commands}"}
        
        try:
            # Execute command
            if hasattr(instance, "run"):
                result = instance.run(command, params or {})
            elif hasattr(instance, command):
                method = getattr(instance, command)
                result = method(params or {})
            else:
                return {"error": f"Command not implemented: {command}"}
            
            return {"status": "success", "result": result}
            
        except Exception as e:
            logger.error(f"[Plugin] Execution error in {name}.{command}: {e}")
            return {"error": str(e)}


# Global plugin manager instance
_manager: Optional[PluginManager] = None

def get_manager() -> PluginManager:
    """Get or create plugin manager"""
    global _manager
    if _manager is None:
        _manager = PluginManager()
    return _manager


# === Endpoints ===

@router.get("/", response_model=List[PluginInfo])
async def list_plugins():
    """
    List all available plugins
    
    Returns plugin metadata including available commands.
    """
    manager = get_manager()
    return manager.list_plugins()


@router.get("/{plugin_name}", response_model=PluginInfo)
async def get_plugin_info(plugin_name: str):
    """
    Get information about a specific plugin
    
    Returns detailed plugin metadata.
    """
    manager = get_manager()
    plugin = manager.get_plugin(plugin_name)
    
    if not plugin:
        raise HTTPException(status_code=404, detail=f"Plugin not found: {plugin_name}")
    
    return plugin


@router.post("/{plugin_name}/run", response_model=PluginRunResponse)
async def run_plugin_command(plugin_name: str, request: PluginRunRequest):
    """
    Execute a plugin command
    
    - **plugin_name**: Name of the plugin
    - **command**: Command to execute
    - **params**: Parameters for the command
    """
    manager = get_manager()
    
    logger.info(f"[Plugin] Running: {plugin_name}.{request.command}")
    
    result = manager.run_command(plugin_name, request.command, request.params)
    
    if "error" in result:
        return PluginRunResponse(
            plugin=plugin_name,
            command=request.command,
            status="error",
            error=result.get("error")
        )
    
    return PluginRunResponse(
        plugin=plugin_name,
        command=request.command,
        status="success",
        result=result.get("result")
    )


@router.post("/{plugin_name}/load")
async def load_plugin(plugin_name: str):
    """
    Load a plugin into memory
    
    Loads the plugin module without executing commands.
    """
    manager = get_manager()
    
    if plugin_name not in manager.plugins:
        raise HTTPException(status_code=404, detail=f"Plugin not found: {plugin_name}")
    
    success = manager.load_plugin(plugin_name)
    
    if success:
        return {"status": "loaded", "plugin": plugin_name}
    else:
        error = manager.plugins[plugin_name].get("error", "Unknown error")
        raise HTTPException(status_code=500, detail=f"Failed to load: {error}")


@router.post("/{plugin_name}/unload")
async def unload_plugin(plugin_name: str):
    """
    Unload a plugin from memory
    """
    manager = get_manager()
    
    if plugin_name not in manager.plugins:
        raise HTTPException(status_code=404, detail=f"Plugin not found: {plugin_name}")
    
    manager.unload_plugin(plugin_name)
    return {"status": "unloaded", "plugin": plugin_name}


@router.post("/{plugin_name}/reload")
async def reload_plugin(plugin_name: str):
    """
    Reload a plugin (unload + load)
    
    Useful for development when plugin code changes.
    """
    manager = get_manager()
    
    if plugin_name not in manager.plugins:
        raise HTTPException(status_code=404, detail=f"Plugin not found: {plugin_name}")
    
    success = manager.reload_plugin(plugin_name)
    
    if success:
        return {"status": "reloaded", "plugin": plugin_name}
    else:
        error = manager.plugins[plugin_name].get("error", "Unknown error")
        raise HTTPException(status_code=500, detail=f"Failed to reload: {error}")


@router.post("/refresh")
async def refresh_plugins():
    """
    Rescan plugin directory for new plugins
    """
    manager = get_manager()
    manager._discover_plugins()
    
    return {
        "status": "refreshed",
        "plugins": len(manager.plugins)
    }
