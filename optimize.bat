@echo off
title JARVIS Performance Optimizer
color 0B

echo =========================================
echo   JARVIS Performance Optimizer
echo =========================================
echo.

:: Check for admin rights
net session >nul 2>&1
if %errorlevel% == 0 (
    echo [*] Running with Administrator privileges
) else (
    echo [!] For best results, run as Administrator
)
echo.

:: Set Python process affinity and priority
echo [1/5] Optimizing Python processes...
for /f "tokens=2" %%i in ('tasklist /fi "imagename eq python.exe" /nh ^| find "python.exe"') do (
    powershell -Command "Get-Process -Id %%i -ErrorAction SilentlyContinue | ForEach-Object { $_.PriorityClass = 'AboveNormal' }" 2>nul
)

:: Set Electron process priority
echo [2/5] Optimizing Electron processes...
for /f "tokens=2" %%i in ('tasklist /fi "imagename eq electron.exe" /nh ^| find "electron.exe"') do (
    powershell -Command "Get-Process -Id %%i -ErrorAction SilentlyContinue | ForEach-Object { $_.PriorityClass = 'AboveNormal' }" 2>nul
)

:: Set Ollama process priority
echo [3/5] Optimizing Ollama processes...
for /f "tokens=2" %%i in ('tasklist /fi "imagename eq ollama.exe" /nh ^| find "ollama.exe"') do (
    powershell -Command "Get-Process -Id %%i -ErrorAction SilentlyContinue | ForEach-Object { $_.PriorityClass = 'High' }" 2>nul
)

:: Clear Python cache
echo [4/5] Clearing Python cache...
del /s /q "backend\__pycache__\*" 2>nul
del /s /q "backend\modules\__pycache__\*" 2>nul
del /s /q "backend\routes\__pycache__\*" 2>nul

:: Garbage collect
echo [5/5] Requesting garbage collection...
powershell -Command "[System.GC]::Collect()" 2>nul

echo.
echo =========================================
echo   Optimization Complete!
echo =========================================
echo.
echo Current JARVIS processes:
echo.
tasklist /fi "imagename eq python.exe" 2>nul | find "python.exe"
tasklist /fi "imagename eq electron.exe" 2>nul | find "electron.exe"
tasklist /fi "imagename eq ollama.exe" 2>nul | find "ollama.exe"
echo.
pause
