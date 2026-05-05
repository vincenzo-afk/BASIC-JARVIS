@echo off
title JARVIS Complete Launcher
color 0B
setlocal EnableDelayedExpansion

echo =========================================
echo   JARVIS Complete Launcher
echo =========================================
echo.

:: Step 1: Check if Ollama is running
echo [1/4] Checking Ollama...
tasklist /FI "IMAGENAME eq ollama.exe" 2>NUL | find /I "ollama.exe" >NUL
if %ERRORLEVEL% neq 0 (
    echo      Starting Ollama...
    start "" /B "ollama" serve >NUL 2>&1
    timeout /t 3 /nobreak >NUL
) else (
    echo      Ollama is running
)

:: Step 2: Start Backend (if not running)
echo [2/4] Starting Backend...
cd /d "%~dp0backend"

:: Check if port 8000 is already in use
netstat -an | find "8000" | find "LISTENING" >NUL 2>&1
if %ERRORLEVEL% equ 0 (
    echo      Backend already running on port 8000
) else (
    echo      Launching Python backend...
    start /MIN "" python main.py
    timeout /t 3 /nobreak >NUL
)

:: Step 3: Wait for backend health
echo [3/4] Waiting for backend...
set /a attempts=0
:healthcheck
set /a attempts+=1
curl -s http://localhost:8000/health >NUL 2>&1
if %ERRORLEVEL% equ 0 (
    echo      Backend is healthy!
) else (
    if !attempts! lss 10 (
        timeout /t 1 /nobreak >NUL
        goto healthcheck
    ) else (
        echo      Warning: Backend health check timed out
    )
)

:: Step 4: Start Electron UI
echo [4/4] Launching JARVIS UI...
cd /d "%~dp0electron-app"
start "" npm run electron

echo.
echo =========================================
echo   JARVIS is starting!
echo =========================================
echo.
echo   Backend: http://localhost:8000
echo   Docs:    http://localhost:8000/docs
echo.
echo   Press any key to close this launcher...
pause >NUL
