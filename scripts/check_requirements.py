import shutil
import sys
import os
import requests

def check_command(cmd):
    # Check local bin first
    bin_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "bin")
    local_cmd = os.path.join(bin_path, cmd + ".exe")
    if os.path.exists(local_cmd):
        return local_cmd
        
    return shutil.which(cmd) is not None

def check_ollama():
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        return response.status_code == 200
    except:
        return False

def main():
    print("Checking JARVIS Requirements...")
    print("-" * 30)
    
    # Python
    print(f"Python: {'OK' if sys.version_info >= (3, 8) else 'Update Required'} ({sys.version.split()[0]})")
    
    # Node
    node = check_command("node")
    print(f"Node.js: {'OK' if node else 'Missing'}")
    
    # Ollama
    ollama_cmd = check_command("ollama")
    ollama_running = check_ollama()
    print(f"Ollama (CLI): {'OK' if ollama_cmd else 'Missing'}")
    print(f"Ollama (Server): {'Running' if ollama_running else 'Not Running (Run: ollama serve)'}")
    
    # Tesseract
    tesseract = check_command("tesseract")
    if not tesseract:
        # Check common locations
        paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "bin", "tesseract.exe"),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "bin", "tesseract", "tesseract.exe")
        ]
        for p in paths:
            if os.path.exists(p):
                tesseract = p
                break
                
    print(f"Tesseract OCR: {'OK' if tesseract else 'Missing (Required for Screen Reader)'}")
    
    # FFmpeg
    ffmpeg = check_command("ffmpeg")
    print(f"FFmpeg: {'OK' if ffmpeg else 'Missing (Required for Voice)'}")
    
    # Piper
    piper = check_command("piper")
    if not piper:
        # Check bin/piper/piper.exe
        bin_piper = os.path.join(os.path.dirname(os.path.dirname(__file__)), "bin", "piper", "piper.exe")
        if os.path.exists(bin_piper):
            piper = bin_piper
            
    print(f"Piper TTS: {'OK' if piper else 'Missing (Using System Fallback)'}")
    
    print("-" * 30)
    if not tesseract or not ffmpeg:
        print("WARNING: Some features will not work without Tesseract and FFmpeg.")
        print("Please install them and add them to your PATH.")

if __name__ == "__main__":
    main()
