# JARVIS API Reference

Complete API documentation for the JARVIS backend.

**Base URL:** `http://localhost:8000`

---

## Table of Contents

- [Health & Status](#health--status)
- [Chat API](#chat-api)
- [Screen API](#screen-api)
- [Control API](#control-api)
- [Voice API](#voice-api)
- [Agent API](#agent-api)
- [Plugin API](#plugin-api)

---

## Health & Status

### GET /

Health check endpoint.

**Response:**
```json
{
  "status": "running",
  "service": "JARVIS Backend",
  "version": "1.0.0",
  "endpoints": {
    "chat": "/api/chat",
    "screen": "/api/screen",
    "control": "/api/control",
    "voice": "/api/voice",
    "agent": "/api/agent",
    "plugins": "/api/plugins"
  }
}
```

### GET /health

Detailed health check with service statuses.

**Response:**
```json
{
  "status": "healthy",
  "ollama": "connected",
  "modules": {
    "chat": true,
    "screen": true,
    "control": true,
    "voice": true,
    "agent": true,
    "plugins": true
  }
}
```

---

## Chat API

Base path: `/api/chat`

### POST /api/chat/

Send a message to the LLM.

**Request Body:**
```json
{
  "model": "llama3.1:8b",
  "prompt": "Hello, JARVIS!",
  "system": "You are a helpful assistant.",
  "temperature": 0.7,
  "max_tokens": 1000
}
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| model | string | No | llama3.1:8b | Ollama model name |
| prompt | string | Yes | - | User message |
| system | string | No | null | System prompt |
| temperature | float | No | 0.7 | Creativity (0.0-2.0) |
| max_tokens | int | No | null | Max response length |

**Response:**
```json
{
  "response": "Hello! How can I assist you today?",
  "model": "llama3.1:8b",
  "tokens_used": 15,
  "duration_ms": 1234.56
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"model": "llama3.1:8b", "prompt": "What is 2+2?"}'
```

---

### POST /api/chat/conversation

Multi-turn conversation with message history.

**Request Body:**
```json
{
  "model": "llama3.1:8b",
  "messages": [
    {"role": "user", "content": "My name is John"},
    {"role": "assistant", "content": "Hello John!"},
    {"role": "user", "content": "What is my name?"}
  ],
  "temperature": 0.7
}
```

**Response:**
```json
{
  "response": "Your name is John.",
  "model": "llama3.1:8b"
}
```

---

### GET /api/chat/models

List available Ollama models.

**Response:**
```json
{
  "models": [
    {
      "name": "llama3.1:8b",
      "size": 4661224448,
      "modified_at": "2024-01-15T10:30:00Z"
    },
    {
      "name": "qwen2.5-coder:7b",
      "size": 4405252096,
      "modified_at": "2024-01-14T08:00:00Z"
    }
  ]
}
```

---

### GET /api/chat/models/{model_name}

Get detailed information about a model.

**Response:**
```json
{
  "modelfile": "...",
  "parameters": "...",
  "template": "..."
}
```

---

### POST /api/chat/models/{model_name}/pull

Pull/download a model from Ollama library.

**Response:**
```json
{
  "status": "success",
  "model": "mistral:7b"
}
```

---

## Screen API

Base path: `/api/screen`

### POST /api/screen/read

Capture screen and extract text via OCR.

**Request Body:**
```json
{
  "region": {
    "x": 0,
    "y": 0,
    "width": 800,
    "height": 600
  },
  "monitor": 1,
  "preprocess": true
}
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| region | object | No | null | Specific area to capture |
| monitor | int | No | 0 | Monitor (0=all, 1+=specific) |
| preprocess | bool | No | true | Apply OCR preprocessing |

**Response:**
```json
{
  "text": "Extracted text from screen...",
  "image_path": "/temp/screenshots/screenshot_20240115_103000.png",
  "width": 1920,
  "height": 1080,
  "word_count": 150
}
```

---

### POST /api/screen/capture

Capture screenshot without OCR.

**Query Parameters:**
- `monitor` (int): Monitor number

**Response:**
```json
{
  "image_path": "/temp/screenshots/screenshot_20240115_103000.png",
  "width": 1920,
  "height": 1080
}
```

---

### GET /api/screen/monitors

List available monitors.

**Response:**
```json
{
  "monitors": [
    {
      "id": 0,
      "left": 0,
      "top": 0,
      "width": 3840,
      "height": 1080,
      "is_primary": false,
      "is_combined": true
    },
    {
      "id": 1,
      "left": 0,
      "top": 0,
      "width": 1920,
      "height": 1080,
      "is_primary": true,
      "is_combined": false
    }
  ]
}
```

---

## Control API

Base path: `/api/control`

### Mouse

#### POST /api/control/mouse/click

**Request Body:**
```json
{
  "x": 500,
  "y": 300,
  "button": "left",
  "clicks": 1
}
```

#### POST /api/control/mouse/move

```json
{
  "x": 500,
  "y": 300,
  "duration": 0.25
}
```

#### POST /api/control/mouse/scroll

```json
{
  "amount": 3,
  "x": 500,
  "y": 300
}
```

#### GET /api/control/mouse/position

**Response:**
```json
{
  "x": 500,
  "y": 300
}
```

---

### Keyboard

#### POST /api/control/keyboard/type

```json
{
  "text": "Hello World",
  "interval": 0.05
}
```

#### POST /api/control/keyboard/press

```json
{
  "key": "enter",
  "modifiers": ["ctrl", "shift"]
}
```

#### POST /api/control/keyboard/hotkey

```json
{
  "keys": ["ctrl", "c"]
}
```

---

### Applications

#### POST /api/control/app/open

```json
{
  "app_name": "notepad",
  "args": []
}
```

#### GET /api/control/app/list

**Response:**
```json
{
  "processes": [
    {
      "pid": 1234,
      "name": "chrome.exe",
      "cpu_percent": 5.2,
      "memory_percent": 12.5,
      "status": "running"
    }
  ]
}
```

#### POST /api/control/app/kill

**Query Parameters:**
- `name` (string): Process name

---

### System

#### GET /api/control/system/info

**Response:**
```json
{
  "platform": {
    "system": "Windows",
    "release": "10",
    "hostname": "MY-PC"
  },
  "cpu": {
    "cores_physical": 8,
    "cores_logical": 16,
    "frequency_mhz": 3600,
    "usage_percent": 25.5
  },
  "memory": {
    "total_gb": 32.0,
    "available_gb": 16.5,
    "percent": 48.4
  },
  "disk": {
    "total_gb": 500,
    "free_gb": 250,
    "percent": 50
  }
}
```

#### POST /api/control/system/shutdown
#### POST /api/control/system/restart
#### POST /api/control/system/sleep

---

## Voice API

Base path: `/api/voice`

### GET /api/voice/status

**Response:**
```json
{
  "stt_available": true,
  "tts_available": true,
  "stt_model": "base",
  "tts_engine": "piper"
}
```

### POST /api/voice/transcribe

Upload audio file for transcription.

**Form Data:**
- `file`: Audio file (WAV, MP3, etc.)

**Response:**
```json
{
  "text": "Transcribed text from audio",
  "filename": "recording.wav"
}
```

### POST /api/voice/speak

**Request Body:**
```json
{
  "text": "Hello, I am JARVIS."
}
```

**Response:**
```json
{
  "status": "success",
  "output": "/temp/audio/speech.wav"
}
```

---

## Agent API

Base path: `/api/agent`

### POST /api/agent/run

Run a simple agent task.

**Request Body:**
```json
{
  "task": "Open notepad and type Hello World",
  "context": {}
}
```

### POST /api/agent/workflow

Run a defined workflow.

**Request Body:**
```json
{
  "name": "my_workflow",
  "description": "Test workflow",
  "steps": [
    {
      "name": "step1",
      "action": "log",
      "params": {"message": "Starting..."}
    },
    {
      "name": "step2",
      "action": "llm_query",
      "params": {"prompt": "What is 2+2?"}
    }
  ],
  "variables": {}
}
```

**Response:**
```json
{
  "status": "completed",
  "results": [
    {"step": "step1", "result": "Starting..."},
    {"step": "step2", "result": "4"}
  ],
  "context": {}
}
```

### GET /api/agent/actions

List available workflow actions.

**Response:**
```json
{
  "actions": ["log", "wait", "set_variable", "http_request", "run_command", "llm_query"]
}
```

---

## Plugin API

Base path: `/api/plugins`

### GET /api/plugins/

List all plugins.

**Response:**
```json
[
  {
    "name": "youtube_dl",
    "description": "Download YouTube videos",
    "version": "1.0.0",
    "commands": ["download", "audio", "info"],
    "installed": true,
    "loaded": false
  }
]
```

### GET /api/plugins/{plugin_name}

Get plugin details.

### POST /api/plugins/{plugin_name}/run

Execute a plugin command.

**Request Body:**
```json
{
  "command": "download",
  "params": {
    "url": "https://youtube.com/watch?v=...",
    "quality": "720"
  }
}
```

**Response:**
```json
{
  "plugin": "youtube_dl",
  "command": "download",
  "result": {
    "status": "success",
    "path": "/Downloads/JARVIS/video.mp4"
  }
}
```

### POST /api/plugins/{plugin_name}/reload

Reload a plugin module.

---

## Error Responses

All endpoints return errors in this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

**Common HTTP Status Codes:**

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad Request |
| 404 | Not Found |
| 500 | Internal Server Error |
| 503 | Service Unavailable |

---

## Rate Limiting

Currently no rate limiting is applied. For production use, consider adding rate limiting.

---

## Authentication

Currently no authentication is required. For production use, consider adding API key authentication.
