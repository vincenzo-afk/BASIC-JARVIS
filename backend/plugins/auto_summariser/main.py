"""
Auto Summarizer Plugin - FULLY FUNCTIONAL
Summarize content using local LLM
"""
import os
import sys
from typing import Dict, Any

# Add backend path for imports
backend_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)


class Plugin:
    """
    Content summarization plugin using local LLM
    
    Commands:
    - summarize: Summarize provided text
    - summarize_screen: Capture screen and summarize
    - summarize_clipboard: Summarize clipboard content
    - summarize_file: Summarize a text file
    - key_points: Extract key points from text
    - explain: Explain text in simple terms
    """
    
    def __init__(self):
        self.name = "Auto Summarizer"
        self.version = "1.0.0"
        self._llm = None
    
    def _get_llm(self):
        """Get LLM client lazily"""
        if self._llm is None:
            from modules.llm.ollama_client import OllamaClient
            self._llm = OllamaClient()
        return self._llm
    
    def run(self, command: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a command"""
        commands = {
            "summarize": self.summarize,
            "summarize_screen": self.summarize_screen,
            "summarize_clipboard": self.summarize_clipboard,
            "summarize_file": self.summarize_file,
            "key_points": self.key_points,
            "explain": self.explain,
        }
        
        handler = commands.get(command)
        if handler:
            try:
                return handler(params)
            except Exception as e:
                return {"error": str(e)}
        
        return {"error": f"Unknown command: {command}"}
    
    def summarize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Summarize provided text
        
        Params:
        - text: Text to summarize
        - style: concise, detailed, bullet (default: concise)
        - model: LLM model to use (default: llama3.1:8b)
        - max_words: Maximum words in summary (default: 150)
        """
        text = params.get("text", "")
        style = params.get("style", "concise")
        model = params.get("model", "llama3.1:8b")
        max_words = params.get("max_words", 150)
        
        if not text:
            return {"error": "No text provided"}
        
        # Build prompt based on style
        if style == "bullet":
            prompt = f"""Summarize the following text as bullet points (max 5-7 points):

{text}

Bullet points:"""
        elif style == "detailed":
            prompt = f"""Provide a detailed summary of the following text in about {max_words} words:

{text}

Detailed summary:"""
        else:  # concise
            prompt = f"""Provide a concise summary of the following text in 2-3 sentences:

{text}

Summary:"""
        
        try:
            llm = self._get_llm()
            result = llm.generate(
                model=model,
                prompt=prompt,
                temperature=0.3
            )
            
            return {
                "summary": result.get("response", "").strip(),
                "style": style,
                "original_length": len(text),
                "summary_length": len(result.get("response", "")),
                "model": model
            }
        except Exception as e:
            return {"error": f"LLM error: {e}"}
    
    def summarize_screen(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Capture screen and summarize content
        
        Params:
        - style: Summary style (default: concise)
        - monitor: Monitor number (default: 1)
        """
        from modules.ocr.screen_capture import ScreenCapture
        from modules.ocr.ocr_engine import OCREngine
        
        style = params.get("style", "concise")
        monitor = params.get("monitor", 1)
        
        try:
            # Capture screen
            capture = ScreenCapture()
            image_path, dims = capture.capture(monitor=monitor)
            
            # Extract text
            ocr = OCREngine()
            text = ocr.extract_text(image_path, preprocess=True)
            
            if not text or len(text.strip()) < 20:
                return {
                    "error": "No readable text found on screen",
                    "image_path": image_path
                }
            
            # Summarize
            result = self.summarize({
                "text": text,
                "style": style,
                "model": params.get("model", "llama3.1:8b")
            })
            
            result["screen_text"] = text[:500] + "..." if len(text) > 500 else text
            result["image_path"] = image_path
            
            return result
            
        except Exception as e:
            return {"error": f"Screen capture error: {e}"}
    
    def summarize_clipboard(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Summarize clipboard content
        
        Params:
        - style: Summary style (default: concise)
        """
        try:
            import subprocess
            
            # Get clipboard content (cross-platform)
            if sys.platform == "win32":
                result = subprocess.run(
                    ["powershell", "-command", "Get-Clipboard"],
                    capture_output=True,
                    text=True
                )
                text = result.stdout
            elif sys.platform == "darwin":
                result = subprocess.run(["pbpaste"], capture_output=True, text=True)
                text = result.stdout
            else:
                result = subprocess.run(
                    ["xclip", "-selection", "clipboard", "-o"],
                    capture_output=True,
                    text=True
                )
                text = result.stdout
            
            if not text or len(text.strip()) < 10:
                return {"error": "Clipboard is empty or has minimal content"}
            
            # Summarize
            return self.summarize({
                "text": text,
                "style": params.get("style", "concise"),
                "model": params.get("model", "llama3.1:8b")
            })
            
        except Exception as e:
            return {"error": f"Clipboard error: {e}"}
    
    def summarize_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Summarize a text file
        
        Params:
        - path: Path to the file
        - style: Summary style (default: concise)
        """
        path = params.get("path", "")
        
        if not path:
            return {"error": "No file path provided"}
        
        if not os.path.exists(path):
            return {"error": f"File not found: {path}"}
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
            
            result = self.summarize({
                "text": text,
                "style": params.get("style", "concise"),
                "model": params.get("model", "llama3.1:8b")
            })
            
            result["file_path"] = path
            result["file_size"] = len(text)
            
            return result
            
        except Exception as e:
            return {"error": f"File read error: {e}"}
    
    def key_points(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract key points from text
        
        Params:
        - text: Text to analyze
        - count: Number of key points (default: 5)
        """
        text = params.get("text", "")
        count = params.get("count", 5)
        model = params.get("model", "llama3.1:8b")
        
        if not text:
            return {"error": "No text provided"}
        
        prompt = f"""Extract exactly {count} key points from the following text. 
Format as a numbered list.

Text:
{text}

Key points:"""
        
        try:
            llm = self._get_llm()
            result = llm.generate(
                model=model,
                prompt=prompt,
                temperature=0.3
            )
            
            # Parse key points
            response = result.get("response", "").strip()
            points = []
            for line in response.split("\n"):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith("-") or line.startswith("•")):
                    # Clean up numbering
                    if line[0].isdigit():
                        line = line.split(".", 1)[-1].strip()
                    elif line[0] in "-•":
                        line = line[1:].strip()
                    if line:
                        points.append(line)
            
            return {
                "key_points": points[:count],
                "count": len(points),
                "model": model
            }
            
        except Exception as e:
            return {"error": f"LLM error: {e}"}
    
    def explain(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Explain text in simple terms
        
        Params:
        - text: Text to explain
        - level: Explanation level (simple, intermediate, technical)
        """
        text = params.get("text", "")
        level = params.get("level", "simple")
        model = params.get("model", "llama3.1:8b")
        
        if not text:
            return {"error": "No text provided"}
        
        level_prompts = {
            "simple": "Explain this in simple terms that a 10-year-old would understand:",
            "intermediate": "Explain this clearly for someone with basic knowledge:",
            "technical": "Provide a technical explanation with relevant details:"
        }
        
        prompt = f"""{level_prompts.get(level, level_prompts['simple'])}

{text}

Explanation:"""
        
        try:
            llm = self._get_llm()
            result = llm.generate(
                model=model,
                prompt=prompt,
                temperature=0.5
            )
            
            return {
                "explanation": result.get("response", "").strip(),
                "level": level,
                "model": model
            }
            
        except Exception as e:
            return {"error": f"LLM error: {e}"}


# Export plugin instance
plugin = Plugin()
