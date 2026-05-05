"""
JARVIS Feature Verification Script
Tests all major features to ensure they work
"""
import requests
import sys
import json
from typing import Dict, Any

API_BASE = "http://localhost:8000"


def test_endpoint(name: str, method: str, url: str, data: Dict = None) -> bool:
    """Test an API endpoint"""
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        else:
            return False
        
        if response.status_code in (200, 201):
            print(f"  ✅ {name}: OK")
            return True
        else:
            print(f"  ❌ {name}: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ {name}: {e}")
        return False


def main():
    print("=" * 50)
    print("  JARVIS Feature Verification")
    print("=" * 50)
    print()
    
    # Check if backend is running
    try:
        requests.get(f"{API_BASE}/health", timeout=2)
    except:
        print("❌ Backend not running. Start with: python main.py")
        return 1
    
    results = []
    
    # 1. Health Check
    print("[1] Health & Status")
    results.append(test_endpoint("Root endpoint", "GET", f"{API_BASE}/"))
    results.append(test_endpoint("Health check", "GET", f"{API_BASE}/health"))
    print()
    
    # 2. Chat API
    print("[2] Chat API")
    results.append(test_endpoint(
        "Chat endpoint", "POST", f"{API_BASE}/api/chat/",
        {"prompt": "Say 'test passed' in one word", "model": "llama3.1:8b"}
    ))
    results.append(test_endpoint("List models", "GET", f"{API_BASE}/api/chat/models"))
    print()
    
    # 3. Screen API
    print("[3] Screen API")
    results.append(test_endpoint("List monitors", "GET", f"{API_BASE}/api/screen/monitors"))
    results.append(test_endpoint("Capture screen", "POST", f"{API_BASE}/api/screen/capture"))
    print()
    
    # 4. Control API
    print("[4] Control API")
    results.append(test_endpoint("Mouse position", "GET", f"{API_BASE}/api/control/mouse/position"))
    results.append(test_endpoint("System info", "GET", f"{API_BASE}/api/control/system/info"))
    results.append(test_endpoint("List apps", "GET", f"{API_BASE}/api/control/app/list"))
    print()
    
    # 5. Voice API
    print("[5] Voice API")
    results.append(test_endpoint("Voice status", "GET", f"{API_BASE}/api/voice/status"))
    results.append(test_endpoint("List voices", "GET", f"{API_BASE}/api/voice/voices"))
    print()
    
    # 6. Agent API
    print("[6] Agent API")
    results.append(test_endpoint("List actions", "GET", f"{API_BASE}/api/agent/actions"))
    results.append(test_endpoint("List agents", "GET", f"{API_BASE}/api/agent/list"))
    print()
    
    # 7. Plugin API
    print("[7] Plugin API")
    results.append(test_endpoint("List plugins", "GET", f"{API_BASE}/api/plugins/"))
    results.append(test_endpoint(
        "System stats plugin", "POST", f"{API_BASE}/api/plugins/system_stats/run",
        {"command": "stats", "params": {}}
    ))
    print()
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("=" * 50)
    print(f"  Results: {passed}/{total} tests passed")
    print("=" * 50)
    
    if passed == total:
        print("✅ All features working!")
        return 0
    else:
        print("⚠️  Some features may need configuration")
        return 1


if __name__ == "__main__":
    sys.exit(main())
