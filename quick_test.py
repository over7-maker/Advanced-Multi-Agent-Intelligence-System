#!/usr/bin/env python3
"""
Quick Test Script for Multi-API System
Tests all components quickly and provides immediate feedback
"""

import os
import sys
from ai_service_manager import AIServiceManager

def test_ai_manager():
    """Test the AI service manager"""
    print("🤖 Testing AI Service Manager...")
    
    try:
        manager = AIServiceManager()
        
        # Check available providers
        available = manager.get_available_providers()
        print(f"✅ Found {len(available)} available providers")
        
        for provider in available:
            print(f"  - {provider.name}: {provider.model}")
        
        # Test basic functionality
        if available:
            print("\n🧪 Testing basic AI functionality...")
            response, provider, error = manager.generate_response("Hello! Please respond with 'Test successful'.")
            
            if response:
                print(f"✅ AI response successful using {provider}")
                print(f"   Response: {response[:100]}...")
                return True
            else:
                print(f"❌ AI response failed: {error}")
                return False
        else:
            print("❌ No AI providers available")
            return False
            
    except Exception as e:
        print(f"❌ AI Manager test failed: {e}")
        return False

def test_environment():
    """Test environment variables"""
    print("\n🔧 Testing Environment Variables...")
    
    required_vars = [
        'DEEPSEEK_API_KEY',
        'GLM_API_KEY', 
        'GROK_API_KEY',
        'KIMI_API_KEY',
        'QWEN_API_KEY',
        'GPTOSS_API_KEY'
    ]
    
    found_vars = []
    missing_vars = []
    
    for var in required_vars:
        if os.getenv(var):
            found_vars.append(var)
            print(f"  ✅ {var}: Set")
        else:
            missing_vars.append(var)
            print(f"  ❌ {var}: Missing")
    
    print(f"\n📊 Environment Status: {len(found_vars)}/{len(required_vars)} variables set")
    
    if missing_vars:
        print(f"⚠️ Missing variables: {', '.join(missing_vars)}")
        print("   Please set these in GitHub Secrets or environment")
        return False
    else:
        print("✅ All environment variables are set")
        return True

def test_imports():
    """Test required imports"""
    print("\n📦 Testing Required Imports...")
    
    try:
        import openai
        print("  ✅ openai: Available")
    except ImportError:
        print("  ❌ openai: Missing - run: pip install openai")
        return False
    
    try:
        import requests
        print("  ✅ requests: Available")
    except ImportError:
        print("  ❌ requests: Missing - run: pip install requests")
        return False
    
    try:
        from ai_service_manager import AIServiceManager
        print("  ✅ ai_service_manager: Available")
    except ImportError:
        print("  ❌ ai_service_manager: Missing - check file exists")
        return False
    
    print("✅ All required imports available")
    return True

def main():
    """Main test function"""
    print("🧪 Quick Multi-API System Test")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Environment Test", test_environment),
        ("AI Manager Test", test_ai_manager)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your multi-API system is ready!")
        print("\n🚀 Next steps:")
        print("1. Push your changes to GitHub")
        print("2. Check GitHub Actions tab for workflow runs")
        print("3. Create a test issue to verify auto-response")
        print("4. Monitor the system performance")
    else:
        print("⚠️ Some tests failed. Please fix the issues above.")
        print("\n🔧 Troubleshooting:")
        print("1. Check API keys in GitHub Secrets")
        print("2. Verify repository permissions")
        print("3. Install missing dependencies")
        print("4. Check file paths and imports")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Quick test failed: {e}")
        sys.exit(1)