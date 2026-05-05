"""
Speech-to-Text Module using Whisper - FULLY FUNCTIONAL
Transcribes audio to text using OpenAI Whisper model
"""
import os
import tempfile
import wave
import numpy as np
from typing import Optional, Dict, Any, Union
from pathlib import Path
from config.settings import WHISPER_MODEL, TEMP_DIR
from modules.utils.logger import logger

# Try to import whisper
_whisper = None
_whisper_model = None
_whisper_available = False

try:
    import whisper
    _whisper = whisper
    _whisper_available = True
    logger.info("[STT] Whisper library available")
except ImportError:
    logger.warning("[STT] Whisper not installed. Run: pip install openai-whisper")

# Alternative: Use faster-whisper if available
_faster_whisper = None
try:
    from faster_whisper import WhisperModel
    _faster_whisper = WhisperModel
    logger.info("[STT] Faster-whisper available")
except ImportError:
    pass


class WhisperSTT:
    """
    Speech-to-Text using Whisper
    
    Supports:
    - openai-whisper (Python)
    - faster-whisper (faster alternative)
    - Audio file transcription
    - Real-time audio transcription
    """
    
    def __init__(self, model_name: str = None, device: str = "auto"):
        """
        Initialize Whisper STT
        
        Args:
            model_name: Model size (tiny, base, small, medium, large)
            device: Device to use (auto, cpu, cuda)
        """
        self.model_name = model_name or WHISPER_MODEL
        self.device = device
        self.model = None
        self.available = False
        self.use_faster = False
        
        self._init_model()
    
    def _init_model(self):
        """Initialize the Whisper model"""
        # Try faster-whisper first (much faster)
        if _faster_whisper:
            try:
                device = "cuda" if self.device == "auto" else self.device
                self.model = _faster_whisper(
                    self.model_name,
                    device=device,
                    compute_type="float16" if device == "cuda" else "int8"
                )
                self.available = True
                self.use_faster = True
                logger.info(f"[STT] Loaded faster-whisper model: {self.model_name}")
                return
            except Exception as e:
                logger.warning(f"[STT] Faster-whisper failed: {e}")
        
        # Fall back to openai-whisper
        if _whisper:
            try:
                self.model = _whisper.load_model(self.model_name)
                self.available = True
                self.use_faster = False
                logger.info(f"[STT] Loaded whisper model: {self.model_name}")
            except Exception as e:
                logger.error(f"[STT] Failed to load whisper model: {e}")
                self.available = False
        else:
            logger.warning("[STT] No whisper implementation available")
    
    def transcribe_file(
        self,
        audio_path: str,
        language: str = None,
        task: str = "transcribe"
    ) -> Dict[str, Any]:
        """
        Transcribe an audio file
        
        Args:
            audio_path: Path to audio file (WAV, MP3, etc.)
            language: Language code (e.g., 'en', 'es') or None for auto-detect
            task: 'transcribe' or 'translate' (to English)
            
        Returns:
            Dict with text, segments, language, duration
        """
        if not self.available:
            return {"error": "Whisper not available", "text": ""}
        
        if not os.path.exists(audio_path):
            return {"error": f"Audio file not found: {audio_path}", "text": ""}
        
        logger.info(f"[STT] Transcribing: {audio_path}")
        
        try:
            if self.use_faster:
                return self._transcribe_faster(audio_path, language, task)
            else:
                return self._transcribe_whisper(audio_path, language, task)
        except Exception as e:
            logger.error(f"[STT] Transcription error: {e}")
            return {"error": str(e), "text": ""}
    
    def _transcribe_whisper(self, audio_path: str, language: str, task: str) -> Dict[str, Any]:
        """Transcribe using openai-whisper"""
        options = {}
        if language:
            options["language"] = language
        options["task"] = task
        
        result = self.model.transcribe(audio_path, **options)
        
        segments = []
        for seg in result.get("segments", []):
            segments.append({
                "start": seg["start"],
                "end": seg["end"],
                "text": seg["text"].strip()
            })
        
        return {
            "text": result.get("text", "").strip(),
            "language": result.get("language", "unknown"),
            "segments": segments,
            "duration": segments[-1]["end"] if segments else 0
        }
    
    def _transcribe_faster(self, audio_path: str, language: str, task: str) -> Dict[str, Any]:
        """Transcribe using faster-whisper"""
        segments_gen, info = self.model.transcribe(
            audio_path,
            language=language,
            task=task,
            beam_size=5
        )
        
        segments = []
        full_text = []
        
        for seg in segments_gen:
            segments.append({
                "start": seg.start,
                "end": seg.end,
                "text": seg.text.strip()
            })
            full_text.append(seg.text.strip())
        
        return {
            "text": " ".join(full_text),
            "language": info.language,
            "segments": segments,
            "duration": info.duration
        }
    
    def transcribe_audio_data(
        self,
        audio_data: Union[bytes, np.ndarray],
        sample_rate: int = 16000,
        language: str = None
    ) -> Dict[str, Any]:
        """
        Transcribe raw audio data
        
        Args:
            audio_data: Raw audio bytes or numpy array
            sample_rate: Audio sample rate (should be 16000 for Whisper)
            language: Language code or None for auto-detect
            
        Returns:
            Transcription result
        """
        if not self.available:
            return {"error": "Whisper not available", "text": ""}
        
        # Convert bytes to numpy array if needed
        if isinstance(audio_data, bytes):
            audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
        else:
            audio_array = audio_data
        
        # Save to temp file (Whisper requires file input)
        temp_path = os.path.join(str(TEMP_DIR), "temp_audio.wav")
        
        try:
            # Write WAV file
            with wave.open(temp_path, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(sample_rate)
                wf.writeframes((audio_array * 32767).astype(np.int16).tobytes())
            
            # Transcribe
            result = self.transcribe_file(temp_path, language=language)
            
            return result
            
        finally:
            # Cleanup
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass
    
    def detect_language(self, audio_path: str) -> str:
        """Detect language of audio file"""
        if not self.available:
            return "unknown"
        
        try:
            if self.use_faster:
                _, info = self.model.transcribe(audio_path, beam_size=1)
                return info.language
            else:
                # Load first 30 seconds
                audio = _whisper.load_audio(audio_path)
                audio = _whisper.pad_or_trim(audio)
                mel = _whisper.log_mel_spectrogram(audio).to(self.model.device)
                _, probs = self.model.detect_language(mel)
                return max(probs, key=probs.get)
        except Exception as e:
            logger.error(f"[STT] Language detection failed: {e}")
            return "unknown"
    
    def is_available(self) -> bool:
        """Check if STT is available"""
        return self.available
    
    def get_info(self) -> Dict[str, Any]:
        """Get STT module info"""
        return {
            "available": self.available,
            "model": self.model_name,
            "backend": "faster-whisper" if self.use_faster else "openai-whisper",
            "device": self.device
        }


# Singleton instance
_stt_instance: Optional[WhisperSTT] = None

def get_stt() -> WhisperSTT:
    """Get or create STT singleton"""
    global _stt_instance
    if _stt_instance is None:
        _stt_instance = WhisperSTT()
    return _stt_instance


def transcribe(audio_path: str, language: str = None) -> str:
    """Quick transcription function"""
    stt = get_stt()
    result = stt.transcribe_file(audio_path, language=language)
    return result.get("text", "")
