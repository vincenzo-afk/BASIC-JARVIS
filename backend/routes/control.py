"""
Control Route - System Control Endpoints
Handles mouse, keyboard, and system automation
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from modules.control import mouse, keyboard, system, apps
from modules.utils.logger import logger
from config.settings import ENABLE_SYSTEM_CONTROL

router = APIRouter()


# Request Models
class MouseClickRequest(BaseModel):
    x: int = Field(..., description="X coordinate")
    y: int = Field(..., description="Y coordinate")
    button: str = Field(default="left", description="Button: left, right, middle")
    clicks: int = Field(default=1, ge=1, le=3)


class MouseMoveRequest(BaseModel):
    x: int
    y: int
    duration: float = Field(default=0.25, ge=0, le=5)


class MouseScrollRequest(BaseModel):
    amount: int = Field(..., description="Scroll amount (positive=up, negative=down)")
    x: Optional[int] = None
    y: Optional[int] = None


class KeyTypeRequest(BaseModel):
    text: str = Field(..., description="Text to type")
    interval: float = Field(default=0.05, ge=0, le=1)


class KeyPressRequest(BaseModel):
    key: str = Field(..., description="Key to press (e.g., 'enter', 'tab', 'f1')")
    modifiers: List[str] = Field(default=[], description="Modifier keys: ctrl, alt, shift, win")


class HotkeyRequest(BaseModel):
    keys: List[str] = Field(..., description="Keys to press together (e.g., ['ctrl', 'c'])")


class AppOpenRequest(BaseModel):
    app_name: str = Field(..., description="Application name or path")
    args: List[str] = Field(default=[], description="Command line arguments")


# Middleware to check if system control is enabled
def check_enabled():
    if not ENABLE_SYSTEM_CONTROL:
        raise HTTPException(
            status_code=403,
            detail="System control is disabled. Set ENABLE_SYSTEM_CONTROL=true to enable."
        )


# Mouse Endpoints
@router.post("/mouse/click")
async def mouse_click(request: MouseClickRequest):
    """Click at specified coordinates"""
    check_enabled()
    
    try:
        mouse.click(request.x, request.y, request.button, request.clicks)
        return {
            "status": "success",
            "action": "click",
            "position": {"x": request.x, "y": request.y}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mouse/move")
async def mouse_move(request: MouseMoveRequest):
    """Move mouse to coordinates"""
    check_enabled()
    
    try:
        mouse.move(request.x, request.y, request.duration)
        return {
            "status": "success",
            "action": "move",
            "position": {"x": request.x, "y": request.y}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mouse/scroll")
async def mouse_scroll(request: MouseScrollRequest):
    """Scroll mouse wheel"""
    check_enabled()
    
    try:
        mouse.scroll(request.amount, request.x, request.y)
        return {
            "status": "success",
            "action": "scroll",
            "amount": request.amount
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/mouse/position")
async def get_mouse_position():
    """Get current mouse position"""
    try:
        pos = mouse.get_position()
        return {"x": pos[0], "y": pos[1]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Keyboard Endpoints
@router.post("/keyboard/type")
async def key_type(request: KeyTypeRequest):
    """Type text"""
    check_enabled()
    
    try:
        keyboard.type_text(request.text, request.interval)
        return {
            "status": "success",
            "action": "type",
            "length": len(request.text)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/keyboard/press")
async def key_press(request: KeyPressRequest):
    """Press a key with optional modifiers"""
    check_enabled()
    
    try:
        keyboard.press_key(request.key, request.modifiers)
        return {
            "status": "success",
            "action": "press",
            "key": request.key,
            "modifiers": request.modifiers
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/keyboard/hotkey")
async def key_hotkey(request: HotkeyRequest):
    """Press a hotkey combination"""
    check_enabled()
    
    try:
        keyboard.hotkey(request.keys)
        return {
            "status": "success",
            "action": "hotkey",
            "keys": request.keys
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Application Endpoints
@router.post("/app/open")
async def open_app(request: AppOpenRequest):
    """Open an application"""
    check_enabled()
    
    try:
        apps.open_application(request.app_name, request.args)
        return {
            "status": "success",
            "action": "open",
            "app": request.app_name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/app/list")
async def list_running_apps():
    """List running applications"""
    try:
        processes = apps.list_running()
        return {"processes": processes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/app/kill")
async def kill_app(name: str):
    """Kill an application by name"""
    check_enabled()
    
    try:
        apps.kill_process(name)
        return {"status": "success", "action": "kill", "app": name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# System Endpoints
@router.post("/system/shutdown")
async def do_shutdown():
    """Shutdown the system"""
    check_enabled()
    
    logger.warning("System shutdown requested!")
    try:
        system.shutdown()
        return {"status": "shutting down"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/system/restart")
async def do_restart():
    """Restart the system"""
    check_enabled()
    
    logger.warning("System restart requested!")
    try:
        system.restart()
        return {"status": "restarting"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/system/sleep")
async def do_sleep():
    """Put system to sleep"""
    check_enabled()
    
    try:
        system.sleep()
        return {"status": "sleeping"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system/info")
async def get_system_info():
    """Get system information"""
    try:
        info = system.get_info()
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
