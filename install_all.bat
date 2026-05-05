@echo off
echo Installing JARVIS dependencies...

:: Backend
echo Installing Backend dependencies...
cd backend
pip install -r requirements.txt
cd ..

:: Frontend
echo Installing Frontend dependencies...
cd electron-app
npm install
cd ..

echo All dependencies installed!
pause
