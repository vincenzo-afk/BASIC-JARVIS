# JARVIS Plugins

This directory contains plugins that extend JARVIS functionality. Plugins are Python modules that can be dynamically loaded and executed.

---

## 📁 Plugin Structure

Each plugin is a folder containing:

```
my_plugin/
├── manifest.json    # Plugin metadata and configuration
├── main.py          # Plugin entry point with Plugin class
└── README.md        # Optional plugin documentation
```

---

## 📝 manifest.json

The manifest file defines plugin metadata:

```json
{
  "name": "my_plugin",
  "description": "Short description of what this plugin does",
  "version": "1.0.0",
  "author": "Your Name",
  "entry": "main.py",
  "commands": ["command1", "command2", "command3"],
  "dependencies": ["requests", "beautifulsoup4"]
}
```

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | ✅ | Unique plugin identifier |
| `description` | string | ✅ | What the plugin does |
| `version` | string | ✅ | Semantic version (x.y.z) |
| `author` | string | ❌ | Plugin author name |
| `entry` | string | ❌ | Entry file (default: main.py) |
| `commands` | array | ✅ | List of available commands |
| `dependencies` | array | ❌ | Python packages required |

---

## 🐍 main.py

The main file must export a `Plugin` class or `plugin` instance:

```python
"""
My Plugin - Description of what it does
"""
from typing import Dict, Any

class Plugin:
    def __init__(self):
        self.name = "My Plugin"
        # Initialize any resources
    
    def run(self, command: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a plugin command
        
        Args:
            command: The command to execute
            params: Parameters passed to the command
            
        Returns:
            Dict with result or error
        """
        commands = {
            "command1": self.do_command1,
            "command2": self.do_command2,
        }
        
        handler = commands.get(command)
        if handler:
            return handler(params)
        
        return {"error": f"Unknown command: {command}"}
    
    def do_command1(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Implementation of command1"""
        value = params.get("input", "default")
        
        # Do something...
        result = f"Processed: {value}"
        
        return {
            "status": "success",
            "result": result
        }
    
    def do_command2(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Implementation of command2"""
        return {"status": "success"}


# Export plugin instance
plugin = Plugin()
```

---

## 📡 API Endpoints

Plugins are accessed via the REST API:

### List All Plugins

```http
GET /api/plugins/
```

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

### Get Plugin Details

```http
GET /api/plugins/{plugin_name}
```

### Run Plugin Command

```http
POST /api/plugins/{plugin_name}/run
Content-Type: application/json

{
  "command": "command1",
  "params": {
    "input": "value",
    "option": true
  }
}
```

**Response:**
```json
{
  "plugin": "my_plugin",
  "command": "command1",
  "result": {
    "status": "success",
    "result": "Processed: value"
  }
}
```

### Reload Plugin

```http
POST /api/plugins/{plugin_name}/reload
```

---

## 📦 Available Plugins

### youtube_dl

Download YouTube videos and audio.

| Command | Parameters | Description |
|---------|------------|-------------|
| `download` | `url`, `quality` | Download video |
| `audio` | `url` | Download audio only (MP3) |
| `info` | `url` | Get video information |

**Example:**
```json
{
  "command": "download",
  "params": {
    "url": "https://youtube.com/watch?v=...",
    "quality": "720"
  }
}
```

---

### system_stats

Monitor system resources.

| Command | Parameters | Description |
|---------|------------|-------------|
| `stats` | - | Quick CPU/RAM/Disk stats |
| `monitor` | - | Detailed system info |
| `processes` | `count`, `sort_by` | Top processes |

**Example:**
```json
{
  "command": "processes",
  "params": {
    "count": 10,
    "sort_by": "memory"
  }
}
```

---

### auto_summariser

Summarize content using LLM.

| Command | Parameters | Description |
|---------|------------|-------------|
| `summarize` | `text`, `style` | Summarize text |
| `summarize_screen` | `style` | Capture & summarize screen |
| `summarize_clipboard` | `style` | Summarize clipboard content |

**Styles:** `concise`, `detailed`, `bullet`

**Example:**
```json
{
  "command": "summarize",
  "params": {
    "text": "Long text to summarize...",
    "style": "bullet"
  }
}
```

---

### auto_debugger

Debug code and analyze errors using LLM.

| Command | Parameters | Description |
|---------|------------|-------------|
| `analyze` | `code`, `file_path`, `language` | Analyze code for bugs |
| `fix` | `code`, `error`, `language` | Suggest fixes for errors |
| `explain` | `error`, `language` | Explain error in simple terms |
| `trace` | `traceback`, `context` | Analyze stack traces |
| `suggest` | `code`, `focus`, `language` | Get improvement suggestions |

**Focus options:** `performance`, `readability`, `security`, `general`

**Example:**
```json
{
  "command": "analyze",
  "params": {
    "code": "def hello(): print('world'",
    "language": "Python"
  }
}
```

---

### browser_automation

Automate web browser tasks using Playwright.

| Command | Parameters | Description |
|---------|------------|-------------|
| `open` | `url`, `headless` | Open a URL |
| `screenshot` | `url`, `full_page` | Take screenshot |
| `get_text` | `url`, `selector` | Extract page text |
| `get_links` | `url`, `limit` | Get all links |
| `click` | `selector`, `wait` | Click element |
| `type` | `selector`, `text` | Type into field |
| `search` | `query`, `limit` | Search Google |
| `fill_form` | `fields`, `submit` | Fill form |

**Example:**
```json
{
  "command": "search",
  "params": {
    "query": "Python tutorials",
    "limit": 5
  }
}
```

---

### scheduled_tasks

Schedule and manage recurring tasks.

| Command | Parameters | Description |
|---------|------------|-------------|
| `list` | - | List all tasks |
| `add` | `name`, `schedule_type`, `action`, `params` | Add task |
| `remove` | `task_id` | Remove task |
| `enable` | `task_id` | Enable task |
| `disable` | `task_id` | Disable task |
| `run_now` | `task_id` | Run immediately |
| `status` | - | Scheduler status |

**Schedule types:** `once`, `interval`, `daily`, `weekly`

**Example:**
```json
{
  "command": "add",
  "params": {
    "name": "Hourly Stats",
    "schedule_type": "interval",
    "interval_seconds": 3600,
    "action": "plugin:system_stats/stats"
  }
}
```

---

## 🛠️ Creating a New Plugin

### Step 1: Create Plugin Directory

```bash
mkdir backend/plugins/my_awesome_plugin
cd backend/plugins/my_awesome_plugin
```

### Step 2: Create manifest.json

```json
{
  "name": "my_awesome_plugin",
  "description": "Does something awesome",
  "version": "1.0.0",
  "author": "Your Name",
  "commands": ["greet", "calculate"]
}
```

### Step 3: Create main.py

```python
from typing import Dict, Any

class Plugin:
    def __init__(self):
        self.name = "My Awesome Plugin"
    
    def run(self, command: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if command == "greet":
            name = params.get("name", "World")
            return {"message": f"Hello, {name}!"}
        
        if command == "calculate":
            a = params.get("a", 0)
            b = params.get("b", 0)
            op = params.get("op", "add")
            
            if op == "add":
                return {"result": a + b}
            elif op == "multiply":
                return {"result": a * b}
            
            return {"error": f"Unknown operation: {op}"}
        
        return {"error": f"Unknown command: {command}"}

plugin = Plugin()
```

### Step 4: Test Your Plugin

```bash
curl -X POST http://localhost:8000/api/plugins/my_awesome_plugin/run \
  -H "Content-Type: application/json" \
  -d '{"command": "greet", "params": {"name": "JARVIS"}}'
```

---

## ⚠️ Best Practices

1. **Error Handling**: Always return `{"error": "message"}` on failure
2. **Type Hints**: Use type hints for better code quality
3. **Documentation**: Include docstrings and a README.md
4. **Dependencies**: List all required packages in manifest
5. **Logging**: Use the logger from `modules.utils.logger`
6. **Security**: Never execute untrusted code or commands

---

## 🔧 Accessing JARVIS Modules

Plugins can access JARVIS modules:

```python
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from modules.llm.ollama_client import OllamaClient
from modules.ocr.screen_capture import capture_screen
from modules.ocr.ocr_engine import extract_text
from modules.utils.logger import logger

class Plugin:
    def __init__(self):
        self.llm = OllamaClient()
    
    def run(self, command: str, params: dict):
        if command == "ask_ai":
            prompt = params.get("prompt", "")
            response = self.llm.generate("llama3.1:8b", prompt)
            return {"response": response["response"]}
        
        if command == "read_screen":
            image_path = capture_screen()
            text = extract_text(image_path)
            return {"text": text}
        
        return {"error": "Unknown command"}

plugin = Plugin()
```

---

## 📄 License

Plugins are part of the JARVIS project and are licensed under MIT.
