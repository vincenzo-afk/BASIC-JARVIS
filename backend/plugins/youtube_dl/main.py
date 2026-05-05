"""
YouTube Download Plugin for JARVIS
Uses yt-dlp for downloading videos and audio
"""
import subprocess
import os
from typing import Dict, Any

class Plugin:
    def __init__(self):
        self.name = "YouTube Downloader"
        self.download_path = os.path.expanduser("~/Downloads/JARVIS")
        os.makedirs(self.download_path, exist_ok=True)
    
    def run(self, command: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute plugin command"""
        commands = {
            "download": self.download_video,
            "audio": self.download_audio,
            "info": self.get_info
        }
        
        handler = commands.get(command)
        if handler:
            return handler(params)
        return {"error": f"Unknown command: {command}"}
    
    def download_video(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Download video from YouTube"""
        url = params.get("url")
        if not url:
            return {"error": "URL required"}
        
        quality = params.get("quality", "best")
        
        try:
            cmd = [
                "yt-dlp",
                "-f", f"bestvideo[height<={quality}]+bestaudio/best" if quality != "best" else "best",
                "-o", f"{self.download_path}/%(title)s.%(ext)s",
                url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    "status": "success",
                    "message": "Video downloaded",
                    "path": self.download_path
                }
            else:
                return {"error": result.stderr}
                
        except FileNotFoundError:
            return {"error": "yt-dlp not installed. Run: pip install yt-dlp"}
        except Exception as e:
            return {"error": str(e)}
    
    def download_audio(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Download audio only from YouTube"""
        url = params.get("url")
        if not url:
            return {"error": "URL required"}
        
        try:
            cmd = [
                "yt-dlp",
                "-x",  # Extract audio
                "--audio-format", "mp3",
                "-o", f"{self.download_path}/%(title)s.%(ext)s",
                url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    "status": "success",
                    "message": "Audio downloaded",
                    "path": self.download_path
                }
            else:
                return {"error": result.stderr}
                
        except FileNotFoundError:
            return {"error": "yt-dlp not installed. Run: pip install yt-dlp"}
        except Exception as e:
            return {"error": str(e)}
    
    def get_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get video information"""
        url = params.get("url")
        if not url:
            return {"error": "URL required"}
        
        try:
            cmd = ["yt-dlp", "--dump-json", "--no-download", url]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                import json
                info = json.loads(result.stdout)
                return {
                    "title": info.get("title"),
                    "duration": info.get("duration"),
                    "uploader": info.get("uploader"),
                    "view_count": info.get("view_count"),
                    "thumbnail": info.get("thumbnail")
                }
            else:
                return {"error": result.stderr}
                
        except Exception as e:
            return {"error": str(e)}


# Plugin instance
plugin = Plugin()
