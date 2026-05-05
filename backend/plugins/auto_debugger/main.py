"""
Auto Debugger Plugin - FULLY FUNCTIONAL
Automated code debugging and error analysis using LLM
"""
import os
import sys
import re
import traceback
import subprocess
from typing import Dict, Any, Optional, List
from pathlib import Path

# Add backend path for imports
backend_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from modules.llm.ollama_client import OllamaClient


class Plugin:
    """
    Auto-debugging plugin using LLM for code analysis
    
    Commands:
    - analyze: Analyze code for potential issues
    - fix: Suggest fixes for errors
    - explain: Explain an error message
    - trace: Analyze a traceback
    - suggest: Get improvement suggestions
    """
    
    def __init__(self):
        self.name = "Auto Debugger"
        self.version = "1.0.0"
        self.ollama = OllamaClient()
    
    def run(self, command: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a command"""
        commands = {
            "analyze": self.analyze_code,
            "fix": self.fix_error,
            "explain": self.explain_error,
            "trace": self.analyze_traceback,
            "suggest": self.suggest_improvements,
        }
        
        handler = commands.get(command)
        if handler:
            try:
                return handler(params)
            except Exception as e:
                return {"error": str(e)}
        
        return {"error": f"Unknown command: {command}"}
    
    def analyze_code(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze code for potential issues
        
        Params:
        - code: Code to analyze (string)
        - file_path: OR path to file to analyze
        - language: Programming language (optional)
        """
        code = params.get("code", "")
        file_path = params.get("file_path")
        language = params.get("language", "")
        
        if file_path and not code:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    code = f.read()
                # Detect language from extension
                ext = Path(file_path).suffix.lower()
                lang_map = {
                    ".py": "Python",
                    ".js": "JavaScript",
                    ".ts": "TypeScript",
                    ".jsx": "React/JSX",
                    ".tsx": "TypeScript React",
                    ".java": "Java",
                    ".cpp": "C++",
                    ".c": "C",
                    ".go": "Go",
                    ".rs": "Rust",
                }
                language = lang_map.get(ext, language)
            except Exception as e:
                return {"error": f"Failed to read file: {e}"}
        
        if not code:
            return {"error": "No code provided"}
        
        prompt = f"""Analyze this {language} code for potential bugs, issues, and improvements:

```{language.lower() if language else ''}
{code[:4000]}
```

Provide a structured analysis:
1. **Bugs/Errors**: List any bugs or potential runtime errors
2. **Code Smells**: Identify code quality issues
3. **Security Issues**: Point out any security concerns
4. **Performance**: Note any performance optimizations
5. **Recommendations**: Summary of recommended changes

Be concise but thorough."""

        try:
            response = self.ollama.generate(prompt, model="llama3.1:8b")
            
            return {
                "status": "success",
                "analysis": response,
                "language": language,
                "code_length": len(code)
            }
        except Exception as e:
            return {"error": f"Analysis failed: {e}"}
    
    def fix_error(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Suggest fixes for code errors
        
        Params:
        - code: Code with the error
        - error: Error message
        - language: Programming language
        """
        code = params.get("code", "")
        error = params.get("error", "")
        language = params.get("language", "Python")
        
        if not error:
            return {"error": "No error message provided"}
        
        prompt = f"""Fix this {language} code error:

**Error:**
```
{error[:1000]}
```

**Code:**
```{language.lower()}
{code[:3000]}
```

Provide:
1. **Root Cause**: What's causing the error
2. **Fixed Code**: The corrected code
3. **Explanation**: Why this fix works

Format the fixed code in a code block."""

        try:
            response = self.ollama.generate(prompt, model="llama3.1:8b")
            
            # Extract code block from response
            code_match = re.search(r'```[\w]*\n(.*?)```', response, re.DOTALL)
            fixed_code = code_match.group(1).strip() if code_match else None
            
            return {
                "status": "success",
                "fix_explanation": response,
                "fixed_code": fixed_code,
                "original_error": error[:200]
            }
        except Exception as e:
            return {"error": f"Fix generation failed: {e}"}
    
    def explain_error(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Explain an error message in simple terms
        
        Params:
        - error: Error message to explain
        - language: Programming language (optional)
        """
        error = params.get("error", "")
        language = params.get("language", "")
        
        if not error:
            return {"error": "No error message provided"}
        
        prompt = f"""Explain this {'in ' + language if language else ''} error message in simple terms:

```
{error[:1500]}
```

Provide:
1. **What it means**: Simple explanation of the error
2. **Common causes**: Why this usually happens
3. **How to fix**: Steps to resolve it
4. **Example**: A quick example if helpful

Keep the explanation beginner-friendly."""

        try:
            response = self.ollama.generate(prompt, model="llama3.1:8b")
            
            return {
                "status": "success",
                "explanation": response,
                "error_type": self._extract_error_type(error)
            }
        except Exception as e:
            return {"error": f"Explanation failed: {e}"}
    
    def analyze_traceback(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a stack trace / traceback
        
        Params:
        - traceback: The full traceback/stack trace
        - context: Additional context (optional)
        """
        tb = params.get("traceback", "")
        context = params.get("context", "")
        
        if not tb:
            return {"error": "No traceback provided"}
        
        prompt = f"""Analyze this stack trace and help debug the issue:

**Traceback:**
```
{tb[:2000]}
```

{f'**Context:** {context}' if context else ''}

Provide:
1. **Error Location**: Where the error occurred (file, line)
2. **Error Type**: What type of error this is
3. **Call Flow**: How the program got to this error
4. **Root Cause**: Most likely cause
5. **Fix Steps**: How to fix this

Focus on the most important frames in the stack."""

        try:
            response = self.ollama.generate(prompt, model="llama3.1:8b")
            
            # Extract file/line info from traceback
            file_refs = re.findall(r'File "([^"]+)", line (\d+)', tb)
            
            return {
                "status": "success",
                "analysis": response,
                "files_involved": [{"file": f[0], "line": int(f[1])} for f in file_refs[:5]],
                "error_type": self._extract_error_type(tb)
            }
        except Exception as e:
            return {"error": f"Traceback analysis failed: {e}"}
    
    def suggest_improvements(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Suggest code improvements
        
        Params:
        - code: Code to improve
        - focus: Area to focus on (performance, readability, security)
        - language: Programming language
        """
        code = params.get("code", "")
        focus = params.get("focus", "general")
        language = params.get("language", "Python")
        
        if not code:
            return {"error": "No code provided"}
        
        focus_prompts = {
            "performance": "Focus on performance optimizations, reducing time/space complexity.",
            "readability": "Focus on code clarity, naming, and documentation.",
            "security": "Focus on security vulnerabilities and best practices.",
            "general": "Focus on overall code quality improvements.",
        }
        
        focus_text = focus_prompts.get(focus, focus_prompts["general"])
        
        prompt = f"""Suggest improvements for this {language} code.

{focus_text}

**Code:**
```{language.lower()}
{code[:3500]}
```

Provide:
1. **Current Issues**: Problems with the current code
2. **Improved Code**: Refactored version with improvements
3. **Changes Made**: List of specific changes and why
4. **Best Practices**: Relevant best practices applied

Show the improved code in a code block."""

        try:
            response = self.ollama.generate(prompt, model="llama3.1:8b")
            
            # Extract improved code
            code_match = re.search(r'```[\w]*\n(.*?)```', response, re.DOTALL)
            improved_code = code_match.group(1).strip() if code_match else None
            
            return {
                "status": "success",
                "suggestions": response,
                "improved_code": improved_code,
                "focus_area": focus
            }
        except Exception as e:
            return {"error": f"Suggestion generation failed: {e}"}
    
    def _extract_error_type(self, error_text: str) -> Optional[str]:
        """Extract error type from error text"""
        # Python errors
        python_match = re.search(r'(\w+Error|\w+Exception):', error_text)
        if python_match:
            return python_match.group(1)
        
        # JavaScript errors
        js_match = re.search(r'(TypeError|ReferenceError|SyntaxError|RangeError):', error_text)
        if js_match:
            return js_match.group(1)
        
        return None


# Export plugin instance
plugin = Plugin()
