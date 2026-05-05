# JARVIS Backend

The Python FastAPI backend powering JARVIS. Handles LLM communication, screen capture, system control, voice processing, and plugin management.

---

## 📁 Structure

```
backend/
├── main.py                 # FastAPI entry point
├── requirements.txt        # Python dependencies
│
├── config/
│   └── settings.py         # Configuration & environment variables
│
├── routes/                 # API endpoints
│   ├── chat.py            # LLM chat (/api/chat)
│   ├── screen.py          # Screen capture & OCR (/api/screen)
│   ├── control.py         # System control (/api/control)
│   ├── voice.py           # STT & TTS (/api/voice)
│   ├── agent.py           # Workflow automation (/api/agent)
│   └── plugins.py         # Plugin management (/api/plugins)
│
├── modules/               # Core functionality
│   ├── llm/
│   │   └── ollama_client.py    # Ollama API client
│   │
│   ├── ocr/
│   │   ├── screen_capture.py   # Screenshot using mss
│   │   └── ocr_engine.py       # Tesseract OCR
│   │
│   ├── control/
│   │   ├── mouse.py            # Mouse automation
│   │   ├── keyboard.py         # Keyboard automation
│   │   ├── system.py           # Shutdown/restart/sleep
│   │   └── apps.py             # Application control
│   │
│   ├── voice/
│   │   ├── stt_whisper.py      # Speech-to-text
│   │   └── tts_piper.py        # Text-to-speech
│   │
│   ├── agents/
│   │   ├── base_agent.py       # Agent base class
│   │   └── workflow_engine.py  # Workflow execution
│   │
│   └── utils/
│       ├── logger.py           # Logging utility
│       ├── file_ops.py         # File operations
│       └── status.py           # Status tracking
│
├── plugins/               # Extension plugins
│   ├── youtube_dl/
│   ├── system_stats/
│   └── auto_summariser/
│
├── temp/                  # Temporary files (screenshots, audio)
└── logs/                  # Log files
```

---

## 🚀 Quick Start

### Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Run Server

```bash
python main.py
```

Or with uvicorn directly:

```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## ⚙️ Configuration

Environment variables (create `.env` file):

```env
# Ollama
OLLAMA_HOST=http://localhost:11434
DEFAULT_MODEL=llama3.1:8b

# OCR
TESSERACT_CMD=C:/Program Files/Tesseract-OCR/tesseract.exe
OCR_LANGUAGE=eng

# Voice
WHISPER_MODEL=base
PIPER_PATH=piper
PIPER_MODEL=en_US-lessac-medium.onnx

# API
API_HOST=127.0.0.1
API_PORT=8000
DEBUG_MODE=false
LOG_LEVEL=INFO

# Feature Toggles
ENABLE_OCR=true
ENABLE_VOICE=true
ENABLE_SYSTEM_CONTROL=true
```

---

## 📡 API Endpoints

### Health Check

```http
GET /
GET /health
```

### Chat (LLM)

```http
POST /api/chat/
POST /api/chat/conversation
GET  /api/chat/models
GET  /api/chat/models/{model_name}
POST /api/chat/models/{model_name}/pull
```

### Screen (OCR)

```http
POST /api/screen/read
POST /api/screen/capture
GET  /api/screen/monitors
POST /api/screen/ocr
```

### Control (System)

```http
# Mouse
POST /api/control/mouse/click
POST /api/control/mouse/move
POST /api/control/mouse/scroll
GET  /api/control/mouse/position

# Keyboard
POST /api/control/keyboard/type
POST /api/control/keyboard/press
POST /api/control/keyboard/hotkey

# Applications
POST /api/control/app/open
GET  /api/control/app/list
POST /api/control/app/kill

# System
POST /api/control/system/shutdown
POST /api/control/system/restart
POST /api/control/system/sleep
GET  /api/control/system/info
```

### Voice

```http
GET  /api/voice/status
POST /api/voice/transcribe
POST /api/voice/speak
POST /api/voice/speak-async
```

### Agent

```http
POST /api/agent/run
POST /api/agent/workflow
GET  /api/agent/status/{agent_id}
POST /api/agent/cancel/{agent_id}
GET  /api/agent/actions
```

### Plugins

```http
GET  /api/plugins/
GET  /api/plugins/{plugin_name}
POST /api/plugins/{plugin_name}/run
POST /api/plugins/{plugin_name}/reload
```

---

## 🧪 Testing

### Test Chat Endpoint

```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"model": "llama3.1:8b", "prompt": "Hello JARVIS!"}'
```

### Test Screen Capture

```bash
curl -X POST http://localhost:8000/api/screen/read
```

### Test System Info

```bash
curl http://localhost:8000/api/control/system/info
```

---

## 📦 Dependencies

### Core

| Package | Purpose |
|---------|---------|
| `fastapi` | Web framework |
| `uvicorn` | ASGI server |
| `pydantic` | Data validation |
| `requests` | HTTP client |

### AI/LLM

| Package | Purpose |
|---------|---------|
| `ollama` | Ollama Python client |

### Screen/OCR

| Package | Purpose |
|---------|---------|
| `mss` | Screenshot capture |
| `pytesseract` | OCR engine |
| `opencv-python` | Image processing |
| `Pillow` | Image handling |

### System Control

| Package | Purpose |
|---------|---------|
| `pyautogui` | Mouse/keyboard |
| `psutil` | Process management |

### Voice

| Package | Purpose |
|---------|---------|
| `pyaudio` | Audio I/O |
| `numpy` | Audio processing |
| `soundfile` | Audio file handling |

---

## 🔧 Development

### Code Style

```bash
# Format code
black .

# Sort imports
isort .

# Type checking
mypy .
```

### Running Tests

```bash
pytest tests/
```

---

## 📄 License

MIT License - Part of the JARVIS project.
