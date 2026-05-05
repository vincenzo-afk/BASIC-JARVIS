# JARVIS Electron App

The desktop UI for JARVIS built with Electron and React. Provides a modern, transparent, overlay-style interface for interacting with the AI assistant.

---

## 📁 Structure

```
electron-app/
├── package.json           # Node dependencies & scripts
├── electron.js            # Main Electron process
├── preload.js             # Secure IPC bridge
├── tailwind.config.js     # Tailwind CSS configuration
├── postcss.config.js      # PostCSS configuration
│
├── public/
│   ├── index.html         # HTML template
│   └── icon.png           # App icon
│
└── src/
    ├── index.jsx          # React entry point
    ├── App.jsx            # Main application component
    │
    ├── components/
    │   ├── CommandBar.jsx     # Chat input & response
    │   ├── Waveform.jsx       # Audio visualization
    │   ├── HistoryPanel.jsx   # Activity history
    │   ├── Settings.jsx       # Configuration modal
    │   └── PluginPanel.jsx    # Plugin management
    │
    └── styles/
        └── globals.css        # All CSS styles
```

---

## 🚀 Quick Start

### Install Dependencies

```bash
cd electron-app
npm install
```

### Run in Development

```bash
npm run dev
```

This runs React dev server and Electron concurrently.

### Build for Production

```bash
npm run build
npm run electron
```

---

## 🎨 Features

### Frameless Window

The app uses a frameless, transparent window for a modern overlay look:

```javascript
mainWindow = new BrowserWindow({
  frame: false,
  transparent: true,
  resizable: true,
  alwaysOnTop: false
});
```

### Global Hotkey

Toggle visibility with `Alt+Space`:

```javascript
globalShortcut.register('Alt+Space', () => {
  mainWindow.isVisible() ? mainWindow.hide() : mainWindow.show();
});
```

### System Tray

Right-click tray icon for quick actions:
- Show JARVIS
- Settings
- Quit

---

## 🧩 Components

### App.jsx

Main application component that:
- Manages global state (settings, history, status)
- Communicates with backend API
- Coordinates all child components
- Handles Electron IPC events

### CommandBar.jsx

Chat input and response display:
- Text input with submit button
- Loading state indicator
- LLM response display
- Model indicator
- Keyboard shortcuts (Enter to send, Escape to clear)

### Waveform.jsx

Audio visualization component:
- Canvas-based animation
- Active/idle states
- Configurable colors and bar count

### HistoryPanel.jsx

Activity history display:
- Chat messages
- Screen captures
- Voice inputs
- Plugin actions
- Timestamps and icons

### Settings.jsx

Configuration modal:
- Model selection (fetches from Ollama)
- Ollama host configuration
- Feature toggles (OCR, Voice)
- Hotkey display
- Connection testing

### PluginPanel.jsx

Plugin management:
- List installed plugins
- View plugin details/commands
- Run plugin commands
- Reload plugins

---

## 🎨 Styling

All styles are in `src/styles/globals.css` using:
- CSS custom properties (variables)
- Tailwind CSS utilities
- Custom animations
- Glassmorphism effects

### Color Palette

```css
:root {
  --color-cyan: #22d3ee;
  --color-cyan-light: #67e8f9;
  --color-cyan-dark: #0891b2;
  --color-blue: #3b82f6;
  --color-bg-primary: #0a0a0a;
  --color-bg-secondary: #111111;
  --color-bg-tertiary: #1a1a1a;
}
```

---

## 🔌 IPC Communication

### Window Controls

```javascript
// Renderer (React)
window.electronAPI.minimizeWindow();
window.electronAPI.maximizeWindow();
window.electronAPI.closeWindow();
window.electronAPI.hideWindow();

// Main (Electron)
ipcMain.on('window-minimize', () => mainWindow.minimize());
ipcMain.on('window-maximize', () => mainWindow.maximize());
ipcMain.on('window-close', () => mainWindow.hide());
```

### Event Listeners

```javascript
// Listen for events from main process
window.electronAPI.onOpenSettings((callback) => {
  // Handle settings open request
});

window.electronAPI.onFocusInput((callback) => {
  // Focus command input
});
```

---

## 📦 Dependencies

### Production

| Package | Purpose |
|---------|---------|
| `react` | UI framework |
| `react-dom` | React DOM |
| `axios` | HTTP client |

### Development

| Package | Purpose |
|---------|---------|
| `electron` | Desktop framework |
| `react-scripts` | React tooling |
| `tailwindcss` | CSS framework |
| `concurrently` | Run multiple scripts |
| `wait-on` | Wait for port |

---

## 🛠️ Scripts

| Script | Description |
|--------|-------------|
| `npm start` | Start React dev server |
| `npm run build` | Build for production |
| `npm run electron` | Start Electron only |
| `npm run dev` | Start React + Electron |

---

## ⚙️ Configuration

### Tailwind Config

```javascript
// tailwind.config.js
module.exports = {
  content: ["./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        jarvis: {
          cyan: '#22d3ee',
          blue: '#3b82f6',
          dark: '#0a0a0a'
        }
      }
    }
  }
}
```

---

## 🔧 Development Tips

### Hot Reload

React hot reloads automatically. For Electron changes, restart the app.

### DevTools

Open DevTools with `Ctrl+Shift+I` or set `CONFIG.devTools = true` in electron.js.

### Debugging

```javascript
// In renderer
console.log('[JARVIS]', 'Debug message');

// In main process
console.log('[Electron]', 'Debug message');
```

---

## 📄 License

MIT License - Part of the JARVIS project.
