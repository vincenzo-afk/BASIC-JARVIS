@echo off
echo ========================================
echo    JARVIS Desktop UI
echo ========================================
echo.

cd /d "%~dp0..\electron-app"

echo [1/2] Installing Node.js dependencies...
call npm install --silent

echo.
echo [2/2] Starting Electron + React app...
echo.
echo JARVIS UI will open shortly...
echo Press Alt+Space to toggle window visibility
echo ========================================
echo.

call npm run dev
