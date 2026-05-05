"""
Voice Routes - FULLY FUNCTIONAL
Speech-to-Text and Text-to-Speech API endpoints
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional
import os
import tempfile
import shutil
from modules.voice.stt_whisper import get_stt, WhisperSTT
from modules.voice.tts_piper import get_tts, PiperTTS
from modules.utils.logger import logger
from config.settings import TEMP_DIR

router = APIRouter()


class SpeakRequest(BaseModel):
    """Request to convert text to speech"""
    text: str = Field(..., description="Text to convert to speech")
    voice: Optional[str] = Field(default=None, description="Voice name")
    rate: float = Field(default=1.0, ge=0.5, le=2.0, description="Speech rate")


class TranscribeResponse(BaseModel):
    """Transcription response"""
    text: str
    language: Optional[str] = None
    duration: Optional[float] = None
    segments: Optional[list] = None


class SpeakResponse(BaseModel):
    """TTS response"""
    status: str
    output: Optional[str] = None
    backend: Optional[str] = None
    error: Optional[str] = None


class VoiceStatus(BaseModel):
    """Voice module status"""
    stt_available: bool
    tts_available: bool
    stt_backend: Optional[str] = None
    tts_backend: Optional[str] = None
    stt_model: Optional[str] = None


@router.get("/status", response_model=VoiceStatus)
async def voice_status():
    """
    Get status of voice modules (STT and TTS)
    """
    stt = get_stt()
    tts = get_tts()
    
    stt_info = stt.get_info()
    tts_info = tts.get_info()
    
    return VoiceStatus(
        stt_available=stt_info.get("available", False),
        tts_available=tts_info.get("available", False),
        stt_backend=stt_info.get("backend"),
        tts_backend=tts_info.get("backend"),
        stt_model=stt_info.get("model")
    )


@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe_audio(
    file: UploadFile = File(...),
    language: Optional[str] = Form(default=None)
):
    """
    Transcribe an audio file to text
    
    Accepts: WAV, MP3, M4A, FLAC, OGG, etc.
    
    - **file**: Audio file to transcribe
    - **language**: Optional language code (e.g., 'en', 'es', 'fr')
    """
    stt = get_stt()
    
    if not stt.is_available():
        raise HTTPException(
            status_code=503,
            detail="Speech-to-text not available. Install whisper: pip install openai-whisper"
        )
    
    # Save uploaded file temporarily
    temp_dir = str(TEMP_DIR / "uploads")
    os.makedirs(temp_dir, exist_ok=True)
    
    # Get file extension
    ext = os.path.splitext(file.filename)[1] or ".wav"
    temp_path = os.path.join(temp_dir, f"upload_{os.urandom(8).hex()}{ext}")
    
    try:
        # Save file
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        logger.info(f"[Voice] Transcribing: {file.filename} ({len(content)} bytes)")
        
        # Transcribe
        result = stt.transcribe_file(temp_path, language=language)
        
        if "error" in result and result["error"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return TranscribeResponse(
            text=result.get("text", ""),
            language=result.get("language"),
            duration=result.get("duration"),
            segments=result.get("segments")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Voice] Transcription error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass


@router.post("/speak", response_model=SpeakResponse)
async def text_to_speech(request: SpeakRequest):
    """
    Convert text to speech
    
    - **text**: Text to convert
    - **voice**: Optional voice name
    - **rate**: Speech rate (0.5 to 2.0)
    """
    tts = get_tts()
    
    if not tts.is_available():
        raise HTTPException(
            status_code=503,
            detail="Text-to-speech not available"
        )
    
    logger.info(f"[Voice] TTS: {len(request.text)} chars, rate={request.rate}")
    
    try:
        result = tts.speak(
            text=request.text,
            voice=request.voice,
            rate=request.rate,
            blocking=True
        )
        
        if result.get("status") == "error":
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return SpeakResponse(
            status=result.get("status", "error"),
            output=result.get("output"),
            backend=result.get("backend")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Voice] TTS error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/speak-async")
async def text_to_speech_async(request: SpeakRequest):
    """
    Convert text to speech asynchronously (fire and forget)
    
    Speaks immediately without waiting for completion.
    """
    tts = get_tts()
    
    if not tts.is_available():
        raise HTTPException(
            status_code=503,
            detail="Text-to-speech not available"
        )
    
    # Speak asynchronously
    tts.speak_async(request.text)
    
    return {"status": "speaking", "text_length": len(request.text)}


@router.get("/speak/download/{filename}")
async def download_audio(filename: str):
    """
    Download a generated audio file
    
    - **filename**: Name of the audio file to download
    """
    audio_dir = str(TEMP_DIR / "audio")
    file_path = os.path.join(audio_dir, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    return FileResponse(
        file_path,
        media_type="audio/wav",
        filename=filename
    )


@router.get("/voices")
async def list_voices():
    """
    List available TTS voices
    """
    tts = get_tts()
    
    return {
        "backend": tts.backend,
        "voices": tts.list_voices()
    }


@router.post("/detect-language")
async def detect_language(file: UploadFile = File(...)):
    """
    Detect the language of an audio file
    """
    stt = get_stt()
    
    if not stt.is_available():
        raise HTTPException(status_code=503, detail="STT not available")
    
    # Save file temporarily
    temp_path = os.path.join(str(TEMP_DIR), f"lang_detect_{os.urandom(4).hex()}.wav")
    
    try:
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        language = stt.detect_language(temp_path)
        
        return {"language": language}
        
    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass


@router.post("/voice-chat")
async def voice_to_chat(
    file: UploadFile = File(...),
    model: str = Form(default="llama3.1:8b"),
    speak_response: bool = Form(default=True)
):
    """
    Complete voice conversation loop:
    1. Transcribe audio input
    2. Send to LLM for response
    3. Optionally convert response to speech
    
    Returns transcription, LLM response, and audio URL if speak_response=True
    """
    from modules.llm.ollama_client import OllamaClient, OllamaError
    
    stt = get_stt()
    tts = get_tts()
    
    if not stt.is_available():
        raise HTTPException(status_code=503, detail="STT not available")
    
    # Save uploaded audio
    temp_audio = os.path.join(str(TEMP_DIR), f"voice_input_{os.urandom(8).hex()}.wav")
    
    try:
        with open(temp_audio, "wb") as f:
            content = await file.read()
            f.write(content)
        
        logger.info(f"[Voice] Received audio: {len(content)} bytes")
        
        # Step 1: Transcribe
        transcription = stt.transcribe_file(temp_audio)
        user_text = transcription.get("text", "").strip()
        
        if not user_text:
            return {
                "success": False,
                "error": "Could not transcribe audio - no speech detected",
                "transcription": ""
            }
        
        logger.info(f"[Voice] Transcribed: {user_text}")
        
        # Step 2: Get LLM response
        # Step 2: Get LLM response (via VoiceAgent)
        try:
            from modules.agents.voice_agent import VoiceAgent
            agent = VoiceAgent()
            agent_result = await agent.process_command(user_text, model=model)
            ai_response = agent_result.get("response", "")
            
            if not agent_result.get("success"):
                logger.warning(f"[Voice] Agent error: {agent_result.get('error')}")
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Agent error: {e}",
                "transcription": user_text
            }
        
        logger.info(f"[Voice] LLM response: {len(ai_response)} chars")
        
        result = {
            "success": True,
            "transcription": user_text,
            "response": ai_response,
            "model": model,
            "language": transcription.get("language", "en")
        }
        
        # Step 3: Text-to-Speech (optional)
        if speak_response and tts.is_available() and ai_response:
            tts_result = tts.speak(ai_response, blocking=True)
            if tts_result.get("status") == "success":
                audio_file = os.path.basename(tts_result.get("output", ""))
                result["audio_url"] = f"/api/voice/speak/download/{audio_file}"
                result["audio_path"] = tts_result.get("output")
        
        return result
        
    except Exception as e:
        logger.error(f"[Voice] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_audio):
            try:
                os.remove(temp_audio)
            except:
                pass


@router.post("/speak-base64")
async def speak_to_base64(request: SpeakRequest):
    """
    Convert text to speech and return audio as base64
    
    Useful for web clients that can play audio directly.
    """
    import base64
    
    tts = get_tts()
    
    if not tts.is_available():
        raise HTTPException(status_code=503, detail="TTS not available")
    
    try:
        result = tts.speak(
            text=request.text,
            voice=request.voice,
            rate=request.rate,
            blocking=True
        )
        
        if result.get("status") != "success":
            raise HTTPException(status_code=500, detail=result.get("error", "TTS failed"))
        
        audio_path = result.get("output")
        
        if not audio_path or not os.path.exists(audio_path):
            raise HTTPException(status_code=500, detail="Audio file not created")
        
        # Read and encode
        with open(audio_path, "rb") as f:
            audio_data = f.read()
        
        audio_base64 = base64.b64encode(audio_data).decode("utf-8")
        
        return {
            "status": "success",
            "audio_base64": audio_base64,
            "format": "wav",
            "size_bytes": len(audio_data)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Voice] Base64 TTS error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/transcribe-raw")
async def transcribe_raw_audio(
    audio_data: bytes = File(...),
    sample_rate: int = Form(default=16000),
    language: Optional[str] = Form(default=None)
):
    """
    Transcribe raw audio data (PCM format)
    
    Useful for real-time audio streaming from browser.
    """
    stt = get_stt()
    
    if not stt.is_available():
        raise HTTPException(status_code=503, detail="STT not available")
    
    try:
        result = stt.transcribe_audio_data(
            audio_data=audio_data,
            sample_rate=sample_rate,
            language=language
        )
        
        return TranscribeResponse(
            text=result.get("text", ""),
            language=result.get("language"),
            duration=result.get("duration"),
            segments=result.get("segments")
        )
        
    except Exception as e:
        logger.error(f"[Voice] Raw transcription error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

