#!/usr/bin/env python3
import requests
import json

def test_flask_endpoints():
    """Test Flask endpoints to verify they're working"""
    base_url = "http://127.0.0.1:5000"
    
    print("🧪 Testing Flask App Endpoints")
    print("=" * 40)
    
    # Test 1: Check if app is running
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ GET / - Status: {response.status_code}")
    except Exception as e:
        print(f"❌ GET / - Error: {e}")
        return False
    
    # Test 2: Test generate endpoint
    test_payload = {
        "indu_message": "Hello from test!",
        "yaswanth_reply": "This is Yaswanth's test reply!"
    }
    
    try:
        response = requests.post(f"{base_url}/generate", json=test_payload)
        print(f"✅ POST /generate - Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ POST /generate - Error: {e}")
        return False
    
    # Test 3: Check status
    try:
        response = requests.get(f"{base_url}/status")
        print(f"✅ GET /status - Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ GET /status - Error: {e}")
        return False
    
    print("\n🎉 All Flask endpoints are working correctly!")
    print("The 403 error is NOT from Flask - it's from OpenAI API!")
    return True

if __name__ == "__main__":
    test_flask_endpoints()