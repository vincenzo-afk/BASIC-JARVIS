@echo off
echo ========================================
echo    JARVIS Backend Server
echo ========================================
echo.

cd /d "%~dp0..\backend"

echo [1/2] Installing Python dependencies...
pip install -r requirements.txt --quiet

echo.
echo [2/2] Starting FastAPI server...
echo.
echo Server will be available at: http://localhost:8000
echo API Documentation at: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

python main.py
