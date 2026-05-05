"""
Screen Capture Module
Handles screenshot functionality using mss
"""
import mss
import mss.tools
import os
from datetime import datetime
from typing import Optional, Dict, Tuple, List
from config.settings import TEMP_DIR
from modules.utils.logger import logger


class ScreenCapture:
    """
    Screen capture utility using mss library
    
    Features:
    - Multi-monitor support
    - Region-specific capture
    - Automatic file management
    """
    
    def __init__(self, output_dir: str = None):
        self.output_dir = output_dir or str(TEMP_DIR / "screenshots")
        os.makedirs(self.output_dir, exist_ok=True)
        self._sct = None
    
    def _get_sct(self) -> mss.mss:
        """Get or create mss instance"""
        if self._sct is None:
            self._sct = mss.mss()
        return self._sct
    
    def capture(
        self,
        monitor: int = 0,
        region: Optional[Dict[str, int]] = None,
        filename: Optional[str] = None
    ) -> Tuple[str, Dict[str, int]]:
        """
        Capture screen or region
        
        Args:
            monitor: Monitor number (0 = all monitors combined, 1+ = specific)
            region: Optional dict with left, top, width, height
            filename: Optional custom filename
            
        Returns:
            Tuple of (filepath, dimensions dict)
        """
        sct = self._get_sct()
        
        # Determine capture area
        if region:
            capture_area = {
                "left": region.get("left", 0),
                "top": region.get("top", 0),
                "width": region.get("width", 800),
                "height": region.get("height", 600)
            }
        elif monitor == 0:
            # All monitors
            capture_area = sct.monitors[0]
        else:
            # Specific monitor
            if monitor < len(sct.monitors):
                capture_area = sct.monitors[monitor]
            else:
                logger.warning(f"Monitor {monitor} not found, using primary")
                capture_area = sct.monitors[1] if len(sct.monitors) > 1 else sct.monitors[0]
        
        # Capture
        screenshot = sct.grab(capture_area)
        
        # Generate filename
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"screenshot_{timestamp}.png"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Save
        mss.tools.to_png(screenshot.rgb, screenshot.size, output=filepath)
        
        dimensions = {
            "width": screenshot.width,
            "height": screenshot.height,
            "left": capture_area.get("left", 0),
            "top": capture_area.get("top", 0)
        }
        
        logger.info(f"Screenshot saved: {filepath} ({screenshot.width}x{screenshot.height})")
        
        return filepath, dimensions
    
    def capture_active_window(self) -> Tuple[str, Dict[str, int]]:
        """
        Capture the currently active window
        
        Note: This is platform-specific and may require additional libraries
        """
        # For now, capture primary monitor
        # Full implementation would use pygetwindow or similar
        return self.capture(monitor=1)
    
    def list_monitors(self) -> List[Dict[str, int]]:
        """
        List all available monitors
        
        Returns:
            List of monitor info dicts
        """
        sct = self._get_sct()
        
        monitors = []
        for i, mon in enumerate(sct.monitors):
            monitors.append({
                "id": i,
                "left": mon["left"],
                "top": mon["top"],
                "width": mon["width"],
                "height": mon["height"],
                "is_primary": i == 1,  # Monitor 1 is typically primary
                "is_combined": i == 0   # Monitor 0 is all monitors
            })
        
        return monitors
    
    def cleanup_old_screenshots(self, max_age_hours: int = 24):
        """Remove screenshots older than specified hours"""
        import time
        
        now = time.time()
        cutoff = now - (max_age_hours * 3600)
        
        removed = 0
        for filename in os.listdir(self.output_dir):
            filepath = os.path.join(self.output_dir, filename)
            if os.path.isfile(filepath):
                if os.path.getmtime(filepath) < cutoff:
                    os.remove(filepath)
                    removed += 1
        
        if removed > 0:
            logger.info(f"Cleaned up {removed} old screenshots")
        
        return removed
    
    def __del__(self):
        """Cleanup mss instance"""
        if self._sct:
            self._sct.close()


# Convenience function
def capture_screen() -> str:
    """Quick capture of primary screen, returns filepath"""
    sc = ScreenCapture()
    filepath, _ = sc.capture(monitor=1)
    return filepath
