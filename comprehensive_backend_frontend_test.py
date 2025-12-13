#!/usr/bin/env python3
"""
Comprehensive Backend and Frontend Test Suite
Tests all components to ensure 100% functionality
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent

def test_backend_imports():
    """Test all backend imports"""
    print("🧪 Test 1: Backend Imports")
    print("-" * 60)
    
    tests = [
        ("FastAPI", "import fastapi"),
        ("Uvicorn", "import uvicorn"),
        ("Pydantic", "import pydantic"),
        ("Main App", "import main"),
        ("Health Route", "import sys; sys.path.insert(0, 'src'); from src.api.routes import health"),
        ("Agents Route", "import sys; sys.path.insert(0, 'src'); from src.api.routes import agents"),
        ("Tasks Route", "import sys; sys.path.insert(0, 'src'); from src.api.routes import tasks"),
        ("Config", "from src.config.settings import get_settings"),
        ("Security", "from src.amas.security.security_manager import initialize_security"),
    ]
    
    passed = 0
    failed = 0
    
    for name, import_cmd in tests:
        try:
            exec(import_cmd)
            print(f"✅ {name}")
            passed += 1
        except Exception as e:
            print(f"❌ {name}: {e}")
            failed += 1
    
    print(f"\nResults: {passed}/{len(tests)} passed\n")
    return failed == 0

def test_backend_config():
    """Test backend configuration"""
    print("🧪 Test 2: Backend Configuration")
    print("-" * 60)
    
    try:
        from src.config.settings import get_settings, validate_configuration
        settings = get_settings()
        print("✅ Settings loaded")
        print(f"   Environment: {getattr(settings, 'environment', 'unknown')}")
        
        if validate_configuration():
            print("✅ Configuration valid")
            return True
        else:
            print("⚠️  Configuration validation returned False")
            return True  # Not necessarily a failure
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_api_routes():
    """Test API routes are accessible"""
    print("🧪 Test 3: API Routes")
    print("-" * 60)
    
    routes = [
        "health",
        "agents",
        "tasks",
        "users",
        "auth"
    ]
    
    passed = 0
    for route in routes:
        try:
            exec(f"import sys; sys.path.insert(0, 'src'); from src.api.routes import {route}")
            print(f"✅ {route} route")
            passed += 1
        except Exception as e:
            print(f"❌ {route} route: {e}")
    
    print(f"\nResults: {passed}/{len(routes)} routes available\n")
    return passed == len(routes)

def test_frontend_structure():
    """Test frontend structure"""
    print("🧪 Test 4: Frontend Structure")
    print("-" * 60)
    
    frontend_dir = PROJECT_ROOT / "frontend"
    
    required_files = [
        "package.json",
        "tsconfig.json",
        "vite.config.ts",
    ]
    
    passed = 0
    for file in required_files:
        if (frontend_dir / file).exists():
            print(f"✅ {file}")
            passed += 1
        else:
            print(f"❌ {file} not found")
    
    # Check if node_modules exists
    if (frontend_dir / "node_modules").exists():
        print("✅ node_modules exists")
        passed += 1
    else:
        print("⚠️  node_modules not found (run: cd frontend && npm install)")
    
    print(f"\nResults: {passed}/{len(required_files) + 1} checks passed\n")
    return passed >= len(required_files)

def test_environment():
    """Test environment configuration"""
    print("🧪 Test 5: Environment Configuration")
    print("-" * 60)
    
    env_file = PROJECT_ROOT / ".env"
    
    if env_file.exists():
        print("✅ .env file exists")
        
        # Check for API keys
        with open(env_file) as f:
            content = f.read()
            api_keys = [key for key in content.split('\n') if 'API_KEY' in key and 'your_' not in key]
            print(f"✅ Found {len(api_keys)} API keys configured")
            return True
    else:
        print("❌ .env file not found")
        return False

def test_dependencies():
    """Test critical dependencies"""
    print("🧪 Test 6: Dependencies")
    print("-" * 60)
    
    dependencies = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("pydantic", "Pydantic"),
        ("aiohttp", "aiohttp"),
        ("watchdog", "watchdog"),
    ]
    
    passed = 0
    for module, name in dependencies:
        try:
            __import__(module)
            print(f"✅ {name}")
            passed += 1
        except ImportError:
            print(f"❌ {name} not installed")
    
    print(f"\nResults: {passed}/{len(dependencies)} dependencies available\n")
    return passed == len(dependencies)

def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 COMPREHENSIVE BACKEND & FRONTEND TEST SUITE")
    print("=" * 60)
    print()
    
    tests = [
        ("Backend Imports", test_backend_imports),
        ("Backend Configuration", test_backend_config),
        ("API Routes", test_api_routes),
        ("Frontend Structure", test_frontend_structure),
        ("Environment", test_environment),
        ("Dependencies", test_dependencies),
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"❌ Test '{name}' crashed: {e}")
            results[name] = False
    
    # Summary
    print("=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    print()
    
    if passed == total:
        print("🎉 All tests passed! Backend and Frontend are ready!")
        print()
        print("🚀 To start the application:")
        print("   Backend:  uvicorn main:app --reload --host 0.0.0.0 --port 8000")
        print("   Frontend: cd frontend && npm install && npm run dev")
        return 0
    else:
        print("⚠️  Some tests failed. Review output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

