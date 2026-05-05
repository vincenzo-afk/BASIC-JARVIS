# JARVIS v1.1.0 - Enhanced Edition

## 🚀 New Features

### 🎙️ Advanced Voice System
- **Intelligent Commands**: "Open Notepad", "Take a screenshot", "Shutdown computer".
- **Real-time Visualization**: See your voice levels as you speak.
- **Hands-Free Mode**: Click the "🎧 Off/On" button to enable continuous conversation loop.
- **Keyboard Shortcut**: Hold `Ctrl+Space` to talk.
- **Toggle Mic**: Press `Ctrl+M` to toggle microphone.
- **Auto-Speak**: JARVIS reads out responses automatically (configurable).

### 💬 Streaming Chat
- **Real-time Responses**: Watch the answer type out as it's generated.
- **Token Counter**: See how many tokens are generated in real-time.
- **Command Suggestions**: Type `/` in the input box to see available commands.

### 🧠 Conversation Memory
- **Context Awareness**: JARVIS remembers the last 10 turns of conversation.
- **History Panel**: View your chat history with timestamps and icons.

### ⌨️ Keyboard Shortcuts
Press `F1` or `Ctrl+/` to view the full list of shortcuts.

| Key | Action |
|-----|--------|
| `Alt+Space` | Toggle JARVIS Window |
| `Ctrl+Space` | Hold to Speak |
| `Ctrl+,` | Open Settings |
| `Ctrl+P` | Open Plugins |
| `Ctrl+Shift+S` | Capture Screen |

### 🧩 Plugin System
- **Manage Plugins**: Enable/disable/reload plugins from the UI.
- **Browser Automation**: New plugin for web tasks.
- **Scheduled Tasks**: New plugin for reminders and automation.

## 🛠️ Troubleshooting

- **Backend Offline?**: Run `python main.py` in the `backend` folder.
- **Voice Not Working?**: Ensure you have a microphone connected and allowed permissions.
- **Screen Read Failed?**: Install Tesseract OCR (see main README).

## 📦 Installation

If you haven't already:
1. Install Python dependencies: `pip install -r backend/requirements.txt`
2. Install Node dependencies: `cd electron-app && npm install`
3. Start Backend: `python backend/main.py`
4. Start Frontend: `npm start` (in `electron-app`)
