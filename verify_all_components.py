#!/usr/bin/env python3
"""
Comprehensive verification script for all AMAS components
"""
import requests
import json
from typing import Dict, List, Tuple

BASE_URL = "http://localhost:8000/api/v1"

def test_endpoint(method: str, endpoint: str, data: dict = None, token: str = None) -> Tuple[bool, str, int]:
    """Test an API endpoint"""
    try:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers, timeout=5)
        elif method == "POST":
            response = requests.post(f"{BASE_URL}{endpoint}", json=data, headers=headers, timeout=5)
        elif method == "PUT":
            response = requests.put(f"{BASE_URL}{endpoint}", json=data, headers=headers, timeout=5)
        elif method == "DELETE":
            response = requests.delete(f"{BASE_URL}{endpoint}", headers=headers, timeout=5)
        else:
            return False, f"Unknown method: {method}", 0
        
        return response.status_code < 500, f"{response.status_code}: {response.text[:100]}", response.status_code
    except requests.exceptions.ConnectionError:
        return False, "Connection refused - backend not running", 0
    except Exception as e:
        return False, f"Error: {str(e)}", 0

def main():
    print("=" * 80)
    print("AMAS Component Verification")
    print("=" * 80)
    
    # Step 1: Login to get token
    print("\n[1] Testing Authentication...")
    login_success, login_msg, login_code = test_endpoint("POST", "/login", {
        "username": "admin",
        "password": "admin123"
    })
    
    token = None
    if login_success and login_code == 200:
        try:
            response = requests.post(f"{BASE_URL}/login", json={
                "username": "admin",
                "password": "admin123"
            }, timeout=5)
            if response.status_code == 200:
                token = response.json().get("access_token")
                print(f"✅ Login successful - Token: {token[:50]}...")
        except:
            pass
    
    if not token:
        print(f"❌ Login failed: {login_msg}")
        print("⚠️  Continuing with unauthenticated tests...")
    
    # Step 2: Test all endpoints
    endpoints = [
        # Authentication
        ("GET", "/me", None, "Get current user"),
        
        # Tasks
        ("GET", "/tasks?limit=10&offset=0", None, "List tasks"),
        ("POST", "/tasks", {
            "title": "Test Task",
            "description": "Test Description",
            "task_type": "intelligence_gathering",
            "target": "test.com",
            "priority": 5
        }, "Create task"),
        
        # Agents
        ("GET", "/agents", None, "List agents"),
        ("GET", "/agents/performance", None, "Get agent performance"),
        
        # Integrations
        ("GET", "/integrations", None, "List integrations"),
        
        # System
        ("GET", "/system/metrics", None, "Get system metrics"),
        ("GET", "/system/health", None, "Get system health"),
        ("GET", "/health", None, "Health check"),
        
        # Analytics
        ("GET", "/analytics/tasks", None, "Get task analytics"),
        ("GET", "/analytics/agents", None, "Get agent analytics"),
        
        # Predictions
        ("POST", "/predictions/predict/task", {
            "task_type": "intelligence_gathering",
            "target": "test.com"
        }, "Predict task outcome"),
        
        # Metrics
        ("GET", "/metrics", None, "Prometheus metrics"),
    ]
    
    print("\n[2] Testing All Endpoints...")
    print("-" * 80)
    
    results = []
    for method, endpoint, data, description in endpoints:
        success, msg, code = test_endpoint(method, endpoint, data, token)
        status = "✅" if success else "❌"
        results.append((status, description, endpoint, code, msg))
        print(f"{status} {description:40} {endpoint:30} [{code}]")
        if not success and code != 404:
            print(f"   └─ {msg[:70]}")
    
    # Summary
    print("\n" + "=" * 80)
    print("Summary")
    print("=" * 80)
    
    successful = sum(1 for r in results if r[0] == "✅")
    total = len(results)
    
    print(f"✅ Successful: {successful}/{total}")
    print(f"❌ Failed: {total - successful}/{total}")
    
    # List failed endpoints
    failed = [r for r in results if r[0] == "❌"]
    if failed:
        print("\nFailed Endpoints:")
        for status, desc, endpoint, code, msg in failed:
            print(f"  ❌ {desc}: {endpoint} [{code}]")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()

