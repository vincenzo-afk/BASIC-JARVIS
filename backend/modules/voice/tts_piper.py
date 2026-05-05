"""
Text-to-Speech Module using Piper - FULLY FUNCTIONAL
Converts text to speech using Piper TTS or system fallbacks
"""
import os
import subprocess
import platform
import tempfile
import wave
import threading
from typing import Optional, Dict, Any
from pathlib import Path
from config.settings import PIPER_PATH, PIPER_MODEL, TEMP_DIR
from modules.utils.logger import logger

# Try to import audio playback
_pygame_available = False
try:
    import pygame
    pygame.mixer.init()
    _pygame_available = True
except ImportError:
    pass

# Alternative: playsound
_playsound_available = False
try:
    from playsound import playsound as _playsound
    _playsound_available = True
except ImportError:
    pass


class PiperTTS:
    """
    Text-to-Speech using Piper or system fallbacks
    
    Supports:
    - Piper TTS (high quality, offline)
    - Windows SAPI (fallback)
    - espeak (Linux/Mac fallback)
    - macOS say command
    """
    
    def __init__(self, piper_path: str = None, model_path: str = None):
        """
        Initialize TTS
        
        Args:
            piper_path: Path to piper executable
            model_path: Path to .onnx voice model
        """
        self.piper_path = piper_path or PIPER_PATH
        self.model_path = model_path or PIPER_MODEL
        self.output_dir = str(TEMP_DIR / "audio")
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.available = False
        self.backend = "none"
        self._init_backend()
    
    def _init_backend(self):
        """Initialize the best available TTS backend"""
        # Try Piper first
        if self._check_piper():
            self.available = True
            self.backend = "piper"
            logger.info(f"[TTS] Using Piper: {self.piper_path}")
            return
        
        # Windows SAPI
        if platform.system() == "Windows":
            try:
                import win32com.client
                self._sapi = win32com.client.Dispatch("SAPI.SpVoice")
                self.available = True
                self.backend = "sapi"
                logger.info("[TTS] Using Windows SAPI")
                return
            except:
                pass
        
        # macOS say command
        if platform.system() == "Darwin":
            if self._check_command("say"):
                self.available = True
                self.backend = "say"
                logger.info("[TTS] Using macOS say")
                return
        
        # espeak (Linux)
        if self._check_command("espeak"):
            self.available = True
            self.backend = "espeak"
            logger.info("[TTS] Using espeak")
            return
        
        # espeak-ng
        if self._check_command("espeak-ng"):
            self.available = True
            self.backend = "espeak-ng"
            logger.info("[TTS] Using espeak-ng")
            return
        
        logger.warning("[TTS] No TTS backend available")
    
    def _check_piper(self) -> bool:
        """Check if Piper is available"""
        try:
            # Check if piper exists
            if os.path.exists(self.piper_path):
                return True
            
            # Check if in PATH
            result = subprocess.run(
                [self.piper_path, "--help"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    def _check_command(self, cmd: str) -> bool:
        """Check if a command is available"""
        try:
            subprocess.run(
                [cmd, "--version"] if cmd != "say" else [cmd, "-v", "?"],
                capture_output=True,
                timeout=5
            )
            return True
        except:
            return False
    
    def speak(
        self,
        text: str,
        output_file: str = None,
        voice: str = None,
        rate: float = 1.0,
        blocking: bool = True
    ) -> Dict[str, Any]:
        """
        Convert text to speech
        
        Args:
            text: Text to convert
            output_file: Optional output WAV file path
            voice: Voice name (backend-specific)
            rate: Speech rate multiplier (0.5-2.0)
            blocking: Wait for completion
            
        Returns:
            Dict with status, output file path
        """
        if not self.available:
            return {"error": "TTS not available", "status": "error"}
        
        if not text or not text.strip():
            return {"error": "Empty text", "status": "error"}
        
        text = text.strip()
        
        # Generate output filename
        if not output_file:
            import time
            timestamp = int(time.time() * 1000)
            output_file = os.path.join(self.output_dir, f"speech_{timestamp}.wav")
        
        try:
            if self.backend == "piper":
                return self._speak_piper(text, output_file, rate)
            elif self.backend == "sapi":
                return self._speak_sapi(text, output_file, rate, blocking)
            elif self.backend == "say":
                return self._speak_say(text, output_file, rate)
            elif self.backend in ("espeak", "espeak-ng"):
                return self._speak_espeak(text, output_file, rate)
            else:
                return {"error": "No TTS backend", "status": "error"}
        except Exception as e:
            logger.error(f"[TTS] Error: {e}")
            return {"error": str(e), "status": "error"}
    
    def _speak_piper(self, text: str, output_file: str, rate: float) -> Dict[str, Any]:
        """Speak using Piper"""
        cmd = [
            self.piper_path,
            "--model", self.model_path,
            "--output_file", output_file
        ]
        
        if rate != 1.0:
            cmd.extend(["--length_scale", str(1.0 / rate)])
        
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        stdout, stderr = process.communicate(input=text.encode())
        
        if process.returncode != 0:
            return {"error": stderr.decode(), "status": "error"}
        
        return {
            "status": "success",
            "output": output_file,
            "backend": "piper"
        }
    
    def _speak_sapi(self, text: str, output_file: str, rate: float, blocking: bool) -> Dict[str, Any]:
        """Speak using Windows SAPI"""
        import win32com.client
        
        # Adjust rate (-10 to 10)
        sapi_rate = int((rate - 1.0) * 5)
        self._sapi.Rate = max(-10, min(10, sapi_rate))
        
        if blocking:
            # Save to file
            stream = win32com.client.Dispatch("SAPI.SpFileStream")
            stream.Open(output_file, 3)  # SSFMCreateForWrite
            self._sapi.AudioOutputStream = stream
            self._sapi.Speak(text)
            stream.Close()
            
            # Reset to default output
            self._sapi.AudioOutputStream = None
        else:
            # Speak directly (non-blocking not really supported, use thread)
            def _speak():
                self._sapi.Speak(text)
            thread = threading.Thread(target=_speak)
            thread.start()
        
        return {
            "status": "success",
            "output": output_file if blocking else None,
            "backend": "sapi"
        }
    
    def _speak_say(self, text: str, output_file: str, rate: float) -> Dict[str, Any]:
        """Speak using macOS say command"""
        # Rate: words per minute (default ~175)
        wpm = int(175 * rate)
        
        cmd = ["say", "-r", str(wpm), "-o", output_file, "--data-format=LEI16@16000", text]
        
        result = subprocess.run(cmd, capture_output=True)
        
        if result.returncode != 0:
            return {"error": result.stderr.decode(), "status": "error"}
        
        return {
            "status": "success",
            "output": output_file,
            "backend": "say"
        }
    
    def _speak_espeak(self, text: str, output_file: str, rate: float) -> Dict[str, Any]:
        """Speak using espeak/espeak-ng"""
        # Rate: words per minute (default 175)
        wpm = int(175 * rate)
        
        cmd_name = "espeak-ng" if self.backend == "espeak-ng" else "espeak"
        cmd = [cmd_name, "-w", output_file, "-s", str(wpm), text]
        
        result = subprocess.run(cmd, capture_output=True)
        
        if result.returncode != 0:
            return {"error": result.stderr.decode(), "status": "error"}
        
        return {
            "status": "success",
            "output": output_file,
            "backend": self.backend
        }
    
    def speak_async(self, text: str, callback=None) -> None:
        """
        Speak text asynchronously
        
        Args:
            text: Text to speak
            callback: Optional callback(result) when done
        """
        def _run():
            result = self.speak(text, blocking=True)
            if result.get("status") == "success" and "output" in result:
                self.play_audio(result["output"])
            if callback:
                callback(result)
        
        thread = threading.Thread(target=_run)
        thread.daemon = True
        thread.start()
    
    def play_audio(self, audio_path: str):
        """Play an audio file"""
        if not os.path.exists(audio_path):
            return
        
        if _pygame_available:
            try:
                pygame.mixer.music.load(audio_path)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pygame.time.wait(100)
                return
            except:
                pass
        
        if _playsound_available:
            try:
                _playsound(audio_path)
                return
            except:
                pass
        
        # System command fallback
        system = platform.system()
        try:
            if system == "Windows":
                os.system(f'start "" "{audio_path}"')
            elif system == "Darwin":
                os.system(f'afplay "{audio_path}"')
            else:
                os.system(f'aplay "{audio_path}"')
        except:
            pass
    
    def is_available(self) -> bool:
        """Check if TTS is available"""
        return self.available
    
    def get_info(self) -> Dict[str, Any]:
        """Get TTS module info"""
        return {
            "available": self.available,
            "backend": self.backend,
            "piper_path": self.piper_path,
            "model_path": self.model_path
        }
    
    def list_voices(self) -> list:
        """List available voices (backend-specific)"""
        if self.backend == "sapi":
            try:
                voices = []
                for voice in self._sapi.GetVoices():
                    voices.append(voice.GetDescription())
                return voices
            except:
                return []
        elif self.backend == "say":
            try:
                result = subprocess.run(["say", "-v", "?"], capture_output=True, text=True)
                voices = []
                for line in result.stdout.split("\n"):
                    if line.strip():
                        voices.append(line.split()[0])
                return voices
            except:
                return []
        return []


# Singleton instance
_tts_instance: Optional[PiperTTS] = None

def get_tts() -> PiperTTS:
    """Get or create TTS singleton"""
    global _tts_instance
    if _tts_instance is None:
        _tts_instance = PiperTTS()
    return _tts_instance


def speak(text: str, blocking: bool = True) -> str:
    """Quick speak function, returns audio file path"""
    tts = get_tts()
    result = tts.speak(text, blocking=blocking)
    return result.get("output", "")
