@echo off
echo ========================================
echo    JARVIS - Full Installation
echo ========================================
echo.

cd /d "%~dp0.."

echo [1/3] Installing Python dependencies...
cd backend
pip install -r requirements.txt
cd ..

echo.
echo [2/3] Installing Node.js dependencies...
cd electron-app
call npm install
cd ..

echo.
echo [3/3] Verifying Ollama...
where ollama >nul 2>nul
if %ERRORLEVEL% == 0 (
    echo Ollama found!
    ollama list
) else (
    echo WARNING: Ollama not found in PATH
    echo Please install Ollama from: https://ollama.ai
)

echo.
echo ========================================
echo    Installation Complete!
echo ========================================
echo.
echo To start JARVIS:
echo   1. Open Terminal 1: scripts\run_backend.bat
echo   2. Open Terminal 2: scripts\start_electron.bat
echo.
echo Make sure Ollama is running with a model:
echo   ollama pull llama3.1:8b
echo   ollama serve
echo.
pause
