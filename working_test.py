#!/usr/bin/env python3
"""
Working Test - Simple and Reliable
Tests the Ultimate 16-API Fallback System
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.append('.')

async def test_simple_ai_call():
    """Test simple AI call"""
    print("🧪 TESTING SIMPLE AI CALL")
    print("=" * 40)
    
    try:
        from ultimate_16_api_fallback_manager import generate_ai_response
        
        # Test 1: Simple math
        print("🔍 Test 1: Simple math")
        response = await generate_ai_response("What is 2+2? Answer with just the number.")
        print(f"✅ Response: {response}")
        
        # Test 2: Simple question
        print("\n🔍 Test 2: Simple question")
        response = await generate_ai_response("Say 'Hello World'")
        print(f"✅ Response: {response}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def test_fallback_manager():
    """Test the fallback manager directly"""
    print("\n🧪 TESTING FALLBACK MANAGER")
    print("=" * 40)
    
    try:
        from ultimate_16_api_fallback_manager import Ultimate16APIFallbackManager
        
        manager = Ultimate16APIFallbackManager()
        
        # Test with simple message
        messages = [{"role": "user", "content": "Say 'Test successful'"}]
        result = await manager.generate_with_fallback(messages, max_tokens=50)
        
        print(f"✅ Provider: {result['provider']}")
        print(f"✅ Success: {result['success']}")
        print(f"✅ Response: {result['content']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def test_provider_stats():
    """Test provider statistics"""
    print("\n🧪 TESTING PROVIDER STATS")
    print("=" * 40)
    
    try:
        from ultimate_16_api_fallback_manager import Ultimate16APIFallbackManager
        
        manager = Ultimate16APIFallbackManager()
        stats = manager.get_provider_stats()
        
        print(f"✅ Total Providers: {stats['total_providers']}")
        print(f"✅ Healthy Providers: {stats['healthy_providers']}")
        print(f"✅ Success Rate: {stats['success_rate']:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def main():
    """Main test function"""
    print("🚀 WORKING TEST - ULTIMATE 16-API SYSTEM")
    print("=" * 60)
    
    tests = [
        ("Simple AI Call", test_simple_ai_call),
        ("Fallback Manager", test_fallback_manager),
        ("Provider Stats", test_provider_stats)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            result = await test_func()
            if result:
                print(f"✅ {test_name}: PASSED")
                passed += 1
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print(f"\n📊 TEST RESULTS")
    print("=" * 30)
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    print(f"📈 Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! System is working!")
    else:
        print(f"\n⚠️  {total - passed} tests failed. Check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)