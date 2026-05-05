"""
JARVIS Backend Configuration Settings
"""
import os
import shutil
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Plugin directory
PLUGIN_DIR = BASE_DIR / "plugins"

# Temp directory for screenshots, audio, etc.
TEMP_DIR = BASE_DIR / "temp"
TEMP_DIR.mkdir(exist_ok=True)

# Ollama Configuration
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "llama3.1:8b")

# OCR Configuration
# Tool Paths
BIN_DIR = BASE_DIR.parent / "bin"

# OCR Configuration
# Check common install locations for Tesseract
_tesseract_path = os.getenv("TESSERACT_CMD")
if not _tesseract_path:
    possible_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        str(BIN_DIR / "tesseract.exe"),
        str(BIN_DIR / "tesseract" / "tesseract.exe")
    ]
    for p in possible_paths:
        if os.path.exists(p):
            _tesseract_path = p
            break

TESSERACT_CMD = _tesseract_path
OCR_LANGUAGE = os.getenv("OCR_LANGUAGE", "eng")

# Voice Configuration
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")

# Check local piper
_piper_path = os.getenv("PIPER_PATH", "piper")
if not shutil.which(_piper_path) and (BIN_DIR / "piper" / "piper.exe").exists():
    _piper_path = str(BIN_DIR / "piper" / "piper.exe")

PIPER_PATH = _piper_path
PIPER_MODEL = os.getenv("PIPER_MODEL", str(BIN_DIR / "piper" / "en_US-lessac-medium.onnx"))

# Add bin to PATH for FFmpeg
if (BIN_DIR / "ffmpeg.exe").exists():
    os.environ["PATH"] += os.pathsep + str(BIN_DIR)

# API Configuration
API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("API_PORT", "8000"))
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = BASE_DIR / "logs" / "jarvis.log"
LOG_FILE.parent.mkdir(exist_ok=True)

# Security
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_ORIGINS = ["*"]  # Configure for production

# Feature Flags
ENABLE_OCR = os.getenv("ENABLE_OCR", "true").lower() == "true"
ENABLE_VOICE = os.getenv("ENABLE_VOICE", "true").lower() == "true"
ENABLE_SYSTEM_CONTROL = os.getenv("ENABLE_SYSTEM_CONTROL", "true").lower() == "true"

# Export all settings
__all__ = [
    "BASE_DIR",
    "PLUGIN_DIR",
    "TEMP_DIR",
    "OLLAMA_HOST",
    "DEFAULT_MODEL",
    "TESSERACT_CMD",
    "OCR_LANGUAGE",
    "WHISPER_MODEL",
    "PIPER_PATH",
    "PIPER_MODEL",
    "API_HOST",
    "API_PORT",
    "DEBUG_MODE",
    "LOG_LEVEL",
    "LOG_FILE",
    "MAX_UPLOAD_SIZE",
    "ALLOWED_ORIGINS",
    "ENABLE_OCR",
    "ENABLE_VOICE",
    "ENABLE_SYSTEM_CONTROL",
]
