"""
Ollama Client Module - FULLY FUNCTIONAL
Complete implementation for Ollama LLM communication
"""
import requests
import json
import time
from typing import Optional, List, Dict, Any, Generator
from config.settings import OLLAMA_HOST, DEFAULT_MODEL
from modules.utils.logger import logger


class OllamaError(Exception):
    """Custom exception for Ollama-related errors"""
    pass


class OllamaClient:
    """
    Complete client for interacting with Ollama API
    
    Features:
    - Text generation (sync and streaming)
    - Multi-turn chat
    - Model management
    - Embeddings
    - Connection validation
    """
    
    def __init__(self, host: str = None):
        self.host = host or OLLAMA_HOST
        self.default_model = DEFAULT_MODEL
        self.timeout = 120
        self.connected = self._verify_connection()
    
    def _verify_connection(self) -> bool:
        """Verify Ollama server is running"""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            if response.status_code == 200:
                logger.info(f"[Ollama] Connected to {self.host}")
                return True
            logger.warning(f"[Ollama] Server returned status {response.status_code}")
            return False
        except requests.exceptions.ConnectionError:
            logger.warning(f"[Ollama] Cannot connect to {self.host}")
            return False
        except Exception as e:
            logger.warning(f"[Ollama] Connection check failed: {e}")
            return False
    
    def generate(
        self,
        model: str = None,
        prompt: str = "",
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        context: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """
        Generate text completion
        
        Args:
            model: Model name (e.g., llama3.1:8b)
            prompt: User prompt
            system: Optional system prompt
            temperature: Creativity (0.0-2.0)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream response
            context: Previous context for continuation
            
        Returns:
            Dict with response, tokens, and timing info
        """
        model = model or self.default_model
        url = f"{self.host}/api/generate"
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "temperature": temperature
            }
        }
        
        if system:
            payload["system"] = system
        
        if max_tokens:
            payload["options"]["num_predict"] = max_tokens
        
        if context:
            payload["context"] = context
        
        start_time = time.time()
        
        try:
            if stream:
                return self._generate_stream(url, payload, start_time)
            
            response = requests.post(url, json=payload, timeout=self.timeout)
            
            if response.status_code != 200:
                error_detail = response.text[:500]
                raise OllamaError(f"Ollama API error ({response.status_code}): {error_detail}")
            
            data = response.json()
            duration_ms = (time.time() - start_time) * 1000
            
            return {
                "response": data.get("response", ""),
                "model": data.get("model", model),
                "tokens": data.get("eval_count", 0),
                "prompt_tokens": data.get("prompt_eval_count", 0),
                "duration_ms": round(duration_ms, 2),
                "done": data.get("done", True),
                "context": data.get("context", [])
            }
            
        except requests.exceptions.ConnectionError:
            raise OllamaError(f"Cannot connect to Ollama at {self.host}. Is Ollama running?")
        except requests.exceptions.Timeout:
            raise OllamaError("Request timed out. Model may be loading or query too complex.")
        except json.JSONDecodeError as e:
            raise OllamaError(f"Invalid response from Ollama: {e}")
        except OllamaError:
            raise
        except Exception as e:
            raise OllamaError(f"Unexpected error: {e}")
    
    def _generate_stream(self, url: str, payload: dict, start_time: float) -> Generator:
        """Stream generation response"""
        try:
            response = requests.post(url, json=payload, stream=True, timeout=self.timeout)
            
            if response.status_code != 200:
                raise OllamaError(f"Stream error: {response.status_code}")
            
            full_response = ""
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    chunk = data.get("response", "")
                    full_response += chunk
                    
                    yield {
                        "chunk": chunk,
                        "done": data.get("done", False),
                        "full_response": full_response
                    }
            
        except Exception as e:
            raise OllamaError(f"Stream error: {e}")
    
    def chat(
        self,
        model: str = None,
        messages: List[Dict[str, str]] = None,
        temperature: float = 0.7,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Multi-turn chat conversation
        
        Args:
            model: Model name
            messages: List of {"role": "user/assistant/system", "content": "..."}
            temperature: Creativity setting
            stream: Whether to stream response
            
        Returns:
            Dict with response text
        """
        model = model or self.default_model
        url = f"{self.host}/api/chat"
        
        payload = {
            "model": model,
            "messages": messages or [],
            "stream": stream,
            "options": {
                "temperature": temperature
            }
        }
        
        start_time = time.time()
        
        try:
            response = requests.post(url, json=payload, timeout=self.timeout)
            
            if response.status_code != 200:
                raise OllamaError(f"Chat error ({response.status_code}): {response.text[:200]}")
            
            data = response.json()
            duration_ms = (time.time() - start_time) * 1000
            
            message = data.get("message", {})
            
            return {
                "response": message.get("content", ""),
                "role": message.get("role", "assistant"),
                "model": data.get("model", model),
                "duration_ms": round(duration_ms, 2),
                "done": data.get("done", True)
            }
            
        except requests.exceptions.ConnectionError:
            raise OllamaError(f"Cannot connect to Ollama at {self.host}")
        except OllamaError:
            raise
        except Exception as e:
            raise OllamaError(f"Chat error: {e}")
    
    def list_models(self) -> List[Dict[str, Any]]:
        """List all available models"""
        url = f"{self.host}/api/tags"
        
        try:
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                raise OllamaError(f"Failed to list models: {response.status_code}")
            
            data = response.json()
            models = data.get("models", [])
            
            # Sort by name
            models.sort(key=lambda x: x.get("name", ""))
            
            return models
            
        except requests.exceptions.ConnectionError:
            raise OllamaError(f"Cannot connect to Ollama at {self.host}")
        except Exception as e:
            raise OllamaError(f"Error listing models: {e}")
    
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get detailed information about a model"""
        url = f"{self.host}/api/show"
        
        try:
            response = requests.post(url, json={"name": model_name}, timeout=10)
            
            if response.status_code != 200:
                raise OllamaError(f"Model not found: {model_name}")
            
            return response.json()
            
        except requests.exceptions.ConnectionError:
            raise OllamaError(f"Cannot connect to Ollama at {self.host}")
        except Exception as e:
            raise OllamaError(f"Error getting model info: {e}")
    
    def pull_model(self, model_name: str, stream: bool = False) -> Dict[str, Any]:
        """Pull/download a model"""
        url = f"{self.host}/api/pull"
        
        try:
            logger.info(f"[Ollama] Pulling model: {model_name}")
            
            response = requests.post(
                url, 
                json={"name": model_name, "stream": stream},
                timeout=1800  # 30 minute timeout for downloads
            )
            
            if response.status_code != 200:
                raise OllamaError(f"Failed to pull model: {response.text}")
            
            logger.info(f"[Ollama] Model pulled: {model_name}")
            return {"status": "success", "model": model_name}
            
        except requests.exceptions.Timeout:
            raise OllamaError("Model download timed out")
        except Exception as e:
            raise OllamaError(f"Error pulling model: {e}")
    
    def delete_model(self, model_name: str) -> Dict[str, Any]:
        """Delete a model"""
        url = f"{self.host}/api/delete"
        
        try:
            response = requests.delete(url, json={"name": model_name}, timeout=30)
            
            if response.status_code != 200:
                raise OllamaError(f"Failed to delete model: {response.text}")
            
            return {"status": "deleted", "model": model_name}
            
        except Exception as e:
            raise OllamaError(f"Error deleting model: {e}")
    
    def embeddings(self, model: str, prompt: str) -> List[float]:
        """Generate embeddings for text"""
        url = f"{self.host}/api/embeddings"
        
        try:
            response = requests.post(
                url,
                json={"model": model, "prompt": prompt},
                timeout=60
            )
            
            if response.status_code != 200:
                raise OllamaError(f"Embeddings error: {response.status_code}")
            
            data = response.json()
            return data.get("embedding", [])
            
        except Exception as e:
            raise OllamaError(f"Embeddings error: {e}")
    
    def is_available(self) -> bool:
        """Check if Ollama is available"""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=3)
            return response.status_code == 200
        except:
            return False
    
    def get_running_models(self) -> List[Dict[str, Any]]:
        """Get currently loaded models"""
        url = f"{self.host}/api/ps"
        
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return response.json().get("models", [])
            return []
        except:
            return []


# Singleton instance
_client: Optional[OllamaClient] = None

def get_client() -> OllamaClient:
    """Get or create Ollama client singleton"""
    global _client
    if _client is None:
        _client = OllamaClient()
    return _client
