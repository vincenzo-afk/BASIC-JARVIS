"""
JARVIS Backend - FastAPI Entry Point
Main API server for the JARVIS desktop assistant
Optimized for maximum performance
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse, ORJSONResponse
from contextlib import asynccontextmanager
import uvicorn
import time
import asyncio
import os
import multiprocessing

from routes import chat, screen, control, voice, agent, plugins
from modules.utils.logger import logger

# Performance: Calculate optimal workers
CPU_COUNT = multiprocessing.cpu_count()
WORKERS = max(1, min(CPU_COUNT - 1, 4))  # Leave 1 core for Ollama

# Startup/Shutdown lifecycle
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 JARVIS Backend starting...")
    logger.info(f"💻 Using {WORKERS} workers on {CPU_COUNT} CPU cores")
    logger.info("📍 API running at http://localhost:8000")
    logger.info("📖 Docs available at http://localhost:8000/docs")
    
    # Pre-load heavy modules in background
    asyncio.create_task(_preload_modules())
    
    yield
    
    # Shutdown
    logger.info("👋 JARVIS Backend shutting down...")


async def _preload_modules():
    """Pre-load heavy modules for faster first requests"""
    try:
        # Pre-initialize voice modules (they can be slow to load)
        from modules.voice.stt_whisper import get_stt
        from modules.voice.tts_piper import get_tts
        
        await asyncio.get_event_loop().run_in_executor(None, get_stt)
        await asyncio.get_event_loop().run_in_executor(None, get_tts)
        
        logger.info("✅ Voice modules pre-loaded")
    except Exception as e:
        logger.warning(f"⚠️ Voice module pre-load failed: {e}")


# Create FastAPI app with performance optimizations
app = FastAPI(
    title="JARVIS Backend",
    description="Local AI-powered desktop assistant API",
    version="1.0.0",
    lifespan=lifespan,
    default_response_class=ORJSONResponse,  # Faster JSON serialization
)

# CORS Middleware - Allow Electron app to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZip compression for large responses
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(round(process_time * 1000, 2))
    return response

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "path": str(request.url)
        }
    )

# Include Routers
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(screen.router, prefix="/api/screen", tags=["Screen"])
app.include_router(control.router, prefix="/api/control", tags=["Control"])
app.include_router(voice.router, prefix="/api/voice", tags=["Voice"])
app.include_router(agent.router, prefix="/api/agent", tags=["Agent"])
app.include_router(plugins.router, prefix="/api/plugins", tags=["Plugins"])

# Root endpoint
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "service": "JARVIS Backend",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/api/chat",
            "screen": "/api/screen",
            "control": "/api/control",
            "voice": "/api/voice",
            "agent": "/api/agent",
            "plugins": "/api/plugins"
        }
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Detailed health check"""
    from config.settings import OLLAMA_HOST
    import httpx
    
    # Check Ollama (with connection pooling)
    ollama_status = "unknown"
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            res = await client.get(f"{OLLAMA_HOST}/api/tags")
            ollama_status = "connected" if res.status_code == 200 else "error"
    except:
        ollama_status = "disconnected"
    
    # Check Modules (cached singletons)
    from modules.voice.stt_whisper import get_stt
    from modules.voice.tts_piper import get_tts
    from modules.ocr.ocr_engine import OCREngine
    
    stt = get_stt()
    tts = get_tts()
    
    ocr_available = False
    try:
        OCREngine()
        ocr_available = True
    except:
        pass

    return {
        "status": "healthy",
        "ollama": ollama_status,
        "workers": WORKERS,
        "cpu_cores": CPU_COUNT,
        "modules": {
            "chat": True,
            "screen": ocr_available,
            "control": True,
            "voice": stt.is_available() or tts.is_available(),
            "stt": stt.is_available(),
            "tts": tts.is_available(),
            "agent": True,
            "plugins": True
        }
    }

if __name__ == "__main__":
    # Optimized uvicorn settings
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=False,  # Disable for production performance
        log_level="info",
        workers=1,  # Single worker for development, increase for production
        access_log=False,  # Disable access log for performance
        loop="auto",  # Use uvloop if available
        http="auto",  # Use httptools if available
    )

