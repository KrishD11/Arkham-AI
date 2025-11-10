#!/usr/bin/env python3
"""Quick test script to verify deployment"""

import requests
import sys
import json

BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080"

def test_endpoint(name, method, path, data=None, expected_status=200):
    """Test an API endpoint"""
    url = f"{BASE_URL}{path}"
    print(f"\n🧪 Testing {name}...")
    print(f"   {method} {url}")
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, headers={"Content-Type": "application/json"}, timeout=10)
        else:
            print(f"   ❌ Unsupported method: {method}")
            return False
        
        if response.status_code == expected_status:
            print(f"   ✅ Success ({response.status_code})")
            if response.headers.get("content-type", "").startswith("application/json"):
                result = response.json()
                print(f"   📄 Response: {json.dumps(result, indent=2)[:200]}...")
            return True
        else:
            print(f"   ❌ Failed ({response.status_code})")
            print(f"   Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def main():
    print(f"🚀 Testing Arkham AI Agent at {BASE_URL}")
    print("=" * 60)
    
    tests = [
        ("Health Check", "GET", "/"),
        ("API Health", "GET", "/api/health"),
        ("Agent Info", "GET", "/api/agent/info"),
        ("Agent Query", "POST", "/api/agent/query", {
            "message": "What is your status?",
            "user_id": "test-user"
        }),
        ("Get Trade News", "GET", "/api/data/trade-news?limit=5"),
        ("Get Political Data", "GET", "/api/data/political"),
        ("Get Port Data", "GET", "/api/data/ports"),
        ("Assess Route", "POST", "/api/routes/assess", {
            "origin": "Taiwan",
            "destination": "Los Angeles",
            "route_regions": ["South China Sea"]
        }),
        ("Get Routes", "GET", "/api/routes"),
    ]
    
    passed = 0
    failed = 0
    
    for name, method, path, *args in tests:
        data = args[0] if args else None
        if test_endpoint(name, method, path, data):
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())

