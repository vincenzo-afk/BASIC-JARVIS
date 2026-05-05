# JARVIS Shared Resources

Shared schemas, types, and resources used by both the backend (Python) and frontend (Electron/React).

---

## 📁 Structure

```
shared/
├── ipc_schemas/         # JSON schemas for API communication
│   ├── chat.json        # Chat request/response schema
│   ├── screen.json      # Screen capture schema
│   ├── control.json     # System control schema
│   ├── agent.json       # Agent workflow schema
│   └── plugin.json      # Plugin execution schema
│
└── types/               # TypeScript type definitions
    └── common.ts        # Shared TypeScript interfaces
```

---

## 📋 IPC Schemas

### chat.json

Defines the structure for LLM chat requests:

```json
{
  "type": "object",
  "properties": {
    "model": { "type": "string" },
    "prompt": { "type": "string" },
    "system": { "type": "string" },
    "temperature": { "type": "number" }
  },
  "required": ["prompt"]
}
```

### screen.json

Defines screen capture parameters:

```json
{
  "type": "object",
  "properties": {
    "region": {
      "type": "object",
      "properties": {
        "x": { "type": "integer" },
        "y": { "type": "integer" },
        "width": { "type": "integer" },
        "height": { "type": "integer" }
      }
    }
  }
}
```

### control.json

Defines system control actions:

```json
{
  "type": "object",
  "oneOf": [
    {
      "properties": {
        "action": { "const": "mouse_click" },
        "x": { "type": "integer" },
        "y": { "type": "integer" }
      }
    },
    {
      "properties": {
        "action": { "const": "key_type" },
        "text": { "type": "string" }
      }
    }
  ]
}
```

### agent.json

Defines workflow structure:

```json
{
  "type": "object",
  "properties": {
    "name": { "type": "string" },
    "steps": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": { "type": "string" },
          "action": { "type": "string" },
          "params": { "type": "object" }
        }
      }
    }
  }
}
```

### plugin.json

Defines plugin execution:

```json
{
  "type": "object",
  "properties": {
    "plugin_name": { "type": "string" },
    "command": { "type": "string" },
    "params": { "type": "object" }
  }
}
```

---

## 📝 TypeScript Types

### common.ts

```typescript
// Chat
export interface ChatRequest {
  model: string;
  prompt: string;
  system?: string;
  temperature?: number;
}

export interface ChatResponse {
  response: string;
  model: string;
  tokens_used?: number;
  duration_ms?: number;
}

// Screen
export interface ScreenRegion {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface ScreenReadResponse {
  text: string;
  image_path: string;
  width: number;
  height: number;
}

// Control
export interface MouseClickRequest {
  x: number;
  y: number;
  button?: 'left' | 'right' | 'middle';
  clicks?: number;
}

export interface KeyTypeRequest {
  text: string;
  interval?: number;
}

// Plugin
export interface PluginInfo {
  name: string;
  description: string;
  version: string;
  commands: string[];
}

export interface PluginRunRequest {
  command: string;
  params: Record<string, any>;
}
```

---

## 🔧 Usage

### In Python (Backend)

```python
import json
from pathlib import Path

# Load schema
schema_path = Path("shared/ipc_schemas/chat.json")
with open(schema_path) as f:
    chat_schema = json.load(f)

# Validate with jsonschema
from jsonschema import validate
validate(instance=request_data, schema=chat_schema)
```

### In TypeScript (Frontend)

```typescript
import { ChatRequest, ChatResponse } from '../shared/types/common';

const request: ChatRequest = {
  model: 'llama3.1:8b',
  prompt: 'Hello JARVIS!'
};

const response: ChatResponse = await api.post('/chat/', request);
```

---

## 📄 License

MIT License - Part of the JARVIS project.
