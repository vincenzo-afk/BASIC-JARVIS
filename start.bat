@echo off
title JARVIS Launcher - Optimized
color 0A

echo =========================================
echo   JARVIS - AI Desktop Assistant
echo   Optimized Performance Mode
echo =========================================
echo.

:: Check if Ollama is running
echo [1/4] Checking Ollama...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Ollama not running. Starting Ollama...
    start "" "ollama" serve
    timeout /t 3 /nobreak >nul
) else (
    echo [OK] Ollama is running
)

:: Start Backend with optimizations
echo [2/4] Starting Backend ^(Optimized^)...
cd backend
start "JARVIS-Backend" /HIGH cmd /c "set OMP_NUM_THREADS=%NUMBER_OF_PROCESSORS% && set MKL_NUM_THREADS=%NUMBER_OF_PROCESSORS% && set NUMEXPR_NUM_THREADS=%NUMBER_OF_PROCESSORS% && python main.py"
cd ..

:: Wait for backend to be ready
echo [3/4] Waiting for Backend...
:wait_backend
timeout /t 1 /nobreak >nul
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% neq 0 goto wait_backend
echo [OK] Backend is online

:: Start Electron App (Production)
echo [4/4] Starting JARVIS UI...
cd electron-app
start "JARVIS-UI" /HIGH cmd /c "npm run electron"
cd ..

:: Set process priorities for performance
echo.
echo [*] Optimizing process priorities...
timeout /t 5 /nobreak >nul

:: Set high priority for critical processes
powershell -Command "Get-Process -Name 'python*' -ErrorAction SilentlyContinue | ForEach-Object { $_.PriorityClass = 'AboveNormal' }" 2>nul
powershell -Command "Get-Process -Name 'electron*' -ErrorAction SilentlyContinue | ForEach-Object { $_.PriorityClass = 'AboveNormal' }" 2>nul

echo.
echo =========================================
echo   JARVIS is now running!
echo =========================================
echo.
echo   Backend API: http://localhost:8000
echo   API Docs:    http://localhost:8000/docs
echo   Hotkey:      Alt+Space (toggle window)
echo.
echo   Press any key to stop JARVIS...
pause >nul

:: Cleanup
echo.
echo Shutting down JARVIS...
taskkill /FI "WINDOWTITLE eq JARVIS-Backend*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq JARVIS-UI*" /F >nul 2>&1
echo Goodbye!
