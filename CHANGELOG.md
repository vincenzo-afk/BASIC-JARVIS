# Changelog

All notable changes to the BASIC-JARVIS project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2024-12-07

### Added

#### Frontend (Electron + React)
- Initial Electron application with frameless, transparent window
- React-based UI with modern JARVIS aesthetic
- Global hotkey `Alt+Space` to toggle visibility
- System tray integration with context menu
- **CommandBar** component for chat input/output
- **Waveform** component for audio visualization
- **HistoryPanel** component for activity tracking
- **Settings** modal for configuration
- **PluginPanel** modal for plugin management
- Custom CSS with glassmorphism effects and animations
- Draggable title bar with window controls

#### Backend (Python FastAPI)
- FastAPI server with CORS support
- **Chat API** - Ollama LLM integration
  - Single prompt generation
  - Multi-turn conversation
  - Model listing and management
- **Screen API** - OCR functionality
  - Multi-monitor screenshot capture
  - Tesseract OCR text extraction
  - Image preprocessing for accuracy
- **Control API** - System automation
  - Mouse control (click, move, scroll, drag)
  - Keyboard control (type, press, hotkey)
  - Application management (open, close, list)
  - System control (shutdown, restart, sleep)
- **Voice API** - Speech processing (placeholder)
  - Whisper STT integration structure
  - Piper TTS integration structure
- **Agent API** - Workflow automation
  - BaseAgent class for custom agents
  - WorkflowEngine for multi-step tasks
  - Built-in actions (log, wait, http, llm)
- **Plugin API** - Extension system
  - Dynamic plugin loading
  - Plugin execution and reload

#### Plugins
- **youtube_dl** - Download YouTube videos/audio
- **system_stats** - System resource monitoring
- **auto_summariser** - Content summarization with LLM

#### Scripts
- `install_all.bat/.sh` - Full installation
- `run_backend.bat/.sh` - Backend server
- `start_electron.bat/.sh` - Frontend UI

#### Documentation
- Comprehensive README.md
- Backend API documentation
- Plugin development guide
- Configuration reference

### Technical Details
- Python 3.8+ required
- Node.js 16+ required
- Ollama for local LLM execution
- Tesseract for OCR
- PyAutoGUI for system control
- mss for screen capture

---

## [1.1.0] - 2024-12-07

### Added

#### Voice System (FULLY FUNCTIONAL)
- **Whisper STT Integration** - Complete speech-to-text
  - Support for `openai-whisper` and `faster-whisper` backends
  - Audio file transcription with language detection
  - Configurable models (tiny, base, small, medium, large)
- **Piper TTS Integration** - High-quality text-to-speech
  - Primary Piper TTS with ONNX models
  - Fallback support: Windows SAPI, macOS `say`, espeak
  - Async and sync speech generation
- **Voice Chat Endpoint** - Complete voice conversation loop
  - Audio → Transcription → LLM → Speech response
  - Base64 audio return for web clients
- **VoiceInput Component** - Frontend microphone recording
  - Real-time audio level visualization
  - Permission handling and error feedback
  - Ctrl+Space keyboard shortcut

#### Streaming & Real-time
- **Streaming Chat Endpoint** (`/api/chat/stream`)
  - Server-Sent Events (SSE) for token streaming
  - Real-time response generation
- **WebSocket Chat** (`/api/chat/ws`)
  - Bidirectional real-time communication
  - Chunked response streaming

#### New Plugins
- **Browser Automation Plugin** - Playwright-based web automation
  - Open pages, take screenshots
  - Extract text and links
  - Click, type, scroll, fill forms
  - Google search automation
- **Scheduled Tasks Plugin** - Task scheduling system
  - One-time, interval, daily, weekly schedules
  - Persistent storage
  - Integration with other plugins
  - Background execution

### Enhanced
- Chat routes now support streaming responses
- Voice routes with combined voice-chat endpoint
- Improved error handling across all modules
- Better WebSocket connection management

---

## [Unreleased]

### Changed
- Replaced the stale root README with repository-specific installation, configuration, usage, API, testing, deployment, security, and contribution guidance.
- Fixed Electron development startup so `npm run dev` loads the React development server instead of the production bundle.
- Added a non-secret backend environment template, CI checks, issue templates, pull-request guidance, and security documentation.

### Planned
- [x] ~~Full Whisper STT integration~~ ✅
- [x] ~~Full Piper TTS integration~~ ✅
- [x] ~~Browser automation plugin~~ ✅
- [x] ~~Scheduled tasks~~ ✅
- [ ] Auto-debugger plugin
- [ ] Multi-language support
- [ ] Theme customization
- [ ] Keyboard shortcuts panel
- [ ] Voice activation ("Hey JARVIS")
- [ ] Conversation memory/context

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 1.1.0 | 2024-12-07 | Full voice integration, streaming, browser automation, scheduled tasks |
| 1.0.0 | 2024-12-07 | Initial release |

---

## Contributing

See [README.md](README.md#contributing) and [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.
