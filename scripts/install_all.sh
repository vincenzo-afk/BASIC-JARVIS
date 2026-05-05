#!/bin/bash
echo "Installing JARVIS Dependencies..."

# Backend
echo "📦 Installing Python dependencies..."
cd "$(dirname "$0")/../backend"
pip install -r requirements.txt

# Frontend
echo "📦 Installing Node dependencies..."
cd "$(dirname "$0")/../electron-app"
npm install

echo "✅ Installation complete!"
echo ""
echo "To start JARVIS:"
echo "  1. Terminal 1: ./scripts/run_backend.sh"
echo "  2. Terminal 2: ./scripts/start_electron.sh"
