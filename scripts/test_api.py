#!/usr/bin/env python3
"""
JARVIS Backend API Test Script
Tests all major endpoints to verify functionality
"""
import requests
import json
import sys
import os
from time import sleep

BASE_URL = "http://localhost:8000"

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}  {text}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.RESET}\n")


def print_test(name, passed, details=""):
    status = f"{Colors.GREEN}✓ PASS{Colors.RESET}" if passed else f"{Colors.RED}✗ FAIL{Colors.RESET}"
    print(f"  {status}  {name}")
    if details and not passed:
        print(f"         {Colors.YELLOW}{details}{Colors.RESET}")


def test_root():
    """Test root endpoint"""
    try:
        r = requests.get(f"{BASE_URL}/", timeout=5)
        passed = r.status_code == 200 and r.json().get("status") == "running"
        print_test("Root endpoint", passed)
        return passed
    except Exception as e:
        print_test("Root endpoint", False, str(e))
        return False


def test_health():
    """Test health check"""
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        passed = r.status_code == 200 and r.json().get("status") == "healthy"
        print_test("Health check", passed)
        return passed
    except Exception as e:
        print_test("Health check", False, str(e))
        return False


def test_chat_models():
    """Test chat models listing"""
    try:
        r = requests.get(f"{BASE_URL}/api/chat/models", timeout=10)
        passed = r.status_code == 200 and "models" in r.json()
        models = r.json().get("models", [])
        print_test(f"Chat models ({len(models)} found)", passed)
        return passed
    except Exception as e:
        print_test("Chat models", False, str(e))
        return False


def test_chat_simple():
    """Test simple chat"""
    try:
        r = requests.post(
            f"{BASE_URL}/api/chat/",
            json={"prompt": "Hello, respond with just 'Hi!'", "model": "llama3.1:8b"},
            timeout=60
        )
        passed = r.status_code == 200 and "response" in r.json()
        print_test("Simple chat", passed)
        return passed
    except Exception as e:
        print_test("Simple chat", False, str(e))
        return False


def test_voice_status():
    """Test voice module status"""
    try:
        r = requests.get(f"{BASE_URL}/api/voice/status", timeout=5)
        passed = r.status_code == 200
        data = r.json()
        stt = "✓" if data.get("stt_available") else "✗"
        tts = "✓" if data.get("tts_available") else "✗"
        print_test(f"Voice status (STT:{stt} TTS:{tts})", passed)
        return passed
    except Exception as e:
        print_test("Voice status", False, str(e))
        return False


def test_voice_voices():
    """Test available voices listing"""
    try:
        r = requests.get(f"{BASE_URL}/api/voice/voices", timeout=5)
        passed = r.status_code == 200 and "voices" in r.json()
        voices = r.json().get("voices", [])
        print_test(f"Voice list ({len(voices)} voices)", passed)
        return passed
    except Exception as e:
        print_test("Voice list", False, str(e))
        return False


def test_screen_read():
    """Test screen capture"""
    try:
        r = requests.post(f"{BASE_URL}/api/screen/read", timeout=30)
        passed = r.status_code == 200
        print_test("Screen capture", passed)
        return passed
    except Exception as e:
        print_test("Screen capture", False, str(e))
        return False


def test_control_mouse():
    """Test mouse position"""
    try:
        r = requests.get(f"{BASE_URL}/api/control/mouse/position", timeout=5)
        passed = r.status_code == 200 and "x" in r.json() and "y" in r.json()
        print_test("Mouse position", passed)
        return passed
    except Exception as e:
        print_test("Mouse position", False, str(e))
        return False


def test_plugins_list():
    """Test plugins listing"""
    try:
        r = requests.get(f"{BASE_URL}/api/plugins/", timeout=5)
        passed = r.status_code == 200 and isinstance(r.json(), list)
        plugins = r.json() if passed else []
        print_test(f"Plugins list ({len(plugins)} plugins)", passed)
        return passed
    except Exception as e:
        print_test("Plugins list", False, str(e))
        return False


def test_plugin_system_stats():
    """Test system stats plugin"""
    try:
        r = requests.post(
            f"{BASE_URL}/api/plugins/system_stats/run",
            json={"command": "stats"},
            timeout=10
        )
        passed = r.status_code == 200 and "cpu_percent" in r.json().get("result", {})
        print_test("System stats plugin", passed)
        return passed
    except Exception as e:
        print_test("System stats plugin", False, str(e))
        return False


def test_agent_actions():
    """Test agent actions listing"""
    try:
        r = requests.get(f"{BASE_URL}/api/agent/actions", timeout=5)
        passed = r.status_code == 200 and "actions" in r.json()
        actions = r.json().get("actions", [])
        print_test(f"Agent actions ({len(actions)} actions)", passed)
        return passed
    except Exception as e:
        print_test("Agent actions", False, str(e))
        return False


def test_agent_list():
    """Test running agents list"""
    try:
        r = requests.get(f"{BASE_URL}/api/agent/list", timeout=5)
        passed = r.status_code == 200 and "agents" in r.json()
        print_test("Agent list", passed)
        return passed
    except Exception as e:
        print_test("Agent list", False, str(e))
        return False


def main():
    print_header("JARVIS Backend API Tests")
    
    print(f"{Colors.YELLOW}Testing: {BASE_URL}{Colors.RESET}\n")
    
    results = []
    
    # Core Tests
    print(f"{Colors.BOLD}Core Endpoints:{Colors.RESET}")
    results.append(test_root())
    results.append(test_health())
    
    # Chat Tests
    print(f"\n{Colors.BOLD}Chat API:{Colors.RESET}")
    results.append(test_chat_models())
    # Uncomment for full LLM test (requires Ollama running)
    # results.append(test_chat_simple())
    
    # Voice Tests
    print(f"\n{Colors.BOLD}Voice API:{Colors.RESET}")
    results.append(test_voice_status())
    results.append(test_voice_voices())
    
    # Screen Tests
    print(f"\n{Colors.BOLD}Screen API:{Colors.RESET}")
    results.append(test_screen_read())
    
    # Control Tests
    print(f"\n{Colors.BOLD}Control API:{Colors.RESET}")
    results.append(test_control_mouse())
    
    # Plugin Tests
    print(f"\n{Colors.BOLD}Plugin API:{Colors.RESET}")
    results.append(test_plugins_list())
    results.append(test_plugin_system_stats())
    
    # Agent Tests
    print(f"\n{Colors.BOLD}Agent API:{Colors.RESET}")
    results.append(test_agent_actions())
    results.append(test_agent_list())
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print_header("Test Summary")
    
    if passed == total:
        print(f"  {Colors.GREEN}{Colors.BOLD}All {total} tests passed!{Colors.RESET}")
    else:
        print(f"  {Colors.YELLOW}{passed}/{total} tests passed{Colors.RESET}")
        print(f"  {Colors.RED}{total - passed} tests failed{Colors.RESET}")
    
    print()
    return 0 if passed == total else 1


if __name__ == "__main__":
    # Check if backend is running
    try:
        requests.get(f"{BASE_URL}/", timeout=2)
    except:
        print(f"{Colors.RED}Error: Backend not running at {BASE_URL}{Colors.RESET}")
        print(f"{Colors.YELLOW}Start backend with: python main.py{Colors.RESET}")
        sys.exit(1)
    
    sys.exit(main())
