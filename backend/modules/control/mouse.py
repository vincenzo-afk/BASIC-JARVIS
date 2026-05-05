"""
Mouse Control Module
Handles mouse automation using pyautogui
"""
import pyautogui
from typing import Tuple
from modules.utils.logger import logger

# Safety settings
pyautogui.FAILSAFE = True  # Move to corner to abort
pyautogui.PAUSE = 0.1  # Small pause between actions


def click(x: int, y: int, button: str = "left", clicks: int = 1):
    """
    Click at specified coordinates
    
    Args:
        x: X coordinate
        y: Y coordinate
        button: 'left', 'right', or 'middle'
        clicks: Number of clicks (1-3)
    """
    logger.info(f"Mouse click: ({x}, {y}) button={button} clicks={clicks}")
    pyautogui.click(x=x, y=y, button=button, clicks=clicks)


def double_click(x: int, y: int):
    """Double click at coordinates"""
    logger.info(f"Mouse double-click: ({x}, {y})")
    pyautogui.doubleClick(x=x, y=y)


def right_click(x: int, y: int):
    """Right click at coordinates"""
    logger.info(f"Mouse right-click: ({x}, {y})")
    pyautogui.rightClick(x=x, y=y)


def move(x: int, y: int, duration: float = 0.25):
    """
    Move mouse to coordinates
    
    Args:
        x: Target X
        y: Target Y
        duration: Time to move (0 = instant)
    """
    logger.info(f"Mouse move: ({x}, {y}) duration={duration}s")
    pyautogui.moveTo(x, y, duration=duration)


def move_relative(dx: int, dy: int, duration: float = 0.25):
    """Move mouse relative to current position"""
    pyautogui.moveRel(dx, dy, duration=duration)


def drag(start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 0.5):
    """
    Drag from start to end position
    """
    logger.info(f"Mouse drag: ({start_x}, {start_y}) -> ({end_x}, {end_y})")
    pyautogui.moveTo(start_x, start_y)
    pyautogui.drag(end_x - start_x, end_y - start_y, duration=duration)


def scroll(amount: int, x: int = None, y: int = None):
    """
    Scroll mouse wheel
    
    Args:
        amount: Positive = up, negative = down
        x, y: Optional position to scroll at
    """
    logger.info(f"Mouse scroll: {amount} at ({x}, {y})")
    
    if x is not None and y is not None:
        pyautogui.moveTo(x, y)
    
    pyautogui.scroll(amount)


def get_position() -> Tuple[int, int]:
    """Get current mouse position"""
    try:
        pos = pyautogui.position()
        return (pos.x, pos.y)
    except Exception as e:
        logger.warning(f"Failed to get mouse position: {e}")
        return (0, 0)


def get_screen_size() -> Tuple[int, int]:
    """Get screen dimensions"""
    size = pyautogui.size()
    return (size.width, size.height)


def mouse_down(button: str = "left"):
    """Press and hold mouse button"""
    pyautogui.mouseDown(button=button)


def mouse_up(button: str = "left"):
    """Release mouse button"""
    pyautogui.mouseUp(button=button)
