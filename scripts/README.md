# JARVIS Scripts

Utility scripts for running and managing JARVIS.

---

## 📁 Files

| Script | Platform | Description |
|--------|----------|-------------|
| `install_all.bat` | Windows | Install all dependencies |
| `install_all.sh` | Linux/Mac | Install all dependencies |
| `run_backend.bat` | Windows | Start Python backend |
| `run_backend.sh` | Linux/Mac | Start Python backend |
| `start_electron.bat` | Windows | Start Electron UI |
| `start_electron.sh` | Linux/Mac | Start Electron UI |

---

## 🚀 Usage

### Windows

```powershell
# First time: Install everything
.\scripts\install_all.bat

# Start backend (Terminal 1)
.\scripts\run_backend.bat

# Start UI (Terminal 2)
.\scripts\start_electron.bat
```

### Linux/macOS

```bash
# Make scripts executable
chmod +x scripts/*.sh

# First time: Install everything
./scripts/install_all.sh

# Start backend (Terminal 1)
./scripts/run_backend.sh

# Start UI (Terminal 2)
./scripts/start_electron.sh
```

---

## 📋 Script Details

### install_all.bat/.sh

1. Installs Python dependencies (`pip install -r requirements.txt`)
2. Installs Node.js dependencies (`npm install`)
3. Verifies Ollama installation
4. Displays next steps

### run_backend.bat/.sh

1. Changes to backend directory
2. Installs/updates Python dependencies
3. Starts FastAPI server on port 8000

### start_electron.bat/.sh

1. Changes to electron-app directory
2. Installs/updates Node.js dependencies
3. Starts Electron + React dev server

---

## ⚙️ Environment

Scripts expect:
- Python 3.8+ in PATH
- Node.js 16+ in PATH
- pip and npm available
- Ollama installed (optional but recommended)

---

## 🔧 Troubleshooting

### "pip not found"

Add Python to PATH or use full path:
```
C:\Python311\python.exe -m pip install -r requirements.txt
```

### "npm not found"

Add Node.js to PATH or reinstall Node.js with "Add to PATH" option.

### Port already in use

Backend uses port 8000, React uses port 3000.

Kill existing processes:
```powershell
# Windows
netstat -ano | findstr :8000
taskkill /PID <pid> /F

# Linux/Mac
lsof -i :8000
kill -9 <pid>
```

---

## 📄 License

MIT License - Part of the JARVIS project.
