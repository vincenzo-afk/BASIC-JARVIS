"""
Chat Route - Ollama LLM Integration - FULLY FUNCTIONAL
Handles chat requests to local LLM models with streaming support
"""
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, List, AsyncGenerator
import asyncio
import json
from modules.llm.ollama_client import OllamaClient, OllamaError
from modules.utils.logger import logger

router = APIRouter()

# Initialize LLM client
llm_client = OllamaClient()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def send_json(self, websocket: WebSocket, data: dict):
        await websocket.send_json(data)

manager = ConnectionManager()


class ChatRequest(BaseModel):
    """Chat request model"""
    model: str = Field(default="llama3.1:8b", description="Ollama model to use")
    prompt: str = Field(..., description="User prompt/message")
    system: Optional[str] = Field(default=None, description="System prompt")
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, description="Max tokens to generate")


class ChatResponse(BaseModel):
    """Chat response model"""
    response: str
    model: str
    tokens_used: Optional[int] = None
    duration_ms: Optional[float] = None


class ChatHistoryRequest(BaseModel):
    """Multi-turn chat request"""
    model: str = Field(default="llama3.1:8b")
    messages: List[dict] = Field(..., description="Chat history")
    temperature: Optional[float] = Field(default=0.7)


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a message to the LLM and get a response
    
    - **model**: Ollama model name (e.g., llama3.1:8b, qwen2.5-coder:7b)
    - **prompt**: The user's message/question
    - **system**: Optional system prompt to set context
    - **temperature**: Creativity (0.0-2.0, default 0.7)
    """
    logger.info(f"Chat request: model={request.model}, prompt_length={len(request.prompt)}")
    
    try:
        result = llm_client.generate(
            model=request.model,
            prompt=request.prompt,
            system=request.system,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        logger.info(f"Chat response: length={len(result['response'])}")
        
        return ChatResponse(
            response=result["response"],
            model=request.model,
            tokens_used=result.get("tokens"),
            duration_ms=result.get("duration_ms")
        )
        
    except OllamaError as e:
        logger.error(f"Ollama error: {e}")
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/conversation")
async def chat_conversation(request: ChatHistoryRequest):
    """
    Multi-turn conversation with message history
    
    Messages format: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
    """
    try:
        result = llm_client.chat(
            model=request.model,
            messages=request.messages,
            temperature=request.temperature
        )
        
        return {
            "response": result["response"],
            "model": request.model
        }
        
    except OllamaError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models")
async def list_models():
    """List all available Ollama models"""
    try:
        models = llm_client.list_models()
        return {"models": models}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Failed to fetch models: {e}")


@router.get("/models/{model_name}")
async def get_model_info(model_name: str):
    """Get information about a specific model"""
    try:
        info = llm_client.get_model_info(model_name)
        return info
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Model not found: {e}")


@router.post("/models/{model_name}/pull")
async def pull_model(model_name: str):
    """Pull/download a model from Ollama library"""
    try:
        result = llm_client.pull_model(model_name)
        return {"status": "success", "model": model_name, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to pull model: {e}")


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """
    Stream chat response token by token
    
    Returns Server-Sent Events (SSE) stream.
    Each event contains a JSON object with 'chunk' and 'done' fields.
    """
    logger.info(f"Stream request: model={request.model}")
    
    async def generate() -> AsyncGenerator[str, None]:
        try:
            for chunk_data in llm_client.generate(
                model=request.model,
                prompt=request.prompt,
                system=request.system,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                stream=True
            ):
                data = {
                    "chunk": chunk_data.get("chunk", ""),
                    "done": chunk_data.get("done", False),
                    "full_response": chunk_data.get("full_response", "")
                }
                yield f"data: {json.dumps(data)}\n\n"
                
                if chunk_data.get("done"):
                    break
                    
        except OllamaError as e:
            error_data = {"error": str(e), "done": True}
            yield f"data: {json.dumps(error_data)}\n\n"
        except Exception as e:
            error_data = {"error": str(e), "done": True}
            yield f"data: {json.dumps(error_data)}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.websocket("/ws")
async def websocket_chat(websocket: WebSocket):
    """
    WebSocket endpoint for real-time chat
    
    Send: {"type": "chat", "model": "llama3.1:8b", "prompt": "Hello"}
    Receive: {"type": "chunk", "content": "..."} or {"type": "done", "response": "..."}
    """
    await manager.connect(websocket)
    logger.info("[Chat] WebSocket connection established")
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            
            msg_type = data.get("type", "chat")
            
            if msg_type == "chat":
                model = data.get("model", "llama3.1:8b")
                prompt = data.get("prompt", "")
                system = data.get("system")
                
                if not prompt:
                    await websocket.send_json({"type": "error", "message": "No prompt provided"})
                    continue
                
                logger.info(f"[Chat WS] Query: {prompt[:50]}...")
                
                try:
                    # Stream response
                    full_response = ""
                    for chunk_data in llm_client.generate(
                        model=model,
                        prompt=prompt,
                        system=system,
                        stream=True
                    ):
                        chunk = chunk_data.get("chunk", "")
                        full_response += chunk
                        
                        await websocket.send_json({
                            "type": "chunk",
                            "content": chunk,
                            "done": chunk_data.get("done", False)
                        })
                        
                        if chunk_data.get("done"):
                            break
                    
                    # Send complete message
                    await websocket.send_json({
                        "type": "done",
                        "response": full_response,
                        "model": model
                    })
                    
                except OllamaError as e:
                    await websocket.send_json({
                        "type": "error",
                        "message": str(e)
                    })
                    
            elif msg_type == "ping":
                await websocket.send_json({"type": "pong"})
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("[Chat] WebSocket disconnected")
    except Exception as e:
        logger.error(f"[Chat WS] Error: {e}")
        manager.disconnect(websocket)

