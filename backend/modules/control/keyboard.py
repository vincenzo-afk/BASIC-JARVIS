"""
Keyboard Control Module
Handles keyboard automation using pyautogui
"""
import pyautogui
from typing import List
from modules.utils.logger import logger

# Safety settings
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.05


def type_text(text: str, interval: float = 0.05):
    """
    Type text string
    
    Args:
        text: Text to type
        interval: Delay between keystrokes
    """
    logger.info(f"Keyboard type: {len(text)} characters")
    pyautogui.write(text, interval=interval)


def type_with_enter(text: str):
    """Type text and press enter"""
    type_text(text)
    press_key("enter")


def press_key(key: str, modifiers: List[str] = None):
    """
    Press a single key with optional modifiers
    
    Args:
        key: Key to press (e.g., 'enter', 'tab', 'a', 'f1')
        modifiers: List of modifier keys ['ctrl', 'alt', 'shift', 'win']
    """
    logger.info(f"Keyboard press: {key} modifiers={modifiers}")
    
    if modifiers:
        # Hold modifiers, press key, release modifiers
        for mod in modifiers:
            pyautogui.keyDown(mod)
        
        pyautogui.press(key)
        
        for mod in reversed(modifiers):
            pyautogui.keyUp(mod)
    else:
        pyautogui.press(key)


def hotkey(keys: List[str]):
    """
    Press a hotkey combination
    
    Args:
        keys: List of keys to press together (e.g., ['ctrl', 'c'])
    """
    logger.info(f"Keyboard hotkey: {'+'.join(keys)}")
    pyautogui.hotkey(*keys)


def key_down(key: str):
    """Press and hold a key"""
    pyautogui.keyDown(key)


def key_up(key: str):
    """Release a key"""
    pyautogui.keyUp(key)


# Common shortcuts
def copy():
    """Ctrl+C"""
    hotkey(['ctrl', 'c'])


def paste():
    """Ctrl+V"""
    hotkey(['ctrl', 'v'])


def cut():
    """Ctrl+X"""
    hotkey(['ctrl', 'x'])


def undo():
    """Ctrl+Z"""
    hotkey(['ctrl', 'z'])


def redo():
    """Ctrl+Y"""
    hotkey(['ctrl', 'y'])


def select_all():
    """Ctrl+A"""
    hotkey(['ctrl', 'a'])


def save():
    """Ctrl+S"""
    hotkey(['ctrl', 's'])


def find():
    """Ctrl+F"""
    hotkey(['ctrl', 'f'])


def new_tab():
    """Ctrl+T"""
    hotkey(['ctrl', 't'])


def close_tab():
    """Ctrl+W"""
    hotkey(['ctrl', 'w'])


def switch_window():
    """Alt+Tab"""
    hotkey(['alt', 'tab'])


def screenshot():
    """Print Screen"""
    press_key('printscreen')


def open_run():
    """Win+R"""
    hotkey(['win', 'r'])


def open_explorer():
    """Win+E"""
    hotkey(['win', 'e'])


def lock_screen():
    """Win+L"""
    hotkey(['win', 'l'])


def minimize_all():
    """Win+D"""
    hotkey(['win', 'd'])
