"""
Logger Utility Module
Centralized logging for JARVIS backend
"""
import logging
import sys
from datetime import datetime
from pathlib import Path
from config.settings import LOG_LEVEL, LOG_FILE

# Create logs directory
LOG_FILE.parent.mkdir(exist_ok=True)

# Custom formatter
class JarvisFormatter(logging.Formatter):
    """Custom formatter with colors for console"""
    
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'
    }
    
    def format(self, record):
        # Add color for console
        if hasattr(sys.stdout, 'isatty') and sys.stdout.isatty():
            color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
            reset = self.COLORS['RESET']
            record.levelname = f"{color}{record.levelname}{reset}"
        
        return super().format(record)


def setup_logger(name: str = "JARVIS") -> logging.Logger:
    """
    Set up and return a configured logger
    
    Args:
        name: Logger name
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_format = JarvisFormatter(
        fmt='%(asctime)s │ %(levelname)-8s │ %(name)s │ %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # File handler
    try:
        file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Could not set up file logging: {e}")
    
    return logger


# Create default logger
logger = setup_logger()


# Convenience functions
def debug(msg: str):
    logger.debug(msg)

def info(msg: str):
    logger.info(msg)

def warning(msg: str):
    logger.warning(msg)

def error(msg: str):
    logger.error(msg)

def critical(msg: str):
    logger.critical(msg)
