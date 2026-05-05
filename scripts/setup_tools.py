import os
import sys
import shutil
import urllib.request
import zipfile
import tarfile
from pathlib import Path

# Configuration
BASE_DIR = Path(__file__).parent.parent
BIN_DIR = BASE_DIR / "bin"
INSTALLERS_DIR = BASE_DIR / "installers"
TEMP_DIR = BASE_DIR / "temp"

# URLs
FFMPEG_URL = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
PIPER_URL = "https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_windows_amd64.zip"
PIPER_VOICE_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx"
PIPER_VOICE_JSON_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json"
TESSERACT_URL = "https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.3.20231005.exe"

def download_file(url, dest_path):
    print(f"Downloading {url}...")
    try:
        urllib.request.urlretrieve(url, dest_path)
        print(f"Downloaded to {dest_path}")
        return True
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return False

def extract_zip(zip_path, extract_to):
    print(f"Extracting {zip_path}...")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        print("Extraction complete.")
        return True
    except Exception as e:
        print(f"Failed to extract {zip_path}: {e}")
        return False

def setup_ffmpeg():
    print("\n--- Setting up FFmpeg ---")
    ffmpeg_zip = TEMP_DIR / "ffmpeg.zip"
    if download_file(FFMPEG_URL, ffmpeg_zip):
        extract_dir = TEMP_DIR / "ffmpeg_extract"
        extract_zip(ffmpeg_zip, extract_dir)
        
        # Find bin folder
        for root, dirs, files in os.walk(extract_dir):
            if "ffmpeg.exe" in files:
                print(f"Found ffmpeg in {root}")
                shutil.copy2(os.path.join(root, "ffmpeg.exe"), BIN_DIR / "ffmpeg.exe")
                shutil.copy2(os.path.join(root, "ffprobe.exe"), BIN_DIR / "ffprobe.exe")
                print("FFmpeg installed to bin/")
                break
    else:
        print("Skipping FFmpeg setup due to download failure.")

def setup_piper():
    print("\n--- Setting up Piper TTS ---")
    piper_zip = TEMP_DIR / "piper.zip"
    if download_file(PIPER_URL, piper_zip):
        extract_dir = TEMP_DIR / "piper_extract"
        extract_zip(piper_zip, extract_dir)
        
        # Move piper folder
        piper_dest = BIN_DIR / "piper"
        if piper_dest.exists():
            shutil.rmtree(piper_dest)
        
        # Find piper folder in extract
        # usually piper_windows_amd64/piper
        found = False
        for root, dirs, files in os.walk(extract_dir):
            if "piper.exe" in files:
                shutil.copytree(root, piper_dest)
                print(f"Piper installed to {piper_dest}")
                found = True
                break
        
        if found:
            # Download voice
            print("Downloading default voice model...")
            download_file(PIPER_VOICE_URL, piper_dest / "en_US-lessac-medium.onnx")
            download_file(PIPER_VOICE_JSON_URL, piper_dest / "en_US-lessac-medium.onnx.json")

def setup_tesseract():
    print("\n--- Downloading Tesseract Installer ---")
    installer_path = INSTALLERS_DIR / "tesseract_setup.exe"
    if download_file(TESSERACT_URL, installer_path):
        print(f"Tesseract installer saved to {installer_path}")
        print("PLEASE RUN THIS INSTALLER MANUALLY TO INSTALL TESSERACT.")

def main():
    # Create dirs
    BIN_DIR.mkdir(exist_ok=True)
    INSTALLERS_DIR.mkdir(exist_ok=True)
    TEMP_DIR.mkdir(exist_ok=True)
    
    setup_ffmpeg()
    setup_piper()
    setup_tesseract()
    
    # Cleanup
    try:
        shutil.rmtree(TEMP_DIR)
    except:
        pass
    
    print("\nDone! Tools setup complete.")
    print("NOTE: You must install Tesseract manually from the installers/ folder.")

if __name__ == "__main__":
    main()
